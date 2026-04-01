import json
import html as html_mod
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

with open(ROOT / "src" / "data" / "questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open(ROOT / "src" / "data" / "interpretations.json", "r", encoding="utf-8") as f:
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
            f'<span class="q-text" onclick="toggleEl(\'{prefix}-hint-{num}\')">{text}</span>'
            f"{hint_html}"
            f'<span class="q-opts">{opts}</span>'
            f"</div>"
        )
    return "\n".join(parts)


ysq_html = render_questions(ysq, "ysq")
smi_html = render_questions(smi, "smi")
total = len(ysq) + len(smi)

# Build JS constants
interpretations_js = json.dumps(interpretations, ensure_ascii=False)

page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<title>Схемные опросники</title>
<style>
:root {{
  --bg: #faf7f2;
  --bg-card: #fffdf9;
  --bg-hover: #f5f0e8;
  --accent: #c4704b;
  --accent-dark: #a85a3a;
  --accent-light: #f0ddd4;
  --text: #2d2a26;
  --text-muted: #7a7168;
  --text-light: #a69e94;
  --border: #e8e2d9;
  --success: #6b8f5e;
  --warning: #d4943a;
  --danger: #c45a4a;
  --font-display: 'Playfair Display', Georgia, serif;
  --font-body: 'Source Sans 3', 'Segoe UI', sans-serif;
  --shadow-sm: 0 1px 3px rgba(45,42,38,0.06);
  --shadow-md: 0 2px 8px rgba(45,42,38,0.08);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: var(--font-body); background: var(--bg); color: var(--text); line-height: 1.6; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 24px 20px; animation: fadeIn 0.4s ease; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
h1 {{ font-family: var(--font-display); text-align: center; margin: 24px 0; color: var(--text); font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
h2 {{ font-family: var(--font-display); margin: 32px 0 12px; color: var(--text); border-bottom: 2px solid var(--accent); padding-bottom: 8px; font-size: 22px; font-weight: 600; }}
.instructions {{ background: var(--accent-light); border-left: 4px solid var(--accent); padding: 16px 20px; margin: 16px 0 28px; border-radius: 0 8px 8px 0; font-size: 14px; color: var(--text); line-height: 1.7; }}
.scale-legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 24px; }}
.scale-legend span {{ background: var(--bg-card); padding: 5px 12px; border-radius: 6px; font-size: 13px; border: 1px solid var(--border); color: var(--text-muted); }}
.q {{ background: var(--bg-card); padding: 16px 20px; margin: 5px 0; border-radius: 8px; display: flex; align-items: center; gap: 14px; box-shadow: var(--shadow-sm); transition: all 0.2s ease; flex-wrap: wrap; border: 1px solid transparent; }}
.q:hover {{ background: var(--bg-hover); border-color: var(--border); }}
.q.answered {{ border-left: 3px solid var(--accent); }}
.q-num {{ font-family: var(--font-display); font-weight: 700; color: var(--accent); min-width: 32px; font-size: 16px; }}
.q-text {{ flex: 1; font-size: 15px; cursor: pointer; transition: color 0.15s; }}
.q-text:hover {{ color: var(--accent); }}
.q-hint {{ display: none; width: 100%; font-size: 13px; color: var(--text-light); font-style: italic; padding: 4px 0 0 32px; }}
.q-hint.open {{ display: block; }}
.q-opts {{ display: flex; gap: 5px; flex-shrink: 0; }}
.q-opts label {{ display: flex; align-items: center; justify-content: center; width: 38px; height: 38px; border: 2px solid var(--border); border-radius: 50%; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.15s ease; user-select: none; color: var(--text-muted); }}
.q-opts label:hover {{ border-color: var(--accent); background: var(--accent-light); color: var(--accent-dark); }}
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
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}}
.q-opts label:has(input:checked) {{ border-color: var(--accent); background: var(--accent); color: #fff; }}
.progress {{ position: sticky; top: 0; z-index: 100; background: var(--bg-card); padding: 10px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; backdrop-filter: blur(8px); }}
.progress-bar {{ flex: 1; min-width: 60px; height: 6px; background: var(--border); border-radius: 3px; }}
.progress-fill {{ height: 100%; background: linear-gradient(90deg, var(--accent), var(--success)); border-radius: 3px; transition: width 0.3s ease; }}
.btn {{ display: block; margin: 32px auto; padding: 14px 28px; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-family: var(--font-body); font-size: 15px; font-weight: 600; cursor: pointer; max-width: 100%; transition: background 0.2s; }}
.btn:hover {{ background: var(--accent-dark); }}
#results {{ display: none; background: var(--bg-card); padding: 20px; border-radius: 8px; margin: 20px 0; white-space: pre-wrap; font-family: monospace; font-size: 13px; }}
#ysq-results {{ display: none; margin: 20px 0; }}
#smi-results {{ display: none; margin: 20px 0; }}
.level-very-high {{ background: #f8d7da; color: #9b2c2c; }}
.cat-header {{ font-family: var(--font-display); font-size: 14px; font-weight: 600; color: var(--accent-dark); padding: 14px 0 6px; border-bottom: 2px solid var(--accent); margin-top: 12px; }}
.reverse-tag {{ font-size: 10px; color: var(--text-light); margin-left: 4px; font-style: italic; }}
@media (max-width: 600px) {{
  .q {{ flex-wrap: wrap; padding: 12px 14px; gap: 8px; }}
  .q-text {{ min-width: 100%; font-size: 14px; }}
  .q-opts label {{ width: 34px; height: 34px; font-size: 13px; }}
  .schema-row {{ flex-wrap: wrap; gap: 4px; }}
  .schema-name {{ min-width: calc(100% - 55px); font-size: 12px; }}
  .schema-bar-wrap {{ flex: 1; }}
  .progress {{ padding: 8px 10px; gap: 6px; }}
  .container {{ padding: 12px; }}
  h1 {{ font-size: 22px; }}
  h2 {{ font-size: 18px; }}
  .scale-legend span {{ padding: 3px 8px; font-size: 11px; }}
  .domain-card {{ flex-wrap: wrap; gap: 4px; }}
}}
.results-section {{ background: var(--bg-card); border-radius: 8px; padding: 24px; margin: 16px 0; box-shadow: var(--shadow-md); border: 1px solid var(--border); }}
.results-section h3 {{ font-family: var(--font-display); margin: 0 0 16px; color: var(--text); font-size: 17px; font-weight: 600; }}
.schema-row {{ display: flex; align-items: center; gap: 10px; padding: 10px 6px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s; border-radius: 4px; }}
.schema-row:last-child {{ border-bottom: none; }}
.schema-row:hover {{ background: var(--bg-hover); }}
.schema-code {{ font-family: var(--font-display); font-weight: 700; min-width: 45px; color: var(--accent); font-size: 14px; }}
.schema-name {{ flex: 1; font-size: 13px; color: var(--text); }}
.schema-bar-wrap {{ width: 120px; height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }}
.schema-bar {{ height: 100%; border-radius: 4px; transition: width 0.5s ease; }}
.schema-mean {{ min-width: 35px; text-align: right; font-weight: 600; font-size: 13px; color: var(--text); }}
.schema-level {{ min-width: 100px; font-size: 12px; padding: 3px 10px; border-radius: 12px; text-align: center; font-weight: 600; }}
.level-low {{ background: #e8f0e4; color: #4a6b3e; }}
.level-reduced {{ background: #edf2e4; color: #5a7a42; }}
.level-medium {{ background: #faf0dd; color: #8a6a2a; }}
.level-elevated {{ background: var(--accent-light); color: var(--accent-dark); }}
.level-high {{ background: #f5ddd8; color: #8b3a2e; }}
.domain-card {{ background: var(--bg-card); border-left: 4px solid var(--accent); padding: 14px 20px; margin: 8px 0; border-radius: 0 8px 8px 0; display: flex; justify-content: space-between; align-items: center; box-shadow: var(--shadow-sm); }}
.domain-name {{ font-family: var(--font-display); font-weight: 600; font-size: 15px; color: var(--text); }}
.domain-mean {{ font-family: var(--font-display); font-size: 22px; font-weight: 700; color: var(--accent); }}
.tab-bar {{ display: flex; gap: 0; margin: 24px 0 0; }}
.tab {{ font-family: var(--font-body); padding: 12px 24px; background: var(--border); border: none; cursor: pointer; font-size: 14px; font-weight: 600; border-radius: 8px 8px 0 0; color: var(--text-muted); transition: all 0.2s; }}
.tab:hover {{ background: var(--accent-light); color: var(--accent-dark); }}
.tab.active {{ background: var(--accent); color: #fff; }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}
.unanswered-warning {{ color: var(--danger); font-weight: 600; margin: 10px 0; display: none; }}
.schema-detail {{ display: none; padding: 10px 20px 14px 60px; font-size: 13px; color: var(--text-muted); border-bottom: 1px solid var(--border); line-height: 1.7; }}
.schema-detail.open {{ display: block; }}
.disclaimer {{ background: #fdf6ed; border-left: 4px solid var(--warning); padding: 14px 20px; margin: 16px 0; border-radius: 0 8px 8px 0; font-size: 13px; color: #7a5a2a; line-height: 1.6; }}
.summary-box {{ background: #f0f4ec; border-left: 4px solid var(--success); padding: 14px 20px; margin: 12px 0; border-radius: 0 8px 8px 0; font-size: 14px; color: #3d5a30; line-height: 1.6; }}
.item-breakdown {{ margin: 10px 0 0; padding: 0; list-style: none; font-size: 13px; }}
.item-breakdown li {{ padding: 5px 8px; color: var(--text-muted); cursor: pointer; border-radius: 4px; transition: all 0.15s; }}
.item-breakdown li:hover {{ background: var(--accent-light); color: var(--accent-dark); }}
.item-breakdown .high-item {{ color: var(--danger); font-weight: 600; }}
.item-breakdown .high-item:hover {{ background: #f5ddd8; color: #8b3a2e; }}
</style>
</head>
<body>

<div class="progress" id="progressBar">
  <button id="shareBtn" onclick="shareUrl()" style="padding:5px 12px;background:var(--accent);color:#fff;border:none;border-radius:6px;cursor:pointer;font-family:var(--font-body);font-size:11px;font-weight:600;white-space:nowrap;transition:background 0.2s">Поделиться</button>
  <button onclick="resetAll()" style="padding:5px 12px;background:var(--danger);color:#fff;border:none;border-radius:6px;cursor:pointer;font-family:var(--font-body);font-size:11px;font-weight:600;white-space:nowrap;transition:background 0.2s">Сбросить</button>
  <span id="progressText">0 / {total}</span>
  <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:0%"></div></div>
  <span id="progressPct">0%</span>
</div>

<button id="back-to-results" onclick="backToResults()" style="display:none;position:fixed;bottom:20px;right:20px;z-index:200;padding:12px 20px;background:var(--accent);color:#fff;border:none;border-radius:8px;font-family:var(--font-body);font-size:14px;font-weight:600;cursor:pointer;box-shadow:0 4px 12px rgba(196,112,75,0.3);transition:background 0.2s">&larr; К результатам</button>

<div class="container">
<h1>Schema Questionnaires</h1>

<div class="tab-bar">
  <button class="tab active" id="tab-btn-ysq" onclick="switchTab('ysq', event)">YSQ-S3R (0/90)</button>
  <button class="tab" id="tab-btn-smi" onclick="switchTab('smi', event)">SMI v1.1 (0/124)</button>
</div>

<div class="tab-content active" id="tab-ysq">
<h2 style="cursor:pointer" onclick="toggleEl('ysq-method-desc')">Young Schema Questionnaire (YSQ-S3R) <span style="font-size:13px;color:#888;font-weight:400">&#9432; о методике</span></h2>
<div class="q-hint" id="ysq-method-desc" style="padding:0 0 15px 0;font-size:14px;line-height:1.6;color:#444">
YSQ-S3R (Young Schema Questionnaire - Short Form, 3rd Revision) - это опросник из 90 вопросов, разработанный Джеффри Янгом для выявления <b>ранних дезадаптивных схем</b> (РДС). Эти схемы формируются в детстве и подростковом возрасте в результате неудовлетворения базовых эмоциональных потребностей и продолжают влиять на восприятие, мышление и поведение во взрослой жизни.<br><br>
Опросник измеряет 18 схем, объединенных в 5 доменов: разобщенность и отвержение, нарушение автономии, направленность на других, сверхбдительность и подавление, нарушенные границы. Каждая схема оценивается по 5 утверждениям на шкале от 1 (абсолютно не соответствует) до 6 (полностью соответствует).<br><br>
Результаты не являются диагнозом. Они помогают терапевту и клиенту определить ключевые темы для работы в схема-терапии.
</div>
<div class="instructions">
Ниже перечислены утверждения, с помощью которых Вы можете описать себя. Прочитайте каждое утверждение и решите, насколько точно оно Вас характеризует. Основывайте свой ответ на том, как Вы <b>ЧУВСТВУЕТЕ</b>, а не на том, что Вы считаете правильным.
</div>
<div class="scale-legend">
  <span>1 = Абсолютно не соответствует</span>
  <span>2 = По большей части не соответствует</span>
  <span>3 = Скорее соответствует, чем нет</span>
  <span>4 = В общем, соответствует</span>
  <span>5 = По большей части соответствует</span>
  <span>6 = Полностью соответствует</span>
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
<h2 style="cursor:pointer" onclick="toggleEl('smi-method-desc')">Schema Mode Inventory (SMI v1.1) <span style="font-size:13px;color:#888;font-weight:400">&#9432; о методике</span></h2>
<div class="q-hint" id="smi-method-desc" style="padding:0 0 15px 0;font-size:14px;line-height:1.6;color:#444">
SMI v1.1 (Schema Mode Inventory) - это опросник из 124 вопросов, разработанный Лоббестаель, ван Врисвейк и Арнтцем для измерения <b>схемных режимов</b> (mode). Если схемы - это устойчивые убеждения, то режимы - это эмоциональные состояния, которые активируются в конкретных ситуациях.<br><br>
Опросник измеряет 14 режимов в 5 категориях: детские режимы (уязвимый, рассерженный, яростный, импульсивный, недисциплинированный, счастливый ребенок), избегающие режимы (покорный капитулянт, отстраняющийся защитник, отстраненное самоуспокоение), режимы гиперкомпенсации (самовозвеличение, угрозы и нападение), родительские режимы (карающий и требовательный родитель) и здоровый взрослый.<br><br>
Режимы «Счастливый ребенок» и «Здоровый взрослый» оцениваются по обратной шкале: высокий балл означает здоровое функционирование. Для остальных режимов высокий балл указывает на клиническую значимость.
</div>
<div class="instructions">
Ниже перечислены утверждения, которые могут использоваться людьми для самоописания. Проставьте по каждому утверждению нужный балл, используя таблицу частотности.
</div>
<div class="scale-legend">
  <span>1 = Никогда или почти никогда</span>
  <span>2 = Редко</span>
  <span>3 = Время от времени</span>
  <span>4 = Часто</span>
  <span>5 = Очень часто</span>
  <span>6 = Постоянно</span>
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

function getQuestionText(prefix, num) {{
  var el = document.querySelector('#' + prefix + '-q' + num + ' .q-text');
  return el ? el.textContent : '#' + num;
}}
const INTERPRETATIONS = {interpretations_js};

const LEVEL_CSS = {{
  "низкий": "level-low",
  "пониженный": "level-reduced",
  "умеренный": "level-medium",
  "повышенный": "level-elevated",
  "высокий": "level-high",
  "оч. высокий": "level-very-high",
}};

const LEVEL_COLORS = {{
  "низкий": "#6b8f5e",
  "пониженный": "#7a9a5e",
  "умеренный": "#d4943a",
  "повышенный": "#c4704b",
  "высокий": "#c45a4a",
  "оч. высокий": "#9b2c2c",
}};

function toggleEl(id) {{
  var el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}}

var _savedScrollPos = null;
var _savedTab = null;

function goToQuestion(prefix, num) {{
  _savedScrollPos = window.scrollY;
  _savedTab = document.querySelector('.tab.active');
  switchTab(prefix, {{target: document.getElementById('tab-btn-' + prefix)}});
  var el = document.getElementById(prefix + '-q' + num);
  if (el) {{
    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
    el.style.boxShadow = '0 0 0 3px #0f3460';
    setTimeout(function() {{ el.style.boxShadow = ''; }}, 3000);
  }}
  document.getElementById('back-to-results').style.display = 'block';
}}

function backToResults() {{
  if (_savedTab) {{
    var tabId = _savedTab.id.replace('tab-btn-', '');
    switchTab(tabId, {{target: _savedTab}});
  }}
  window.scrollTo({{top: _savedScrollPos || 0, behavior: 'smooth'}});
  document.getElementById('back-to-results').style.display = 'none';
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
    if (entry[1].level === 'повышенный') elevated++;
    if (entry[1].level === 'высокий') high++;
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
  if (high > 0) summaryParts.push('Высокий уровень: ' + high + ' схем');
  if (elevated > 0) summaryParts.push('Повышенный: ' + elevated + ' схем');
  if (strongestDomain) summaryParts.push('Сильнейший домен: ' + strongestDomain + ' (' + strongestMean.toFixed(2) + ')');
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
      (d.highCount > 0 ? ' <span style="color:#a85a3a;font-size:12px">Высокие (5-6): ' + d.highCount + '</span>' : '') +
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
        highItems.push('<li class="' + cssClass + '" style="cursor:pointer" onclick="goToQuestion(\\'ysq\\', ' + qnum + ')">#' + qnum + ': ' + getQuestionText('ysq', qnum) + ' = ' + val + '</li>');
      }});
    }}

    schemaFragments.push(
      '<div class="schema-row" onclick="toggleEl(\\'' + detailId + '\\')">' +
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
    if (mR.level === 'повышенный' || mR.level === 'высокий' || mR.level === 'оч. высокий') {{
      elevatedModes.push(mR.ru + ' (' + mR.level + ')');
    }}
  }}
  if (elevatedModes.length > 0) {{
    document.getElementById('smi-summary').innerHTML =
      '<div class="summary-box">Значимые режимы: ' + elevatedModes.join(', ') + '</div>';
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
        itemBreakdown.push('<li class="' + cssClass + '" style="cursor:pointer" onclick="goToQuestion(\\'smi\\', ' + qnum + ')">#' + qnum + ': ' + getQuestionText('smi', qnum) + ' = ' + val + '</li>');
      }});
    }}

    var reverseNote = r.reverse ? '<p style="margin-top:6px;color:#888;font-style:italic">Обратная шкала: низкие баллы указывают на клиническую значимость.</p>' : '';

    clinFragments.push(
      '<div class="schema-row" onclick="toggleEl(\\'' + detailId + '\\')">' +
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
    var highTag = r.highCount > 0 ? ' <span style="color:#a85a3a;font-size:11px">(' + r.highCount + ' выс.)</span>' : '';
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
        itemBreakdown.push('<li class="' + cssClass + '" style="cursor:pointer" onclick="goToQuestion(\\'smi\\', ' + qnum + ')">#' + qnum + ': ' + getQuestionText('smi', qnum) + ' = ' + val + '</li>');
      }});
    }}

    var reverseNote = r.reverse ? '<p style="margin-top:6px;color:#888;font-style:italic">Обратная шкала: низкие баллы указывают на клиническую значимость.</p>' : '';

    catFragments.push(
      '<div class="schema-row" onclick="toggleEl(\\'' + detailId + '\\')">' +
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

function resetAll() {{
  if (!confirm('Сбросить все ответы? Это действие нельзя отменить.')) return;
  document.querySelectorAll('input[type=radio]:checked').forEach(function(el) {{
    el.checked = false;
  }});
  document.querySelectorAll('.q').forEach(function(el) {{
    el.classList.remove('answered');
    el.style.border = '';
    el.style.boxShadow = '';
  }});
  document.querySelectorAll('.q-hint').forEach(function(el) {{
    el.classList.remove('open');
  }});
  document.getElementById('ysq-results').style.display = 'none';
  document.getElementById('smi-results').style.display = 'none';
  localStorage.removeItem('schema_answers');
  history.replaceState(null, '', location.pathname);
  updateProgress();
}}

// Auto-save to localStorage (only when answers change)
var _lastSaved = '';
function autoSave() {{
  var all = {{}};
  document.querySelectorAll('input[type=radio]:checked').forEach(function(el) {{
    all[el.name] = el.value;
  }});
  var json = JSON.stringify(all);
  if (json !== _lastSaved) {{
    localStorage.setItem('schema_answers', json);
    _lastSaved = json;
  }}
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
  btn.textContent = 'Скопировано!';
  setTimeout(function() {{ btn.textContent = 'Поделиться'; }}, 2000);
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

dist = ROOT / "dist"
dist.mkdir(exist_ok=True)

with open(dist / "index.html", "w", encoding="utf-8") as f:
    f.write(page)

# Copy scoring modules
shutil.copy2(ROOT / "src" / "scoring" / "ysq_scoring.js", dist / "ysq_scoring.js")
shutil.copy2(ROOT / "src" / "scoring" / "smi_scoring.js", dist / "smi_scoring.js")

print(f"Done: dist/index.html ({total} questions)")
