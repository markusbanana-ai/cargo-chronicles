const fs = require('fs');
const topojson = require('topojson-client');
const simp = require('topojson-simplify');
const out = process.argv[2];
const W_WORLD = +process.argv[3], A_WORLD = +process.argv[4], W_NORD = +process.argv[5], W_OTHER = +process.argv[6];

function prep(file, filterIds, minWeight, minArea) {
  let t = JSON.parse(fs.readFileSync('node_modules/world-atlas/' + file, 'utf8'));
  if (filterIds) t.objects.countries.geometries = t.objects.countries.geometries.filter((g) => filterIds.has(String(g.id)));
  t = simp.presimplify(t, simp.sphericalTriangleArea);
  t = simp.simplify(t, minWeight);
  t = simp.filter(t, simp.filterWeight(t, minArea, simp.sphericalRingArea));
  return t;
}
const round = (k) => (c) => Array.isArray(c[0]) ? c.map(round(k)) : [Math.round(c[0] * k) / k, Math.round(c[1] * k) / k];
function dedupe(ring) { const o = []; for (const p of ring) { const q = o[o.length - 1]; if (!q || q[0] !== p[0] || q[1] !== p[1]) o.push(p); } return o; }
function cleanGeom(g, k) {
  const r = round(k);
  if (g.type === 'Polygon') return { type: 'Polygon', coordinates: g.coordinates.map((ring) => dedupe(r(ring))).filter((x) => x.length >= 4) };
  if (g.type === 'MultiPolygon') return { type: 'MultiPolygon', coordinates: g.coordinates.map((poly) => poly.map((ring) => dedupe(r(ring))).filter((x) => x.length >= 4)).filter((p) => p.length) };
  return g;
}
// Sutherland–Hodgman clip of a ring to a lon/lat box
function clipRing(ring, [x0, y0, x1, y1]) {
  const edges = [[(p) => p[0] >= x0, (a, b) => [x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0])]],
                 [(p) => p[0] <= x1, (a, b) => [x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0])]],
                 [(p) => p[1] >= y0, (a, b) => [a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0]],
                 [(p) => p[1] <= y1, (a, b) => [a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1]]];
  let pts = ring.slice(0, -1);
  for (const [inside, cut] of edges) {
    const res = [];
    for (let i = 0; i < pts.length; i++) {
      const a = pts[i], b = pts[(i + 1) % pts.length];
      const ia = inside(a), ib = inside(b);
      if (ia) res.push(a);
      if (ia !== ib) res.push(cut(a, b));
    }
    pts = res;
    if (!pts.length) return null;
  }
  pts.push(pts[0]);
  return pts.length >= 4 ? pts : null;
}
function clipGeom(g, box) {
  const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
  const outP = [];
  for (const poly of polys) {
    const outer = clipRing(poly[0], box);
    if (!outer) continue;
    outP.push([outer, ...poly.slice(1).map((r) => clipRing(r, box)).filter(Boolean)]);
  }
  return outP.length ? { type: 'MultiPolygon', coordinates: outP } : null;
}

// 1. world land (shipping map)
const wt = prep('land-50m.json', null, W_WORLD, A_WORLD);
const land = topojson.feature(wt, wt.objects.land);
const world = { type: 'FeatureCollection', features: (land.features || [land]).map((f) => ({ type: 'Feature', properties: {}, geometry: cleanGeom(f.geometry, 100) })) };
fs.writeFileSync(out + '/world-land.json', JSON.stringify(world));

// 2. Nordic map: NO/SE/FI/DK at 10m, neighbours at 50m clipped to the view
const NORDIC = { '578': 'NO', '752': 'SE', '246': 'FI', '208': 'DK' };
const nt = prep('countries-10m.json', new Set(Object.keys(NORDIC)), W_NORD, 3e-8);
const nf = topojson.feature(nt, nt.objects.countries).features.map((f) => ({ type: 'Feature', properties: { id: NORDIC[String(f.id)] }, geometry: cleanGeom(f.geometry, 1000) }));
const OTH = new Set(['643', '276', '826', '233', '428', '440', '616', '372', '528', '056', '112', '804', '250', '352', '234']);
const ot = prep('countries-50m.json', OTH, W_OTHER, 3e-8);
const box = [-12, 50.5, 42, 72.5];
const of = topojson.feature(ot, ot.objects.countries).features.map((f) => {
  const unwrap = (c) => Array.isArray(c[0]) ? c.map(unwrap) : [c[0] < -30 ? c[0] + 360 : c[0], c[1]];
  const g0 = cleanGeom(f.geometry, 100);
  const g = clipGeom({ type: g0.type, coordinates: unwrap(g0.coordinates) }, box);
  return g ? { type: 'Feature', properties: { id: 'X' + f.id }, geometry: g } : null;
}).filter(Boolean);
fs.writeFileSync(out + '/nordic.json', JSON.stringify({ type: 'FeatureCollection', features: [...of, ...nf] }));
const pts = (fc) => JSON.stringify(fc).split('],[').length;
console.log('world', fs.statSync(out + '/world-land.json').size, 'nordic', fs.statSync(out + '/nordic.json').size, 'pts', pts(world), pts({ features: nf }));
