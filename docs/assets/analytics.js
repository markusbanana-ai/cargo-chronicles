/* Cargo Chronicles — analytics: live market charts and teaching models.
   The models are deliberately simple so the mechanics are visible. They are not forecasts. */
(function () {
  'use strict';
  const F = (window.Fairway = window.Fairway || {});
  const el = (...a) => F.el(...a);
  const fill = (...a) => F.fill(...a);
  const lab = (F.lab = F.lab || {
    range: 180,
    rates: { demand: 0, fleet: 0, speed: 0, cong: 0, divert: 0 },
    voyage: null,
    truck: { route: 'bgo-osl', km: 465, tolls: 1200, diesel: 17.5, cons: 0.33, speed: 65, wage: 480, vehicle: 4.5, loadH: 1.5, empty: false, pallets: 33 },
    effect: 'oil-spike',
  });
  let charts = [];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const TABS = [
    ['markets', 'Market pulse'],
    ['rates', 'Freight rate lab'],
    ['voyage', 'Voyage economics'],
    ['truck', 'Truck trip cost'],
    ['effects', 'Cause & effect'],
  ];

  // ---------------------------------------------------------------- formatting
  const nf0 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 });
  const nf1 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1, minimumFractionDigits: 1 });
  const nf2 = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
  const usd = (n) => 'USD ' + nf0.format(Math.round(n));
  const nok = (n) => 'NOK ' + nf0.format(Math.round(n));
  const pct = (n, dp = 1) => (n >= 0 ? '+' : '−') + Math.abs(n).toFixed(dp) + '%';
  const compact = (n) => {
    const a = Math.abs(n);
    if (a >= 1e6) return (n / 1e6).toFixed(a >= 1e7 ? 0 : 1) + 'M';
    if (a >= 1e3) return (n / 1e3).toFixed(a >= 1e4 ? 0 : 1) + 'K';
    return String(Math.round(n));
  };

  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function colors() {
    return {
      c1: css('--c1'), c2: css('--c2'), c3: css('--c3'), c4: css('--c4'), cm: css('--c-muted'),
      ink: css('--ink'), ink2: css('--ink-2'), muted: css('--muted'), line: css('--line'), soft: css('--line-soft'), surface: css('--surface'),
    };
  }
  function alpha(hex, a) {
    const h = hex.replace('#', '');
    const n = parseInt(h.length === 3 ? h.split('').map((c) => c + c).join('') : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }

  // ---------------------------------------------------------------- chart helpers
  let registered = false;
  function ensureChart() {
    if (!window.Chart) return false;
    if (!registered) {
      window.Chart.register({
        id: 'crosshair',
        afterDatasetsDraw(chart) {
          const opt = chart.options.plugins.crosshair;
          if (!opt || !opt.on) return;
          const act = chart.tooltip && chart.tooltip.getActiveElements();
          if (!act || !act.length) return;
          const x = act[0].element.x, { top, bottom } = chart.chartArea, ctx = chart.ctx;
          ctx.save(); ctx.strokeStyle = opt.color; ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(x, top); ctx.lineTo(x, bottom); ctx.stroke(); ctx.restore();
        },
      });
      window.Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
      registered = true;
    }
    return true;
  }

  function axis(c, title, fmt, extra) {
    return Object.assign({
      grid: { color: c.soft, drawTicks: false },
      border: { color: c.line },
      ticks: { color: c.muted, font: { size: 11 }, padding: 6, maxTicksLimit: 6, callback: fmt ? function (v) { return fmt(this.getLabelForValue ? (typeof v === 'number' && this.type !== 'category' ? v : this.getLabelForValue(v)) : v); } : undefined },
      title: title ? { display: true, text: title, color: c.muted, font: { size: 11 } } : { display: false },
    }, extra || {});
  }

  function baseOptions(c, o) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: reduced ? false : { duration: 220 },
      interaction: { mode: o.mode || 'index', intersect: false },
      plugins: {
        legend: { display: false },
        crosshair: { on: o.crosshair !== false, color: c.line },
        tooltip: {
          backgroundColor: c.surface, titleColor: c.ink2, bodyColor: c.ink, borderColor: c.line, borderWidth: 1,
          padding: 10, boxWidth: 12, boxHeight: 2, bodyFont: { weight: '600' },
          callbacks: o.tooltip || {},
          filter: o.tooltipFilter,
        },
      },
      scales: { x: o.x, y: o.y },
    };
  }

  function makeChart(canvas, cfg) {
    if (!ensureChart()) {
      canvas.replaceWith(el('p', { class: 'small-note' }, 'The chart library could not load. The numbers above still update.'));
      return null;
    }
    const ch = new window.Chart(canvas.getContext('2d'), cfg);
    charts.push(ch);
    return ch;
  }

  function chartCard(title, cap, box, opts) {
    opts = opts || {};
    const canvas = el('canvas', { role: 'img', 'aria-label': title });
    const node = el('section', { class: 'chart-card' },
      el('h3', null, title),
      cap ? el('p', { class: 'cap' }, cap) : null,
      opts.legend || null,
      el('div', { class: 'chart-box' + (box === 'short' ? ' short' : '') }, canvas),
      opts.after || null);
    return { node, canvas };
  }

  function legend(items) {
    return el('div', { class: 'legend' }, items.map(([color, label, sq]) => el('span', null, el('i', { class: sq ? 'sq' : '', style: 'background:' + color }), label)));
  }

  function slider(id, label, val, min, max, step, fmt, onInput, help) {
    const out = el('output', { for: id }, fmt(val));
    const input = el('input', { type: 'range', id, min, max, step, value: val });
    input.addEventListener('input', () => { const v = parseFloat(input.value); out.textContent = fmt(v); onInput(v); });
    return el('div', { class: 'ctl' }, el('div', { class: 'ctl-top' }, el('label', { for: id }, label), out), input, help ? el('span', { class: 'help' }, help) : null);
  }

  function numberField(id, label, val, step, onInput, help) {
    const input = el('input', { type: 'number', id, value: val, step, inputmode: 'decimal' });
    input.addEventListener('input', () => { const v = parseFloat(input.value); if (!Number.isNaN(v)) onInput(v); });
    return el('div', { class: 'ctl' }, el('label', { for: id, class: 'ctl-top' }, label), input, help ? el('span', { class: 'help' }, help) : null);
  }

  function termsRow(ids) {
    return el('div', { class: 'learn-row' }, el('span', { class: 'small-note', style: 'margin-right:4px' }, 'Terms used here:'), ids.map((id) => F.termChip(id)));
  }

  // ---------------------------------------------------------------- page
  F.renderAnalytics = function (main, tab) {
    charts.forEach((c) => c.destroy());
    charts = [];
    if (!TABS.some(([id]) => id === tab)) tab = 'markets';
    const body = el('div');
    F.fill(main,
      el('div', { class: 'page-head' },
        el('span', { class: 'eyebrow' }, 'Analytics'),
        el('h1', { class: 'page-title' }, 'What happens if…'),
        el('p', { class: 'page-intro' }, 'Live market data and hands-on models that show how fuel prices, rules and events move transport costs and freight rates. The models are simplified to show the mechanics; they are not forecasts.')),
      el('div', { class: 'tabs', role: 'tablist' }, TABS.map(([id, name]) => el('button', {
        class: 'tab', role: 'tab', type: 'button', 'aria-selected': String(id === tab),
        onclick: () => { location.hash = 'analytics.' + id; },
      }, name))),
      body);
    ({ markets, rates, voyage, truck, effects })[tab](body);
  };

  const rerender = () => { if (F.state && F.state.route === 'analytics' && F.render) F.render(); };
  window.addEventListener('fairway:theme', rerender);
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', rerender);

  // ---------------------------------------------------------------- 1. market pulse
  const MARKET_INFO = {
    brent: { title: 'Brent crude oil', unit: 'USD per barrel', why: 'Brent sets the direction for bunker fuel and diesel. When it rises, voyage costs rise, ships slow down, and Norwegian hauliers pay more at the pump a few weeks later.', terms: ['bunkers', 'slow-steaming', 'road-tax'] },
    usdnok: { title: 'US dollar in Norwegian kroner', unit: 'NOK per USD', why: 'Freight, ship prices and loans are in dollars, while Norwegian crew, offices and taxes are paid in kroner. A stronger dollar (higher number) lifts Norwegian shipowners’ earnings measured in NOK, but makes dollar-priced fuel and imports dearer.', terms: ['sofr', 'opex'] },
    eurnok: { title: 'Euro in Norwegian kroner', unit: 'NOK per EUR', why: 'Most of Norway’s trade is with Europe. Trucks, trailers, spare parts and EU emission allowances are priced in euros, so a stronger euro raises costs for Norwegian hauliers and shipping companies.', terms: ['eu-ets', 'electric-truck'] },
  };

  function markets(box) {
    const S = (F.data.markets && F.data.markets.series) || {};
    const c = colors();
    const ranges = [[30, '1M'], [90, '3M'], [180, '6M'], [365, '1Y']];
    box.append(el('div', { class: 'filters' }, el('span', { class: 'lbl' }, 'Period'),
      el('div', { class: 'chips', role: 'group', 'aria-label': 'Period' }, ranges.map(([d, name]) => el('button', {
        class: 'chip', type: 'button', 'aria-pressed': String(lab.range === d), onclick: () => { lab.range = d; F.render(); },
      }, name)))));
    const grid = el('div', { class: 'results' });
    box.append(grid);
    for (const key of ['brent', 'usdnok', 'eurnok']) {
      const info = MARKET_INFO[key];
      const s = S[key];
      if (!s || !s.points || s.points.length < 2) {
        grid.append(el('section', { class: 'chart-card' }, el('h3', null, info.title),
          el('p', { class: 'small-note' }, key === 'brent' ? 'The Brent price chart appears after the first automatic update (data from the U.S. Energy Information Administration via FRED).' : 'No data yet. It appears after the first automatic update.'),
          el('p', { class: 'cap' }, info.why), termsRow(info.terms)));
        continue;
      }
      const lastDate = new Date(s.points[s.points.length - 1][0]);
      const from = new Date(lastDate - lab.range * 864e5);
      const pts = s.points.filter((p) => new Date(p[0]) >= from);
      const last = pts[pts.length - 1][1], first = pts[0][1];
      const hi = Math.max(...pts.map((p) => p[1])), lo = Math.min(...pts.map((p) => p[1]));
      const dp = key === 'brent' ? 1 : 2;
      const table = el('details', null, el('summary', { class: 'small-note', style: 'cursor:pointer' }, 'Show the latest values as a table'),
        el('div', { class: 'table-wrap', style: 'margin-top:8px' }, el('table', { class: 'data' },
          el('thead', null, el('tr', null, el('th', null, 'Date'), el('th', { style: 'text-align:right' }, info.unit))),
          el('tbody', null, pts.slice(-12).reverse().map((p) => el('tr', null, el('td', null, p[0]), el('td', { class: 'num' }, p[1].toFixed(dp + (key === 'brent' ? 1 : 2)))))))));
      const { node, canvas } = chartCard(info.title, `${info.unit} · ${s.source} · latest ${s.points[s.points.length - 1][0]}`, 'normal', {
        legend: el('div', { class: 'kpis' },
          el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Latest'), el('div', { class: 'v' }, last.toFixed(dp))),
          el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Change over period'), el('div', { class: 'v' }, pct(((last - first) / first) * 100))),
          el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Range in period'), el('div', { class: 'v', style: 'font-size:1.2rem' }, `${lo.toFixed(dp)} – ${hi.toFixed(dp)}`))),
        after: [el('div', { class: 'explain' }, el('span', { class: 'h' }, 'Why it matters'), el('p', null, info.why), termsRow(info.terms)), table],
      });
      grid.append(node);
      makeChart(canvas, {
        type: 'line',
        data: {
          labels: pts.map((p) => p[0]),
          datasets: [{
            label: info.title, data: pts.map((p) => p[1]), borderColor: c.c1, borderWidth: 2, tension: 0.15,
            backgroundColor: alpha(c.c1, 0.1), fill: 'start',
            pointRadius: pts.map((_, i) => (i === pts.length - 1 ? 4 : 0)), pointHoverRadius: 5,
            pointBackgroundColor: c.c1, pointBorderColor: c.surface, pointBorderWidth: 2,
          }],
        },
        options: baseOptions(c, {
          x: axis(c, null, (v) => { const d = new Date(v); return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }); }, { ticks: { color: c.muted, font: { size: 11 }, maxTicksLimit: 6, maxRotation: 0, callback(v) { const d = new Date(this.getLabelForValue(v)); return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }); } } }),
          y: axis(c, null, null, { ticks: { color: c.muted, font: { size: 11 }, maxTicksLimit: 5 } }),
          tooltip: { label: (ctx) => ` ${ctx.parsed.y.toFixed(dp + 1)} ${info.unit}` },
        }),
      });
    }
  }

  // ---------------------------------------------------------------- 2. freight rate lab
  const U0 = 0.86, M = 0.7, RMIN = 8000, K = 12000, UMAX = 0.997;
  function rateAt(u) {
    if (u <= M) return RMIN;
    const x = Math.min(u, UMAX);
    return RMIN + K * -Math.log(1 - (x - M) / (1 - M));
  }
  const capOf = (p) => (1 + p.fleet) * (1 + p.speed) * (1 - p.cong);
  const demOf = (p) => (1 + p.demand) * (1 + p.divert);

  const RATE_PRESETS = [
    ['Reset', { demand: 0, fleet: 0, speed: 0, cong: 0, divert: 0 }],
    ['Red Sea diversion', { demand: 0, fleet: 0, speed: 0, cong: 0, divert: 0.1 }],
    ['China slowdown', { demand: -0.06, fleet: 0, speed: 0, cong: 0, divert: 0 }],
    ['Delivery wave', { demand: 0, fleet: 0.08, speed: 0, cong: 0, divert: 0 }],
    ['Slow steaming', { demand: 0, fleet: 0, speed: -0.1, cong: 0, divert: 0 }],
    ['Port congestion', { demand: 0, fleet: 0, speed: 0, cong: 0.05, divert: 0 }],
  ];

  function rates(box) {
    const p = lab.rates;
    const c = colors();
    const out = el('div', { class: 'results' });
    const fmtP = (v) => (v > 0 ? '+' : v < 0 ? '−' : '±') + Math.abs(Math.round(v)) + '%';
    const controls = el('div', { class: 'controls' },
      el('div', { class: 'ctl' }, el('span', { class: 'ctl-top' }, 'Start from a scenario'),
        el('div', { class: 'presets' }, RATE_PRESETS.map(([name, v]) => el('button', { class: 'chip', type: 'button', onclick: () => { Object.assign(p, v); F.render(); } }, name)))),
      slider('r-demand', 'Cargo demand', p.demand * 100, -15, 15, 1, fmtP, (v) => { p.demand = v / 100; draw(); }, 'Tonnes to be shipped, e.g. Chinese iron ore imports.'),
      slider('r-divert', 'Longer routes', p.divert * 100, 0, 30, 1, fmtP, (v) => { p.divert = v / 100; draw(); }, 'Extra distance per cargo, e.g. avoiding Suez. Raises ton-miles.'),
      slider('r-fleet', 'Fleet size', p.fleet * 100, -5, 15, 1, fmtP, (v) => { p.fleet = v / 100; draw(); }, 'Newbuilding deliveries minus scrapping.'),
      slider('r-speed', 'Average speed', p.speed * 100, -20, 10, 1, fmtP, (v) => { p.speed = v / 100; draw(); }, 'Slower ships carry less per year.'),
      slider('r-cong', 'Ships stuck in congestion', p.cong * 100, 0, 10, 1, (v) => Math.round(v) + '%', (v) => { p.cong = v / 100; draw(); }, 'Share of the fleet waiting outside ports.'));
    box.append(el('div', { class: 'lab' }, controls, out));

    const kpis = el('div', { class: 'kpis' });
    const explain = el('div', { class: 'explain' });
    const cc = chartCard('Supply meets demand', 'Freight rate for a typical ship (USD per day) against the amount of transport the market needs. Illustrative numbers.', 'normal', {
      legend: legend([[c.cm, 'Supply today'], [c.c1, 'Supply after change'], [c.cm, 'Demand today'], [c.c2, 'Demand after change']]),
    });
    out.append(kpis, cc.node, explain, termsRow(['utilisation', 'ton-miles', 'slow-steaming', 'congestion', 'orderbook', 'spot-market']),
      el('p', { class: 'disclaimer' }, 'Model: ships lay up when rates fall to operating cost (USD 8,000/day), and the supply curve turns almost vertical as utilisation approaches 100%. Starting point: 86% utilisation. Real markets also depend on expectations, contracts and specific trades.'));

    const xs = [];
    for (let x = 60; x <= 140; x += 0.5) xs.push(x);
    const chart = makeChart(cc.canvas, {
      type: 'scatter',
      data: { datasets: [
        { label: 'Supply today', data: [], showLine: true, borderColor: c.cm, borderWidth: 2, pointRadius: 0, order: 4 },
        { label: 'Supply after change', data: [], showLine: true, borderColor: c.c1, borderWidth: 2, pointRadius: 0, order: 3 },
        { label: 'Demand today', data: [], showLine: true, borderColor: c.cm, borderWidth: 2, pointRadius: 0, order: 2 },
        { label: 'Demand after change', data: [], showLine: true, borderColor: c.c2, borderWidth: 2, pointRadius: 0, order: 1 },
        { label: 'Market rate', data: [], pointRadius: 5, pointHoverRadius: 6, pointBackgroundColor: [c.cm, c.c2], pointBorderColor: c.surface, pointBorderWidth: 2, order: 0 },
      ] },
      options: baseOptions(c, {
        mode: 'nearest', crosshair: false,
        x: axis(c, 'Transport demand (today = 100)', null, { type: 'linear', min: 60, max: 140, ticks: { color: c.muted, font: { size: 11 }, stepSize: 20 } }),
        y: axis(c, 'USD per day', null, { min: 0, max: 70000, ticks: { color: c.muted, font: { size: 11 }, stepSize: 10000, callback: (v) => compact(v) } }),
        tooltip: { title: () => '', label: (ctx) => ` ${ctx.dataset.label}: ${usd(ctx.parsed.y)}` },
        tooltipFilter: (item) => item.datasetIndex === 4,
      }),
    });

    function draw() {
      const C = capOf(p), D = demOf(p);
      const u0 = U0, u1 = (U0 * D) / C;
      const r0 = rateAt(u0), r1 = rateAt(u1);
      if (chart) {
        const ds = chart.data.datasets;
        ds[0].data = xs.filter((x) => (U0 * x) / 100 <= UMAX).map((x) => ({ x, y: rateAt((U0 * x) / 100) }));
        ds[1].data = xs.filter((x) => (U0 * x) / 100 / C <= UMAX).map((x) => ({ x, y: rateAt((U0 * x) / 100 / C) }));
        ds[2].data = [{ x: 100, y: 0 }, { x: 100, y: 70000 }];
        const dx = Math.max(60, Math.min(140, 100 * D));
        ds[3].data = [{ x: dx, y: 0 }, { x: dx, y: 70000 }];
        ds[4].data = [{ x: 100, y: r0 }, { x: dx, y: Math.min(70000, r1) }];
        chart.update(reduced ? 'none' : undefined);
      }
      const ch = ((r1 - r0) / r0) * 100;
      fill(kpis, 
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Fleet utilisation'), el('div', { class: 'v' }, Math.min(99.9, u1 * 100).toFixed(1) + '%'), el('div', { class: 'd' }, 'from ' + (u0 * 100).toFixed(0) + '%')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Freight rate'), el('div', { class: 'v' }, usd(r1)), el('div', { class: 'd' }, 'from ' + usd(r0) + ' per day')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Change in rate'), el('div', { class: 'v' }, pct(ch, 0)), el('div', { class: 'd' }, `demand ×${D.toFixed(2)}, supply ×${C.toFixed(2)}`)));
      const lines = [];
      if (Math.abs(D - C) < 0.002) lines.push('Demand and effective supply moved together, so utilisation and the rate stay where they were.');
      else if (D > C) lines.push(`Transport demand grew ${((D / C - 1) * 100).toFixed(1)}% faster than effective supply, so a larger share of the fleet is needed and rates rise.`);
      else lines.push(`Effective supply grew ${((C / D - 1) * 100).toFixed(1)}% faster than demand, so more ships compete for each cargo and rates fall.`);
      if (u1 >= UMAX) lines.push('Demand now exceeds what the fleet can carry. In reality rates would spike until cargo owners delay shipments or ships sail faster; the chart is capped.');
      else if (u1 > 0.92) lines.push('Above about 92% utilisation the supply curve is almost vertical: each extra percent of demand adds thousands of dollars a day. This is why freight rates can explode while volumes barely change.');
      else if (u1 < 0.75) lines.push('With this much spare capacity the curve is flat near the floor: rates sit close to operating costs until the slack is absorbed, and some ships go into lay-up.');
      else lines.push('In the middle of the curve, rates react noticeably but not wildly to changes in the balance.');
      if (p.speed < 0) lines.push('Slower sailing is a common reaction to high fuel or emission costs. It quietly removes capacity, which is why expensive bunkers can support freight rates.');
      if (p.divert > 0) lines.push('Longer routes need more ships for the same cargo: ton-mile demand rises even if tonnes stay flat.');
      fill(explain, el('span', { class: 'h' }, 'What happened'), lines.map((t) => el('p', null, t)));
    }
    draw();
  }

  // ---------------------------------------------------------------- 3. voyage economics
  function eurUsd() {
    const S = (F.data.markets && F.data.markets.series) || {};
    if (S.eurnok && S.usdnok) {
      const e = S.eurnok.points[S.eurnok.points.length - 1][1], u = S.usdnok.points[S.usdnok.points.length - 1][1];
      return Math.round((e / u) * 1000) / 1000;
    }
    return 1.1;
  }

  function voyageCalc(p, over) {
    const q = Object.assign({}, p, over || {});
    const seaDays = q.dist / (q.speed * 24);
    const consAt = q.cons * Math.pow(q.speed / 12.5, 3);
    const fuel = seaDays * consAt + q.portDays * q.portCons;
    const bunkerCost = fuel * q.bunker;
    const co2 = fuel * 3.114;
    const etsCost = co2 * q.ets * q.eua * q.eurusd;
    const revenue = q.cargo * q.freight;
    const net = revenue * (1 - q.comm / 100);
    const days = seaDays + q.portDays;
    const tce = (net - bunkerCost - q.portCost - etsCost) / days;
    return { seaDays, consAt, fuel, bunkerCost, co2, etsCost, revenue, net, days, tce };
  }

  function voyage(box) {
    if (!lab.voyage) lab.voyage = { cargo: 55000, freight: 25, dist: 9000, speed: 12.5, cons: 28, portDays: 6, portCons: 4, bunker: 600, portCost: 120000, comm: 3.75, ets: 0.5, eua: 70, eurusd: eurUsd(), opex: 6500 };
    const p = lab.voyage;
    const c = colors();
    const out = el('div', { class: 'results' });
    const etsSel = el('select', { id: 'v-ets' },
      [[0, 'Outside the EU/EEA (0%)'], [0.5, 'Into or out of the EU/EEA (50%)'], [1, 'Within the EU/EEA (100%)']].map(([v, l]) => el('option', { value: v, selected: p.ets === v ? true : null }, l)));
    etsSel.addEventListener('change', () => { p.ets = parseFloat(etsSel.value); draw(); });
    const controls = el('div', { class: 'controls' },
      el('p', { class: 'small-note' }, 'A Supramax carrying grain on a voyage charter. Change the inputs to see what the owner earns per day.'),
      slider('v-freight', 'Freight rate', p.freight, 10, 60, 0.5, (v) => 'USD ' + v.toFixed(1) + '/t', (v) => { p.freight = v; draw(); }),
      slider('v-bunker', 'Bunker price (VLSFO)', p.bunker, 300, 1000, 10, (v) => 'USD ' + v + '/t', (v) => { p.bunker = v; draw(); }),
      slider('v-speed', 'Speed', p.speed, 9, 15, 0.1, (v) => v.toFixed(1) + ' kn', (v) => { p.speed = v; draw(); }, 'Fuel use rises with roughly the cube of speed.'),
      el('div', { class: 'ctl' }, el('label', { for: 'v-ets', class: 'ctl-top' }, 'EU ETS coverage'), etsSel),
      slider('v-eua', 'Carbon price (EUA)', p.eua, 0, 150, 1, (v) => 'EUR ' + v + '/t CO2', (v) => { p.eua = v; draw(); }),
      el('details', null, el('summary', { class: 'small-note', style: 'cursor:pointer' }, 'More assumptions'),
        el('div', { style: 'display:flex;flex-direction:column;gap:10px;margin-top:10px' },
          numberField('v-cargo', 'Cargo (tonnes)', p.cargo, 500, (v) => { p.cargo = v; draw(); }),
          numberField('v-dist', 'Distance, laden + ballast (nautical miles)', p.dist, 100, (v) => { p.dist = v; draw(); }),
          numberField('v-cons', 'Fuel use at 12.5 knots (t/day)', p.cons, 0.5, (v) => { p.cons = v; draw(); }),
          numberField('v-pd', 'Days in port', p.portDays, 0.5, (v) => { p.portDays = v; draw(); }),
          numberField('v-pc', 'Port costs (USD)', p.portCost, 1000, (v) => { p.portCost = v; draw(); }),
          numberField('v-comm', 'Commission (%)', p.comm, 0.25, (v) => { p.comm = v; draw(); }),
          numberField('v-fx', 'EUR/USD', p.eurusd, 0.01, (v) => { p.eurusd = v; draw(); }, 'Prefilled from the latest Norges Bank rates.'),
          numberField('v-opex', 'Daily running costs, OPEX (USD/day)', p.opex, 100, (v) => { p.opex = v; draw(); }))));
    box.append(el('div', { class: 'lab' }, controls, out));

    const kpis = el('div', { class: 'kpis' });
    const explain = el('div', { class: 'explain' });
    const breakdown = el('div', { class: 'break-list' });
    const a = chartCard('Daily earnings vs bunker price', 'TCE in USD per day at different fuel prices, all else unchanged.', 'normal', { legend: legend([[c.c1, 'TCE'], [c.c2, 'Your inputs']]) });
    const b = chartCard('Daily earnings vs speed', 'Faster means fewer days but much more fuel. The best speed balances the two.', 'normal', { legend: legend([[c.c1, 'TCE'], [c.c2, 'Your speed'], [c.c3, 'Best speed']]) });
    out.append(kpis, el('section', { class: 'chart-card' }, el('h3', null, 'Where the freight money goes'), breakdown), explain, el('div', { class: 'mini-grid' }, a.node, b.node),
      termsRow(['tce', 'voyage-charter', 'bunkers', 'eu-ets', 'slow-steaming', 'opex', 'breakeven']),
      el('p', { class: 'disclaimer' }, 'CO2 is estimated at 3.114 t per tonne of fuel. Port fuel and costs are kept fixed. Simplified for learning.'));

    const tceCfg = (xTitle, xFmt, extra) => baseOptions(c, Object.assign({
      mode: 'nearest', crosshair: false,
      x: axis(c, xTitle, null, { type: 'linear', ticks: { color: c.muted, font: { size: 11 }, maxTicksLimit: 7, callback: xFmt } }),
      y: axis(c, 'USD per day', null, { ticks: { color: c.muted, font: { size: 11 }, maxTicksLimit: 6, callback: (v) => compact(v) } }),
      tooltip: { title: () => '', label: (ctx) => ` ${ctx.dataset.label}: ${usd(ctx.parsed.y)} at ${xFmt(ctx.parsed.x)}` },
    }, extra));
    const chA = makeChart(a.canvas, { type: 'scatter', data: { datasets: [
      { label: 'TCE', data: [], showLine: true, borderColor: c.c1, borderWidth: 2, pointRadius: 0, pointHitRadius: 8 },
      { label: 'Your inputs', data: [], pointRadius: 5, pointBackgroundColor: c.c2, pointBorderColor: c.surface, pointBorderWidth: 2 },
    ] }, options: tceCfg('Bunker price, USD per tonne', (v) => compact(v)) });
    const chB = makeChart(b.canvas, { type: 'scatter', data: { datasets: [
      { label: 'TCE', data: [], showLine: true, borderColor: c.c1, borderWidth: 2, pointRadius: 0, pointHitRadius: 8 },
      { label: 'Your speed', data: [], pointRadius: 5, pointBackgroundColor: c.c2, pointBorderColor: c.surface, pointBorderWidth: 2 },
      { label: 'Best speed', data: [], pointRadius: 5, pointStyle: 'rectRot', pointBackgroundColor: c.c3, pointBorderColor: c.surface, pointBorderWidth: 2 },
    ] }, options: tceCfg('Speed, knots', (v) => Number(v).toFixed(1)) });

    function draw() {
      const r = voyageCalc(p);
      const r100 = voyageCalc(p, { bunker: p.bunker + 100 });
      let best = { v: 9, t: -Infinity };
      const speeds = [];
      for (let v = 9; v <= 15.001; v += 0.1) { const t = voyageCalc(p, { speed: v }).tce; speeds.push({ x: Math.round(v * 10) / 10, y: t }); if (t > best.t) best = { v: Math.round(v * 10) / 10, t }; }
      if (chA) {
        const xs = [];
        for (let b2 = 300; b2 <= 1000; b2 += 25) xs.push({ x: b2, y: voyageCalc(p, { bunker: b2 }).tce });
        chA.data.datasets[0].data = xs;
        chA.data.datasets[1].data = [{ x: p.bunker, y: r.tce }];
        chA.update('none');
      }
      if (chB) {
        chB.data.datasets[0].data = speeds;
        chB.data.datasets[1].data = [{ x: p.speed, y: r.tce }];
        chB.data.datasets[2].data = [{ x: best.v, y: best.t }];
        chB.update('none');
      }
      const margin = r.tce - p.opex;
      fill(kpis, 
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'TCE (daily earnings)'), el('div', { class: 'v' }, usd(r.tce)), el('div', { class: 'd' }, 'per day')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Voyage length'), el('div', { class: 'v' }, nf1.format(r.days) + ' days'), el('div', { class: 'd' }, nf1.format(r.seaDays) + ' at sea')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Fuel burned'), el('div', { class: 'v' }, nf0.format(r.fuel) + ' t'), el('div', { class: 'd' }, nf1.format(r.consAt) + ' t/day at sea')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'After OPEX'), el('div', { class: 'v' }, usd(margin)), el('div', { class: 'd' }, 'per day for capital costs')));
      const parts = [
        ['Bunkers', r.bunkerCost, c.c1],
        ['Port costs', p.portCost, c.c2],
        ['EU ETS allowances', r.etsCost, c.c3],
        ['Commission', r.revenue - r.net, c.c4],
        ['Owner’s earnings (TCE × days)', Math.max(0, r.net - r.bunkerCost - p.portCost - r.etsCost), c.cm],
      ];
      fill(breakdown, 
        el('div', { class: 'stack', style: 'grid-column:1/-1;margin-bottom:6px', role: 'img', 'aria-label': 'Breakdown of gross freight' },
          parts.map(([name, v, col]) => el('span', { title: `${name}: ${usd(v)}`, style: `flex:${Math.max(0, v)} 0 0;background:${col}` }))),
        parts.map(([name, v, col]) => [el('span', { class: 'sw', style: 'background:' + col }), el('span', null, name), el('span', { class: 'num' }, usd(v)), el('span', { class: 'num' }, ((v / r.revenue) * 100).toFixed(0) + '%')]),
        el('span'), el('b', null, 'Gross freight'), el('b', { class: 'num' }, usd(r.revenue)), el('span', { class: 'num' }, '100%'));
      const lines = [
        `Each USD 100 per tonne rise in bunker prices cuts earnings on this voyage by about ${usd(r.tce - r100.tce)} per day.`,
        Math.abs(best.v - p.speed) < 0.15
          ? `You are sailing at about the best speed for these inputs (${best.v.toFixed(1)} knots).`
          : `At these prices the most profitable speed is about ${best.v.toFixed(1)} knots, earning ${usd(best.t)} per day. Raise the bunker price and watch the best speed drop: that is slow steaming.`,
        p.ets > 0 ? `EU ETS adds ${usd(r.etsCost)} for this voyage (${nf0.format(r.co2 * p.ets)} t of CO2 at EUR ${p.eua}).` : 'This voyage does not touch the EU/EEA, so no EU ETS cost applies.',
        margin >= 0 ? `After running costs of ${usd(p.opex)} per day, ${usd(margin)} per day is left for interest and loan repayments.` : `The voyage does not cover running costs of ${usd(p.opex)} per day. An owner would rather wait for a better cargo or lay the ship up.`,
      ];
      fill(explain, el('span', { class: 'h' }, 'What this tells you'), lines.map((t) => el('p', null, t)));
    }
    draw();
  }

  // ---------------------------------------------------------------- 4. truck trip cost
  const ROUTES = {
    'bgo-osl': { name: 'Bergen – Oslo', km: 465, tolls: 1200 },
    'bgo-svg': { name: 'Bergen – Stavanger (with ferries)', km: 210, tolls: 3500 },
    'bgo-trd': { name: 'Bergen – Trondheim', km: 680, tolls: 1800 },
    'bgo-agt': { name: 'Bergen – CCB Ågotnes (local)', km: 30, tolls: 250 },
    custom: { name: 'Custom', km: null, tolls: null },
  };

  function truckCalc(p, over) {
    const q = Object.assign({}, p, over || {});
    const hours = q.km / q.speed;
    const breaks = Math.max(0, Math.ceil(hours / 4.5) - 1) * 0.75;
    const diesel = q.km * q.cons * q.diesel;
    const driver = (hours + breaks + q.loadH) * q.wage;
    const vehicle = q.km * q.vehicle;
    const tolls = q.tolls;
    const empty = q.empty ? q.km * q.cons * 0.8 * q.diesel + (hours + breaks) * q.wage + q.km * q.vehicle : 0;
    const total = diesel + driver + vehicle + tolls + empty;
    return { hours, breaks, diesel, driver, vehicle, tolls, empty, total };
  }

  function truck(box) {
    const p = lab.truck;
    const c = colors();
    const out = el('div', { class: 'results' });
    const routeSel = el('select', { id: 't-route' }, Object.entries(ROUTES).map(([id, r]) => el('option', { value: id, selected: p.route === id ? true : null }, r.name)));
    routeSel.addEventListener('change', () => {
      p.route = routeSel.value;
      const r = ROUTES[p.route];
      if (r.km != null) { p.km = r.km; p.tolls = r.tolls; }
      F.render();
    });
    const emptyBox = el('input', { type: 'checkbox', id: 't-empty', checked: p.empty ? true : null });
    emptyBox.addEventListener('change', () => { p.empty = emptyBox.checked; draw(); });
    const controls = el('div', { class: 'controls' },
      el('div', { class: 'ctl' }, el('label', { for: 't-route', class: 'ctl-top' }, 'Route'), routeSel, el('span', { class: 'help' }, 'Distances and tolls are rough estimates. Replace them with your own figures.')),
      numberField('t-km', 'Distance (km)', p.km, 5, (v) => { p.km = v; p.route = 'custom'; draw(); }),
      numberField('t-tolls', 'Tolls and ferries (NOK)', p.tolls, 50, (v) => { p.tolls = v; draw(); }),
      slider('t-diesel', 'Diesel price, excl. VAT', p.diesel, 12, 26, 0.1, (v) => 'NOK ' + v.toFixed(1) + '/l', (v) => { p.diesel = v; draw(); }, 'Businesses deduct VAT, so use the price without it.'),
      slider('t-cons', 'Fuel use', p.cons, 0.22, 0.5, 0.01, (v) => (v * 10).toFixed(1) + ' l/10 km', (v) => { p.cons = v; draw(); }, 'A loaded 50-tonne truck typically uses 3–4 litres per 10 km.'),
      slider('t-speed', 'Average speed', p.speed, 40, 80, 1, (v) => v + ' km/h', (v) => { p.speed = v; draw(); }, 'Mountain passes, ferries and towns pull the average down.'),
      el('div', { class: 'ctl' }, el('label', { class: 'ctl-top', for: 't-empty', style: 'justify-content:flex-start;gap:8px;cursor:pointer' }, emptyBox, 'Truck returns empty')),
      el('details', null, el('summary', { class: 'small-note', style: 'cursor:pointer' }, 'More assumptions'),
        el('div', { style: 'display:flex;flex-direction:column;gap:10px;margin-top:10px' },
          numberField('t-wage', 'Driver cost incl. social costs (NOK/hour)', p.wage, 10, (v) => { p.wage = v; draw(); }),
          numberField('t-veh', 'Vehicle cost: depreciation, tyres, maintenance, insurance (NOK/km)', p.vehicle, 0.1, (v) => { p.vehicle = v; draw(); }),
          numberField('t-load', 'Loading and unloading (hours)', p.loadH, 0.25, (v) => { p.loadH = v; draw(); }),
          numberField('t-pal', 'Pallets on board', p.pallets, 1, (v) => { p.pallets = v; draw(); }))));
    box.append(el('div', { class: 'lab' }, controls, out));

    const kpis = el('div', { class: 'kpis' });
    const rules = el('div', { class: 'chart-card' });
    const breakdown = el('div', { class: 'break-list' });
    const explain = el('div', { class: 'explain' });
    const cc = chartCard('Trip cost vs diesel price', 'Total trip cost in NOK at different diesel prices, all else unchanged.', 'normal', { legend: legend([[c.c1, 'Trip cost'], [c.c2, 'Your diesel price']]) });
    out.append(kpis, rules, el('section', { class: 'chart-card' }, el('h3', null, 'Cost breakdown'), breakdown), explain, cc.node,
      termsRow(['driving-rest', 'fuel-surcharge', 'road-tax', 'autopass', 'backhaul', 'empty-running', 'euro-pallet']),
      el('p', { class: 'disclaimer' }, 'A simplified cost model for learning. Real costs vary with vehicle, contract, season and route.'));

    const chart = makeChart(cc.canvas, { type: 'scatter', data: { datasets: [
      { label: 'Trip cost', data: [], showLine: true, borderColor: c.c1, borderWidth: 2, pointRadius: 0, pointHitRadius: 8 },
      { label: 'Your diesel price', data: [], pointRadius: 5, pointBackgroundColor: c.c2, pointBorderColor: c.surface, pointBorderWidth: 2 },
    ] }, options: baseOptions(c, {
      mode: 'nearest', crosshair: false,
      x: axis(c, 'Diesel price, NOK per litre excl. VAT', null, { type: 'linear', min: 12, max: 26, ticks: { color: c.muted, font: { size: 11 }, stepSize: 2 } }),
      y: axis(c, 'NOK per trip', null, { ticks: { color: c.muted, font: { size: 11 }, maxTicksLimit: 6, callback: (v) => compact(v) } }),
      tooltip: { title: () => '', label: (ctx) => ` ${nok(ctx.parsed.y)} at NOK ${ctx.parsed.x.toFixed(1)}/l` },
    }) });

    function draw() {
      const r = truckCalc(p);
      const up = truckCalc(p, { diesel: p.diesel + 1 });
      if (chart) {
        const pts = [];
        for (let d = 12; d <= 26.001; d += 0.5) pts.push({ x: d, y: truckCalc(p, { diesel: d }).total });
        chart.data.datasets[0].data = pts;
        chart.data.datasets[1].data = [{ x: p.diesel, y: r.total }];
        chart.update('none');
      }
      fill(kpis, 
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Trip cost'), el('div', { class: 'v' }, nok(r.total)), el('div', { class: 'd' }, p.empty ? 'incl. empty return' : 'one way, loaded')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Per km'), el('div', { class: 'v' }, 'NOK ' + nf2.format(r.total / p.km)), el('div', { class: 'd' }, 'loaded km')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Per pallet'), el('div', { class: 'v' }, nok(r.total / Math.max(1, p.pallets))), el('div', { class: 'd' }, p.pallets + ' pallets')),
        el('div', { class: 'kpi' }, el('div', { class: 'l' }, 'Driving time'), el('div', { class: 'v' }, nf1.format(r.hours) + ' h'), el('div', { class: 'd' }, '+ ' + nf0.format(r.breaks * 60) + ' min breaks')));
      let status;
      if (r.hours <= 9) status = ['ok', '✓', `Fits within the 9-hour daily driving limit (${nf1.format(r.hours)} h).`];
      else if (r.hours <= 10) status = ['warn', '!', 'Needs one of the driver’s two allowed 10-hour days this week.'];
      else status = ['warn', '!', `Too long for one driver in one day (${nf1.format(r.hours)} h). Plan an 11-hour daily rest on the way, or use two drivers.`];
      fill(rules, el('h3', null, 'Driving and rest rules'),
        el('div', { class: 'status-line' }, el('span', { class: 'ic ' + status[0], 'aria-hidden': 'true' }, status[1]), el('span', null, status[2])),
        el('p', { class: 'small-note' }, r.breaks > 0 ? `The driver needs ${nf0.format(r.breaks * 60)} minutes of breaks: 45 minutes after every 4.5 hours of driving.` : 'No break is needed on a trip this short (under 4.5 hours of driving).'));
      const parts = [['Diesel', r.diesel, c.c1], ['Driver', r.driver, c.c2], ['Vehicle', r.vehicle, c.c3], ['Tolls & ferries', r.tolls, c.c4]];
      if (p.empty) parts.push(['Empty return', r.empty, c.cm]);
      fill(breakdown, 
        el('div', { class: 'stack', style: 'grid-column:1/-1;margin-bottom:6px', role: 'img', 'aria-label': 'Cost breakdown' },
          parts.map(([name, v, col]) => el('span', { title: `${name}: ${nok(v)}`, style: `flex:${Math.max(0, v)} 0 0;background:${col}` }))),
        parts.map(([name, v, col]) => [el('span', { class: 'sw', style: 'background:' + col }), el('span', null, name), el('span', { class: 'num' }, nok(v)), el('span', { class: 'num' }, ((v / r.total) * 100).toFixed(0) + '%')]));
      const lines = [
        `Diesel up NOK 1 per litre adds ${nok(up.total - r.total)} to this trip (${pct(((up.total - r.total) / r.total) * 100)}). A diesel clause in the contract decides whether you or the customer pays it.`,
        `Diesel is ${((r.diesel / r.total) * 100).toFixed(0)}% of the cost here and the driver ${((r.driver / r.total) * 100).toFixed(0)}%. On short trips, time and tolls weigh more; on long trips, fuel dominates.`,
        p.empty ? `The empty return costs ${nok(r.empty)}. Finding a backhaul would cut the cost per loaded km by about ${((r.empty / r.total) * 100).toFixed(0)}%.` : 'Tick “Truck returns empty” to see what a missing backhaul costs.',
      ];
      fill(explain, el('span', { class: 'h' }, 'What this tells you'), lines.map((t) => el('p', null, t)));
    }
    draw();
  }

  // ---------------------------------------------------------------- 5. cause & effect
  function effects(box) {
    const S = F.data.scenarios;
    if (!S) { box.append(el('p', { class: 'empty' }, 'Scenario data is missing.')); return; }
    const ev = S.events.find((e) => e.id === lab.effect) || S.events[0];
    const DIR = { up: ['↑', 'Up'], down: ['↓', 'Down'], mixed: ['↕', 'Mixed'] };
    const segName = (id) => (F.segments.get(id) || { name: id }).name;
    const col = (level, name, scope) => {
      const list = ev.effects.filter((e) => e.level === level);
      return el('section', { class: 'level-col' },
        el('h3', null, name, el('span', { class: 'scope' }, scope)),
        list.length ? list.map((e) => el('div', { class: 'effect seg-' + e.seg },
          el('div', { class: 'top' }, el('span', { class: 'seg-dot' }), segName(e.seg),
            el('span', { style: 'margin-left:auto', class: 'arrow', title: DIR[e.dir][1] }, DIR[e.dir][0] + ' ' + DIR[e.dir][1])),
          el('div', { class: 'what' }, e.label),
          el('p', null, e.text),
          e.terms && e.terms.length ? el('div', { class: 'learn-row' }, e.terms.map((id) => F.termChip(id))) : null))
          : el('p', { class: 'level-empty' }, 'Little direct effect at this level.'));
    };
    box.append(
      el('p', { class: 'small-note', style: 'margin-bottom:10px' }, 'Pick an event to see how its effects typically spread, from world markets down to Norway and Western Norway.'),
      el('div', { class: 'events chips', role: 'group', 'aria-label': 'Event' }, S.events.map((e) => el('button', {
        class: 'chip', type: 'button', 'aria-pressed': String(e.id === ev.id), onclick: () => { lab.effect = e.id; F.render(); },
      }, e.name))),
      el('div', { class: 'explain', style: 'margin-bottom:18px' }, el('span', { class: 'h' }, 'The event'), el('p', null, el('b', null, ev.name + '. '), ev.summary)),
      el('div', { class: 'levels' },
        col('local', 'Western Norway', 'Local'),
        col('national', 'Norway', 'National'),
        col('international', 'World', 'International')),
      el('p', { class: 'disclaimer', style: 'margin-top:14px' }, 'Typical directions based on how these markets usually react. Real outcomes depend on timing, contracts and what else is happening.'));
  }
})();
