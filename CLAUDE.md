# Schema Questionnaire Tool

Personal project: combined YSQ-S3R (Young Schema Questionnaire) + SMI v1.1 (Schema Mode Inventory) as a single static HTML page deployed to Surge.

## Commands

```bash
# Build the deployed page
python src/build_form.py

# Deploy to Surge
cd dist && npx surge .
# Domain is auto-detected from dist/CNAME -> schema-questionnaire.surge.sh

# Run YSQ scoring tests (open in browser)
# tests/test_ysq_scoring.html

# Run SMI scoring tests (open in browser)
# tests/test_smi_scoring.html

# Verify SMI scores against Excel reference
node tests/verify_smi.js
```

## Architecture

Static HTML site, no backend. Build-time generation, client-side scoring.

```
src/data/questions.json + src/data/interpretations.json
        |  (src/build_form.py)
dist/index.html  <-  loads  <-  dist/ysq_scoring.js
                                dist/smi_scoring.js
```

`src/build_form.py` is the single source of truth for the deployed page. Do not hand-edit `dist/index.html` - regenerate it.

## Project Structure

```
src/
  build_form.py              # generates dist/index.html from data files
  scoring/
    ysq_scoring.js            # YSQ scoring: 18 schemas, 5 domains
    smi_scoring.js            # SMI scoring: 14 modes, reverse scoring, shared items
  data/
    questions.json            # 214 question texts + per-item hints
    interpretations.json      # clinical descriptions, level meanings, disclaimer
tests/
  test_ysq_scoring.html       # YSQ scoring tests (open in browser)
  test_smi_scoring.html       # SMI scoring tests (open in browser)
  verify_smi.js               # Node.js verification against Excel values
reference/
  results.json                # real test answers for verification
  score_ysq.py                # Python YSQ reference (development artifact)
  score_smi.py                # Python SMI reference (development artifact)
  excel/                      # source Excel files
dist/                         # deployment output (generated, do not hand-edit)
```

## Scoring Details

### YSQ-S3R
- 18 schemas, each with 5 questions (cycling: q1, q19, q37, q55, q73 for first schema)
- Formula: `pct = (total - 5) / 25 * 100` (maps sum 5-30 to 0-100%)
- Levels: <=20% low, <=40% reduced, <=60% moderate, <=80% elevated, >80% high
- 5 domains aggregate schema means

### SMI v1.1
- 14 modes with 4-10 items each
- 15 items are shared across 2 modes (by design per SMI manual)
- Normative cutoffs per mode (5-point norms array)
- Reverse scoring for CC (Happy Child) and HA (Healthy Adult): high raw score = low clinical concern
- `clinicalScore(mean, reverse)` normalizes for sorting: `reverse ? 7 - mean : mean`
- 6 levels: low through very high

## Key Conventions

- All user-facing text is in Russian
- Schema codes are Cyrillic - must match between `src/scoring/ysq_scoring.js` and `src/data/interpretations.json`
- Mode codes are Latin - must match between `src/scoring/smi_scoring.js` and `src/data/interpretations.json`
- Build script uses Python f-strings with `{{`/`}}` for JS braces and `\\'` for JS single quotes inside onclick handlers
- Tests are HTML files that run in the browser (not Node.js test frameworks)
- URL sharing encodes 214 answers as a base64 hash fragment

## Deployment

Surge static hosting at `schema-questionnaire.surge.sh`. The `dist/CNAME` file stores the domain.

## Gotchas

- Python f-string escaping: JS `toggleEl('id')` in onclick requires `\\'` in the f-string to produce `\'` in output. Using just `\'` produces bare `'` which breaks the JS parser
- Scoring JS files exist in both `src/scoring/` (source of truth) and `dist/` (copied by build). Edit the source files, then rebuild
- Tests load scoring JS via relative paths from `tests/` to `src/scoring/`
