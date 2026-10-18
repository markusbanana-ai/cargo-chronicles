/* Cargo Chronicles — route maps.
   Shipping: key Baltic routes per market, chokepoints, what-if closures and live news per place.
   Roads: annual average daily traffic (ÅDT) on Norway's main roads from Statens vegvesen (NVDB),
   with mountain passes, ferries, border crossings and links to Sweden, Finland and Denmark.
   Map libraries and data load only when this page is opened. */
(function () {
  'use strict';
  const F = (window.Fairway = window.Fairway || {});
  const el = (...a) => F.el(...a);
  const fill = (...a) => F.fill(...a);
  const NS = 'http://www.w3.org/2000/svg';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const nf0 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 });
  const nf1 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });

  const M = (F.maps = F.maps || { token: 0, view: null, market: 'crude', closed: null, speed: {}, mode: 'all', region: null });

  function svg(tag, attrs, ...kids) {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) if (v != null && v !== false) n.setAttribute(k, v);
    for (const k of kids.flat(3)) if (k != null && k !== false) n.append(k instanceof Node ? k : String(k));
    return n;
  }

  // names for links from the reading guide, available before the map data loads
  const ALIAS = { 'red-sea': 'bab-el-mandeb', grain: 'usg-grain' };
  const NAMES = {
    td3c: 'TD3C Gulf → China', td15: 'TD15 West Africa → China', td22: 'TD22 US Gulf → China', td20: 'TD20 West Africa → Europe',
    td25: 'TD25 US Gulf → Europe', td7: 'TD7 Cross North Sea', mongstad: 'Mongstad → Rotterdam', tc20: 'TC20 Gulf → Europe',
    'mr-triangle': 'MR Atlantic triangulation', c5: 'C5 Australia → China', c3: 'C3 Brazil → China', 'brazil-soy': 'Brazil soybeans → China',
    'usg-grain': 'US grain → China via Panama', grain: 'US grain → China via Panama', 'indo-coal': 'Indonesia coal → India',
    'asia-europe': 'China → North Europe', 'asia-med': 'China → Mediterranean', transpacific: 'China → US West Coast',
    'china-usec': 'China → US East Coast', 'qatar-lng': 'Qatar LNG → Japan', blng1: 'BLNG1 Australia → Japan', blng2: 'BLNG2 US Gulf → Europe',
    blng3: 'BLNG3 US Gulf → Japan', blpg1: 'BLPG1 Gulf → Japan (LPG)', hammerfest: 'Hammerfest LNG → Rotterdam',
    hormuz: 'Strait of Hormuz', 'bab-el-mandeb': 'Bab el-Mandeb', 'red-sea': 'Red Sea and Suez', suez: 'Suez Canal', malacca: 'Strait of Malacca',
    panama: 'Panama Canal', bosporus: 'Turkish Straits', danish: 'Danish Straits', cape: 'Cape of Good Hope',
    E6: 'E6', E18: 'E18', E39: 'E39', E16: 'E16', E134: 'E134', E136: 'E136', E10: 'E10', E8: 'E8', E14: 'E14', Rv7: 'Rv7', Rv52: 'Rv52', Rv3: 'Rv3', Rv15: 'Rv15',
  };
  F.mapNames = () => NAMES;

  // ---------------------------------------------------------------- loading
  const cache = {};
  function loadScript(src) {
    return new Promise((res, rej) => { const s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = () => rej(new Error(src)); document.head.append(s); });
  }
  async function ensureD3() {
    if (window.d3 && window.d3.geoPath) return;
    if (!window.d3 || !window.d3.range) await loadScript('assets/vendor/d3-array.min.js');
    await loadScript('assets/vendor/d3-geo.min.js');
  }
  function getJSON(name) {
    if (!cache[name]) cache[name] = fetch('data/' + name, { cache: 'no-cache' }).then((r) => { if (!r.ok) throw new Error(name); return r.json(); });
    return cache[name];
  }

  // ---------------------------------------------------------------- news matching
  const WB = '(?<![\\p{L}\\p{N}_])', WE = '(?![\\p{L}\\p{N}_])';
  function kwTest(list) {
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (!list || !list.length) return () => false;
    // whole words, or a prefix when the keyword ends with *; "=ABC" matches exact capitals
    const part = (k) => { const star = k.endsWith('*'); const w = star ? k.slice(0, -1) : k; return esc(w).replace(/ /g, '[\\s-]?') + (star ? '' : WE); };
    const ci = list.filter((k) => k[0] !== '='), cs = list.filter((k) => k[0] === '=').map((k) => k.slice(1));
    const rxi = ci.length ? new RegExp(WB + '(?:' + ci.map(part).join('|') + ')', 'iu') : null;
    const rxs = cs.length ? new RegExp(WB + '(?:' + cs.map(part).join('|') + ')', 'u') : null;
    return (a) => { const t = a.title + ' ' + (a.excerpt || ''); return (rxi && rxi.test(t)) || (rxs && rxs.test(t)); };
  }
  function newsFor(list) {
    const test = kwTest(list);
    const arts = (F.data && F.data.articles && F.data.articles.articles) || [];
    return arts.filter(test).sort((x, y) => (y.published || y.seen).localeCompare(x.published || x.seen));
  }
  function newsBlock(list, max) {
    const items = newsFor(list);
    if (!items.length) return el('p', { class: 'small-note' }, 'No current headlines mention this.');
    return el('ul', { class: 'map-news' }, items.slice(0, max || 4).map((a) => el('li', null,
      el('button', { class: 'map-news-item', type: 'button', onclick: () => F.openReader && F.openReader(a) },
        el('span', { class: 't' }, a.title), el('span', { class: 'm' }, (F.sources && F.sources.get(a.source) ? F.sources.get(a.source).name : a.source))))),
      items.length > (max || 4) ? el('li', { class: 'small-note' }, `${items.length - (max || 4)} more in the news`) : null);
  }

  // ---------------------------------------------------------------- pan and zoom frame
  function makeFrame(box, bounds, opts) {
    const [[bx0, by0], [bx1, by1]] = bounds;
    const root = svg('svg', { class: 'map-svg', role: 'img', 'aria-label': opts.label, preserveAspectRatio: 'xMidYMid meet' });
    box.prepend(root);
    const st = { cx: (bx0 + bx1) / 2, cy: (by0 + by1) / 2, s: 1, W: 1, H: 1, min: 1, max: 1 };
    const onZoom = [];
    function size() {
      const r = box.getBoundingClientRect();
      st.W = Math.max(1, r.width); st.H = Math.max(1, r.height);
      st.min = Math.min(st.W / (bx1 - bx0), st.H / (by1 - by0)) * (opts.minFactor || 1);
      st.max = st.min * (opts.maxZoom || 24);
    }
    function clamp() {
      st.s = Math.max(st.min, Math.min(st.max, st.s));
      const hw = st.W / st.s / 2, hh = st.H / st.s / 2;
      st.cx = (bx1 - bx0) <= 2 * hw ? (bx0 + bx1) / 2 : Math.max(bx0 + hw, Math.min(bx1 - hw, st.cx));
      st.cy = (by1 - by0) <= 2 * hh ? (by0 + by1) / 2 : Math.max(by0 + hh, Math.min(by1 - hh, st.cy));
    }
    function apply() {
      clamp();
      const w = st.W / st.s, h = st.H / st.s;
      root.setAttribute('viewBox', `${st.cx - w / 2} ${st.cy - h / 2} ${w} ${h}`);
      onZoom.forEach((f) => f(st.s / st.min, 1 / st.s));
    }
    function fit(b, pad) {
      const [[x0, y0], [x1, y1]] = b;
      const p = pad == null ? 0.08 : pad;
      return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, s: Math.min(st.W / ((x1 - x0) * (1 + p)), st.H / ((y1 - y0) * (1 + p))) };
    }
    let anim = null;
    function go(t, animate) {
      cancelAnimationFrame(anim);
      if (!animate || reduced) { Object.assign(st, t); apply(); return; }
      const a = { cx: st.cx, cy: st.cy, s: st.s }, t0 = performance.now(), D = 450;
      const step = (now) => {
        const k = Math.min(1, (now - t0) / D), e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        const ls = Math.log(a.s) + (Math.log(Math.max(st.min, Math.min(st.max, t.s))) - Math.log(a.s)) * e;
        st.s = Math.exp(ls); st.cx = a.cx + (t.cx - a.cx) * e; st.cy = a.cy + (t.cy - a.cy) * e;
        apply();
        if (k < 1) anim = requestAnimationFrame(step);
      };
      anim = requestAnimationFrame(step);
    }
    function zoomAt(px, py, f) {
      const ux = st.cx + (px - st.W / 2) / st.s, uy = st.cy + (py - st.H / 2) / st.s;
      const s0 = st.s;
      st.s = Math.max(st.min, Math.min(st.max, st.s * f));
      st.cx = ux - (px - st.W / 2) / st.s; st.cy = uy - (py - st.H / 2) / st.s;
      if (st.s !== s0) apply();
    }
    // wheel, drag and pinch
    root.addEventListener('wheel', (e) => {
      if (!e.ctrlKey && !opts.wheel) return;
      e.preventDefault();
      const r = root.getBoundingClientRect();
      zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * 0.0022));
    }, { passive: false });
    const ptrs = new Map();
    let moved = false, pinch0 = null;
    root.addEventListener('pointerdown', (e) => {
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
      moved = false;
      if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = { d: Math.hypot(a.x - b.x, a.y - b.y), s: st.s }; }
    });
    root.addEventListener('pointermove', (e) => {
      const p = ptrs.get(e.pointerId);
      if (!p) return;
      const dx = e.clientX - p.x, dy = e.clientY - p.y;
      if (!moved && Math.hypot(dx, dy) < 4) return;
      if (!moved) { moved = true; try { root.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ } }
      p.x = e.clientX; p.y = e.clientY;
      if (ptrs.size === 2 && pinch0) {
        const [a, b] = [...ptrs.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const r = root.getBoundingClientRect();
        zoomAt((a.x + b.x) / 2 - r.left, (a.y + b.y) / 2 - r.top, (pinch0.s * d / pinch0.d) / st.s);
      } else if (ptrs.size === 1) {
        st.cx -= dx / st.s; st.cy -= dy / st.s; apply();
      }
      root.classList.add('dragging');
    });
    const up = (e) => { ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch0 = null; root.classList.remove('dragging'); };
    root.addEventListener('pointerup', up);
    root.addEventListener('pointercancel', up);
    root.addEventListener('click', (e) => { if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);
    root.addEventListener('dblclick', (e) => { const r = root.getBoundingClientRect(); zoomAt(e.clientX - r.left, e.clientY - r.top, 2); });

    const ro = new ResizeObserver(() => { const k = st.s / st.min; size(); st.s = st.min * k; apply(); });
    ro.observe(box);
    size();
    const controls = el('div', { class: 'map-zoom' },
      el('button', { class: 'icon-btn', type: 'button', 'aria-label': 'Zoom in', onclick: () => zoomAt(st.W / 2, st.H / 2, 1.6) }, '+'),
      el('button', { class: 'icon-btn', type: 'button', 'aria-label': 'Zoom out', onclick: () => zoomAt(st.W / 2, st.H / 2, 1 / 1.6) }, '−'));
    box.append(controls);
    return { root, st, apply, go, fit, onZoom, size, destroy: () => ro.disconnect() };
  }

  // keep markers a constant size on screen: wrap them in <g transform="translate scale">
  function placeMarkers(frame, nodes) {
    frame.onZoom.push((k, inv) => {
      for (const n of nodes) n.g.setAttribute('transform', `translate(${n.x},${n.y}) scale(${inv})`);
    });
  }

  function tipFor(box) {
    const tip = el('div', { class: 'map-tip', role: 'status', 'aria-live': 'polite' });
    box.append(tip);
    return {
      show(e, kids) {
        fill(tip, kids);
        tip.classList.add('on');
        const r = box.getBoundingClientRect();
        let x = e.clientX - r.left + 14, y = e.clientY - r.top + 14;
        const w = tip.offsetWidth, h = tip.offsetHeight;
        if (x + w > r.width - 6) x = e.clientX - r.left - w - 14;
        if (y + h > r.height - 6) y = e.clientY - r.top - h - 14;
        tip.style.transform = `translate(${Math.max(6, x)}px, ${Math.max(6, y)}px)`;
      },
      hide() { tip.classList.remove('on'); },
    };
  }

  function parseArg(arg) {
    const s = (arg || 'sea').split('.');
    const tab = s[0] === 'road' ? 'road' : 'sea';
    let id = s.slice(1).join('.') || null;
    if (id && ALIAS[id]) id = ALIAS[id];
    return [tab, id];
  }

  // ---------------------------------------------------------------- page
  F.renderMaps = function (main, arg) {
    const [tab, id] = parseArg(arg);
    if (M.view && M.view.destroy) M.view.destroy();
    M.view = null;
    const token = ++M.token;
    const body = el('div', { class: 'maps-body' }, el('p', { class: 'empty' }, 'Loading the map…'));
    fill(main,
      el('div', { class: 'page-head' },
        el('span', { class: 'eyebrow' }, 'Route maps'),
        el('h1', { class: 'page-title' }, tab === 'sea' ? 'Shipping routes and chokepoints' : 'Norway’s main roads for freight'),
        el('p', { class: 'page-intro' }, tab === 'sea'
          ? 'The benchmark routes behind freight rates, with the narrow passages they depend on. Pick a market, then click a route or a chokepoint. Close a chokepoint to see the detour and what it does to ship demand.'
          : 'Traffic on Norway’s main roads from Statens vegvesen’s counts, with mountain passes, ferries and border crossings. Switch to heavy vehicles to see where the trucks are.')),
      el('div', { class: 'tabs', role: 'tablist' }, [['sea', 'Shipping routes'], ['road', 'Road network']].map(([t, name]) => el('button', {
        class: 'tab', role: 'tab', type: 'button', 'aria-selected': String(t === tab), onclick: () => { location.hash = 'maps.' + t; },
      }, name))),
      body);
    (tab === 'sea' ? buildSea : buildRoad)(body, id, token).catch((err) => {
      if (token !== M.token) return;
      console.error(err);
      fill(body, el('p', { class: 'empty' }, 'The map could not be loaded. Check your connection and reload the page.'));
    });
  };

  F.mapsUpdate = function (arg) {
    const [tab, id] = parseArg(arg);
    if (!M.view || M.view.tab !== tab || !document.body.contains(M.view.node)) return false;
    M.view.select(id, true);
    return true;
  };

  // ================================================================ SHIPPING MAP
  async function buildSea(body, id, token) {
    await ensureD3();
    const [geo, sea] = await Promise.all([getJSON('geo/world.json'), getJSON('sea.json')]);
    if (token !== M.token) return;
    const d3 = window.d3;
    const proj = d3.geoNaturalEarth1().rotate(geo.proj.rotate).scale(geo.proj.scale).translate([0, 0]).precision(0.2);
    const gp = d3.geoPath(proj);
    const routes = new Map(sea.routes.map((r) => [r.id, r]));
    const chokes = new Map(sea.chokepoints.map((c) => [c.id, c]));
    const markets = new Map(sea.markets.map((m) => [m.id, m]));
    if (!markets.has(M.market) && M.market !== 'all') M.market = 'crude';
    // crop Antarctica and the far Arctic
    const [[gx0], [gx1]] = geo.bounds;
    const top = proj([0, 78])[1], bottom = proj([0, -58])[1];
    const bounds = [[gx0, top], [gx1, bottom]];

    const mapBox = el('div', { class: 'map-box sea' });
    const panel = el('aside', { class: 'map-panel', 'aria-live': 'polite' });
    const marketChips = el('div', { class: 'chips', role: 'group', 'aria-label': 'Market' });
    const regionChips = el('div', { class: 'chips map-regions', role: 'group', 'aria-label': 'Zoom to region' });
    const legend = el('div', { class: 'map-legend' });
    fill(body, el('div', { class: 'map-layout' },
      el('div', { class: 'map-col' },
        el('div', { class: 'map-toolbar' }, marketChips),
        mapBox,
        el('div', { class: 'map-under' }, regionChips, legend)),
      panel));

    const frame = makeFrame(mapBox, bounds, { label: 'World map of shipping routes and chokepoints', maxZoom: 14, wheel: true });
    const tip = tipFor(mapBox);
    const R = frame.root;
    R.append(
      svg('path', { class: 'sea-sphere', d: geo.sphere }),
      svg('path', { class: 'graticule', d: geo.graticule }),
      svg('path', { class: 'land', d: geo.land }));
    const gRoutes = svg('g', { class: 'routes' });
    const gAlt = svg('g', { class: 'alts' });
    const gSel = svg('g', { class: 'sel-layer' });
    const gPorts = svg('g', { class: 'ports' });
    const gChoke = svg('g', { class: 'chokes' });
    R.append(gRoutes, gAlt, gSel, gPorts, gChoke);

    const line = (pts) => gp({ type: 'LineString', coordinates: pts });
    const routeNodes = new Map();
    for (const r of sea.routes) {
      const d = line(r.pts);
      const vis = svg('path', { class: 'route-line', d });
      const extra = (r.legs_extra || []).map((leg) => svg('path', { class: 'route-line ' + (leg.kind === 'ballast' ? 'ballast' : ''), d: line(leg.pts) }));
      const hit = svg('path', { class: 'route-hit', d: d + (r.legs_extra || []).map((leg) => line(leg.pts)).join(''), 'data-id': r.id });
      const g = svg('g', { class: 'route m-' + r.market, 'data-id': r.id }, vis, extra, hit);
      gRoutes.append(g);
      routeNodes.set(r.id, g);
      hit.addEventListener('pointermove', (e) => tip.show(e, [el('b', null, (r.code ? r.code + '  ' : '') + r.name), el('span', null, `${r.ship}, about ${nf0.format(r.nm)} nm`)]));
      hit.addEventListener('pointerleave', () => tip.hide());
      hit.addEventListener('click', () => { tip.hide(); location.hash = 'maps.sea.' + r.id; });
    }

    // ports: route ends
    const portMap = new Map();
    for (const r of sea.routes) {
      [[r.pts[0], r.frm], [r.pts[r.pts.length - 1], r.to]].forEach(([p, name]) => {
        const key = p.join(',');
        if (!portMap.has(key)) portMap.set(key, { p, name: name.split(',')[0].replace(/\s*\(.*\)$/, ''), routes: new Set() });
        portMap.get(key).routes.add(r.id);
      });
    }
    const markerNodes = [];
    for (const port of portMap.values()) {
      const [x, y] = proj(port.p);
      const g = svg('g', { class: 'port' }, svg('circle', { r: 2.6 }), svg('text', { x: 5, y: 3.5 }, port.name));
      port.g = g; port.x = x; port.y = y;
      gPorts.append(g);
      markerNodes.push({ g, x, y });
    }

    // chokepoints with news counts
    const chokeNodes = new Map();
    const MAJOR = new Set(['hormuz', 'bab-el-mandeb', 'suez', 'malacca', 'panama', 'bosporus', 'cape']);
    for (const c of sea.chokepoints) {
      const [x, y] = proj(c.at);
      const n = newsFor(c.kw).length;
      const g = svg('g', { class: 'choke' + (MAJOR.has(c.id) ? ' major' : ''), 'data-id': c.id, tabindex: '0', role: 'button', 'aria-label': c.name + (n ? `, ${n} headlines` : '') },
        svg('rect', { x: -5, y: -5, width: 10, height: 10, transform: 'rotate(45)' }),
        n ? svg('g', { class: 'badge', transform: 'translate(8,-9)' }, svg('circle', { r: 7 }), svg('text', { y: 3 }, n > 99 ? '99+' : String(n))) : null,
        svg('text', { class: 'lbl', x: 10, y: 15 }, c.name));
      g.addEventListener('pointermove', (e) => tip.show(e, [el('b', null, c.name), el('span', null, n ? `${n} headline${n > 1 ? 's' : ''} in the news` : 'Click for details')]));
      g.addEventListener('pointerleave', () => tip.hide());
      g.addEventListener('click', () => { tip.hide(); location.hash = 'maps.sea.' + c.id; });
      g.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); location.hash = 'maps.sea.' + c.id; } });
      gChoke.append(g);
      chokeNodes.set(c.id, g);
      markerNodes.push({ g, x, y });
    }
    placeMarkers(frame, markerNodes);
    frame.onZoom.push((k) => R.classList.toggle('zoomed', k > 2.2));

    // regions
    const REGIONS = [
      ['world', 'World', null],
      ['europe', 'Europe', [[-14, 33], [32, 64]]],
      ['gulf', 'Middle East', [[30, 8], [66, 33]]],
      ['asia', 'East Asia', [[95, -12], [145, 40]]],
      ['americas', 'Americas', [[-125, -30], [-35, 45]]],
    ];
    const regionBox = (b) => { const a = proj([b[0][0], b[1][1]]), c = proj([b[1][0], b[0][1]]); return [[Math.min(a[0], c[0]), Math.min(a[1], c[1])], [Math.max(a[0], c[0]), Math.max(a[1], c[1])]]; };
    function drawRegions(cur) {
      fill(regionChips, REGIONS.map(([rid, name, b]) => el('button', { class: 'chip', type: 'button', 'aria-pressed': String(cur === rid),
        onclick: () => { M.region = rid; frame.go(b ? frame.fit(regionBox(b)) : frame.fit(bounds, 0), true); drawRegions(rid); } }, name)));
    }

    function drawMarkets() {
      fill(marketChips, [['all', 'All markets'], ...sea.markets.map((m) => [m.id, m.name])].map(([mid, name]) => el('button', {
        class: 'chip', type: 'button', 'aria-pressed': String(M.market === mid),
        onclick: () => { M.market = mid; const cur = view.sel; if (cur && routes.has(cur) && mid !== 'all' && routes.get(cur).market !== mid) location.hash = 'maps.sea'; else update(); drawMarkets(); },
      }, name)));
    }

    function drawLegend() {
      fill(legend,
        el('span', null, el('i', { class: 'lg-line' }), 'Laden route'),
        el('span', null, el('i', { class: 'lg-line ballast' }), 'Ballast leg'),
        el('span', null, el('i', { class: 'lg-line sel' }), 'Selected'),
        M.closed ? el('span', null, el('i', { class: 'lg-line detour' }), 'Detour') : null,
        el('span', null, el('i', { class: 'lg-diamond' }), 'Chokepoint'),
        el('span', null, el('i', { class: 'lg-badge' }), 'Headlines now'),
        el('span', { class: 'small-note' }, 'Drag to move, scroll or pinch to zoom'));
    }

    // ---------------------------------------------------------- state rendering
    const view = { tab: 'sea', node: body, sel: null, destroy: frame.destroy };
    function shown(r) { return M.market === 'all' || r.market === M.market; }
    function blockedBy(r) { return M.closed && (r.via || []).includes(M.closed) ? M.closed : null; }

    function update() {
      for (const r of sea.routes) {
        const g = routeNodes.get(r.id);
        g.classList.toggle('hidden', !shown(r) && view.sel !== r.id);
        g.classList.toggle('sel', view.sel === r.id);
        g.classList.toggle('blocked', !!blockedBy(r));
        g.classList.toggle('muted', M.market === 'all');
      }
      for (const [cid, g] of chokeNodes) {
        g.classList.toggle('sel', view.sel === cid);
        g.classList.toggle('closed', M.closed === cid);
      }
      // ports: show those on visible routes
      for (const port of portMap.values()) {
        const vis = [...port.routes].some((rid) => shown(routes.get(rid)) || view.sel === rid);
        port.g.classList.toggle('hidden', !vis);
        port.g.classList.toggle('sel', view.sel && port.routes.has(view.sel));
      }
      // detours
      gAlt.replaceChildren();
      if (M.closed) {
        for (const r of sea.routes) {
          const alt = r.alts && r.alts[M.closed];
          if (alt && (shown(r) || view.sel === r.id)) gAlt.append(svg('path', { class: 'detour-line' + (view.sel === r.id ? ' sel' : ''), d: line(alt.pts) }));
        }
      }
      // selected route on top
      gSel.replaceChildren();
      if (view.sel && routes.has(view.sel)) {
        const r = routes.get(view.sel);
        const d = line(r.pts);
        gSel.append(svg('path', { class: 'sel-casing', d }), svg('path', { class: 'sel-line' + (blockedBy(r) ? ' blocked' : ''), d }),
          svg('path', { class: 'sel-flow', d }));
        for (const leg of r.legs_extra || []) gSel.append(svg('path', { class: 'sel-line ' + (leg.kind === 'ballast' ? 'ballast' : ''), d: line(leg.pts) }));
      }
      drawLegend();
    }

    // ---------------------------------------------------------- panels
    function marketPanel() {
      const list = sea.routes.filter(shown);
      const m = markets.get(M.market);
      return [
        el('h2', { class: 'mp-title' }, m ? m.name : 'All markets'),
        m ? el('p', { class: 'mp-sub' }, m.sizes.replace(/ · /g, ', ')) : el('p', { class: 'mp-sub' }, 'Every benchmark route on the map. Pick a market above to focus.'),
        el('p', null, 'Click a route or a chokepoint on the map, or pick one below. Each route shows the ship, how freight is quoted, what moves the rate, and what it means for ship finance and insurance.'),
        el('h3', { class: 'mp-h' }, 'Routes'),
        el('ul', { class: 'mp-list' }, list.map((r) => el('li', null, el('a', { href: '#maps.sea.' + r.id, class: 'mp-row' },
          el('span', { class: 'code' }, r.code || '—'), el('span', { class: 'nm' }, r.name), el('span', { class: 'v' }, nf0.format(r.nm) + ' nm'))))),
        el('h3', { class: 'mp-h' }, 'Chokepoints'),
        el('ul', { class: 'mp-list' }, sea.chokepoints.map((c) => {
          const n = newsFor(c.kw).length;
          return el('li', null, el('a', { href: '#maps.sea.' + c.id, class: 'mp-row' },
            el('span', { class: 'nm' }, c.name), el('span', { class: 'v' }, n ? `${n} in the news` : '')));
        })),
        el('p', { class: 'small-note' }, 'Routes follow Baltic Exchange route definitions where one exists. Distances are approximate great-circle sums along typical sea lanes. Oil volumes: EIA (2023 data).'),
      ];
    }

    function voyageDays(r, nmLaden, speed) {
      const laden = nmLaden / (speed * 24);
      const ballastNm = r.id === 'mr-triangle' ? (r.legs_extra || []).filter((l) => l.kind === 'ballast').reduce((s, l) => s + l.nm, 0) : nmLaden;
      const ladenExtra = r.id === 'mr-triangle' ? (r.legs_extra || []).filter((l) => l.kind === 'laden').reduce((s, l) => s + l.nm, 0) : 0;
      const ballast = ballastNm / (r.ballast * 24);
      return { laden: laden + ladenExtra / (speed * 24), ballast, port: r.port_days, total: laden + ladenExtra / (speed * 24) + ballast + r.port_days, ballastNm, ladenNm: nmLaden + ladenExtra };
    }

    function routePanel(r) {
      const sp = M.speed[r.id] || r.speed;
      const out = el('div', { class: 'mp-route' });
      const draw = () => {
        const speed = M.speed[r.id] || r.speed;
        const v = voyageDays(r, r.nm, speed);
        const blocked = blockedBy(r);
        const alt = blocked && r.alts ? r.alts[blocked] : null;
        const va = alt ? voyageDays(r, alt.nm, speed) : null;
        fill(out,
          el('div', { class: 'mp-facts' },
            fact('Ship', r.ship), fact('Cargo', r.size), fact('From', r.frm), fact('To', r.to),
            fact('Distance', `≈ ${nf0.format(v.ladenNm)} nm laden` + (r.id === 'mr-triangle' ? `, ${nf0.format(v.ballastNm)} nm ballast` : '')),
            fact('Round voyage', `≈ ${nf0.format(v.total)} days`, `${nf1.format(v.laden)} laden + ${nf1.format(v.ballast)} ballast + ${r.port_days} in port`)),
          blocked ? el('div', { class: 'mp-alert' + (alt ? '' : ' stuck') },
            el('b', null, `${chokes.get(blocked).name} is closed in your scenario. `),
            alt ? `${alt.note} About ${nf0.format(alt.nm - r.nm)} nm longer each way: the round voyage takes ${nf0.format(va.total)} days instead of ${nf0.format(v.total)} (${pctTxt(va.total / v.total - 1)} ship-days per cargo).`
              : 'There is no practical sea detour for this cargo: it is stuck, or buyers switch to other suppliers.') : null);
      };
      const speedCtl = el('input', { type: 'range', min: String(Math.max(8, r.speed - 4)), max: String(r.speed + 4), step: '0.5', value: String(sp), 'aria-label': 'Laden speed in knots' });
      const outSpeed = el('output', null, sp + ' kn');
      speedCtl.addEventListener('input', () => { M.speed[r.id] = +speedCtl.value; outSpeed.textContent = speedCtl.value + ' kn'; draw(); });
      draw();
      const via = (r.via || []).map((cid) => chokes.get(cid)).filter(Boolean);
      return [
        el('div', { class: 'mp-head' }, r.code ? el('span', { class: 'code' }, r.code) : null, el('h2', { class: 'mp-title' }, r.name)),
        out,
        el('div', { class: 'ctl' }, el('div', { class: 'ctl-top' }, el('label', null, 'Laden speed'), outSpeed), speedCtl,
          el('span', { class: 'help' }, 'Slower sailing saves fuel but ties up the ship longer: one way the market absorbs spare ships (slow steaming).')),
        el('h3', { class: 'mp-h' }, 'How freight is quoted'), el('p', null, r.quote),
        via.length ? [el('h3', { class: 'mp-h' }, 'Passes'), el('div', { class: 'chips' }, via.map((c) => el('a', { class: 'chip', href: '#maps.sea.' + c.id }, c.name)))] : null,
        el('h3', { class: 'mp-h' }, 'What moves this rate'), el('ul', { class: 'mp-bul' }, r.moves.map((m) => el('li', null, m))),
        el('h3', { class: 'mp-h' }, 'Finance and insurance angle'), el('p', null, r.course),
        el('div', { class: 'mp-actions' },
          r.voyage ? el('button', { class: 'btn-primary', type: 'button', onclick: () => openVoyage(r) }, 'Model this voyage') : null,
          el('button', { class: 'chip', type: 'button', onclick: () => { location.hash = 'analytics.rates'; } }, 'Freight rate lab')),
        el('h3', { class: 'mp-h' }, 'In the news'), newsBlock(r.kw, 4),
      ];
    }

    function openVoyage(r) {
      if (!F.lab) { location.hash = 'analytics.voyage'; return; }
      const speed = M.speed[r.id] || r.speed;
      const v = voyageDays(r, r.nm, speed);
      // the voyage tab applies these on top of its own defaults (including today's EUR/USD)
      F.lab.voyagePreset = {
        cargo: r.voyage.cargo, freight: r.voyage.freight, cons: r.voyage.cons, speed, portDays: r.port_days, dist: Math.round(v.ladenNm + v.ballastNm),
        ets: /rotterdam|wilhelmshaven|genoa/i.test(r.to) ? 0.5 : 0,
      };
      location.hash = 'analytics.voyage';
    }

    function chokePanel(c) {
      const affected = sea.routes.filter((r) => (r.via || []).includes(c.id));
      const closed = M.closed === c.id;
      const rows = affected.map((r) => {
        const alt = r.alts && r.alts[c.id];
        const sp = M.speed[r.id] || r.speed;
        const base = voyageDays(r, r.nm, sp).total;
        const extra = alt ? voyageDays(r, alt.nm, sp).total / base - 1 : null;
        return { r, alt, extra };
      });
      const withAlt = rows.filter((x) => x.alt);
      const avg = withAlt.length ? withAlt.reduce((s, x) => s + x.extra, 0) / withAlt.length : 0;
      return [
        el('h2', { class: 'mp-title' }, c.name),
        el('h3', { class: 'mp-h' }, 'What passes here'), el('p', null, c.flow),
        el('p', null, c.note),
        el('h3', { class: 'mp-h' }, 'Alternatives'), el('p', null, c.bypass),
        c.insurance ? [el('h3', { class: 'mp-h' }, 'Insurance angle'), el('p', null, c.insurance)] : null,
        c.closable ? el('div', { class: 'mp-whatif' + (closed ? ' on' : '') },
          el('button', { class: closed ? 'btn-primary' : 'chip', type: 'button', 'aria-pressed': String(closed),
            onclick: () => {
              M.closed = closed ? null : c.id;
              // show every affected route, whichever market is selected
              if (M.closed && M.market !== 'all' && !affected.some((r) => r.market === M.market)) { M.market = 'all'; drawMarkets(); }
              update(); renderPanel();
            } }, closed ? 'Reopen ' + c.name : 'What if it closes?'),
          closed ? [
            rows.length ? el('table', { class: 'data mp-table' },
              el('thead', null, el('tr', null, el('th', null, 'Route'), el('th', { class: 'num' }, 'Detour'), el('th', { class: 'num' }, 'Ship-days'))),
              el('tbody', null, rows.map((x) => el('tr', null,
                el('td', null, el('a', { href: '#maps.sea.' + x.r.id }, (x.r.code ? x.r.code + ' ' : '') + x.r.name)),
                el('td', { class: 'num' }, x.alt ? '+' + nf0.format(x.alt.nm - x.r.nm) + ' nm' : 'none'),
                el('td', { class: 'num' }, x.alt ? pctTxt(x.extra) : 'stuck'))))) : el('p', { class: 'small-note' }, 'None of the routes on this map pass here.'),
            withAlt.length ? el('p', null, `On these routes each cargo needs on average ${pctTxt(avg)} more ship-days. If they were the whole market, that is like ${pctTxt(avg)} more demand for ships with the same fleet. `,
              el('button', { class: 'btn-link', type: 'button', onclick: () => { if (F.lab) F.lab.rates = { demand: 0, fleet: 0, speed: 0, cong: 0, divert: Math.min(0.3, Math.round(avg * 100) / 100) }; location.hash = 'analytics.rates'; } },
                'Try it in the freight rate lab')) : null,
            c.alt_kind === 'none' ? el('p', null, 'With no sea alternative, ships inside are trapped and ships outside lose cargo: demand for ships on this trade falls while the price of the cargo rises elsewhere.') : null,
            c.alt_kind === 'pipeline' ? el('p', null, 'Only the oil that fits in the bypass pipelines can still be shipped, from Yanbu and Fujairah. Most Gulf cargo, including Qatari LNG, would have no way out: tanker demand from the Gulf collapses while long-haul trades from the Atlantic to Asia boom.') : null,
          ] : el('p', { class: 'small-note' }, `Shows the detour for ${affected.length} route${affected.length === 1 ? '' : 's'} on the map and the extra ship-days each cargo needs.`)) : null,
        affected.length ? [el('h3', { class: 'mp-h' }, 'Routes through here'), el('div', { class: 'chips' }, affected.map((r) => el('a', { class: 'chip', href: '#maps.sea.' + r.id }, r.code || r.name)))] : null,
        el('h3', { class: 'mp-h' }, 'In the news'), newsBlock(c.kw, 5),
      ];
    }

    function renderPanel() {
      const sel = view.sel;
      const back = sel ? el('a', { class: 'mp-back', href: '#maps.sea' }, '← All routes') : null;
      if (sel && routes.has(sel)) fill(panel, back, routePanel(routes.get(sel)));
      else if (sel && chokes.has(sel)) fill(panel, back, chokePanel(chokes.get(sel)));
      else fill(panel, marketPanel());
    }

    view.select = (sid, animate) => {
      view.sel = sid && (routes.has(sid) || chokes.has(sid)) ? sid : null;
      if (view.sel && routes.has(view.sel)) {
        const r = routes.get(view.sel);
        if (M.market !== 'all' && r.market !== M.market) { M.market = r.market; drawMarkets(); }
        const pts = r.pts.concat(...(r.legs_extra || []).map((l) => l.pts));
        const b = gp.bounds({ type: 'LineString', coordinates: pts });
        if (isFinite(b[0][0]) && b[1][0] - b[0][0] < (bounds[1][0] - bounds[0][0]) * 0.9) frame.go(frame.fit(b, 0.25), animate);
        else frame.go(frame.fit(bounds, 0), animate);
        M.region = null; drawRegions(null);
      } else if (view.sel && chokes.has(view.sel)) {
        const [x, y] = proj(chokes.get(view.sel).at);
        frame.go({ cx: x, cy: y, s: Math.max(frame.st.s, frame.st.min * 3.2) }, animate);
        M.region = null; drawRegions(null);
      }
      update();
      renderPanel();
      if (animate && window.matchMedia('(max-width: 860px)').matches && view.sel) panel.scrollIntoView({ block: 'nearest', behavior: reduced ? 'auto' : 'smooth' });
    };

    function fact(k, v, sub) { return el('div', { class: 'fact' }, el('span', { class: 'k' }, k), el('span', { class: 'v' }, v), sub ? el('span', { class: 's' }, sub) : null); }

    M.view = view;
    drawMarkets();
    const startRegion = REGIONS.find((x) => x[0] === M.region);
    frame.go(startRegion && startRegion[2] ? frame.fit(regionBox(startRegion[2])) : frame.fit(bounds, 0), false);
    drawRegions(M.region || 'world');
    view.select(id, false);
  }

  function pctTxt(x) { return (x >= 0 ? '+' : '−') + Math.abs(Math.round(x * 100)) + '%'; }

  // ================================================================ ROAD MAP
  async function buildRoad(body, id, token) {
    await ensureD3();
    const [geo, data, info] = await Promise.all([getJSON('geo/nordic.json'), getJSON('roads.json'), getJSON('roadinfo.json')]);
    if (token !== M.token) return;
    const d3 = window.d3;
    const proj = d3.geoTransverseMercator().rotate(geo.proj.rotate).scale(geo.proj.scale).translate([0, 0]);
    const P = (c) => proj(c);
    const r1 = (v) => Math.round(v * 10) / 10;
    const pathOf = (pts) => pts.map((c, i) => { const [x, y] = P(c); return (i ? 'L' : 'M') + r1(x) + ',' + r1(y); }).join('');
    const bb = (pts) => { let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; for (const c of pts) { const [x, y] = P(c); x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); } return [[x0, y0], [x1, y1]]; };
    const bounds = bb([[3.5, 57.4], [31.5, 71.4], [25, 56], [8, 54.5], [16, 69.6]]);
    const roads = new Map(data.roads.map((r) => [r.id, r]));
    const rinfo = info.roads;
    const pois = new Map(info.pois.map((p) => [p.id, p]));

    const mapBox = el('div', { class: 'map-box road' });
    const panel = el('aside', { class: 'map-panel', 'aria-live': 'polite' });
    const modeChips = el('div', { class: 'chips', role: 'group', 'aria-label': 'Colour roads by' });
    const regionChips = el('div', { class: 'chips map-regions', role: 'group', 'aria-label': 'Zoom to region' });
    const legend = el('div', { class: 'map-legend ramp' });
    fill(body, el('div', { class: 'map-layout' },
      el('div', { class: 'map-col' },
        el('div', { class: 'map-toolbar' }, modeChips),
        mapBox,
        el('div', { class: 'map-under' }, regionChips, legend)),
      panel));

    const frame = makeFrame(mapBox, bounds, { label: 'Map of Norway’s main roads coloured by traffic', maxZoom: 16, wheel: true });
    const tip = tipFor(mapBox);
    const R = frame.root;
    const gLand = svg('g', { class: 'countries' });
    for (const c of geo.countries) gLand.append(svg('path', { class: 'country ' + (c.id === 'NO' ? 'no' : c.id[0] === 'X' ? 'far' : 'near'), d: c.d }));
    const gLinks = svg('g', { class: 'links' });
    for (const l of info.links) {
      const p = svg('path', { class: 'sea-link', d: pathOf(l.pts) });
      const hit = svg('path', { class: 'link-hit', d: pathOf(l.pts) });
      hit.addEventListener('pointermove', (e) => tip.show(e, [el('b', null, l.name), el('span', null, 'Ferry with trailers and trucks')]));
      hit.addEventListener('pointerleave', () => tip.hide());
      gLinks.append(p, hit);
    }
    const gNordic = svg('g', { class: 'nordic-roads' });
    for (const n of info.nordic) {
      const p = svg('path', { class: 'nordic-road', d: pathOf(n.pts) });
      const hit = svg('path', { class: 'link-hit', d: pathOf(n.pts) });
      hit.addEventListener('pointermove', (e) => tip.show(e, [el('b', null, n.name), el('span', null, 'Main road outside Norway (no traffic data shown)')]));
      hit.addEventListener('pointerleave', () => tip.hide());
      gNordic.append(p, hit);
    }
    const gRoads = svg('g', { class: 'roads' });
    const gSel = svg('g', { class: 'road-sel' });
    const gPoi = svg('g', { class: 'pois' });
    R.append(gLand, gLinks, gNordic, gRoads, gSel, gPoi);

    // classes for colour and width
    const CLS = { all: data.classes || [2000, 5000, 10000, 20000, 40000], heavy: [250, 500, 1000, 2000, 4000] };
    const val = (st, mode) => mode === 'heavy' ? (st.heavy == null ? null : st.adt * st.heavy / 100) : st.adt;
    const clsOf = (v, mode) => { if (v == null) return -1; const c = CLS[mode]; let i = 0; while (i < c.length && v >= c[i]) i++; return i; };

    const stretchNodes = [];
    for (const r of data.roads) {
      r.stretches.forEach((st, i) => {
        const d = pathOf(st.pts);
        const vis = svg('path', { class: 'rd', d });
        const hit = svg('path', { class: 'rd-hit', d });
        const node = { r, st, vis, hit, i };
        hit.addEventListener('pointermove', (e) => tip.show(e, stretchTip(r, st)));
        hit.addEventListener('pointerleave', () => tip.hide());
        hit.addEventListener('click', () => {
          tip.hide();
          view.focusStretch = node;
          if (location.hash === '#maps.road.' + r.id) view.select(r.id, false);
          else location.hash = 'maps.road.' + r.id;
        });
        stretchNodes.push(node);
      });
    }
    function paint() {
      const mode = M.mode;
      const ordered = stretchNodes.map((n) => ({ n, c: clsOf(val(n.st, mode), mode) })).sort((a, b) => a.c - b.c);
      gRoads.replaceChildren();
      for (const { n, c } of ordered) {
        n.vis.setAttribute('class', 'rd q' + Math.max(0, c) + (c < 0 ? ' nodata' : ''));
        gRoads.append(n.vis);
      }
      for (const { n } of ordered) gRoads.append(n.hit);
      drawLegend();
    }

    function stretchTip(r, st) {
      const hv = st.heavy != null ? Math.round(st.adt * st.heavy / 100) : null;
      return [
        el('b', null, r.id + (st.places.length ? '  ' + st.places.slice(0, 3).join(', ') : '')),
        el('span', null, `${nf0.format(st.adt)} vehicles a day` + (st.min !== st.max ? ` (${nf0.format(st.min)}–${nf0.format(st.max)})` : '')),
        hv != null ? el('span', null, `${nf0.format(hv)} heavy vehicles a day (${nf1.format(st.heavy)}% long vehicles)`) : null,
        el('span', { class: 'sub' }, `${nf1.format(st.km)} km` + (st.year ? `, counted ${st.year}` : '')),
      ];
    }

    // points of interest
    const SYMBOL = {
      pass: () => svg('path', { d: 'M0,-6 L6,5 L-6,5 Z' }),
      ferry: () => svg('g', null, svg('circle', { r: 5.5 }), svg('path', { class: 'wave', d: 'M-3.5,0.5 q1.75,-2 3.5,0 t3.5,0' })),
      border: () => svg('rect', { x: -4.5, y: -4.5, width: 9, height: 9 }),
      hub: () => svg('circle', { r: 4 }),
    };
    const markers = [];
    for (const p of info.pois) {
      const [x, y] = P(p.at);
      const g = svg('g', { class: 'poi ' + p.kind, tabindex: '0', role: 'button', 'aria-label': p.name },
        SYMBOL[p.kind](), p.kind === 'hub' ? svg('text', { class: 'lbl', x: 7, y: 4 }, p.name.replace(/\s*\(.*\)$/, '')) : svg('text', { class: 'lbl minor', x: 8, y: 4 }, p.name));
      g.addEventListener('pointermove', (e) => tip.show(e, [el('b', null, p.name), el('span', null, ({ pass: 'Mountain pass', ferry: 'Ferry crossing', border: 'Border crossing', hub: 'Freight hub' })[p.kind] + (p.road ? ' on ' + p.road : ''))]));
      g.addEventListener('pointerleave', () => tip.hide());
      g.addEventListener('click', () => { tip.hide(); location.hash = 'maps.road.' + p.id; });
      g.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); location.hash = 'maps.road.' + p.id; } });
      gPoi.append(g);
      markers.push({ g, x, y });
    }
    placeMarkers(frame, markers);
    frame.onZoom.push((k) => { R.classList.toggle('zoomed', k > 2.6); R.classList.toggle('zoomed2', k > 5); });

    function drawModes() {
      fill(modeChips, [['all', 'All traffic'], ['heavy', 'Heavy vehicles']].map(([mid, name]) => el('button', {
        class: 'chip', type: 'button', 'aria-pressed': String(M.mode === mid), onclick: () => { M.mode = mid; drawModes(); paint(); renderPanel(); },
      }, name)));
    }
    function drawLegend() {
      const c = CLS[M.mode];
      const labels = [`under ${nf0.format(c[0])}`, ...c.slice(0, -1).map((v, i) => `${nf0.format(v)}–${nf0.format(c[i + 1])}`), `over ${nf0.format(c[c.length - 1])}`];
      fill(legend,
        el('span', { class: 'lg-title' }, M.mode === 'heavy' ? 'Heavy vehicles a day' : 'Vehicles a day (ÅDT)'),
        el('span', { class: 'ramp-row' }, labels.map((t, i) => el('span', { class: 'ramp-item' }, el('i', { class: 'q' + i }), t))),
        el('span', { class: 'sym-row' },
          el('span', null, el('i', { class: 'sym pass' }), 'Mountain pass'), el('span', null, el('i', { class: 'sym ferry' }), 'Ferry'),
          el('span', null, el('i', { class: 'sym border' }), 'Border'), el('span', null, el('i', { class: 'sym link' }), 'Ferry link abroad')));
    }

    const REGIONS = [
      ['norway', 'All of Norway', [[4, 57.8], [31.2, 71.2]]],
      ['south', 'Southern Norway', [[4.6, 57.9], [12.6, 63.6]]],
      ['west', 'Western Norway', [[4.6, 58.6], [8.6, 62.8]]],
      ['north', 'Northern Norway', [[11.5, 64.5], [31.2, 71.2]]],
      ['nordic', 'Links abroad', [[4, 53.6], [25, 64]]],
    ];
    function drawRegions(cur) {
      fill(regionChips, REGIONS.map(([rid, name, b]) => el('button', { class: 'chip', type: 'button', 'aria-pressed': String(cur === rid),
        onclick: () => { M.roadRegion = rid; frame.go(frame.fit(bb(b), 0.04), true); drawRegions(rid); } }, name)));
    }

    // ---------------------------------------------------------- panels
    const view = { tab: 'road', node: body, sel: null, focusStretch: null, destroy: frame.destroy };
    const heavyPerDay = (st) => st.heavy == null ? 0 : st.adt * st.heavy / 100;

    function roadStats(r) {
      const sts = r.stretches;
      const busiest = sts.reduce((a, b) => (b.max > a.max ? b : a), sts[0]);
      const trucks = sts.reduce((a, b) => (heavyPerDay(b) > heavyPerDay(a) ? b : a), sts[0]);
      const len = sts.reduce((s, x) => s + x.km, 0);
      const avgAdt = sts.reduce((s, x) => s + x.adt * x.km, 0) / (len || 1);
      const avgHv = sts.reduce((s, x) => s + heavyPerDay(x) * x.km, 0) / (len || 1);
      return { busiest, trucks, len, avgAdt, avgHv };
    }

    function overviewPanel() {
      const ranked = data.roads.map((r) => ({ r, s: roadStats(r) })).sort((a, b) => b.s.avgHv - a.s.avgHv);
      return [
        el('h2', { class: 'mp-title' }, 'Where the trucks are'),
        el('p', null, 'ÅDT is the average number of vehicles passing a point per day over a year. The share of long vehicles (5.6 m and longer) is the best available measure of trucks. Multiply the two and you get heavy vehicles per day.'),
        el('h3', { class: 'mp-h' }, 'Roads ranked by trucks per day'),
        el('table', { class: 'data mp-table' },
          el('thead', null, el('tr', null, el('th', null, 'Road'), el('th', { class: 'num' }, 'Trucks/day'), el('th', { class: 'num' }, 'Share'))),
          el('tbody', null, ranked.map(({ r, s }) => el('tr', null,
            el('td', null, el('a', { href: '#maps.road.' + r.id }, r.id), el('span', { class: 'small-note' }, ' ' + (rinfo[r.id] ? rinfo[r.id].title : ''))),
            el('td', { class: 'num' }, nf0.format(s.avgHv)),
            el('td', { class: 'num' }, r.summary.heavyShare != null ? nf1.format(r.summary.heavyShare) + '%' : '–'))))),
        el('p', { class: 'small-note' }, 'Trucks per day is a length-weighted average along the road. Numbers vary a lot along each road; hover the map for each stretch.'),
        el('h3', { class: 'mp-h' }, 'Mountain passes'), poiChips('pass'),
        el('h3', { class: 'mp-h' }, 'Ferries on the E39'), poiChips('ferry'),
        el('h3', { class: 'mp-h' }, 'Border crossings'), poiChips('border'),
        el('p', { class: 'small-note' }, `Traffic data: Statens vegvesen, NVDB (Trafikkmengde), NLOD licence. Updated ${data.updated ? data.updated.slice(0, 10) : ''}. Roads outside Norway and ferry links are drawn as simple lines.`),
      ];
    }
    function poiChips(kind) {
      return el('div', { class: 'chips' }, info.pois.filter((p) => p.kind === kind).map((p) => el('a', { class: 'chip', href: '#maps.road.' + p.id }, p.name)));
    }

    function roadPanel(r) {
      const meta = rinfo[r.id] || {};
      const s = roadStats(r);
      const fs = view.focusStretch && view.focusStretch.r === r ? view.focusStretch.st : null;
      const ps = info.pois.filter((p) => p.road === r.id);
      return [
        el('div', { class: 'mp-head' }, el('span', { class: 'code road' }, r.id), el('h2', { class: 'mp-title' }, meta.title || r.id)),
        el('p', null, meta.role),
        el('p', null, meta.freight),
        fs ? el('div', { class: 'mp-alert info' }, el('b', null, 'The stretch you clicked: '), `${fs.places.join(', ')}. ${nf0.format(fs.adt)} vehicles a day`,
          fs.heavy != null ? `, of which ${nf1.format(fs.heavy)}% long vehicles (about ${nf0.format(heavyPerDay(fs))} trucks).` : '.') : null,
        el('div', { class: 'mp-facts' },
          fact('Length with counts', `${nf0.format(s.len)} km`),
          fact('Traffic', `${nf0.format(r.summary.minAdt)}–${nf0.format(r.summary.maxAdt)} a day`),
          fact('Busiest', s.busiest.places.slice(0, 2).join(', '), `${nf0.format(s.busiest.max)} vehicles a day`),
          fact('Most trucks', s.trucks.places.slice(0, 2).join(', '), `about ${nf0.format(heavyPerDay(s.trucks))} a day`),
          fact('Long vehicles', r.summary.heavyShare != null ? `${nf1.format(r.summary.heavyShare)}% on average` : 'no data'),
          fact('Trucks per day', `about ${nf0.format(s.avgHv)} on average`)),
        ps.length ? [el('h3', { class: 'mp-h' }, 'On this road'), el('div', { class: 'chips' }, ps.map((p) => el('a', { class: 'chip', href: '#maps.road.' + p.id }, p.name)))] : null,
        el('div', { class: 'mp-actions' },
          meta.truck && meta.truck !== 'custom' ? el('button', { class: 'btn-primary', type: 'button', onclick: () => { if (F.lab) F.lab.truck.route = meta.truck; location.hash = 'analytics.truck'; } }, 'Price a trip on this road')
            : el('button', { class: 'chip', type: 'button', onclick: () => { location.hash = 'analytics.truck'; } }, 'Truck trip calculator')),
        el('h3', { class: 'mp-h' }, 'In the news'), newsBlock(meta.kw || [r.id.toLowerCase()], 4),
      ];
    }

    function poiPanel(p) {
      const r = p.road ? roads.get(p.road) : null;
      let near = null;
      if (r) {
        const [px, py] = P(p.at);
        let best = Infinity;
        for (const st of r.stretches) for (const c of st.pts) { const [x, y] = P(c); const d = (x - px) ** 2 + (y - py) ** 2; if (d < best) { best = d; near = st; } }
      }
      const kindName = ({ pass: 'Mountain pass', ferry: 'Ferry crossing', border: 'Border crossing', hub: 'Freight hub' })[p.kind];
      const kw = [p.name.split(/[–(]/)[0].trim().toLowerCase()];
      return [
        el('div', { class: 'mp-head' }, el('span', { class: 'code road' }, kindName), el('h2', { class: 'mp-title' }, p.name)),
        el('p', null, p.text),
        near ? el('div', { class: 'mp-facts' },
          fact('Road', p.road),
          fact('Traffic nearby', `${nf0.format(near.adt)} a day`, near.places.join(', ')),
          near.heavy != null ? fact('Trucks nearby', `about ${nf0.format(heavyPerDay(near))} a day`, `${nf1.format(near.heavy)}% long vehicles`) : null) : null,
        r ? el('div', { class: 'mp-actions' }, el('a', { class: 'chip', href: '#maps.road.' + r.id }, 'More about ' + r.id)) : null,
        p.kind === 'pass' || p.kind === 'ferry' ? el('p', { class: 'small-note' }, 'For live road status and closures, check Statens vegvesen’s traffic information (vegvesen.no/trafikk).') : null,
        el('h3', { class: 'mp-h' }, 'In the news'), newsBlock(kw, 4),
      ];
    }

    function renderPanel() {
      const sel = view.sel;
      const back = sel ? el('a', { class: 'mp-back', href: '#maps.road' }, '← All roads') : null;
      if (sel && roads.has(sel)) fill(panel, back, roadPanel(roads.get(sel)));
      else if (sel && pois.has(sel)) fill(panel, back, poiPanel(pois.get(sel)));
      else fill(panel, overviewPanel());
    }

    view.select = (sid, animate) => {
      view.sel = sid && (roads.has(sid) || pois.has(sid)) ? sid : null;
      if (!view.sel || !roads.has(view.sel)) view.focusStretch = null;
      gSel.replaceChildren();
      R.classList.toggle('has-sel', !!(view.sel && roads.has(view.sel)));
      for (const n of stretchNodes) n.vis.classList.toggle('on', !!view.sel && n.r.id === view.sel);
      for (const m of gPoi.children) m.classList.toggle('sel', m.getAttribute('aria-label') === (pois.get(view.sel) || {}).name);
      if (view.sel && roads.has(view.sel)) {
        const r = roads.get(view.sel);
        for (const st of r.stretches) gSel.append(svg('path', { class: 'sel-casing', d: pathOf(st.pts) }));
        if (!view.focusStretch) frame.go(frame.fit(bb(r.stretches.flatMap((s) => s.pts)), 0.12), animate);
        M.roadRegion = null; drawRegions(null);
      } else if (view.sel && pois.has(view.sel)) {
        const [x, y] = P(pois.get(view.sel).at);
        frame.go({ cx: x, cy: y, s: Math.max(frame.st.s, frame.st.min * 4) }, animate);
        M.roadRegion = null; drawRegions(null);
      }
      renderPanel();
      if (animate && window.matchMedia('(max-width: 860px)').matches && view.sel) panel.scrollIntoView({ block: 'nearest', behavior: reduced ? 'auto' : 'smooth' });
    };
    function fact(k, v, sub) { return el('div', { class: 'fact' }, el('span', { class: 'k' }, k), el('span', { class: 'v' }, v), sub ? el('span', { class: 's' }, sub) : null); }

    M.view = view;
    drawModes();
    paint();
    const start = REGIONS.find((x) => x[0] === (M.roadRegion || 'south'));
    frame.go(frame.fit(bb(start[2]), 0.04), false);
    drawRegions(start[0]);
    view.select(id, false);
  }
})();
