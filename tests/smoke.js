// Smoke test: render every frame of every example in Node, fail on NaN/undefined, report speed.
// usage: node tests/smoke.js
const fs = require('fs'), path = require('path');
const F = require('../src/figures.js');
const dir = path.join(__dirname, '..', 'examples');
let bad = 0;
for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.json'))) {
  const spec = JSON.parse(fs.readFileSync(path.join(dir, f)));
  const d = spec.duration || 10, st = spec.start || 0, n = Math.round(d * 30);
  const t0 = process.hrtime.bigint(); let chars = 0;
  for (let i = 0; i < n; i++) {
    const s = F.svg(spec, st + i / 30); chars += s.length;
    if (/NaN|undefined/.test(s)) { console.error(`FAIL ${f} at t=${(i / 30).toFixed(2)}: ${s.match(/.{40}(NaN|undefined).{20}/)[0]}`); bad++; break; }
  }
  const ms = Number(process.hrtime.bigint() - t0) / 1e6;
  console.log(`${f.padEnd(14)} ${n} frames  ${(ms / n).toFixed(3)} ms/frame  ~${Math.round(chars / n / 1000)} KB svg`);
}
if (bad) process.exit(1);
console.log('ok');
