// SMI v1.1 Scoring Module
// Item lists extracted from Excel formula cell references (source of truth).
// 15 items are shared across 2 modes — this is by design in the SMI.

const SMI_MODE_ORDER = ["VC","AC","EC","IC","UC","CC","CS","DP","DS","SA","BA","PP","DPa","HA"];

const SMI_MODES = {
  "VC":  {ru: "Уязвимый ребенок",              cat: "Детские режимы",            norms: [1.0, 1.47, 1.98, 3.36, 4.47], reverse: false, items: [4, 6, 36, 50, 67, 71, 105, 106, 111, 119]},
  "AC":  {ru: "Рассерженный ребенок",           cat: "Детские режимы",            norms: [1.0, 1.81, 2.29, 3.09, 4.03], reverse: false, items: [22, 42, 47, 49, 56, 63, 76, 79, 103, 109]},
  "EC":  {ru: "Яростный ребенок",               cat: "Детские режимы",            norms: [1.0, 1.20, 1.49, 2.05, 2.97], reverse: false, items: [14, 25, 26, 46, 54, 60, 92, 98, 101, 123]},
  "IC":  {ru: "Импульсивный ребенок",           cat: "Детские режимы",            norms: [1.0, 2.15, 2.68, 3.05, 4.12], reverse: false, items: [12, 15, 35, 40, 66, 69, 78, 97, 110]},
  "UC":  {ru: "Недисциплинированный ребенок",   cat: "Детские режимы",            norms: [1.0, 2.27, 2.87, 3.47, 3.89], reverse: false, items: [10, 18, 27, 62, 67, 104]},
  "CC":  {ru: "Счастливый ребенок",             cat: "Детские режимы",            norms: [6.0, 5.06, 4.52, 2.88, 2.11], reverse: true,  items: [2, 17, 19, 48, 61, 68, 95, 96, 113, 122]},
  "CS":  {ru: "Покорный капитулянт",            cat: "Избегающие режимы",         norms: [1.0, 2.51, 3.07, 3.63, 4.27], reverse: false, items: [5, 15, 34, 35, 52, 97, 105]},
  "DP":  {ru: "Отстраняющийся защитник",        cat: "Избегающие режимы",         norms: [1.0, 1.59, 2.11, 2.95, 3.89], reverse: false, items: [28, 33, 34, 39, 43, 59, 64, 75, 88]},
  "DS":  {ru: "Отстраненное самоуспокоение",    cat: "Избегающие режимы",         norms: [1.0, 1.93, 2.58, 3.32, 4.30], reverse: false, items: [38, 49, 54, 83]},
  "SA":  {ru: "Самовозвеличение",               cat: "Режимы гиперкомпенсации",   norms: [1.0, 2.31, 2.90, 3.49, 4.08], reverse: false, items: [10, 11, 27, 31, 44, 74, 81, 89, 91, 114]},
  "BA":  {ru: "Угрозы и нападение",             cat: "Режимы гиперкомпенсации",   norms: [1.0, 1.72, 2.23, 2.74, 3.25], reverse: false, items: [1, 24, 32, 53, 77, 93, 99, 102, 112]},
  "PP":  {ru: "Карающий родитель",               cat: "Родительские режимы",       norms: [1.0, 1.47, 1.86, 2.75, 3.72], reverse: false, items: [3, 5, 9, 16, 58, 72, 84, 87, 94, 118]},
  "DPa": {ru: "Требовательный родитель",         cat: "Родительские режимы",       norms: [1.0, 3.06, 3.66, 4.26, 4.86], reverse: false, items: [7, 23, 44, 51, 82, 83, 90, 104, 115, 116]},
  "HA":  {ru: "Здоровый взрослый",               cat: "Режимы здорового взрослого",norms: [6.0, 5.16, 4.60, 3.60, 2.77], reverse: true,  items: [20, 29, 62, 73, 80, 85, 117, 120, 121, 124]},
};

function scoreMode(answers, items) {
  const scores = items.map(i => answers[i]);
  const total = scores.reduce((a, b) => a + b, 0);
  const mean = total / scores.length;
  const highCount = scores.filter(s => s >= 5).length;
  return {total, mean, highCount, scores};
}

function getSmiLevel(score, norms, reverse) {
  if (reverse) {
    if (score >= norms[0]) return "низкий";
    if (score >= norms[1]) return "пониженный";
    if (score >= norms[2]) return "умеренный";
    if (score >= norms[3]) return "повышенный";
    if (score >= norms[4]) return "высокий";
    return "оч. высокий";
  } else {
    if (score <= norms[0]) return "низкий";
    if (score <= norms[1]) return "пониженный";
    if (score <= norms[2]) return "умеренный";
    if (score <= norms[3]) return "повышенный";
    if (score <= norms[4]) return "высокий";
    return "оч. высокий";
  }
}

function scoreAllModes(answers) {
  const results = {};
  for (const [code, mode] of Object.entries(SMI_MODES)) {
    const r = scoreMode(answers, mode.items);
    r.level = getSmiLevel(r.mean, mode.norms, mode.reverse);
    r.ru = mode.ru;
    r.cat = mode.cat;
    r.reverse = mode.reverse;
    results[code] = r;
  }
  return results;
}

function clinicalScore(mean, reverse) {
  return reverse ? 7 - mean : mean;
}
