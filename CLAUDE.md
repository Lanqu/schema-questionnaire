# Schema Questionnaire Tool

Personal project: combined YSQ-S3R (Young Schema Questionnaire) + SMI v1.1 (Schema Mode Inventory) as a single static HTML page deployed to Surge.

## Commands

```bash
# Build the deployed page
python build_form.py

# Deploy to Surge
cd dist && npx surge .
# Domain is auto-detected from dist/CNAME → schema-questionnaire.surge.sh

# Run YSQ scoring tests (open in browser)
# test_ysq_scoring.html

# Run SMI scoring tests (open in browser)
# test_smi_scoring.html

# Verify SMI scores against Excel reference
node verify_smi.js
```

## Architecture

Static HTML site, no backend. Build-time generation, client-side scoring.

```
questions.json + interpretations.json
        ↓  (build_form.py)
dist/index.html  ←  loads  ←  dist/ysq_scoring.js
                              dist/smi_scoring.js
```

`build_form.py` is the single source of truth for the deployed page. Do not hand-edit `dist/index.html` - regenerate it.

## File Responsibilities

| File | Purpose |
|------|---------|
| `build_form.py` | Generates `dist/index.html` from data files. Embeds questions, interpretations, CSS, and all JS |
| `questions.json` | Question texts: `ysq` (90 items) and `smi` (124 items) |
| `interpretations.json` | Clinical descriptions for schemas, modes, domains, categories, and level meanings (Russian) |
| `ysq_scoring.js` | YSQ scoring module: 18 schemas, 5 domains, percentage formula, level thresholds |
| `smi_scoring.js` | SMI scoring module: 14 modes, normative cutoffs, reverse scoring for CC/HA, shared items |
| `dist/` | Deployment folder. Contains generated `index.html` + copied scoring JS + `CNAME` |
| `score_ysq.py` | Python YSQ reference implementation with hardcoded test answers |
| `score_smi.py` | Python SMI reference implementation with hardcoded test answers |
| `results.json` | Real test answers for both questionnaires (verification data) |
| `questionnaire.html` | Legacy basic form (superseded by dist/index.html, kept for reference) |

## Scoring Details

### YSQ-S3R
- 18 schemas, each with 5 questions (cycling: q1, q19, q37, q55, q73 for first schema)
- Formula: `pct = (total - 5) / 25 * 100` (maps sum 5-30 to 0-100%)
- Levels: <=20% низкий, <=40% пониженный, <=60% умеренный, <=80% повышенный, >80% высокий
- 5 domains aggregate schema means

### SMI v1.1
- 14 modes with 4-10 items each
- 15 items are shared across 2 modes (by design per SMI manual)
- Normative cutoffs per mode (5-point norms array)
- Reverse scoring for CC (Happy Child) and HA (Healthy Adult): high raw score = low clinical concern
- `clinicalScore(mean, reverse)` normalizes for sorting: `reverse ? 7 - mean : mean`
- 6 levels: низкий through оч. высокий

## Key Conventions

- All user-facing text is in Russian
- Schema codes are Cyrillic (ЭД, ПН, НН, etc.) - must match between `ysq_scoring.js` and `interpretations.json`
- Mode codes are Latin (VC, AC, EC, etc.) - must match between `smi_scoring.js` and `interpretations.json`
- Build script uses Python f-strings with `{{`/`}}` for JS braces and `\\'` for JS single quotes inside onclick handlers
- Tests are HTML files that run in the browser (not Node.js test frameworks)
- URL sharing encodes 214 answers as a base64 hash fragment

## Deployment

Surge static hosting at `schema-questionnaire.surge.sh`. The `dist/CNAME` file stores the domain.

## Gotchas

- Python f-string escaping: JS `toggleDetail('id')` in onclick requires `\\'` in the f-string to produce `\'` in output. Using just `\'` produces bare `'` which breaks the JS parser
- Scoring JS files exist in both root (source of truth) and `dist/` (copied by build). Edit the root files, then rebuild
- `test_*.html` files load scoring JS from the root directory via relative `src="ysq_scoring.js"`, not from `dist/`
- Excel files (`.xls`/`.xlsx`) are reference data only - no descriptions were found in them, all interpretation text comes from schema therapy literature
