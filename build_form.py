import json
import html as html_mod
import shutil

with open("F:/personal/psyco/questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("F:/personal/psyco/interpretations.json", "r", encoding="utf-8") as f:
    interpretations = json.load(f)

ysq = data["ysq"]
smi = data["smi"]


def render_questions(questions, prefix):
    parts = []
    for q in questions:
        num = q["num"]
        text = html_mod.escape(q["text"])
        hint = html_mod.escape(q.get("hint", ""))
        opts = ""
        for v in range(1, 7):
            opts += (
                f'<label><input type="radio" name="{prefix}_{num}" value="{v}" '
                f'onchange="markAnswered(this)"><span>{v}</span></label>'
            )
        hint_html = (
            f'<div class="q-hint" id="{prefix}-hint-{num}">{hint}</div>' if hint else ""
        )
        parts.append(
            f'<div class="q" id="{prefix}-q{num}">'
            f'<span class="q-num">{num}.</span>'
            f'<span class="q-text" onclick="toggleHint(\'{prefix}-hint-{num}\')">{text}</span>'
            f"{hint_html}"
            f'<span class="q-opts">{opts}</span>'
            f"</div>"
        )
    return "\n".join(parts)


ysq_html = render_questions(ysq, "ysq")
smi_html = render_questions(smi, "smi")
total = len(ysq) + len(smi)

# Build question text JS constants
ysq_questions_js = json.dumps({q["num"]: q["text"] for q in ysq}, ensure_ascii=False)
smi_questions_js = json.dumps({q["num"]: q["text"] for q in smi}, ensure_ascii=False)
interpretations_js = json.dumps(interpretations, ensure_ascii=False)

page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Schema Questionnaires</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; line-height: 1.5; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
h1 {{ text-align: center; margin: 20px 0; color: #1a1a2e; }}
h2 {{ margin: 30px 0 10px; color: #16213e; border-bottom: 2px solid #0f3460; padding-bottom: 8px; }}
.instructions {{ background: #e8f0fe; border-left: 4px solid #0f3460; padding: 15px; margin: 15px 0 25px; border-radius: 0 8px 8px 0; font-size: 14px; }}
.scale-legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 20px; }}
.scale-legend span {{ background: #fff; padding: 4px 10px; border-radius: 4px; font-size: 13px; border: 1px solid #ddd; }}
.q {{ background: #fff; padding: 14px 18px; margin: 6px 0; border-radius: 8px; display: flex; align-items: center; gap: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); transition: background 0.2s; flex-wrap: wrap; }}
.q:hover {{ background: #f8f9ff; }}
.q.answered {{ border-left: 3px solid #4caf50; }}
.q-num {{ font-weight: 700; color: #0f3460; min-width: 30px; font-size: 15px; }}
.q-text {{ flex: 1; font-size: 15px; cursor: pointer; }}
.q-text:hover {{ color: #0f3460; }}
.q-hint {{ display: none; width: 100%; font-size: 12px; color: #888; font-style: italic; padding: 2px 0 0 30px; }}
.q-hint.open {{ display: block; }}
.q-opts {{ display: flex; gap: 4px; flex-shrink: 0; }}
.q-opts label {{ display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border: 2px solid #ddd; border-radius: 50%; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.15s; user-select: none; }}
.q-opts label:hover {{ border-color: #0f3460; background: #e8f0fe; }}
.q-opts input {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}}
.q-opts label:focus-within {{
  outline: 2px solid #0f3460;
  outline-offset: 2px;
}}
.q-opts label:has(input:checked) {{ border-color: #0f3460; background: #0f3460; color: #fff; }}
.progress {{ position: sticky; top: 0; z-index: 100; background: #fff; padding: 8px 12px; border-bottom: 1px solid #ddd; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.progress-bar {{ flex: 1; min-width: 60px; height: 8px; background: #e0e0e0; border-radius: 4px; }}
.progress-fill {{ height: 100%; background: linear-gradient(90deg, #0f3460, #4caf50); border-radius: 4px; transition: width 0.3s; }}
.btn {{ display: block; margin: 30px auto; padding: 12px 24px; background: #0f3460; color: #fff; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; max-width: 100%; }}
.btn:hover {{ background: #16213e; }}
#results {{ display: none; background: #fff; padding: 20px; border-radius: 8px; margin: 20px 0; white-space: pre-wrap; font-family: monospace; font-size: 13px; }}
#ysq-results {{ display: none; margin: 20px 0; }}
#smi-results {{ display: none; margin: 20px 0; }}
.level-very-high {{ background: #ffcdd2; color: #b71c1c; }}
.cat-header {{ font-size: 13px; font-weight: 700; color: #0f3460; padding: 12px 0 4px; border-bottom: 2px solid #0f3460; margin-top: 10px; }}
.reverse-tag {{ font-size: 10px; color: #888; margin-left: 4px; }}
@media (max-width: 600px) {{
  .q {{ flex-wrap: wrap; padding: 10px 12px; gap: 6px; }}
  .q-text {{ min-width: 100%; font-size: 14px; }}
  .q-opts label {{ width: 32px; height: 32px; font-size: 13px; }}
  .schema-row {{ flex-wrap: wrap; gap: 4px; }}
  .schema-name {{ min-width: calc(100% - 55px); font-size: 12px; }}
  .schema-bar-wrap {{ flex: 1; }}
  .progress {{ padding: 6px 8px; gap: 6px; }}
  .container {{ padding: 10px; }}
  h1 {{ font-size: 20px; }}
  .scale-legend {{ font-size: 11px; }}
  .scale-legend span {{ padding: 3px 6px; }}
  .domain-card {{ flex-wrap: wrap; gap: 4px; }}
}}
.results-section {{ background: #fff; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }}
.results-section h3 {{ margin: 0 0 15px; color: #16213e; font-size: 16px; }}
.schema-row {{ display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; cursor: pointer; }}
.schema-row:last-child {{ border-bottom: none; }}
.schema-row:hover {{ background: #f8f9ff; }}
.schema-code {{ font-weight: 700; min-width: 45px; color: #0f3460; font-size: 13px; }}
.schema-name {{ flex: 1; font-size: 13px; }}
.schema-bar-wrap {{ width: 120px; height: 10px; background: #e0e0e0; border-radius: 5px; overflow: hidden; }}
.schema-bar {{ height: 100%; border-radius: 5px; transition: width 0.5s; }}
.schema-mean {{ min-width: 35px; text-align: right; font-weight: 600; font-size: 13px; }}
.schema-level {{ min-width: 100px; font-size: 12px; padding: 2px 8px; border-radius: 10px; text-align: center; }}
.level-low {{ background: #e8f5e9; color: #2e7d32; }}
.level-reduced {{ background: #f1f8e9; color: #558b2f; }}
.level-medium {{ background: #fff8e1; color: #f57f17; }}
.level-elevated {{ background: #fff3e0; color: #e65100; }}
.level-high {{ background: #fbe9e7; color: #bf360c; }}
.domain-card {{ background: #f8f9ff; border-left: 4px solid #0f3460; padding: 12px 16px; margin: 8px 0; border-radius: 0 8px 8px 0; display: flex; justify-content: space-between; align-items: center; }}
.domain-name {{ font-weight: 600; font-size: 14px; }}
.domain-mean {{ font-size: 20px; font-weight: 700; color: #0f3460; }}
.tab-bar {{ display: flex; gap: 0; margin: 20px 0 0; }}
.tab {{ padding: 12px 24px; background: #ddd; border: none; cursor: pointer; font-size: 15px; font-weight: 600; border-radius: 8px 8px 0 0; }}
.tab.active {{ background: #0f3460; color: #fff; }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
.unanswered-warning {{ color: #d32f2f; font-weight: 600; margin: 10px 0; display: none; }}
.schema-detail {{ display: none; padding: 8px 16px 12px 60px; font-size: 13px; color: #555; border-bottom: 1px solid #f0f0f0; }}
.schema-detail.open {{ display: block; }}
.disclaimer {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px 16px; margin: 15px 0; border-radius: 0 8px 8px 0; font-size: 13px; color: #e65100; }}
.summary-box {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px 16px; margin: 10px 0; border-radius: 0 8px 8px 0; font-size: 14px; }}
.item-breakdown {{ margin: 8px 0 0; padding: 0; list-style: none; font-size: 12px; }}
.item-breakdown li {{ padding: 2px 0; color: #777; }}
.item-breakdown .high-item {{ color: #d32f2f; font-weight: 600; }}
</style>
</head>
<body>

<div class="progress" id="progressBar">
  <button id="shareBtn" onclick="shareUrl()" style="padding:4px 10px;background:#0f3460;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600;white-space:nowrap">Share URL</button>
  <span id="progressText">0 / {total}</span>
  <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:0%"></div></div>
  <span id="progressPct">0%</span>
</div>

<div class="container">
<h1>Schema Questionnaires</h1>

<div class="tab-bar">
  <button class="tab active" id="tab-btn-ysq" onclick="switchTab('ysq', event)">YSQ-S3R (0/90)</button>
  <button class="tab" id="tab-btn-smi" onclick="switchTab('smi', event)">SMI v1.1 (0/124)</button>
</div>

<div class="tab-content active" id="tab-ysq">
<h2>Young Schema Questionnaire (YSQ-S3R)</h2>
<div class="instructions">
\u041d\u0438\u0436\u0435 \u043f\u0435\u0440\u0435\u0447\u0438\u0441\u043b\u0435\u043d\u044b \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f, \u0441 \u043f\u043e\u043c\u043e\u0449\u044c\u044e \u043a\u043e\u0442\u043e\u0440\u044b\u0445 \u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u043e\u043f\u0438\u0441\u0430\u0442\u044c \u0441\u0435\u0431\u044f. \u041f\u0440\u043e\u0447\u0438\u0442\u0430\u0439\u0442\u0435 \u043a\u0430\u0436\u0434\u043e\u0435 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u0438 \u0440\u0435\u0448\u0438\u0442\u0435, \u043d\u0430\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0442\u043e\u0447\u043d\u043e \u043e\u043d\u043e \u0412\u0430\u0441 \u0445\u0430\u0440\u0430\u043a\u0442\u0435\u0440\u0438\u0437\u0443\u0435\u0442. \u041e\u0441\u043d\u043e\u0432\u044b\u0432\u0430\u0439\u0442\u0435 \u0441\u0432\u043e\u0439 \u043e\u0442\u0432\u0435\u0442 \u043d\u0430 \u0442\u043e\u043c, \u043a\u0430\u043a \u0412\u044b <b>\u0427\u0423\u0412\u0421\u0422\u0412\u0423\u0415\u0422\u0415</b>, \u0430 \u043d\u0435 \u043d\u0430 \u0442\u043e\u043c, \u0447\u0442\u043e \u0412\u044b \u0441\u0447\u0438\u0442\u0430\u0435\u0442\u0435 \u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u043c.
</div>
<div class="scale-legend">
  <span>1 = \u0410\u0431\u0441\u043e\u043b\u044e\u0442\u043d\u043e \u043d\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</span>
  <span>2 = \u041f\u043e \u0431\u043e\u043b\u044c\u0448\u0435\u0439 \u0447\u0430\u0441\u0442\u0438 \u043d\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</span>
  <span>3 = \u0421\u043a\u043e\u0440\u0435\u0435 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442, \u0447\u0435\u043c \u043d\u0435\u0442</span>
  <span>4 = \u0412 \u043e\u0431\u0449\u0435\u043c, \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</span>
  <span>5 = \u041f\u043e \u0431\u043e\u043b\u044c\u0448\u0435\u0439 \u0447\u0430\u0441\u0442\u0438 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</span>
  <span>6 = \u041f\u043e\u043b\u043d\u043e\u0441\u0442\u044c\u044e \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u0435\u0442</span>
</div>
{ysq_html}
<p class="unanswered-warning" id="ysq-warning"></p>
<button class="btn" onclick="showYsqResults()">Show YSQ-S3R Results</button>
<div id="ysq-results">
  <h2>YSQ-S3R Results</h2>
  <div id="ysq-disclaimer"></div>
  <div id="ysq-summary"></div>
  <div class="results-section">
    <h3>Домены</h3>
    <div id="ysq-domains"></div>
  </div>
  <div class="results-section">
    <h3>Схемы (по убыванию)</h3>
    <div id="ysq-schemas"></div>
  </div>
</div>
</div>

<div class="tab-content" id="tab-smi">
<h2>Schema Mode Inventory (SMI v1.1)</h2>
<div class="instructions">
\u041d\u0438\u0436\u0435 \u043f\u0435\u0440\u0435\u0447\u0438\u0441\u043b\u0435\u043d\u044b \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f, \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u043c\u043e\u0433\u0443\u0442 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u043b\u044e\u0434\u044c\u043c\u0438 \u0434\u043b\u044f \u0441\u0430\u043c\u043e\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u044f. \u041f\u0440\u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u043e \u043a\u0430\u0436\u0434\u043e\u043c\u0443 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044e \u043d\u0443\u0436\u043d\u044b\u0439 \u0431\u0430\u043b\u043b, \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u0443 \u0447\u0430\u0441\u0442\u043e\u0442\u043d\u043e\u0441\u0442\u0438.
</div>
<div class="scale-legend">
  <span>1 = \u041d\u0438\u043a\u043e\u0433\u0434\u0430 \u0438\u043b\u0438 \u043f\u043e\u0447\u0442\u0438 \u043d\u0438\u043a\u043e\u0433\u0434\u0430</span>
  <span>2 = \u0420\u0435\u0434\u043a\u043e</span>
  <span>3 = \u0412\u0440\u0435\u043c\u044f \u043e\u0442 \u0432\u0440\u0435\u043c\u0435\u043d\u0438</span>
  <span>4 = \u0427\u0430\u0441\u0442\u043e</span>
  <span>5 = \u041e\u0447\u0435\u043d\u044c \u0447\u0430\u0441\u0442\u043e</span>
  <span>6 = \u041f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u043e</span>
</div>
{smi_html}
<p class="unanswered-warning" id="smi-warning"></p>
<button class="btn" onclick="showSmiResults()">Show SMI Results</button>
<div id="smi-results">
  <h2>SMI v1.1 Results</h2>
  <div id="smi-disclaimer"></div>
  <div id="smi-summary"></div>
  <div class="results-section">
    <h3>По клинической значимости</h3>
    <div id="smi-clinical"></div>
  </div>
  <div class="results-section">
    <h3>По категориям</h3>
    <div id="smi-categories"></div>
  </div>
</div>
</div>

</div>

<script src="ysq_scoring.js"></script>
<script src="smi_scoring.js"></script>
<script>
const TOTAL = {total};

const YSQ_QUESTIONS = {ysq_questions_js};
const SMI_QUESTIONS = {smi_questions_js};
const INTERPRETATIONS = {interpretations_js};

const LEVEL_CSS = {{
  "\u043d\u0438\u0437\u043a\u0438\u0439": "level-low",
  "\u043f\u043e\u043d\u0438\u0436\u0435\u043d\u043d\u044b\u0439": "level-reduced",
  "\u0443\u043c\u0435\u0440\u0435\u043d\u043d\u044b\u0439": "level-medium",
  "\u043f\u043e\u0432\u044b\u0448\u0435\u043d\u043d\u044b\u0439": "level-elevated",
  "\u0432\u044b\u0441\u043e\u043a\u0438\u0439": "level-high",
  "\u043e\u0447. \u0432\u044b\u0441\u043e\u043a\u0438\u0439": "level-very-high",
}};

const LEVEL_COLORS = {{
  "\u043d\u0438\u0437\u043a\u0438\u0439": "#4caf50",
  "\u043f\u043e\u043d\u0438\u0436\u0435\u043d\u043d\u044b\u0439": "#8bc34a",
  "\u0443\u043c\u0435\u0440\u0435\u043d\u043d\u044b\u0439": "#ffc107",
  "\u043f\u043e\u0432\u044b\u0448\u0435\u043d\u043d\u044b\u0439": "#ff9800",
  "\u0432\u044b\u0441\u043e\u043a\u0438\u0439": "#f44336",
  "\u043e\u0447. \u0432\u044b\u0441\u043e\u043a\u0438\u0439": "#b71c1c",
}};

function toggleDetail(id) {{
  var el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}}

function toggleHint(id) {{
  var el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}}

function showYsqResults() {{
  var answers = {{}};
  var missing = [];
  for (var i = 1; i <= 90; i++) {{
    var el = document.querySelector('input[name="ysq_' + i + '"]:checked');
    if (el) answers[i] = parseInt(el.value);
    else missing.push(i);
  }}
  if (missing.length > 0) {{
    var w = document.getElementById('ysq-warning');
    w.style.display = 'block';
    w.textContent = 'YSQ: ' + missing.length + ' unanswered questions';
    missing.forEach(function(n) {{
      var el = document.getElementById('ysq-q' + n);
      if (el) el.style.border = '2px solid #d32f2f';
    }});
    return;
  }}
  document.getElementById('ysq-warning').style.display = 'none';

  var schemaResults = scoreAllSchemas(answers);
  var domainResults = scoreDomains(schemaResults);

  // Disclaimer
  document.getElementById('ysq-disclaimer').innerHTML =
    '<div class="disclaimer">' + INTERPRETATIONS.disclaimer + '</div>';

  // Key findings summary
  var elevated = 0;
  var high = 0;
  var sorted = Object.entries(schemaResults).sort(function(a, b) {{ return b[1].mean - a[1].mean; }});
  sorted.forEach(function(entry) {{
    if (entry[1].level === '\u043f\u043e\u0432\u044b\u0448\u0435\u043d\u043d\u044b\u0439') elevated++;
    if (entry[1].level === '\u0432\u044b\u0441\u043e\u043a\u0438\u0439') high++;
  }});
  var strongestDomain = null;
  var strongestMean = 0;
  for (var dCode in domainResults) {{
    if (domainResults[dCode].mean > strongestMean) {{
      strongestMean = domainResults[dCode].mean;
      strongestDomain = domainResults[dCode].name;
    }}
  }}
  var summaryParts = [];
  if (high > 0) summaryParts.push('\u0412\u044b\u0441\u043e\u043a\u0438\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c: ' + high + ' \u0441\u0445\u0435\u043c');
  if (elevated > 0) summaryParts.push('\u041f\u043e\u0432\u044b\u0448\u0435\u043d\u043d\u044b\u0439: ' + elevated + ' \u0441\u0445\u0435\u043c');
  if (strongestDomain) summaryParts.push('\u0421\u0438\u043b\u044c\u043d\u0435\u0439\u0448\u0438\u0439 \u0434\u043e\u043c\u0435\u043d: ' + strongestDomain + ' (' + strongestMean.toFixed(2) + ')');
  if (summaryParts.length > 0) {{
    document.getElementById('ysq-summary').innerHTML =
      '<div class="summary-box">' + summaryParts.join(' &bull; ') + '</div>';
  }} else {{
    document.getElementById('ysq-summary').innerHTML = '';
  }}

  // Render domains
  var domainsEl = document.getElementById('ysq-domains');
  var domainFragments = [];
  for (var code in domainResults) {{
    var d = domainResults[code];
    var domDesc = (INTERPRETATIONS.ysq.domains[code] && INTERPRETATIONS.ysq.domains[code].description) || '';
    domainFragments.push(
      '<div class="domain-card">' +
      '<div><span class="domain-name">' + d.name + '</span> (' + code + ')' +
      (d.highCount > 0 ? ' <span style="color:#e65100;font-size:12px">Высокие (5-6): ' + d.highCount + '</span>' : '') +
      (domDesc ? '<div style="font-size:12px;color:#555;margin-top:4px">' + domDesc + '</div>' : '') +
      '</div>' +
      '<div class="domain-mean">' + d.mean.toFixed(2) + '</div>' +
      '</div>'
    );
  }}
  domainsEl.innerHTML = domainFragments.join('');

  // Render schemas sorted by score
  var schemasEl = document.getElementById('ysq-schemas');
  var schemaFragments = [];
  for (var idx = 0; idx < sorted.length; idx++) {{
    var code = sorted[idx][0];
    var r = sorted[idx][1];
    var barWidth = (r.mean / 6 * 100).toFixed(0);
    var pct = r.pct.toFixed(0);
    var color = LEVEL_COLORS[r.level];
    var levelCss = LEVEL_CSS[r.level];
    var detailId = 'ysq-detail-' + code;

    // Schema description and level meaning
    var schemaInterp = INTERPRETATIONS.ysq.schemas[code];
    var levelMeaning = INTERPRETATIONS.ysq.levels[r.level] || '';
    var schemaDesc = (schemaInterp && schemaInterp.description) || '';

    // Per-item breakdown: questions scoring >= 5
    var highItems = [];
    var schemaObj = YSQ_SCHEMAS.find(function(s) {{ return s.code === code; }});
    if (schemaObj) {{
      schemaObj.questions.forEach(function(qnum) {{
        var val = answers[qnum];
        var cssClass = val >= 5 ? 'high-item' : '';
        highItems.push('<li class="' + cssClass + '">#' + qnum + ': ' + YSQ_QUESTIONS[qnum] + ' = ' + val + '</li>');
      }});
    }}

    schemaFragments.push(
      '<div class="schema-row" onclick="toggleDetail(\\'' + detailId + '\\')">' +
      '<span class="schema-code">' + code + '</span>' +
      '<span class="schema-name">' + r.name + '</span>' +
      '<span class="schema-mean">' + r.mean.toFixed(1) + ' (' + pct + '%)</span>' +
      '<div class="schema-bar-wrap"><div class="schema-bar" style="width:' + barWidth + '%;background:' + color + '"></div></div>' +
      '<span class="schema-level ' + levelCss + '">' + r.level + '</span>' +
      '</div>' +
      '<div class="schema-detail" id="' + detailId + '">' +
      (schemaDesc ? '<p>' + schemaDesc + '</p>' : '') +
      (levelMeaning ? '<p style="margin-top:6px"><strong>' + r.level + ':</strong> ' + levelMeaning + '</p>' : '') +
      (highItems.length > 0 ? '<ul class="item-breakdown">' + highItems.join('') + '</ul>' : '') +
      '</div>'
    );
  }}
  schemasEl.innerHTML = schemaFragments.join('');

  document.getElementById('ysq-results').style.display = 'block';
  document.getElementById('ysq-results').scrollIntoView({{ behavior: 'smooth' }});
}}

function showSmiResults() {{
  var answers = {{}};
  var missing = [];
  for (var i = 1; i <= 124; i++) {{
    var el = document.querySelector('input[name="smi_' + i + '"]:checked');
    if (el) answers[i] = parseInt(el.value);
    else missing.push(i);
  }}
  if (missing.length > 0) {{
    var w = document.getElementById('smi-warning');
    w.style.display = 'block';
    w.textContent = 'SMI: ' + missing.length + ' unanswered questions';
    missing.forEach(function(n) {{
      var el = document.getElementById('smi-q' + n);
      if (el) el.style.border = '2px solid #d32f2f';
    }});
    return;
  }}
  document.getElementById('smi-warning').style.display = 'none';

  var results = scoreAllModes(answers);

  // Disclaimer
  document.getElementById('smi-disclaimer').innerHTML =
    '<div class="disclaimer">' + INTERPRETATIONS.disclaimer + '</div>';

  // Key findings summary
  var elevatedModes = [];
  var highModes = [];
  for (var mCode in results) {{
    var mR = results[mCode];
    if (mR.level === '\u043f\u043e\u0432\u044b\u0448\u0435\u043d\u043d\u044b\u0439' || mR.level === '\u0432\u044b\u0441\u043e\u043a\u0438\u0439' || mR.level === '\u043e\u0447. \u0432\u044b\u0441\u043e\u043a\u0438\u0439') {{
      elevatedModes.push(mR.ru + ' (' + mR.level + ')');
    }}
  }}
  if (elevatedModes.length > 0) {{
    document.getElementById('smi-summary').innerHTML =
      '<div class="summary-box">\u0417\u043d\u0430\u0447\u0438\u043c\u044b\u0435 \u0440\u0435\u0436\u0438\u043c\u044b: ' + elevatedModes.join(', ') + '</div>';
  }} else {{
    document.getElementById('smi-summary').innerHTML = '';
  }}

  // Clinical significance (sorted by clinicalScore)
  var sorted = Object.entries(results)
    .map(function(entry) {{ var code = entry[0]; var r = entry[1]; return {{code: code, ru: r.ru, mean: r.mean, level: r.level, reverse: r.reverse, highCount: r.highCount, cat: r.cat, clinical: clinicalScore(r.mean, r.reverse), scores: r.scores}}; }})
    .sort(function(a, b) {{ return b.clinical - a.clinical; }});

  var clinEl = document.getElementById('smi-clinical');
  var clinFragments = [];
  for (var idx = 0; idx < sorted.length; idx++) {{
    var r = sorted[idx];
    var barWidth = (clinicalScore(r.mean, r.reverse) / 6 * 100).toFixed(0);
    var color = LEVEL_COLORS[r.level];
    var levelCss = LEVEL_CSS[r.level];
    var revTag = r.reverse ? '<span class="reverse-tag">(обр.)</span>' : '';
    var detailId = 'smi-clin-detail-' + r.code;

    var modeInterp = INTERPRETATIONS.smi.modes[r.code];
    var modeDesc = (modeInterp && modeInterp.description) || '';
    var levelMeaning = INTERPRETATIONS.smi.levels[r.level] || '';

    // Per-item breakdown
    var modeData = SMI_MODES[r.code];
    var itemBreakdown = [];
    if (modeData) {{
      modeData.items.forEach(function(qnum, qIdx) {{
        var val = r.scores[qIdx];
        var isHigh = r.reverse ? (val <= 2) : (val >= 5);
        var cssClass = isHigh ? 'high-item' : '';
        itemBreakdown.push('<li class="' + cssClass + '">#' + qnum + ': ' + SMI_QUESTIONS[qnum] + ' = ' + val + '</li>');
      }});
    }}

    var reverseNote = r.reverse ? '<p style="margin-top:6px;color:#888;font-style:italic">\u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0448\u043a\u0430\u043b\u0430: \u043d\u0438\u0437\u043a\u0438\u0435 \u0431\u0430\u043b\u043b\u044b \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u044e\u0442 \u043d\u0430 \u043a\u043b\u0438\u043d\u0438\u0447\u0435\u0441\u043a\u0443\u044e \u0437\u043d\u0430\u0447\u0438\u043c\u043e\u0441\u0442\u044c.</p>' : '';

    clinFragments.push(
      '<div class="schema-row" onclick="toggleDetail(\\'' + detailId + '\\')">' +
      '<span class="schema-code">' + r.code + '</span>' +
      '<span class="schema-name">' + r.ru + revTag + '</span>' +
      '<span class="schema-mean">' + r.mean.toFixed(2) + '</span>' +
      '<div class="schema-bar-wrap"><div class="schema-bar" style="width:' + barWidth + '%;background:' + color + '"></div></div>' +
      '<span class="schema-level ' + levelCss + '">' + r.level + '</span>' +
      '</div>' +
      '<div class="schema-detail" id="' + detailId + '">' +
      (modeDesc ? '<p>' + modeDesc + '</p>' : '') +
      (levelMeaning ? '<p style="margin-top:6px"><strong>' + r.level + ':</strong> ' + levelMeaning + '</p>' : '') +
      reverseNote +
      (itemBreakdown.length > 0 ? '<ul class="item-breakdown">' + itemBreakdown.join('') + '</ul>' : '') +
      '</div>'
    );
  }}
  clinEl.innerHTML = clinFragments.join('');

  // By category
  var catEl = document.getElementById('smi-categories');
  var catFragments = [];
  var currentCat = null;
  for (var cIdx = 0; cIdx < SMI_MODE_ORDER.length; cIdx++) {{
    var code = SMI_MODE_ORDER[cIdx];
    var r = results[code];
    if (r.cat !== currentCat) {{
      currentCat = r.cat;
      var catDesc = (INTERPRETATIONS.smi.categories[currentCat] && INTERPRETATIONS.smi.categories[currentCat].description) || '';
      catFragments.push('<div class="cat-header">' + currentCat +
        (catDesc ? '<div style="font-size:11px;font-weight:400;color:#555;margin-top:2px">' + catDesc + '</div>' : '') +
        '</div>');
    }}
    var barWidth = (clinicalScore(r.mean, r.reverse) / 6 * 100).toFixed(0);
    var color = LEVEL_COLORS[r.level];
    var levelCss = LEVEL_CSS[r.level];
    var revTag = r.reverse ? '<span class="reverse-tag">(обр.)</span>' : '';
    var highTag = r.highCount > 0 ? ' <span style="color:#e65100;font-size:11px">(' + r.highCount + ' выс.)</span>' : '';
    var detailId = 'smi-cat-detail-' + code;

    var modeInterp = INTERPRETATIONS.smi.modes[code];
    var modeDesc = (modeInterp && modeInterp.description) || '';
    var levelMeaning = INTERPRETATIONS.smi.levels[r.level] || '';

    var modeData = SMI_MODES[code];
    var itemBreakdown = [];
    if (modeData) {{
      modeData.items.forEach(function(qnum, qIdx) {{
        var val = r.scores[qIdx];
        var isHigh = r.reverse ? (val <= 2) : (val >= 5);
        var cssClass = isHigh ? 'high-item' : '';
        itemBreakdown.push('<li class="' + cssClass + '">#' + qnum + ': ' + SMI_QUESTIONS[qnum] + ' = ' + val + '</li>');
      }});
    }}

    var reverseNote = r.reverse ? '<p style="margin-top:6px;color:#888;font-style:italic">\u041e\u0431\u0440\u0430\u0442\u043d\u0430\u044f \u0448\u043a\u0430\u043b\u0430: \u043d\u0438\u0437\u043a\u0438\u0435 \u0431\u0430\u043b\u043b\u044b \u0443\u043a\u0430\u0437\u044b\u0432\u0430\u044e\u0442 \u043d\u0430 \u043a\u043b\u0438\u043d\u0438\u0447\u0435\u0441\u043a\u0443\u044e \u0437\u043d\u0430\u0447\u0438\u043c\u043e\u0441\u0442\u044c.</p>' : '';

    catFragments.push(
      '<div class="schema-row" onclick="toggleDetail(\\'' + detailId + '\\')">' +
      '<span class="schema-code">' + code + '</span>' +
      '<span class="schema-name">' + r.ru + revTag + highTag + '</span>' +
      '<span class="schema-mean">' + r.mean.toFixed(2) + '</span>' +
      '<div class="schema-bar-wrap"><div class="schema-bar" style="width:' + barWidth + '%;background:' + color + '"></div></div>' +
      '<span class="schema-level ' + levelCss + '">' + r.level + '</span>' +
      '</div>' +
      '<div class="schema-detail" id="' + detailId + '">' +
      (modeDesc ? '<p>' + modeDesc + '</p>' : '') +
      (levelMeaning ? '<p style="margin-top:6px"><strong>' + r.level + ':</strong> ' + levelMeaning + '</p>' : '') +
      reverseNote +
      (itemBreakdown.length > 0 ? '<ul class="item-breakdown">' + itemBreakdown.join('') + '</ul>' : '') +
      '</div>'
    );
  }}
  catEl.innerHTML = catFragments.join('');

  document.getElementById('smi-results').style.display = 'block';
  document.getElementById('smi-results').scrollIntoView({{ behavior: 'smooth' }});
}}

function updateProgress() {{
  var answered = document.querySelectorAll('input[type=radio]:checked').length;
  document.getElementById('progressText').textContent = answered + ' / ' + TOTAL;
  document.getElementById('progressPct').textContent = Math.round(answered/TOTAL*100) + '%';
  document.getElementById('progressFill').style.width = (answered/TOTAL*100) + '%';
  var ysqAnswered = document.querySelectorAll('input[name^="ysq_"]:checked').length;
  var smiAnswered = document.querySelectorAll('input[name^="smi_"]:checked').length;
  document.getElementById('tab-btn-ysq').textContent = 'YSQ-S3R (' + ysqAnswered + '/90)';
  document.getElementById('tab-btn-smi').textContent = 'SMI v1.1 (' + smiAnswered + '/124)';
}}

function markAnswered(el) {{
  el.closest('.q').classList.add('answered');
  updateProgress();
  var currentQ = el.closest('.q');
  var next = currentQ.nextElementSibling;
  while (next && next.classList.contains('answered')) next = next.nextElementSibling;
  if (next && next.classList.contains('q')) {{
    next.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}
}}

function switchTab(id, evt) {{
  document.querySelectorAll('.tab-content').forEach(function(t) {{ t.classList.remove('active'); }});
  document.querySelectorAll('.tab').forEach(function(t) {{ t.classList.remove('active'); }});
  document.getElementById('tab-' + id).classList.add('active');
  evt.target.classList.add('active');
}}

// Keyboard: hover over a question and press 1-6
document.addEventListener('keydown', function(e) {{
  if (e.key >= '1' && e.key <= '6') {{
    var active = document.querySelector('.q:hover');
    if (active) {{
      var radios = active.querySelectorAll('input[type=radio]');
      radios[parseInt(e.key)-1].checked = true;
      radios[parseInt(e.key)-1].dispatchEvent(new Event('change'));
    }}
  }}
}});

// Auto-save to localStorage
function autoSave() {{
  var all = {{}};
  document.querySelectorAll('input[type=radio]:checked').forEach(function(el) {{
    all[el.name] = el.value;
  }});
  localStorage.setItem('schema_answers', JSON.stringify(all));
}}

function autoLoad() {{
  try {{
    var saved = JSON.parse(localStorage.getItem('schema_answers'));
    if (!saved) return;
    Object.entries(saved).forEach(function(entry) {{
      var name = entry[0]; var val = entry[1];
      var el = document.querySelector('input[name="' + name + '"][value="' + val + '"]');
      if (el) {{
        el.checked = true;
        el.closest('.q').classList.add('answered');
      }}
    }});
    updateProgress();
  }} catch(e) {{}}
}}

// URL sharing: encode answers as compact string in hash
// Format: 90 YSQ digits + 124 SMI digits = 214 chars, 0 = unanswered
function answersToString() {{
  var s = '';
  for (var i = 1; i <= 90; i++) {{
    var el = document.querySelector('input[name="ysq_' + i + '"]:checked');
    s += el ? el.value : '0';
  }}
  for (var i = 1; i <= 124; i++) {{
    var el = document.querySelector('input[name="smi_' + i + '"]:checked');
    s += el ? el.value : '0';
  }}
  return s;
}}

function loadFromString(s) {{
  if (s.length !== 214) return false;
  var loaded = 0;
  for (var i = 0; i < 90; i++) {{
    var v = s[i];
    if (v !== '0') {{
      var el = document.querySelector('input[name="ysq_' + (i+1) + '"][value="' + v + '"]');
      if (el) {{ el.checked = true; el.closest('.q').classList.add('answered'); loaded++; }}
    }}
  }}
  for (var i = 0; i < 124; i++) {{
    var v = s[90 + i];
    if (v !== '0') {{
      var el = document.querySelector('input[name="smi_' + (i+1) + '"][value="' + v + '"]');
      if (el) {{ el.checked = true; el.closest('.q').classList.add('answered'); loaded++; }}
    }}
  }}
  updateProgress();
  return loaded;
}}

function shareUrl() {{
  var encoded = btoa(answersToString());
  var url = location.origin + location.pathname + '#' + encoded;
  history.replaceState(null, '', '#' + encoded);
  navigator.clipboard.writeText(url);
  var btn = document.getElementById('shareBtn');
  btn.textContent = 'Copied!';
  setTimeout(function() {{ btn.textContent = 'Share URL'; }}, 2000);
}}

function loadFromHash() {{
  var hash = location.hash.slice(1);
  if (!hash) return false;
  try {{
    var decoded = atob(hash);
    if (decoded.length === 214) {{
      loadFromString(decoded);
      return true;
    }}
  }} catch(e) {{}}
  return false;
}}

setInterval(autoSave, 5000);
// URL hash takes priority over localStorage
if (!loadFromHash()) {{ autoLoad(); }}
</script>
</body>
</html>"""

with open("F:/personal/psyco/dist/index.html", "w", encoding="utf-8") as f:
    f.write(page)

# Copy scoring modules
shutil.copy2(
    "F:/personal/psyco/ysq_scoring.js", "F:/personal/psyco/dist/ysq_scoring.js"
)
shutil.copy2(
    "F:/personal/psyco/smi_scoring.js", "F:/personal/psyco/dist/smi_scoring.js"
)

print(f"Done: dist/index.html ({total} questions)")
