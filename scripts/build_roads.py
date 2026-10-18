#!/usr/bin/env python3
"""Build docs/data/roads.json: traffic volumes on Norway's main freight roads.

Data: Statens vegvesen, NVDB (Nasjonal vegdatabank), object type 540 "Trafikkmengde"
(annual average daily traffic, ÅDT, and the share of long vehicles >= 5.6 m).
Licence: NLOD 2.0 (free to use with attribution).

Runs on GitHub Actions (see .github/workflows/roads.yml). Standard library only.
"""
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data" / "roads.json"
LOG = ROOT / "docs" / "data" / "roads_log.txt"
API = "https://nvdbapiles.atlas.vegvesen.no"
HEADERS = {
    "Accept": "application/json",
    "X-Client": "cargo-chronicles (personal, non-commercial road freight map)",
    "User-Agent": "CargoChroniclesRoadMap/1.0",
}

# Road number as NVDB writes it -> display name
ROADS = [
    ("EV6", "E6"), ("EV18", "E18"), ("EV39", "E39"), ("EV16", "E16"), ("EV134", "E134"),
    ("EV136", "E136"), ("EV10", "E10"), ("EV8", "E8"), ("EV14", "E14"), ("EV12", "E12"),
    ("RV7", "Rv7"), ("RV52", "Rv52"), ("RV2", "Rv2"), ("RV3", "Rv3"), ("RV4", "Rv4"),
    ("RV5", "Rv5"), ("RV9", "Rv9"), ("RV13", "Rv13"), ("RV15", "Rv15"),
]
ADT_CLASSES = [2000, 5000, 10000, 20000, 40000]      # upper bounds; last class is above
TOLERANCE_M = 120                                    # line simplification in metres

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


def get_json(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if attempt == tries - 1:
                raise
            log(f"  retry {attempt + 1} after error: {e}")
            time.sleep(3 * (attempt + 1))


# ---------------------------------------------------------------- UTM 33 (EUREF89) -> lon/lat
def utm33_to_lonlat(e, n):
    a, f = 6378137.0, 1 / 298.257222101
    k0, lon0 = 0.9996, math.radians(15.0)
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    x, y = e - 500000.0, n
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    p1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
          + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
          + (151 * e1 ** 3 / 96) * math.sin(6 * mu) + (1097 * e1 ** 4 / 512) * math.sin(8 * mu))
    c1 = ep2 * math.cos(p1) ** 2
    t1 = math.tan(p1) ** 2
    n1 = a / math.sqrt(1 - e2 * math.sin(p1) ** 2)
    r1 = a * (1 - e2) / (1 - e2 * math.sin(p1) ** 2) ** 1.5
    d = x / (n1 * k0)
    lat = p1 - (n1 * math.tan(p1) / r1) * (
        d ** 2 / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * ep2) * d ** 4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * ep2 - 3 * c1 ** 2) * d ** 6 / 720)
    lon = lon0 + (d - (1 + 2 * t1 + c1) * d ** 3 / 6
                  + (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * ep2 + 24 * t1 ** 2) * d ** 5 / 120) / math.cos(p1)
    return math.degrees(lon), math.degrees(lat)


def parse_wkt(wkt):
    """Return a list of lines; each line is a list of (x, y) in the source CRS."""
    body = wkt[wkt.index("("):]
    lines = []
    for chunk in re.findall(r"\(([^()]+)\)", body):
        pts = []
        for pair in chunk.split(","):
            nums = pair.split()
            if len(nums) >= 2:
                pts.append((float(nums[0]), float(nums[1])))
        if len(pts) >= 2:
            lines.append(pts)
    return lines


def simplify(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        den = math.hypot(dx, dy) or 1e-9
        best, idx = 0.0, None
        for k in range(i + 1, j):
            x0, y0 = pts[k]
            dist = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / den
            if dist > best:
                best, idx = dist, k
        if idx is not None and best > tol:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return [p for p, k in zip(pts, keep) if k]


def length_m(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def adt_class(v):
    for i, ub in enumerate(ADT_CLASSES):
        if v < ub:
            return i
    return len(ADT_CLASSES)


def prop(obj, name):
    for e in obj.get("egenskaper", []):
        if e.get("navn") == name:
            return e.get("verdi")
    return None


REF_RX = re.compile(r"S(\d+)D(\d+)\s+m(\d+)")


def fetch_road(code):
    url = (f"{API}/vegobjekter/api/v4/vegobjekter/540?"
           + urllib.parse.urlencode({"vegsystemreferanse": code, "inkluder": "egenskaper,lokasjon", "antall": 1000}))
    out, pages = [], 0
    while url and pages < 60:
        data = get_json(url)
        objs = data.get("objekter", [])
        out.extend(objs)
        pages += 1
        meta = data.get("metadata", {})
        nxt = (meta.get("neste") or {}).get("href")
        if not objs or meta.get("returnert", len(objs)) < meta.get("sidestørrelse", 1000) or nxt == url:
            break
        url = nxt
        time.sleep(0.3)
    return out


def build_road(code, name, kommuner):
    raw = fetch_road(code)
    segs = []
    for o in raw:
        adt = prop(o, "ÅDT, total")
        if not isinstance(adt, (int, float)) or adt <= 0:
            continue
        lok = o.get("lokasjon", {})
        main = None
        for r in lok.get("vegsystemreferanser", []):
            k = r.get("kortform", "")
            if not k.startswith(code + " ") or " SD" in k or " KD" in k or "sideanlegg" in r or "kryssystem" in r:
                continue
            if r.get("vegsystem", {}).get("fase", "V") != "V":
                continue
            main = k
            break
        if not main:
            continue
        geo = (lok.get("geometri") or {})
        wkt, srid = geo.get("wkt"), geo.get("srid")
        if not wkt:
            continue
        m = REF_RX.search(main)
        order = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (9999, 0, 0)
        heavy = prop(o, "ÅDT, andel lange kjøretøy")
        year = prop(o, "År, gjelder for")
        kom = (lok.get("kommuner") or [None])[0]
        for line in parse_wkt(wkt):
            if srid and int(srid) in (4326, 4258):
                # degrees; NVDB may write lat lon - detect by value range (Norway: lat > 55, lon < 35)
                line = [(b, a) if a > 50 else (a, b) for a, b in line]
                xy = [(lo * 55000.0, la * 111000.0) for lo, la in line]  # rough metres at ~60°N
                keep = set(simplify(xy, TOLERANCE_M))
                pts = [ll for ll, p in zip(line, xy) if p in keep]
            else:
                xy = line
                s = simplify(xy, TOLERANCE_M)
                pts = [utm33_to_lonlat(x, y) for x, y in s]
            segs.append({
                "order": order, "adt": int(adt), "heavy": heavy if isinstance(heavy, (int, float)) else None,
                "year": year, "kom": kom, "pts": pts, "len": length_m(xy),
            })
    segs.sort(key=lambda s: s["order"])

    # merge consecutive segments in the same traffic class into longer stretches
    def close(p, q):
        return abs(p[0] - q[0]) < 0.002 and abs(p[1] - q[1]) < 0.002

    stretches = []
    for s in segs:
        cls = adt_class(s["adt"])
        cur = stretches[-1] if stretches else None
        if cur and cur["c"] == cls:
            a, b = cur["pts"], s["pts"]
            joined = None
            if close(a[-1], b[0]):
                joined = a + b[1:]
            elif close(a[-1], b[-1]):
                joined = a + b[::-1][1:]
            elif close(a[0], b[-1]):
                joined = b + a[1:]
            elif close(a[0], b[0]):
                joined = b[::-1] + a[1:]
            if joined:
                cur["pts"] = joined
                cur["_w"] += s["len"]
                cur["_adt"] += s["adt"] * s["len"]
                if s["heavy"] is not None:
                    cur["_hw"] += s["len"]
                    cur["_h"] += s["heavy"] * s["len"]
                cur["max"] = max(cur["max"], s["adt"])
                cur["min"] = min(cur["min"], s["adt"])
                if s["kom"] and s["kom"] not in cur["koms"]:
                    cur["koms"].append(s["kom"])
                cur["year"] = max(cur["year"] or 0, s["year"] or 0) or None
                continue
        stretches.append({
            "c": cls, "pts": s["pts"], "_w": s["len"], "_adt": s["adt"] * s["len"],
            "_hw": s["len"] if s["heavy"] is not None else 0.0, "_h": (s["heavy"] or 0) * s["len"],
            "max": s["adt"], "min": s["adt"], "koms": [s["kom"]] if s["kom"] else [], "year": s["year"],
        })

    out = []
    total_len = 0.0
    hv_len = hv_sum = 0.0
    busiest = None
    for st in stretches:
        w = st["_w"] or 1.0
        adt = round(st["_adt"] / w)
        heavy = round(st["_h"] / st["_hw"], 1) if st["_hw"] else None
        total_len += st["_w"]
        if heavy is not None:
            hv_len += st["_w"]
            hv_sum += heavy * st["_w"]
        item = {
            "c": st["c"], "adt": adt, "max": st["max"], "min": st["min"], "heavy": heavy,
            "year": st["year"], "km": round(st["_w"] / 1000, 1),
            "places": [kommuner.get(k, str(k)) for k in st["koms"][:4]],
            "pts": [[round(x, 4), round(y, 4)] for x, y in st["pts"]],
        }
        out.append(item)
        if busiest is None or st["max"] > busiest["max"]:
            busiest = item
    summary = {
        "km": round(total_len / 1000),
        "maxAdt": max((s["max"] for s in out), default=0),
        "minAdt": min((s["min"] for s in out), default=0),
        "heavyShare": round(hv_sum / hv_len, 1) if hv_len else None,
        "busiestAt": busiest["places"][:2] if busiest else [],
    }
    log(f"{name}: {len(raw)} objects, {len(segs)} segments, {len(out)} stretches, {summary['km']} km")
    return {"id": name, "summary": summary, "stretches": out}


def load_kommuner():
    try:
        data = get_json(f"{API}/omrader/api/v4/kommuner")
        items = data if isinstance(data, list) else data.get("objekter", data.get("kommuner", []))
        return {int(k["nummer"]): k["navn"] for k in items if "nummer" in k and "navn" in k}
    except Exception as e:  # noqa: BLE001
        log(f"kommuner: {e}")
        return {}


def main():
    started = datetime.now(timezone.utc).replace(microsecond=0)
    kommuner = load_kommuner()
    log(f"kommuner: {len(kommuner)} names")
    roads, failed = [], []
    for code, name in ROADS:
        try:
            roads.append(build_road(code, name, kommuner))
        except Exception as e:  # noqa: BLE001
            failed.append(name)
            log(f"{name}: FAILED {e}")
    old = {}
    if OUT.exists():
        try:
            old = {r["id"]: r for r in json.loads(OUT.read_text(encoding="utf-8")).get("roads", [])}
        except Exception:  # noqa: BLE001
            old = {}
    for name in failed:            # keep last good data for roads that failed this time
        if name in old:
            roads.append(old[name])
    if roads:
        OUT.write_text(json.dumps({
            "updated": started.isoformat().replace("+00:00", "Z"),
            "source": "Statens vegvesen, NVDB (Trafikkmengde), NLOD 2.0",
            "classes": ADT_CLASSES,
            "roads": roads,
        }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        log(f"wrote {OUT.name}: {OUT.stat().st_size // 1024} KB")
    LOG.write_text("\n".join([f"run {started.isoformat()}"] + log_lines) + "\n", encoding="utf-8")
    return 0 if roads else 1


if __name__ == "__main__":
    sys.exit(main())
