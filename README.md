# Schema Questionnaires

Combined **YSQ-S3R** (Young Schema Questionnaire - Short Form, 3rd Revision) and **SMI v1.1** (Schema Mode Inventory) as a single-page web tool for schema therapy self-assessment.

**Live:** https://schema-questionnaire.surge.sh

## What it does

214 questions (90 YSQ + 124 SMI) with client-side scoring and clinical interpretation. All text in Russian.

**Questionnaire features:**
- Tab-based layout with per-tab completion tracking
- Click any question text to see what a score of 6 means for that item
- Keyboard shortcut: hover over a question and press 1-6
- Auto-save to localStorage, auto-scroll to next unanswered question
- Share results via URL (answers encoded in the hash fragment)

**Results:**
- YSQ: 18 schemas grouped by 5 domains, sorted by score, with percentage and mean
- SMI: 14 modes sorted by clinical significance and by category
- Reverse-scored modes (Happy Child, Healthy Adult) handled correctly in bars and sorting
- Click any schema/mode row to expand: clinical description, level meaning, per-item breakdown
- Click an item in the breakdown to jump to that question and revise your answer
- Floating "back to results" button to return after revising

## How to build and deploy

```bash
python src/build_form.py    # generates dist/index.html
cd dist && npx surge .      # deploys to schema-questionnaire.surge.sh
```

## Project structure

```
src/
  build_form.py              # generates dist/index.html
  scoring/                   # JS scoring modules (source of truth)
    ysq_scoring.js
    smi_scoring.js
  data/                      # question texts, hints, clinical descriptions
    questions.json
    interpretations.json
tests/                       # browser-based scoring tests
dist/                        # generated deployment output
reference/                   # Python reference scripts, Excel source files
```

## Scoring methodology

**YSQ-S3R:** Each of 18 schemas has 5 questions scored 1-6. Percentage formula: `(sum - 5) / 25 * 100`. Five levels from "low" to "high". Schemas aggregate into 5 domains.

**SMI v1.1:** 14 modes with 4-10 items each. 15 items are shared across 2 modes (per the SMI manual). Normative cutoffs produce 6 levels. CC (Happy Child) and HA (Healthy Adult) are reverse-scored: high raw score = healthy.

Scoring verified against Excel reference formulas.

## References

- Young, J.E., Klosko, J.S., & Weishaar, M.E. (2003). Schema Therapy: A Practitioner's Guide
- Lobbestael, J., van Vreeswijk, M., & Arntz, A. (2010). An empirical test of schema mode conceptualizations in personality disorders
- Russian adaptation: [schema-therapy.ru](https://schema-therapy.ru)
