/* Cargo Chronicles — main app. No cookies, no trackers, no third-party requests.
   All article text comes from external feeds, so it is always inserted as text, never as HTML. */
(function () {
  'use strict';
  const F = (window.Fairway = window.Fairway || {});
  const state = { route: 'home', arg: '', level: 'all', sub: {}, theme: {}, limit: {}, glossCat: 'all', glossQ: '', search: '' };
  F.state = state;

  const SEG_ORDER = ['road', 'freight', 'finance', 'insurance', 'offshore'];
  const LEVELS = [
    ['all', 'All'],
    ['local', 'Western Norway'],
    ['national', 'Norway'],
    ['international', 'World'],
  ];
  const TZ = 'Europe/Oslo';
  const fmtShort = new Intl.DateTimeFormat('en-GB', { timeZone: TZ, day: 'numeric', month: 'short' });
  const fmtTime = new Intl.DateTimeFormat('en-GB', { timeZone: TZ, hour: '2-digit', minute: '2-digit' });
  const fmtLong = new Intl.DateTimeFormat('en-GB', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' });
  const fmtKey = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' });
  const fmtStamp = new Intl.DateTimeFormat('en-GB', { timeZone: TZ, day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });

  // ---------------------------------------------------------------- helpers
  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v == null || v === false) continue;
        if (k === 'class') n.className = v;
        else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
        else n.setAttribute(k, v === true ? '' : v);
      }
    }
    for (const k of kids.flat(3)) {
      if (k == null || k === false) continue;
      n.append(k instanceof Node ? k : String(k));
    }
    return n;
  }
  F.el = el;

  // replaceChildren that accepts nested arrays and skips empty values
  function fill(node, ...kids) {
    node.replaceChildren(...kids.flat(4).filter((k) => k != null && k !== false).map((k) => (k instanceof Node ? k : String(k))));
    return node;
  }
  F.fill = fill;

  function store(key, val) {
    try {
      if (val === undefined) return localStorage.getItem(key);
      if (val === null) localStorage.removeItem(key);
      else localStorage.setItem(key, val);
    } catch (e) { /* storage unavailable: fine */ }
    return null;
  }

  function refNow() {
    const a = F.data.articles;
    return a && a.sample ? new Date(a.updated) : new Date();
  }

  function when(a) {
    if (a.upcoming) return 'Upcoming event';
    const d = new Date(a.published || a.seen);
    if (!a.published) return 'Seen ' + fmtShort.format(d);
    const h = (refNow() - d) / 36e5;
    if (h < 1) return Math.max(1, Math.round(h * 60)) + ' min ago';
    if (h < 12) return Math.round(h) + ' h ago';
    return fmtShort.format(d) + ', ' + fmtTime.format(d);
  }

  function dayLabel(iso) {
    const key = fmtKey.format(new Date(iso));
    const today = fmtKey.format(refNow());
    const yest = fmtKey.format(new Date(refNow() - 864e5));
    if (key === today) return 'Today';
    if (key === yest) return 'Yesterday';
    return fmtLong.format(new Date(iso));
  }

  const segName = (id) => (F.segments.get(id) || { name: id }).name;
  const levelName = (l) => ({ local: 'Western Norway', national: 'Norway', international: 'World' })[l] || l;

  // ---------------------------------------------------------------- glossary matching (mirrors scripts/update.py)
  function buildTerms(glossary) {
    const byId = new Map(), ci = new Map(), cs = new Map(), rx = [];
    const B = '(?<![\\p{L}\\p{N}_])', E = '(?![\\p{L}\\p{N}_])';
    for (const t of glossary.terms) {
      byId.set(t.id, t);
      for (const m of t.m || []) {
        if (m[0] === '~') {
          try { rx.push([new RegExp(B + m.slice(1) + E, 'gu'), t.id]); } catch (e) { /* skip bad pattern */ }
        } else if (m[0] === '=') {
          if (!cs.has(m.slice(1))) cs.set(m.slice(1), t.id);
        } else if (!ci.has(m.toLowerCase())) ci.set(m.toLowerCase(), t.id);
      }
    }
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const alt = (keys) => [...keys].sort((a, b) => b.length - a.length).map(esc).join('|');
    return {
      byId, ci, cs, rx,
      rci: ci.size ? new RegExp(B + '(?:' + alt(ci.keys()) + ')' + E, 'giu') : null,
      rcs: cs.size ? new RegExp(B + '(?:' + alt(cs.keys()) + ')' + E, 'gu') : null,
    };
  }

  function findTerms(text) {
    const T = F.terms, hits = [];
    if (!text) return hits;
    if (T.rci) for (const m of text.matchAll(T.rci)) { const id = T.ci.get(m[0].toLowerCase()); if (id) hits.push([m.index, m.index + m[0].length, id]); }
    if (T.rcs) for (const m of text.matchAll(T.rcs)) { const id = T.cs.get(m[0]); if (id) hits.push([m.index, m.index + m[0].length, id]); }
    for (const [r, id] of T.rx) for (const m of text.matchAll(r)) hits.push([m.index, m.index + m[0].length, id]);
    hits.sort((a, b) => a[0] - b[0] || (b[1] - b[0]) - (a[1] - a[0]));
    const out = [];
    let end = -1;
    for (const h of hits) { if (h[0] < end) continue; out.push(h); end = h[1]; }
    return out;
  }
  F.findTerms = findTerms;

  // Text with dotted, explainable terms. `seen` limits each term to its first appearance.
  function highlight(text, seen) {
    const frag = document.createDocumentFragment();
    if (!text) return frag;
    seen = seen || new Set();
    let pos = 0;
    for (const [s, e, id] of findTerms(text)) {
      const t = F.terms.byId.get(id);
      if (!t || t.hl === false || seen.has(id)) continue;
      seen.add(id);
      if (s > pos) frag.append(text.slice(pos, s));
      frag.append(el('span', { class: 'term', tabindex: '0', role: 'button', 'data-term': id, 'aria-haspopup': 'dialog', 'aria-expanded': 'false' }, text.slice(s, e)));
      pos = e;
    }
    if (pos < text.length) frag.append(text.slice(pos));
    return frag;
  }
  F.highlight = highlight;

  function termChip(id) {
    const t = F.terms.byId.get(id);
    if (!t) return null;
    return el('button', { class: 'term-chip', type: 'button', 'data-term': id, 'aria-haspopup': 'dialog' }, t.term);
  }
  F.termChip = termChip;

  function termUsage() {
    if (F._usage) return F._usage;
    const counts = new Map();
    for (const a of F.data.articles.articles) for (const id of a.terms || []) counts.set(id, (counts.get(id) || 0) + 1);
    F._usage = counts;
    return counts;
  }

  // ---------------------------------------------------------------- term popover
  const pop = { node: null, anchor: null, timer: null, pinned: false };

  function closePop() {
    clearTimeout(pop.timer);
    if (pop.anchor) pop.anchor.setAttribute('aria-expanded', 'false');
    document.getElementById('pop-layer').replaceChildren();
    const was = pop.anchor;
    pop.node = null; pop.anchor = null; pop.pinned = false;
    return was;
  }

  function termBody(t, opts) {
    opts = opts || {};
    const cats = F.data.glossary.categories || {};
    const used = termUsage().get(t.id) || 0;
    return [
      el('span', { class: 'cat' }, cats[t.cat] || t.cat),
      el('p', { class: 'pop-def' }, t.def),
      t.ex ? el('div', { class: 'example' }, el('b', null, 'Example'), t.ex) : null,
      t.no ? el('p', { class: 'no-name' }, 'In Norwegian: ', el('i', null, t.no)) : null,
      opts.foot === false ? null : el('div', { class: 'pop-foot' },
        el('span', null, used ? `In ${used} current article${used > 1 ? 's' : ''}` : 'Not in current articles'),
        el('a', { href: '#t.' + t.id }, 'Open in glossary →')),
    ];
  }

  function openTerm(id, anchor, pinned) {
    const t = F.terms.byId.get(id);
    if (!t) return;
    if (pop.anchor === anchor && pop.node) { pop.pinned = pop.pinned || pinned; return; }
    closePop();
    const narrow = window.matchMedia('(max-width: 560px)').matches;
    const layer = document.getElementById('pop-layer');
    const node = el('div', { class: 'pop', role: 'dialog', 'aria-label': 'Explanation: ' + t.term },
      el('div', { class: 'pop-head' },
        el('div', null, el('div', { class: 'pop-term' }, t.term), t.full && t.full !== t.term ? el('div', { class: 'pop-full' }, t.full) : null),
        el('button', { class: 'icon-btn pop-close', type: 'button', 'aria-label': 'Close explanation', onclick: () => { const a = closePop(); if (a) a.focus(); } }, '×')),
      termBody(t));
    if (narrow) layer.append(el('div', { class: 'pop-backdrop', onclick: closePop }));
    layer.append(node);
    pop.node = node; pop.anchor = anchor; pop.pinned = !!pinned;
    if (anchor) anchor.setAttribute('aria-expanded', 'true');
    if (!narrow && anchor) {
      const r = anchor.getBoundingClientRect(), w = node.offsetWidth, h = node.offsetHeight;
      let left = Math.min(Math.max(12, r.left), window.innerWidth - w - 12);
      let top = r.bottom + 8;
      if (top + h > window.innerHeight - 12) top = Math.max(12, r.top - h - 8);
      node.style.left = left + 'px';
      node.style.top = top + 'px';
    }
    node.addEventListener('mouseenter', () => clearTimeout(pop.timer));
    node.addEventListener('mouseleave', () => { if (!pop.pinned) pop.timer = setTimeout(closePop, 220); });
    if (pinned && narrow) node.querySelector('.pop-close').focus();
  }
  F.openTerm = openTerm;

  function wireTerms() {
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
    document.addEventListener('mouseover', (e) => {
      if (!fine.matches) return;
      const t = e.target.closest('.term');
      if (!t || pop.pinned) return;
      clearTimeout(pop.timer);
      pop.timer = setTimeout(() => openTerm(t.dataset.term, t, false), 220);
    });
    document.addEventListener('mouseout', (e) => {
      const t = e.target.closest('.term');
      if (!t) return;
      clearTimeout(pop.timer);
      if (!pop.pinned) pop.timer = setTimeout(closePop, 260);
    });
    document.addEventListener('click', (e) => {
      const t = e.target.closest('[data-term]');
      if (t) {
        e.preventDefault();
        e.stopPropagation();
        if (pop.anchor === t && pop.pinned) closePop();
        else { closePop(); openTerm(t.dataset.term, t, true); }
        return;
      }
      if (pop.node && !e.target.closest('.pop')) closePop();
    }, true);
    document.addEventListener('keydown', (e) => {
      const t = e.target.closest && e.target.closest('.term');
      if (t && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openTerm(t.dataset.term, t, true); }
      if (e.key === 'Escape' && pop.node) { const a = closePop(); if (a) a.focus(); }
    });
    document.addEventListener('focusin', (e) => {
      const t = e.target.closest && e.target.closest('.term');
      if (t && fine.matches && !pop.pinned) openTerm(t.dataset.term, t, false);
    });
    window.addEventListener('scroll', () => { if (pop.node && !pop.pinned) closePop(); }, { passive: true });
    window.addEventListener('resize', () => { if (pop.node) closePop(); });
  }

  // ---------------------------------------------------------------- article cards and reader
  function sourceOf(a) { return F.sources.get(a.source) || { name: a.source, url: a.link }; }

  function card(a) {
    const src = sourceOf(a);
    const seen = new Set();
    const titleNode = el('h3', { class: 'card-title' }, highlight(a.title, seen));
    const exNode = a.excerpt ? el('p', { class: 'card-ex' }, highlight(a.excerpt, seen)) : null;
    const extra = (a.terms || []).filter((id) => !seen.has(id) && F.terms.byId.get(id)).slice(0, 4);
    const node = el('article', { class: 'card seg-' + a.segments[0] },
      el('div', { class: 'meta' },
        el('span', { class: 'src' }, src.name),
        el('span', null, when(a)),
        el('span', { class: 'lang', title: a.lang === 'no' ? 'Norwegian' : 'English' }, a.lang.toUpperCase()),
        a.orig_lang ? el('span', { class: 'flag' }, 'Translated from ' + a.orig_lang.toUpperCase()) : null,
        a.paywall ? el('span', { class: 'flag' }, 'Subscriber') : null,
        el('span', { class: 'segtags' }, a.segments.map((s) => el('span', { class: 'segtag seg-' + s }, el('span', { class: 'seg-dot' }), segName(s))))),
      titleNode,
      exNode,
      el('div', { class: 'card-foot' },
        extra.length ? el('div', { class: 'terms' }, el('span', { class: 'lbl' }, 'Terms'), extra.map(termChip)) : null,
        el('div', { class: 'card-actions' },
          el('button', { class: 'btn-link', type: 'button', onclick: () => openReader(a) }, 'Explain this'),
          el('a', { class: 'ext', href: a.link, target: '_blank', rel: 'noopener noreferrer' }, src.name.replace(/\s*\(.*\)$/, '')))));
    node.addEventListener('click', (e) => {
      if (e.target.closest('a, button, .term, [data-term]')) return;
      if (window.getSelection && String(window.getSelection()).length) return;
      openReader(a);
    });
    return node;
  }

  const TOOLS = {
    truck: { tab: 'truck', name: 'Truck trip cost', text: 'See how diesel price, tolls, wages and driving-time rules add up on a Norwegian trip.' },
    rates: { tab: 'rates', name: 'Freight rate lab', text: 'Move demand and fleet supply, and watch the freight rate react.' },
    voyage: { tab: 'voyage', name: 'Voyage economics', text: 'Turn a freight rate into daily earnings (TCE), with bunker and EU ETS costs.' },
    effects: { tab: 'effects', name: 'Cause & effect', text: 'Follow one event from world markets down to Norway and Western Norway.' },
  };
  TOOLS.markets = { tab: 'markets', name: 'Market pulse', text: 'Brent oil and the krone against the dollar and euro, with what they mean for transport.' };
  TOOLS.valuation = { tab: 'valuation', name: 'Ship valuation', text: 'Value a ship from its earnings, then see it as the bank does: break-even, covenants and what a fall in values does to the equity.' };
  function toolsFor(a) {
    const out = [];
    const s = a.segments;
    if (s.includes('road')) out.push(TOOLS.truck);
    if (s.includes('freight')) out.push(TOOLS.rates);
    if (s.includes('finance')) out.push(TOOLS.valuation);
    if (s.includes('freight') || s.includes('finance')) out.push(TOOLS.voyage);
    if (s.includes('insurance') || s.includes('offshore') || a.policy || out.length < 2) out.push(TOOLS.effects);
    return [...new Set(out)].slice(0, 3);
  }

  // ---------------------------------------------------------------- reading guide (data/insights.json)
  // Each rule describes a situation (keywords), explains the mechanism, and says what to watch.
  // Rules are scored against the headline (x3) and summary (x1); the best two or three are shown.
  const WB = '(?<![\\p{L}\\p{N}_])', WE = '(?![\\p{L}\\p{N}_])';
  function kwRx(k) {
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (k[0] === '~') return new RegExp(WB + '(?:' + k.slice(1) + ')' + WE, 'iu');
    let cs = false;
    if (k[0] === '=') { cs = true; k = k.slice(1); }
    const star = k.endsWith('*');
    const body = esc(star ? k.slice(0, -1) : k) + (star ? '[\\p{L}\\p{N}_-]*' : '');
    return new RegExp(WB + body + WE, cs ? 'u' : 'iu');
  }
  const DIR_UP = ['rise', 'rises', 'rising', 'rose', 'up', 'jump*', 'surge*', 'soar*', 'climb*', 'gain*', 'firm*', 'strengthen*', 'rally', 'rallies', 'increase*', 'higher', 'spike*', 'boost*', 'hike*', 'record high', 'øker', 'stiger', 'steg', 'opp', 'dyrere', 'høyere', 'økning', 'rekordhøy*'].map(kwRx);
  const DIR_DN = ['fall', 'falls', 'falling', 'fell', 'drop*', 'slump*', 'plunge*', 'decline*', 'down', 'ease', 'eases', 'easing', 'eased', 'soften*', 'weaken*', 'lower', 'slide*', 'slid', 'tumble*', 'dip', 'dips', 'faller', 'falt', 'synker', 'ned', 'billigere', 'lavere', 'nedgang'].map(kwRx);

  function guideRules() {
    if (F._rules) return F._rules;
    const raw = (F.data.insights && F.data.insights.rules) || [];
    F._rules = raw.map((r) => ({
      ...r,
      _m: (r.m || []).map(kwRx),
      _x: (r.x || []).map(kwRx),
      _req: (r.req || []).map((g) => g.map(kwRx)),
    }));
    return F._rules;
  }

  function directionNear(title, pos) {
    let best = null;
    for (const [lab, list] of [['up', DIR_UP], ['dn', DIR_DN]]) {
      for (const rx of list) {
        const g = new RegExp(rx.source, rx.flags + 'g');
        for (const m of title.matchAll(g)) {
          const d = Math.abs(m.index - pos);
          if (!best || d < best[0]) best = [d, lab];
        }
      }
    }
    return best && best[0] <= 45 ? best[1] : null;
  }

  function guideFor(a) {
    const rules = guideRules();
    const t = a.title || '', ex = a.excerpt || '', both = t + '\n' + ex;
    const segs = new Set(a.segments), terms = new Set(a.terms || []);
    const hits = [];
    rules.forEach((r, i) => {
      if (r.generic) return;
      if (r.lang && r.lang !== a.lang) return;
      if (r._x.some((x) => x.test(both))) return;
      if (r._req.some((g) => !g.some((k) => k.test(both)))) return;
      const inTitle = r._m.map((k) => k.exec(t)).filter(Boolean);
      const inEx = r._m.filter((k) => k.test(ex)).length;
      if (!inTitle.length && !inEx) return;
      const score = 3 * inTitle.length + inEx + ((r.seg || []).some((s) => segs.has(s)) ? 1 : 0) + ((r.terms || []).some((x) => terms.has(x)) ? 1 : 0);
      if (score < 3) return;
      const dir = (r.up || r.dn) && inTitle.length ? directionNear(t, Math.min(...inTitle.map((m) => m.index))) : null;
      hits.push({ r, dir, score, i });
    });
    hits.sort((x, y) => y.score - x.score || x.i - y.i);
    const out = hits.slice(0, 3);
    if (out.length < 2) {
      const g = rules.find((r) => r.generic && (r.seg || []).includes(a.segments[0]));
      if (g) out.push({ r: g, dir: null, score: 0 });
    }
    return out;
  }
  F.guideFor = guideFor;

  function goLink(spec, close) {
    const [kind, rest] = spec.split(':');
    if (kind === 'tool') {
      const tool = TOOLS[rest];
      if (!tool) return null;
      return el('a', { class: 'go go-tool', href: '#analytics.' + tool.tab, onclick: close }, el('span', { class: 'go-k' }, 'Analytics'), tool.name);
    }
    if (kind === 'map') {
      const parts = rest.split('/');
      const tab = parts[0];
      const id = parts[parts.length - 1] === tab ? '' : parts[parts.length - 1];
      const names = (F.mapNames && F.mapNames()) || {};
      const label = id ? (names[id] || id) : (tab === 'sea' ? 'Shipping routes' : 'Road network');
      return el('a', { class: 'go go-map', href: '#maps.' + tab + (id ? '.' + id : ''), onclick: close }, el('span', { class: 'go-k' }, tab === 'sea' ? 'Sea map' : 'Road map'), label);
    }
    return null;
  }

  // label for the course topic a reading-guide rule belongs to (rules.c)
  const COURSE_LABEL = 'Course topic';
  function guideBlock(a, close) {
    const items = guideFor(a);
    if (!items.length) return null;
    return [
      el('h3', { class: 'section-h' }, 'How to read this story'),
      el('div', { class: 'guide' }, items.map(({ r, dir }) => {
        const v = dir === 'up' ? r.up : dir === 'dn' ? r.dn : null;
        const chips = (r.terms || []).filter((id) => F.terms.byId.get(id)).slice(0, 4).map(termChip);
        const links = (r.go || []).map((g) => goLink(g, close)).filter(Boolean);
        return el('section', { class: 'guide-item' + (dir ? ' dir-' + dir : '') + (r.generic ? ' generic' : '') },
          r.c ? el('span', { class: 'guide-topic' }, COURSE_LABEL + ': ' + r.c) : null,
          el('h4', null, dir ? el('span', { class: 'dir', 'aria-hidden': 'true' }, dir === 'up' ? '▲' : '▼') : null, v ? v.t : r.t),
          el('p', null, v ? r.b + ' ' + v.b : r.b),
          r.w ? el('p', { class: 'watch' }, el('b', null, 'Watch next: '), r.w) : null,
          chips.length || links.length ? el('div', { class: 'guide-foot' }, chips, links) : null);
      })),
    ];
  }

  function openReader(a) {
    closePop();
    const dlg = document.getElementById('reader');
    const body = document.getElementById('reader-body');
    const src = sourceOf(a);
    const seen = new Set();
    dlg.className = 'reader seg-' + a.segments[0];
    const title = el('h2', { class: 'reader-title' }, highlight(a.title, seen));
    const ex = a.excerpt
      ? el('p', { class: 'reader-ex' }, highlight(a.excerpt, seen))
      : el('p', { class: 'small-note' }, 'This source does not share a summary. Open the article to read it.');
    const ids = [...new Set([...seen, ...(a.terms || [])])].filter((id) => F.terms.byId.get(id));
    const notes = [];
    if (a.paywall || src.access === 'members') notes.push('The full article may require a subscription or membership.');
    if (a.orig_title) notes.push(`Translated automatically from ${a.orig_lang.toUpperCase()}. Original title: “${a.orig_title}”.`);
    fill(body, 
      el('div', { class: 'reader-top' },
        el('div', { class: 'meta' }, el('span', { class: 'src' }, src.name), el('span', null, when(a)), el('span', { class: 'lang' }, a.lang.toUpperCase())),
        el('button', { class: 'icon-btn', type: 'button', style: 'margin-left:auto', 'aria-label': 'Close', onclick: () => dlg.close() }, '×')),
      title,
      ex,
      el('a', { class: 'btn-primary ext', href: a.link, target: '_blank', rel: 'noopener noreferrer' }, 'Read the full article at ' + src.name.replace(/\s*\(.*\)$/, '')),
      notes.length ? el('p', { class: 'small-note' }, notes.join(' ')) : null,
      el('div', { class: 'chips', 'aria-label': 'Where this fits' },
        a.segments.map((s) => el('a', { class: 'chip seg-' + s, href: '#' + s, onclick: () => dlg.close() }, el('span', { class: 'seg-dot' }), segName(s))),
        el('span', { class: 'chip', style: 'cursor:default' }, 'Level: ' + levelName(a.level)),
        a.policy ? el('span', { class: 'chip', style: 'cursor:default' }, 'Policy & rules') : null),
      guideBlock(a, () => dlg.close()),
      el('h3', { class: 'section-h' }, 'Terms in this article', el('span', { class: 'n' }, String(ids.length))),
      ids.length
        ? ids.map((id) => {
            const t = F.terms.byId.get(id);
            return el('div', { class: 'term-card' },
              el('h4', null, t.term, t.full && t.full !== t.term ? el('small', null, t.full) : null),
              termBody(t, { foot: false }),
              el('a', { href: '#t.' + id, class: 'small-note', onclick: () => dlg.close() }, 'More in the glossary →'));
          })
        : el('p', { class: 'small-note' }, 'No glossary terms were found in the headline or summary. The full article may still use terms you can look up in the glossary.'),
      el('h3', { class: 'section-h' }, 'Try it yourself'),
      toolsFor(a).map((tool) => el('a', { class: 'tool-link', href: '#analytics.' + tool.tab, onclick: () => dlg.close() },
        el('div', null, el('div', { class: 'k' }, 'Analytics'), el('div', null, el('b', null, tool.name), ' — ', tool.text)))));
    if (!dlg.open) dlg.showModal();
    body.scrollTop = 0;
    dlg.scrollTop = 0;
  }
  F.openReader = openReader;

  // ---------------------------------------------------------------- feeds
  function sortArts(list) {
    return list.slice().sort((x, y) => (y.published || y.seen).localeCompare(x.published || x.seen));
  }

  function matchLevel(a, level) {
    if (level === 'all') return true;
    if (level === 'national') return a.level === 'national' || a.level === 'local';
    return a.level === level;
  }

  function feed(list, key) {
    const limit = state.limit[key] || 30;
    const wrap = el('div', { class: 'feed' });
    if (!list.length) {
      wrap.append(el('p', { class: 'empty' }, 'No articles match this filter right now.'));
      return wrap;
    }
    let lastDay = null;
    for (const a of list.slice(0, limit)) {
      const d = dayLabel(a.published || a.seen);
      if (d !== lastDay) { wrap.append(el('div', { class: 'day-label' }, d)); lastDay = d; }
      wrap.append(card(a));
    }
    if (list.length > limit) {
      wrap.append(el('div', { class: 'more-row' }, el('button', { class: 'btn-link', type: 'button', onclick: () => { state.limit[key] = limit + 30; render(); } }, `Show ${Math.min(30, list.length - limit)} more`)));
    }
    return wrap;
  }

  function chipRow(options, current, onPick, label) {
    return el('div', { class: 'chips', role: 'group', 'aria-label': label },
      options.map(([id, name, n]) => el('button', { class: 'chip', type: 'button', 'aria-pressed': String(current === id), onclick: () => onPick(id) }, name, n != null ? el('span', { class: 'n' }, String(n)) : null)));
  }

  function levelChips(list, key) {
    const opts = LEVELS.map(([id, name]) => [id, name, list.filter((a) => matchLevel(a, id)).length]);
    return chipRow(opts, state.level, (id) => { state.level = id; state.limit[key] = 30; render(); }, 'Level');
  }

  function sampleNotice() {
    const a = F.data.articles;
    if (!a.sample) return null;
    return el('div', { class: 'notice', role: 'note' },
      el('span', null, el('b', null, 'Preview. '),
        `These headlines were collected on ${fmtStamp.format(new Date(a.updated))} to show how the site works. Once it is set up, it refreshes itself every three hours.`));
  }

  // ---------------------------------------------------------------- pages
  const MINI_SEA = '<svg width="54" height="38" viewBox="0 0 54 38" aria-hidden="true"><rect x="0.5" y="0.5" width="53" height="37" rx="4" fill="none" stroke="currentColor" stroke-opacity=".35"/><path d="M6 27c8-2 12-12 21-12s13 7 21 3" fill="none" stroke="var(--seg-freight)" stroke-width="2.4" stroke-linecap="round"/><circle cx="27" cy="15" r="3" fill="var(--accent)"/></svg>';
  const MINI_ROAD = '<svg width="54" height="38" viewBox="0 0 54 38" aria-hidden="true"><rect x="0.5" y="0.5" width="53" height="37" rx="4" fill="none" stroke="currentColor" stroke-opacity=".35"/><path d="M14 33c3-8 2-14 9-18s15-4 18-10" fill="none" stroke="var(--seg-road)" stroke-width="3.2" stroke-linecap="round"/><path d="M14 33c6-4 14-4 26-1" fill="none" stroke="var(--seg-road)" stroke-width="1.6" stroke-linecap="round" stroke-opacity=".7"/></svg>';
  function mapsCell() {
    const svg = (html) => { const t = document.createElement('span'); t.innerHTML = html; return t.firstChild; };
    return el('section', { class: 'board-cell maps-cell', 'aria-label': 'Maps' },
      el('a', { class: 'board-head', href: '#maps' }, el('span', { class: 'nm' }, 'Route maps'), el('span', { class: 'open' }, 'Open maps')),
      el('a', { class: 'maps-link', href: '#maps.sea' }, svg(MINI_SEA), el('b', null, 'Shipping routes'), el('span', null, 'Baltic routes, chokepoints and what-if closures')),
      el('a', { class: 'maps-link', href: '#maps.road' }, svg(MINI_ROAD), el('b', null, 'Road network'), el('span', null, 'Traffic and trucks on Norway’s main roads')));
  }

  // themes: the situations (reading-guide rules) that come up most in a set of articles
  function guideCached(a) {
    F._guideCache = F._guideCache || new Map();
    if (!F._guideCache.has(a.id)) F._guideCache.set(a.id, guideFor(a).filter((g) => !g.r.generic).map((g) => g.r.id));
    return F._guideCache.get(a.id);
  }
  function themesFor(arts) {
    const counts = new Map();
    for (const a of arts) for (const id of guideCached(a)) counts.set(id, (counts.get(id) || 0) + 1);
    const byId = new Map(guideRules().map((r) => [r.id, r]));
    return [...counts.entries()].filter(([, n]) => n >= 2).sort((x, y) => y[1] - x[1]).slice(0, 6).map(([id, n]) => ({ r: byId.get(id), n }));
  }

  function pageHome(main) {
    const arts = sortArts(F.data.articles.articles);
    const list = arts.filter((a) => matchLevel(a, state.level));
    const srcCount = new Set(arts.map((a) => a.source)).size;
    const shown = new Set();
    fill(main,
      el('div', { class: 'page-head' },
        el('span', { class: 'eyebrow' }, fmtLong.format(refNow())),
        el('h1', { class: 'page-title' }, 'What’s moving in transport and shipping'),
        el('p', { class: 'page-intro' }, `${arts.length} articles from ${srcCount} free sources, sorted into five sections. Hover or tap any dotted word for a plain explanation with an example.`)),
      sampleNotice(),
      el('section', { class: 'board', 'aria-label': 'Latest in each section' },
        SEG_ORDER.map((sid) => {
          const sa = arts.filter((a) => a.segments.includes(sid));
          const top = sa.filter((a) => !shown.has(a.id)).slice(0, 3);
          top.forEach((a) => shown.add(a.id));
          return el('section', { class: 'board-cell seg-' + sid, 'aria-label': segName(sid) },
            el('a', { class: 'board-head', href: '#' + sid },
              el('span', { class: 'nm' }, segName(sid)), el('span', { class: 'n' }, String(sa.length)), el('span', { class: 'open' }, 'Open section')),
            el('ul', { class: 'board-list' }, top.length ? top.map((a) => el('li', null,
              el('button', { class: 'board-item', type: 'button', onclick: () => openReader(a) },
                el('span', { class: 't' }, a.title),
                el('span', { class: 'm' }, el('span', null, sourceOf(a).name.replace(/\s*\(.*\)$/, '')), el('span', null, when(a))))))
              : el('li', { class: 'empty' }, 'Nothing new yet')));
        }),
        mapsCell()),
      el('div', { class: 'filters' }, el('span', { class: 'lbl' }, 'Show'), levelChips(arts, 'home')),
      feed(list, 'home'));
  }

  function pageSection(main, sid) {
    const seg = F.segments.get(sid);
    const arts = sortArts(F.data.articles.articles.filter((a) => a.segments.includes(sid)));
    const cur = state.sub[sid] || 'all';
    let list = arts;
    let filterRow;
    if (sid === 'road') {
      const subs = [['all', 'All', arts.length],
        ['norway', 'Norway', arts.filter((a) => a.level !== 'international').length],
        ['international', 'International', arts.filter((a) => a.level === 'international').length],
        ['policy', 'Policy & rules', arts.filter((a) => a.policy).length]];
      list = arts.filter((a) => cur === 'all' || (cur === 'norway' ? a.level !== 'international' : cur === 'international' ? a.level === 'international' : a.policy));
      filterRow = chipRow(subs, cur, (id) => { state.sub[sid] = id; render(); }, 'Filter');
    } else if (seg.subs && seg.subs.length) {
      const subs = [['all', 'All', arts.length], ...seg.subs.map((s) => [s.id, s.name, arts.filter((a) => (a.subs || []).includes(s.id)).length])];
      list = cur === 'all' ? arts : arts.filter((a) => (a.subs || []).includes(cur));
      filterRow = chipRow(subs, cur, (id) => { state.sub[sid] = id; render(); }, 'Filter');
    } else {
      list = arts.filter((a) => matchLevel(a, state.level));
      filterRow = levelChips(arts, sid);
    }
    const core = F.data.glossary.terms.filter((t) => (t.core || []).includes(sid));
    const themes = themesFor(arts);
    const theme = themes.some((x) => x.r.id === state.theme[sid]) ? state.theme[sid] : null;
    const themeRule = theme ? themes.find((x) => x.r.id === theme).r : null;
    if (theme) list = list.filter((a) => guideCached(a).includes(theme));
    fill(main,
      el('div', { class: 'page-head seg-band seg-' + sid },
        el('span', { class: 'eyebrow' }, el('span', { class: 'seg-dot' }), `${arts.length} articles`),
        el('h1', { class: 'page-title' }, seg.name),
        el('p', { class: 'page-intro' }, seg.intro)),
      sampleNotice(),
      themes.length ? el('section', { class: 'learn seg-' + sid, 'aria-label': 'Themes right now' },
        el('h2', null, 'What is driving this section right now'),
        el('div', { class: 'themes' }, themes.map(({ r, n }) => el('button', { class: 'theme-btn', type: 'button', 'aria-pressed': String(theme === r.id),
          onclick: () => { state.theme[sid] = theme === r.id ? null : r.id; state.limit[sid] = 30; render(); } }, r.t, el('span', { class: 'n' }, String(n))))),
        themeRule ? el('div', { class: 'theme-explain' },
          el('p', null, themeRule.b),
          themeRule.w ? el('p', null, el('b', null, 'Watch next: '), themeRule.w) : null,
          el('div', { class: 'guide-foot' }, (themeRule.terms || []).filter((id) => F.terms.byId.get(id)).slice(0, 4).map(termChip), (themeRule.go || []).map((g) => goLink(g)).filter(Boolean),
            el('button', { class: 'btn-link', type: 'button', onclick: () => { state.theme[sid] = null; render(); } }, 'Show all stories'))) : null) : null,
      el('section', { class: 'learn', 'aria-label': 'Learn the basics' },
        el('h2', null, 'Learn the basics'),
        el('div', { class: 'learn-row' }, core.map((t) => termChip(t.id)))),
      el('div', { class: 'filters' }, el('span', { class: 'lbl' }, 'Filter'), filterRow),
      feed(list, sid));
  }

  function pageSearch(main) {
    const q = state.search.trim();
    const ql = q.toLowerCase();
    const arts = q ? sortArts(F.data.articles.articles.filter((a) => (a.title + ' ' + (a.excerpt || '') + ' ' + sourceOf(a).name).toLowerCase().includes(ql))) : [];
    const terms = q ? F.data.glossary.terms.filter((t) => (t.term + ' ' + (t.full || '') + ' ' + (t.no || '') + ' ' + t.m.join(' ')).toLowerCase().includes(ql)).slice(0, 12) : [];
    fill(main,
      el('div', { class: 'page-head' },
        el('span', { class: 'eyebrow' }, 'Search'),
        el('h1', { class: 'page-title' }, q ? `Results for “${q}”` : 'Search'),
        el('p', { class: 'page-intro' }, q ? `${arts.length} article${arts.length === 1 ? '' : 's'} and ${terms.length} glossary term${terms.length === 1 ? '' : 's'}.` : 'Type in the search box to find articles and terms.')),
      terms.length ? el('section', { class: 'learn' }, el('h2', null, 'Matching terms'), el('div', { class: 'learn-row' }, terms.map((t) => termChip(t.id)))) : null,
      q ? feed(arts, 'search:' + q) : null);
  }

  function pageGlossary(main, focusId) {
    const G = F.data.glossary;
    const cats = G.categories;
    const usage = termUsage();
    const counts = {};
    for (const t of G.terms) counts[t.cat] = (counts[t.cat] || 0) + 1;
    const listBox = el('div');
    const input = el('input', { class: 'gl-search', id: 'gq', type: 'search', placeholder: 'Find a term, abbreviation or Norwegian word', value: state.glossQ, autocomplete: 'off' });
    const catRow = el('div');

    function drawCats() {
      fill(catRow, chipRow([['all', 'All', G.terms.length], ...Object.entries(cats).map(([id, name]) => [id, name, counts[id] || 0])],
        state.glossCat, (id) => { state.glossCat = id; drawCats(); drawList(); }, 'Category'));
    }
    function drawList() {
      const q = state.glossQ.trim().toLowerCase();
      const items = G.terms
        .filter((t) => state.glossCat === 'all' || t.cat === state.glossCat)
        .filter((t) => !q || (t.term + ' ' + (t.full || '') + ' ' + (t.no || '') + ' ' + t.def + ' ' + t.m.join(' ')).toLowerCase().includes(q))
        .sort((a, b) => a.term.localeCompare(b.term, 'en', { sensitivity: 'base' }));
      let letter = '';
      const out = [];
      for (const t of items) {
        const L = t.term[0].toUpperCase();
        if (L !== letter) { letter = L; out.push(el('div', { class: 'letter', 'aria-hidden': 'true' }, L)); }
        const n = usage.get(t.id) || 0;
        out.push(el('article', { class: 'gl-entry', id: 't.' + t.id },
          el('div', { class: 'gl-name' }, t.term, t.full && t.full !== t.term ? el('small', null, t.full) : null),
          el('div', { class: 'gl-body' },
            el('p', null, t.def),
            t.ex ? el('div', { class: 'example' }, el('b', null, 'Example'), t.ex) : null,
            el('div', { class: 'gl-meta' },
              el('span', { class: 'cat' }, cats[t.cat]),
              t.no ? el('span', { class: 'no-name' }, 'In Norwegian: ', el('i', null, t.no)) : null,
              n ? el('button', { class: 'btn-link', type: 'button', onclick: () => { state.search = t.term; document.getElementById('q').value = t.term; location.hash = 'search'; } }, `In ${n} current article${n > 1 ? 's' : ''} →`) : null))));
      }
      fill(listBox, out.length ? out : el('p', { class: 'empty' }, 'No terms match. Try a shorter word or another category.'));
    }
    input.addEventListener('input', () => { state.glossQ = input.value; drawList(); });
    drawCats();
    drawList();
    fill(main,
      el('div', { class: 'page-head' },
        el('span', { class: 'eyebrow' }, 'Glossary'),
        el('h1', { class: 'page-title' }, `${G.terms.length} terms, explained with examples`),
        el('p', { class: 'page-intro' }, 'Road transport, chartering, freight markets, ship finance, marine insurance, offshore and the abbreviations you meet in everyday emails. Norwegian terms are matched too.')),
      el('div', { class: 'gl-tools' }, el('label', { class: 'visually-hidden', for: 'gq' }, 'Search the glossary'), input, catRow),
      listBox);
    if (focusId) {
      requestAnimationFrame(() => {
        const n = document.getElementById('t.' + focusId);
        if (n) { n.scrollIntoView({ block: 'start' }); n.classList.add('flash'); setTimeout(() => n.classList.remove('flash'), 2400); }
      });
    }
  }

  function pageAbout(main) {
    const S = F.data.sources;
    const status = (F.data.status && F.data.status.sources) || {};
    const sample = F.data.articles.sample;
    const segs = (s) => (s.segments && s.segments.length ? s.segments.map(segName).join(', ') : 'Sorted by topic');
    fill(main,
      el('div', { class: 'page-head' },
        el('span', { class: 'eyebrow' }, 'About'),
        el('h1', { class: 'page-title' }, 'About Cargo Chronicles and its sources'),
        el('p', { class: 'page-intro' }, 'A personal reading desk for road transport and shipping: free sources in one place, with the vocabulary explained so each article teaches something.')),
      el('div', { class: 'prose' },
        el('h2', null, 'How it works'),
        el('ul', null,
          el('li', null, 'Every three hours a small program reads the sources’ public news feeds (or front-page headlines where no feed exists) and sorts each article into sections by its words.'),
          el('li', null, 'Articles in English and Norwegian are kept as they are. Articles in other languages are translated to English automatically.'),
          el('li', null, 'Dotted words link to the glossary. The program also lists the terms found in each article, so the “Explain this” panel can teach the vocabulary.'),
          el('li', null, 'Cargo Chronicles shows the headline, a short summary where the source provides one, and a link. To read the full story, you go to the source.')),
        el('h2', null, 'Reading guides, maps and data'),
        el('ul', null,
          el('li', null, '“How to read this story” is chosen for each article from a library of situations (for example a chokepoint attack, falling Capesize rates or a diesel tax change), matched on the headline and summary. The library is in data/insights.json.'),
          el('li', null, 'Shipping routes follow Baltic Exchange route definitions where one exists. Oil volumes through chokepoints are from the U.S. EIA (World Oil Transit Chokepoints, 2023 data). War-risk listed areas refer to the Lloyd’s Market Association Joint War Committee.'),
          el('li', null, 'Road traffic is from Statens vegvesen’s national road database (NVDB, Trafikkmengde), used under the Norwegian Licence for Open Government Data (NLOD). It refreshes monthly.'),
          el('li', null, 'The ship valuation tool follows the long-term asset value (LTAV) method described in Kavussanos & Visvikis (eds.), The International Handbook of Shipping Finance (Palgrave Macmillan, 2016), chapter 13. Example ships other than the textbook case are illustrative, not market quotes.'),
          el('li', null, 'Coastlines: Natural Earth (public domain) via world-atlas. Map projections: d3-geo (ISC licence).')),
        el('h2', null, 'Privacy'),
        el('p', null, 'This site sets no cookies, uses no analytics or advertising, and loads nothing from other companies: fonts and chart code are stored on the site itself. The only thing saved in your browser is your light/dark choice, if you change it.'),
        el('h2', null, 'Copyright and corrections'),
        el('p', null, 'Headlines, summaries and articles belong to their publishers. Cargo Chronicles links to the original for every article and does not copy full texts or images. Publishers who want their headlines removed can ask, and they will be removed.'),
        el('h2', null, 'Not advice'),
        el('p', null, 'Explanations, examples and the analytics tools are simplified for learning. They are not legal, insurance, investment or tax advice, and the models are illustrations, not forecasts.')),
      el('h2', { style: 'font-size:1.35rem;margin:26px 0 10px' }, 'Sources'),
      el('div', { class: 'table-wrap' },
        el('table', { class: 'data' },
          el('thead', null, el('tr', null, ['Source', 'Language', 'Sections', 'Access', 'Status'].map((h) => el('th', { scope: 'col' }, h)))),
          el('tbody', null, S.sources.map((s) => {
            const st = status[s.id];
            let stNode;
            if (!s.enabled) stNode = el('span', { class: 'state' }, 'Paused');
            else if (sample || !st) stNode = el('span', { class: 'state' }, 'Starts after setup');
            else if (st.state === 'ok') stNode = el('span', { class: 'state ok' }, `OK · ${st.kept} kept`);
            else stNode = el('span', { class: 'state err', title: st.error || '' }, 'Error, will retry');
            return el('tr', null,
              el('td', null, el('a', { href: s.url, target: '_blank', rel: 'noopener noreferrer' }, s.name), el('div', { class: 'small-note' }, s.about)),
              el('td', null, s.lang === 'auto' ? 'NO / EN' : s.lang.toUpperCase()),
              el('td', null, segs(s)),
              el('td', null, s.access),
              el('td', null, stNode));
          })))),
      el('p', { class: 'small-note', style: 'margin-top:10px' }, 'Sources and the words that sort articles into sections can be edited in the files data/sources.json and data/segments.json.'));
  }

  // ---------------------------------------------------------------- frame: rail, side, ticker, theme
  function drawRail() {
    const arts = F.data.articles.articles;
    const n = (sid) => arts.filter((a) => a.segments.includes(sid)).length;
    const link = (id, name, count, dot) => el('a', { class: 'nav-link' + (dot ? ' seg-' + id : ''), href: '#' + id, 'aria-current': (state.route === id || (state.route === 't' && id === 'glossary')) ? 'page' : null },
      dot ? el('span', { class: 'seg-dot' }) : null, name, count != null ? el('span', { class: 'count' }, String(count)) : null);
    fill(document.getElementById('rail'), el('div', { class: 'rail-groups' },
      el('div', { class: 'rail-group' }, el('div', { class: 'rail-label' }, 'Read'),
        link('home', 'Today', arts.length),
        SEG_ORDER.map((sid) => link(sid, segName(sid), n(sid), true))),
      el('div', { class: 'rail-group' }, el('div', { class: 'rail-label' }, 'Learn'),
        link('maps', 'Route maps'),
        link('analytics', 'Analytics'),
        link('glossary', 'Glossary', F.data.glossary.terms.length)),
      el('div', { class: 'rail-group' }, el('div', { class: 'rail-label' }, 'Site'),
        link('about', 'About & sources'))));
  }

  function drawSide() {
    const usage = termUsage();
    const ranked = [...usage.entries()].filter(([id]) => F.terms.byId.get(id)).sort((a, b) => b[1] - a[1]);
    const pool = ranked.map(([id]) => F.terms.byId.get(id)).filter((t) => t.cat !== 'email');
    const day = Math.floor(refNow() / 864e5);
    const tod = pool.length ? pool[day % pool.length] : F.data.glossary.terms[day % F.data.glossary.terms.length];
    const top = ranked.slice(0, 8);
    const max = top.length ? top[0][1] : 1;
    const bm = (F.data.sources.bookmarks || []);
    fill(document.getElementById('side'), 
      el('section', { class: 'panel', 'aria-label': 'Term of the day' },
        el('span', { class: 'sub' }, 'Term of the day'),
        el('div', { class: 'tod-term' }, tod.term),
        el('p', { class: 'tod-def' }, tod.def),
        tod.ex ? el('div', { class: 'example' }, el('b', null, 'Example'), tod.ex) : null),
      top.length ? el('section', { class: 'panel', 'aria-label': 'Most used terms' },
        el('span', { class: 'sub' }, 'Most used terms in the news now'),
        el('ul', { class: 'rank' }, top.map(([id, c]) => el('li', null,
          el('button', { class: 'btn-link', type: 'button', 'data-term': id }, F.terms.byId.get(id).term),
          el('span', { class: 'bar', style: `width:${Math.max(8, Math.round((c / max) * 60))}px` }),
          el('span', { class: 'n' }, String(c)))))) : null,
      bm.length ? el('section', { class: 'panel', 'aria-label': 'Your subscription sources' },
        el('span', { class: 'sub' }, 'Your other sources'),
        el('div', { class: 'bm' }, bm.map((b) => el('a', { href: b.url, target: '_blank', rel: 'noopener noreferrer' }, b.name, el('span', null, b.note))))) : null);
  }

  function drawTicker() {
    const box = document.getElementById('ticker');
    const S = (F.data.markets && F.data.markets.series) || {};
    const items = [['usdnok', 'USD/NOK', 4], ['eurnok', 'EUR/NOK', 4], ['brent', 'Brent', 2]];
    fill(box, items.filter(([k]) => S[k] && S[k].points && S[k].points.length > 1).map(([k, label, dp]) => {
      const p = S[k].points, last = p[p.length - 1][1], prev = p[p.length - 2][1];
      const ch = ((last - prev) / prev) * 100;
      return el('span', { title: `${S[k].label}, ${p[p.length - 1][0]} (${S[k].source})` }, label + ' ', el('b', null, last.toFixed(dp === 4 ? 2 : 1)), ' ',
        el('span', { class: 'dn' }, (ch >= 0 ? '+' : '−') + Math.abs(ch).toFixed(1) + '%'));
    }));
  }

  const THEMES = ['system', 'light', 'dark'];
  const THEME_ICON = {
    system: '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 2a6 6 0 0 1 0 12z" fill="currentColor"/></svg>',
    light: '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3.2" fill="currentColor"/><g stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.4 1.4M11.6 11.6L13 13M3 13l1.4-1.4M11.6 4.4L13 3"/></g></svg>',
    dark: '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M13.5 10.2A6 6 0 0 1 5.8 2.5a6 6 0 1 0 7.7 7.7z" fill="currentColor"/></svg>',
  };
  function applyTheme(mode) {
    if (mode === 'light' || mode === 'dark') document.documentElement.setAttribute('data-theme', mode);
    else document.documentElement.removeAttribute('data-theme');
    const btn = document.getElementById('theme-btn');
    btn.innerHTML = THEME_ICON[mode];
    btn.setAttribute('aria-label', `Colour theme: ${mode}. Click to change.`);
    btn.title = `Theme: ${mode}`;
    window.dispatchEvent(new CustomEvent('fairway:theme'));
  }

  // ---------------------------------------------------------------- router
  function parseHash() {
    const h = decodeURIComponent(location.hash.slice(1)) || 'home';
    const i = h.indexOf('.');
    return i < 0 ? [h, ''] : [h.slice(0, i), h.slice(i + 1)];
  }

  function render() {
    const main = document.getElementById('main');
    main.replaceChildren();
    const r = state.route;
    document.body.dataset.route = r;
    if (r === 'home') pageHome(main);
    else if (F.segments.has(r)) pageSection(main, r);
    else if (r === 'analytics') {
      if (F.renderAnalytics) F.renderAnalytics(main, state.arg || 'markets');
      else main.append(el('p', { class: 'empty' }, 'The analytics tools could not load.'));
    } else if (r === 'maps') {
      if (F.renderMaps) F.renderMaps(main, state.arg || 'sea');
      else main.append(el('p', { class: 'empty' }, 'The maps could not load.'));
    } else if (r === 'glossary' || r === 't') pageGlossary(main, r === 't' ? state.arg : '');
    else if (r === 'about') pageAbout(main);
    else if (r === 'search') pageSearch(main);
    else pageHome(main);
    drawRail();
  }

  function route() {
    closePop();
    const dlg = document.getElementById('reader');
    if (dlg.open) dlg.close();
    const [r, arg] = parseHash();
    // inside the maps page, selecting a route or chokepoint only updates the map
    if (r === 'maps' && state.route === 'maps' && F.mapsUpdate && F.mapsUpdate(arg || 'sea')) { state.arg = arg; return; }
    const changed = r !== state.route;
    state.route = r === 't' ? 't' : r;
    state.arg = arg;
    if (r === 't') { state.glossCat = 'all'; state.glossQ = ''; }
    render();
    if (changed && r !== 't') window.scrollTo(0, 0);
    if (changed) document.getElementById('main').focus({ preventScroll: true });
    document.title = r === 'home' ? 'Cargo Chronicles' : `${({ analytics: 'Analytics', maps: 'Route maps', glossary: 'Glossary', t: 'Glossary', about: 'About', search: 'Search' })[r] || segName(r)} · Cargo Chronicles`;
  }
  F.render = render;

  // ---------------------------------------------------------------- start
  async function start() {
    let data;
    try {
      data = window.__FAIRWAY_DATA__ || await loadData();
    } catch (e) {
      document.getElementById('main').replaceChildren(el('p', { class: 'empty' }, 'The news data could not be loaded. Try reloading the page.'));
      return;
    }
    F.data = data;
    F.terms = buildTerms(data.glossary);
    F.segments = new Map(data.segments.segments.map((s) => [s.id, s]));
    F.sources = new Map(data.sources.sources.map((s) => [s.id, s]));

    let mode = store('fairway-theme') || 'system';
    if (!THEMES.includes(mode)) mode = 'system';
    applyTheme(mode);
    document.getElementById('theme-btn').addEventListener('click', () => {
      mode = THEMES[(THEMES.indexOf(mode) + 1) % THEMES.length];
      store('fairway-theme', mode === 'system' ? null : mode);
      applyTheme(mode);
    });

    const q = document.getElementById('q');
    if (window.matchMedia('(max-width: 560px)').matches) q.placeholder = 'Search';
    document.getElementById('search-form').addEventListener('submit', (e) => {
      e.preventDefault();
      state.search = q.value;
      if (state.route === 'search') render(); else location.hash = 'search';
    });
    let deb;
    q.addEventListener('input', () => {
      clearTimeout(deb);
      deb = setTimeout(() => {
        state.search = q.value;
        if (q.value.trim().length >= 2) { if (state.route === 'search') render(); else location.hash = 'search'; }
      }, 300);
    });

    const dlg = document.getElementById('reader');
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });

    // Keep the sticky section tabs directly under the top bar, whatever its height.
    const mast = document.querySelector('.masthead');
    const setMastH = () => document.documentElement.style.setProperty('--mast-h', mast.offsetHeight + 'px');
    setMastH();
    if ('ResizeObserver' in window) new ResizeObserver(setMastH).observe(mast);

    wireTerms();
    drawTicker();
    drawSide();
    window.addEventListener('hashchange', route);
    route();
  }

  async function loadData() {
    const names = ['articles', 'glossary', 'sources', 'segments', 'markets', 'scenarios', 'status', 'insights'];
    const out = {};
    await Promise.all(names.map(async (n) => {
      try {
        const r = await fetch('data/' + n + '.json', { cache: 'no-cache' });
        out[n] = r.ok ? await r.json() : null;
      } catch (e) { out[n] = null; }
    }));
    if (!out.articles || !out.glossary || !out.sources || !out.segments) throw new Error('missing data');
    return out;
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
