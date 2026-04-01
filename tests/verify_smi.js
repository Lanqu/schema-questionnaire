const fs = require('fs');
const vm = require('vm');
const path = require('path');
const script = fs.readFileSync(path.join(__dirname, '..', 'src', 'scoring', 'smi_scoring.js'), 'utf8');
vm.runInThisContext(script);

// Verify item counts match Excel
const expected = {VC:10, AC:10, EC:10, IC:9, UC:6, CC:10, CS:7, DP:9, DS:4, SA:10, BA:9, PP:10, DPa:10, HA:10};
for (const mode of Object.keys(expected)) {
  const actual = SMI_MODES[mode].items.length;
  const exp = expected[mode];
  const mark = actual === exp ? 'OK' : 'MISMATCH';
  console.log(`${mode}: ${actual} items (expected ${exp}) ${mark}`);
}

// Calculate scores with real data
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'reference', 'results.json'), 'utf8'));
const answers = {};
for (const k in data.smi) answers[parseInt(k)] = data.smi[k];
const results = scoreAllModes(answers);

console.log('\nScores vs Excel:');
const exScores = {VC:2.5, AC:3.1, EC:1.8, IC:2.556, UC:2.667, CC:3.5, CS:2.714, DP:2.667, DS:3.25, SA:2.8, BA:2.889, PP:2.0, DPa:4.0, HA:4.8};
for (const m of ['VC','AC','EC','IC','UC','CC','CS','DP','DS','SA','BA','PP','DPa','HA']) {
  const r = results[m];
  const ex = exScores[m];
  const match = Math.abs(r.mean - ex) < 0.01 ? 'OK' : 'DIFF';
  console.log(`${m.padEnd(4)}: ${r.mean.toFixed(3)} (excel: ${ex}) ${match}  ${r.level}`);
}
