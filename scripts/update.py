#!/usr/bin/env python3
"""
Fetches news and market data for the site and writes JSON files into docs/data/.

Runs automatically on GitHub Actions every few hours (see .github/workflows/update.yml).
Uses only the Python standard library, so there is nothing to install.

Run locally with:   python scripts/update.py
Test without internet:   python scripts/update.py --offline   (re-processes existing articles only)
"""
import csv
import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"

MAX_AGE_DAYS = 21          # drop articles older than this
MAX_ITEMS = 900            # cap on stored articles
EXCERPT_CHARS = 240        # how much of the publisher's own summary to show (0 = none)
MAX_TRANSLATIONS = 40      # per run, to stay within the free translation service's limits
USER_AGENT = "CargoChroniclesNewsReader/1.0 (personal, non-commercial news overview; links back to every source)"


# ---------------------------------------------------------------- helpers

def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    last = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - report any network error
            last = e
            time.sleep(2)
    raise last


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "figure", "figcaption", "table"):
            self.skip += 1
        if tag in ("p", "br", "div", "li", "h1", "h2", "h3"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "figure", "figcaption", "table") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def strip_html(s):
    if not s:
        return ""
    p = _Text()
    try:
        p.feed(s)
        p.close()
        text = "".join(p.parts)
    except Exception:  # noqa: BLE001
        text = re.sub(r"<[^>]+>", " ", s)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


BOILERPLATE = [
    r"The post .{0,300}? appeared first on .{0,80}?\.?$",
    r"You need to be logged in to view this content\..*$",
    r"Continue reading.*$",
    r"Read more.*$",
    r"\s*Source:\s*\S.*$",
]


def make_excerpt(desc, title):
    text = desc or ""
    for pat in BOILERPLATE:
        text = re.sub(pat, "", text, flags=re.I | re.S).strip()
    text = re.sub(r"\[(?:…|&#8230;|\.\.\.)\]", "…", text).strip()
    if not text or EXCERPT_CHARS <= 0:
        return ""
    if text.lower().startswith(title.lower()[:40]):
        text = text[len(title):].strip(" .:-–")
    if len(text) <= EXCERPT_CHARS:
        return text
    cut = text[:EXCERPT_CHARS]
    end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if end > EXCERPT_CHARS * 0.55:
        return cut[: end + 1]
    return cut.rsplit(" ", 1)[0].rstrip(",;:–-") + " …"


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except (TypeError, ValueError, IndexError):
        pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def local(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def child_text(el, *names):
    for c in el:
        if local(c.tag) in names and (c.text or "").strip():
            return c.text.strip()
    return ""


# ---------------------------------------------------------------- feed parsing

def parse_feed(raw):
    """Return a list of {title, link, date, desc, cats} from RSS 2.0 or Atom."""
    raw = raw.lstrip(b"\xef\xbb\xbf \r\n\t")
    root = ET.fromstring(raw)
    items = []
    for el in root.iter():
        name = local(el.tag)
        if name == "item":  # RSS
            link = child_text(el, "link")
            if not link:
                for c in el:
                    if local(c.tag) == "guid" and (c.get("isPermaLink", "true") != "false"):
                        link = (c.text or "").strip()
            desc = child_text(el, "description") or child_text(el, "encoded")
            items.append({
                "title": strip_html(child_text(el, "title")),
                "link": link,
                "date": parse_date(child_text(el, "pubDate", "date", "published", "updated")),
                "desc": strip_html(desc),
                "cats": [strip_html(c.text) for c in el if local(c.tag) == "category" and c.text],
            })
        elif name == "entry":  # Atom
            link = ""
            for c in el:
                if local(c.tag) == "link" and c.get("rel", "alternate") == "alternate":
                    link = c.get("href", "")
                    break
            items.append({
                "title": strip_html(child_text(el, "title")),
                "link": link,
                "date": parse_date(child_text(el, "published", "updated")),
                "desc": strip_html(child_text(el, "summary", "content")),
                "cats": [c.get("term", "") for c in el if local(c.tag) == "category"],
            })
    return [i for i in items if i["title"] and i["link"]]


def parse_html_links(raw, base, pattern):
    """Headline links from a front page that has no feed."""
    text = raw.decode("utf-8", "replace")
    rx = re.compile(pattern)
    seen, out = set(), []
    for href, inner in re.findall(r"<a\s[^>]*?href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", text, flags=re.S | re.I):
        url = urllib.parse.urljoin(base, html.unescape(href)).split("#")[0]
        if not rx.match(url) or url in seen:
            continue
        title = strip_html(inner)
        if len(title) < 12 or title.startswith("http"):
            continue
        paywall = False
        if title.upper().startswith("INSIDE"):
            paywall = True
            title = re.sub(r"^(INSIDE\s*)+", "", title, flags=re.I).strip()
        seen.add(url)
        out.append({"title": title, "link": url, "date": None, "desc": "", "cats": [], "paywall": paywall})
    return out[:40]


# ---------------------------------------------------------------- keyword & term matching

def keyword_regex(words):
    parts = []
    for w in sorted({w.strip().lower() for w in words if w.strip()}, key=len, reverse=True):
        if w.endswith("*"):
            parts.append(re.escape(w[:-1]) + r"\w*")
        else:
            parts.append(re.escape(w))
    if not parts:
        return None
    return re.compile(r"(?<!\w)(?:" + "|".join(parts) + r")(?!\w)", re.I)


def count_hits(rx, text):
    return len(rx.findall(text)) if (rx and text) else 0


class TermMatcher:
    """Finds glossary terms in text. Mirrors the matching done in the browser (assets/app.js)."""

    def __init__(self, glossary):
        ci, cs, self.rx_list = {}, {}, []
        for t in glossary["terms"]:
            for m in t.get("m", []):
                if m.startswith("~"):
                    self.rx_list.append((re.compile(r"(?<!\w)" + m[1:] + r"(?!\w)"), t["id"]))
                elif m.startswith("="):
                    cs.setdefault(m[1:], t["id"])
                else:
                    ci.setdefault(m.lower(), t["id"])
        self.ci, self.cs = ci, cs
        self.rx_ci = self._alt(ci.keys(), re.I)
        self.rx_cs = self._alt(cs.keys(), 0)

    @staticmethod
    def _alt(keys, flags):
        keys = sorted(keys, key=len, reverse=True)
        if not keys:
            return None
        return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(k) for k in keys) + r")(?!\w)", flags)

    def find(self, text):
        hits = []
        if self.rx_ci:
            hits += [(m.start(), m.end(), self.ci[m.group(0).lower()]) for m in self.rx_ci.finditer(text)]
        if self.rx_cs:
            hits += [(m.start(), m.end(), self.cs[m.group(0)]) for m in self.rx_cs.finditer(text)]
        for rx, tid in self.rx_list:
            hits += [(m.start(), m.end(), tid) for m in rx.finditer(text)]
        hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
        out, last_end = [], -1
        for s, e, tid in hits:
            if s < last_end:
                continue
            out.append(tid)
            last_end = e
        return out

    def terms(self, *texts, limit=10):
        ordered = []
        for t in texts:
            for tid in self.find(t or ""):
                if tid not in ordered:
                    ordered.append(tid)
        return ordered[:limit]


# ---------------------------------------------------------------- language

NO_WORDS = set("og i på er til med som for det en av har ikke skal fra å ble vil nye etter mot ved kan blir også om seg sin får mer dette være når".split())
EN_WORDS = set("the and of to in is for on with as by from at will has its are be new after over this that was were their than".split())


def detect_lang(text):
    words = re.findall(r"[a-zæøåA-ZÆØÅ]+", (text or "").lower())
    no = sum(w in NO_WORDS for w in words)
    en = sum(w in EN_WORDS for w in words)
    if "æ" in text or "ø" in text or "å" in text:
        no += 2
    return "no" if no > en else "en"


_translations = {"count": 0}


def translate(text, src):
    """Free translation through the MyMemory API (no key needed, daily limit applies)."""
    if not text or _translations["count"] >= MAX_TRANSLATIONS:
        return None
    _translations["count"] += 1
    q = urllib.parse.urlencode({"q": text[:480], "langpair": f"{src}|en"})
    try:
        data = json.loads(http_get("https://api.mymemory.translated.net/get?" + q, timeout=15))
        out = (data.get("responseData") or {}).get("translatedText")
        return html.unescape(out) if out and "MYMEMORY WARNING" not in out else None
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------- classification

class Classifier:
    def __init__(self, segcfg, glossary):
        self.segments = segcfg["segments"]
        self.seg_rx = {s["id"]: keyword_regex(s.get("keywords", [])) for s in self.segments}
        self.sub_rx = {}
        for s in self.segments:
            for sub in s.get("subs", []):
                if sub.get("keywords"):
                    self.sub_rx[(s["id"], sub["id"])] = keyword_regex(sub["keywords"])
        self.policy_rx = keyword_regex(segcfg.get("policy_keywords", []))
        lv = segcfg.get("levels", {})
        self.local_rx = keyword_regex(lv.get("local", []))
        self.national_rx = keyword_regex(lv.get("national", []))
        self.terms = TermMatcher(glossary)

    def score(self, rx, title, desc, cats):
        return 3 * count_hits(rx, title) + count_hits(rx, desc) + 2 * count_hits(rx, " | ".join(cats))

    def classify(self, src, title, desc, cats):
        segs = list(src.get("segments", []))
        for s in self.segments:
            sid = s["id"]
            if sid in segs:
                continue
            if self.score(self.seg_rx[sid], title, desc, cats) >= 3:
                segs.append(sid)
        subs = list(src.get("subs", []))
        if "freight" in segs:
            for (sid, sub), rx in self.sub_rx.items():
                if sid == "freight" and sub not in subs and self.score(rx, title, desc, cats) >= 2:
                    subs.append(sub)
        text = f"{title} {desc}"
        policy = count_hits(self.policy_rx, title) > 0 or count_hits(self.policy_rx, desc) >= 2
        if count_hits(self.local_rx, text):
            level = "local"
        elif src.get("region") == "NO" or count_hits(self.national_rx, text):
            level = "national"
        else:
            level = "international"
        return segs, subs, policy, level


def make_article(src, raw, clf, fetched_at):
    title = raw["title"].strip()
    desc = raw.get("desc", "")
    lang = src.get("lang", "en")
    if lang == "auto":
        lang = detect_lang(f"{title} {desc}")
    art = {}
    if lang not in ("en", "no"):
        t_title, t_desc = translate(title, lang), translate(desc[:400], lang) if desc else None
        if t_title:
            art.update({"orig_title": title, "orig_lang": lang})
            title, desc, lang = t_title, (t_desc or desc), "en"
    if src.get("require_keywords"):
        rx = keyword_regex(src["require_keywords"])
        if not count_hits(rx, f"{title} {desc}"):
            return None
    segs, subs, policy, level = clf.classify(src, title, desc, raw.get("cats", []))
    if src.get("auto") and not segs:
        return None  # not relevant enough for any section
    if not segs:
        return None
    link = raw["link"].strip()
    clean_link = re.sub(r"[?&]utm_[^&]+", "", link).rstrip("?&")
    published = raw.get("date")
    upcoming = False
    if published and published > fetched_at + timedelta(hours=1):
        upcoming, published = True, fetched_at  # calendar items announce future events
    art.update({
        "id": hashlib.sha1(clean_link.encode()).hexdigest()[:12],
        "title": title,
        "link": clean_link,
        "source": src["id"],
        "published": iso(published),
        "seen": iso(fetched_at),
        "lang": lang,
        "excerpt": make_excerpt(desc, title),
        "segments": segs,
        "subs": subs,
        "policy": policy,
        "level": level,
        "terms": clf.terms.terms(title, desc),
        "paywall": bool(raw.get("paywall")) or src.get("access") == "members",
    })
    if upcoming:
        art["upcoming"] = True
    return art


# ---------------------------------------------------------------- markets

def fetch_markets(previous):
    start = (now_utc() - timedelta(days=430)).date().isoformat()
    series = dict(previous.get("series", {}))
    status = {}
    try:
        raw = http_get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU&cosd={start}")
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8", "replace"))))[1:]
        pts = [[r[0], round(float(r[1]), 2)] for r in rows if len(r) > 1 and r[1] not in (".", "")]
        if pts:
            series["brent"] = {"label": "Brent crude", "unit": "USD per barrel", "source": "U.S. EIA via FRED",
                               "source_url": "https://fred.stlouisfed.org/series/DCOILBRENTEU", "points": pts}
        status["brent"] = f"ok ({len(pts)} points)"
    except Exception as e:  # noqa: BLE001
        status["brent"] = f"error: {e}"
    try:
        url = ("https://data.norges-bank.no/api/data/EXR/B.USD+EUR.NOK.SP"
               f"?format=csv&startPeriod={start}&locale=en&bom=exclude")
        text = http_get(url).decode("utf-8", "replace")
        delim = ";" if text.count(";") > text.count(",") else ","
        reader = csv.DictReader(io.StringIO(text), delimiter=delim)
        got = {"USD": [], "EUR": []}
        for r in reader:
            cur, d, v = r.get("BASE_CUR"), r.get("TIME_PERIOD"), r.get("OBS_VALUE")
            if cur in got and d and v:
                got[cur].append([d, round(float(v.replace(",", ".")), 4)])
        for cur, key in (("USD", "usdnok"), ("EUR", "eurnok")):
            if got[cur]:
                series[key] = {"label": f"{cur}/NOK", "unit": f"NOK per {cur}", "source": "Norges Bank",
                               "source_url": "https://www.norges-bank.no/en/topics/Statistics/exchange_rates/",
                               "points": sorted(got[cur])}
        status["fx"] = f"ok ({len(got['USD'])} points)"
    except Exception as e:  # noqa: BLE001
        status["fx"] = f"error: {e}"
    return {"updated": iso(now_utc()), "series": series}, status


# ---------------------------------------------------------------- main

def load(name, default):
    p = DATA / name
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def run(offline=False):
    started = now_utc()
    sources = load("sources.json", {})["sources"]
    clf = Classifier(load("segments.json", {}), load("glossary.json", {"terms": []}))
    old = load("articles.json", {"articles": []})
    keep_sample = offline and old.get("sample", False)
    by_id = {a["id"]: a for a in old.get("articles", [])} if (keep_sample or not old.get("sample")) else {}
    status = {}

    for src in sources:
        if not src.get("enabled", True):
            status[src["id"]] = {"state": "paused"}
            continue
        if offline:
            continue
        try:
            if src["type"] == "rss":
                raws = parse_feed(http_get(src["feed"]))
            else:
                raws = parse_html_links(http_get(src["list_url"]), src["list_url"], src["link_pattern"])
            kept = 0
            for pos, raw in enumerate(raws):
                # undated front-page headlines: keep the page's order (top = newest)
                at = started - timedelta(minutes=15 * pos) if src["type"] == "html" else started
                art = make_article(src, raw, clf, at)
                if not art:
                    continue
                prev = by_id.get(art["id"])
                if prev:  # keep first-seen time and any earlier translation
                    art["seen"] = prev.get("seen", art["seen"])
                    if not raw.get("date"):
                        art["published"] = prev.get("published")
                    for k in ("orig_title", "orig_lang"):
                        if k in prev:
                            art[k], art["title"] = prev[k], prev["title"]
                by_id[art["id"]] = art
                kept += 1
            status[src["id"]] = {"state": "ok", "items": len(raws), "kept": kept, "checked": iso(started)}
        except Exception as e:  # noqa: BLE001
            status[src["id"]] = {"state": "error", "error": str(e)[:200], "checked": iso(started)}
            print(f"[{src['id']}] {e}", file=sys.stderr)

    # re-classify everything with the current keyword lists and glossary
    src_by_id = {s["id"]: s for s in sources}
    order = [s["id"] for s in clf.segments]
    for art in by_id.values():
        src = src_by_id.get(art["source"])
        if not src:
            continue
        segs, subs, _policy, _level = clf.classify(src, art["title"], art.get("excerpt", ""), [])
        art["segments"] = sorted(set(art["segments"]) | set(segs), key=lambda s: order.index(s) if s in order else 99)
        art["subs"] = sorted(set(art.get("subs", [])) | set(subs))
        art["terms"] = list(dict.fromkeys(art.get("terms", []) + clf.terms.terms(art["title"], art.get("excerpt", ""))))[:10]

    cutoff = started - timedelta(days=MAX_AGE_DAYS if not keep_sample else 3650)
    arts = [a for a in by_id.values() if (parse_iso(a.get("published") or a["seen"]) or started) >= cutoff]
    arts.sort(key=lambda a: a.get("published") or a["seen"], reverse=True)

    # drop exact duplicate headlines from different sources (keep the first)
    seen_titles, unique = set(), []
    for a in arts:
        key = re.sub(r"\W+", "", a["title"].lower())[:90]
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(a)

    save("articles.json", {"updated": old.get("updated") if keep_sample else iso(started),
                           "sample": keep_sample, "articles": unique[:MAX_ITEMS]})
    if not offline:
        markets, mstatus = fetch_markets(load("markets.json", {}))
        save("markets.json", markets)
        status["_markets"] = mstatus
    save("status.json", {"updated": iso(started), "sources": status})
    print(f"Saved {len(unique[:MAX_ITEMS])} articles.")


if __name__ == "__main__":
    run(offline="--offline" in sys.argv)
