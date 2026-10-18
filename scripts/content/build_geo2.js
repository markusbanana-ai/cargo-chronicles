// Pre-renders map outlines as SVG path strings in projected units, so the browser only
// has to project routes and roads with the same projection settings.
const fs = require('fs');
const d3 = require('d3-geo');
const out = process.argv[2];
const world = JSON.parse(fs.readFileSync('out/world-land.json'));
const nordic = JSON.parse(fs.readFileSync('out/nordic.json'));

// ---- world (shipping): Natural Earth, centred on 12°E, 1 unit ≈ 1/1000 of the radius
const wp = d3.geoNaturalEarth1().rotate([-12, 0]).scale(1000).translate([0, 0]).precision(0.5);
const path = d3.geoPath(wp).digits(1);
const W = {
  proj: { type: 'naturalEarth1', rotate: [-12, 0], scale: 1000 },
  sphere: path({ type: 'Sphere' }),
  graticule: path(d3.geoGraticule().step([30, 30])()),
  land: world.features.map((f) => path(f)).join(''),
};
const b = path.bounds({ type: 'Sphere' });
W.bounds = b.map((p) => p.map((v) => Math.round(v)));
fs.writeFileSync(out + '/world.json', JSON.stringify(W));

// ---- Nordic (roads): transverse Mercator around 15°E, units = km; vertices projected one by one
const np = d3.geoTransverseMercator().rotate([-15, -64]).scale(6371).translate([0, 0]);
const r1 = (v) => Math.round(v * 10) / 10;
function ringPath(ring) {
  let s = '';
  ring.forEach((c, i) => { const [x, y] = np(c); s += (i ? 'L' : 'M') + r1(x) + ',' + r1(y); });
  return s + 'Z';
}
function geomPath(g) {
  const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
  return polys.map((poly) => poly.map(ringPath).join('')).join('');
}
const N = {
  proj: { type: 'transverseMercator', rotate: [-15, -64], scale: 6371 },
  countries: nordic.features.map((f) => ({ id: f.properties.id, d: geomPath(f.geometry) })),
};
fs.writeFileSync(out + '/nordic.json', JSON.stringify(N));
console.log('world.json', fs.statSync(out + '/world.json').size, 'bounds', W.bounds, ' nordic.json', fs.statSync(out + '/nordic.json').size);
