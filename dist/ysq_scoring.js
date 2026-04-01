// YSQ-S3R Scoring Module

const YSQ_SCHEMAS = [
  {code: "ЭД",   name: "Эмоциональная депривация",                    domain: "РСО",   questions: [1, 19, 37, 55, 73]},
  {code: "ПН",   name: "Покинутость / нестабильность",                domain: "РСО",   questions: [2, 20, 38, 56, 74]},
  {code: "НН",   name: "Недоверие / насилие",                          domain: "РСО",   questions: [3, 21, 39, 57, 75]},
  {code: "СИО",  name: "Социальная изоляция / отчуждение",            domain: "РСО",   questions: [4, 22, 40, 58, 76]},
  {code: "ДС",   name: "Дефективность / стыд",                        domain: "РСО",   questions: [5, 23, 41, 59, 77]},
  {code: "НО",   name: "Неуспешность / обреченность на неудачу",      domain: "НЛАНД", questions: [6, 24, 42, 60, 78]},
  {code: "ЗН",   name: "Зависимость / некомпетентность",              domain: "НЛАНД", questions: [7, 25, 43, 61, 79]},
  {code: "У",    name: "Уязвимость",                                   domain: "НЛАНД", questions: [8, 26, 44, 62, 80]},
  {code: "СДНЯ", name: "Слитность с другими / неразвитое Я",          domain: "НЛАНД", questions: [9, 27, 45, 63, 81]},
  {code: "ПП",   name: "Покорность / подчинение",                      domain: "НД",    questions: [10, 28, 46, 64, 82]},
  {code: "С",    name: "Самопожертвование",                            domain: "НД",    questions: [11, 29, 47, 65, 83]},
  {code: "ПЭ",   name: "Подавление эмоций",                            domain: "СбП",   questions: [12, 30, 48, 66, 84]},
  {code: "ЖС",   name: "Жёсткие стандарты / завышенные требования",   domain: "СбП",   questions: [13, 31, 49, 67, 85]},
  {code: "ПГ",   name: "Привилегированность / грандиозность",         domain: "НГ",    questions: [14, 32, 50, 68, 86]},
  {code: "НС",   name: "Недостаток самоконтроля / самодисциплины",    domain: "НГ",    questions: [15, 33, 51, 69, 87]},
  {code: "ПО",   name: "Поиск одобрения",                              domain: "НД",    questions: [16, 34, 52, 70, 88]},
  {code: "НП",   name: "Негативизм / пессимизм",                      domain: "СбП",   questions: [17, 35, 53, 71, 89]},
  {code: "ПК",   name: "Пунитивность / карательность",                domain: "СбП",   questions: [18, 36, 54, 72, 90]},
];

const YSQ_DOMAINS = {
  "РСО":   {name: "Разобщенность и отвержение",                                    schemas: ["ЭД", "ПН", "НН", "СИО", "ДС"]},
  "НЛАНД": {name: "Нарушение личностной автономии и непризнание достижений",       schemas: ["НО", "ЗН", "У", "СДНЯ"]},
  "НГ":    {name: "Нарушенные границы",                                             schemas: ["ПГ", "НС"]},
  "НД":    {name: "Направленность на других",                                       schemas: ["ПП", "С", "ПО"]},
  "СбП":   {name: "Сверхбдительность и подавление",                                 schemas: ["ПЭ", "ЖС", "НП", "ПК"]},
};

function scoreSchema(answers, questionNumbers) {
  const scores = questionNumbers.map(q => answers[q]);
  const total = scores.reduce((a, b) => a + b, 0);
  const mean = total / scores.length;
  const pct = (total - 5) / 25 * 100;
  const highCount = scores.filter(s => s >= 5).length;

  let level;
  if (pct <= 20) level = "низкий";
  else if (pct <= 40) level = "пониженный";
  else if (pct <= 60) level = "умеренный";
  else if (pct <= 80) level = "повышенный";
  else level = "высокий";

  return {total, mean, pct, level, highCount, scores};
}

function scoreAllSchemas(answers) {
  const results = {};
  for (const schema of YSQ_SCHEMAS) {
    results[schema.code] = scoreSchema(answers, schema.questions);
    results[schema.code].name = schema.name;
    results[schema.code].domain = schema.domain;
  }
  return results;
}

function scoreDomains(schemaResults) {
  const domains = {};
  for (const [code, domain] of Object.entries(YSQ_DOMAINS)) {
    const schemaScores = domain.schemas.map(s => schemaResults[s]);
    const mean = schemaScores.reduce((a, b) => a + b.mean, 0) / schemaScores.length;
    const highCount = schemaScores.reduce((a, b) => a + b.highCount, 0);
    domains[code] = {name: domain.name, mean, highCount, schemas: domain.schemas};
  }
  return domains;
}
