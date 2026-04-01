import sys

sys.stdout.reconfigure(encoding="utf-8")

answers = {
    1: 4,
    2: 4,
    3: 3,
    4: 2,
    5: 1,
    6: 2,
    7: 3,
    8: 4,
    9: 3,
    10: 2,
    11: 3,
    12: 3,
    13: 3,
    14: 3,
    15: 2,
    16: 2,
    17: 3,
    18: 4,
    19: 4,
    20: 5,
    21: 4,
    22: 3,
    23: 5,
    24: 3,
    25: 1,
    26: 3,
    27: 1,
    28: 2,
    29: 5,
    30: 2,
    31: 2,
    32: 3,
    33: 2,
    34: 3,
    35: 3,
    36: 3,
    37: 2,
    38: 5,
    39: 3,
    40: 2,
    41: 5,
    42: 4,
    43: 2,
    44: 2,
    45: 4,
    46: 3,
    47: 3,
    48: 4,
    49: 3,
    50: 3,
    51: 5,
    52: 4,
    53: 4,
    54: 1,
    55: 4,
    56: 3,
    57: 3,
    58: 2,
    59: 2,
    60: 1,
    61: 2,
    62: 4,
    63: 3,
    64: 4,
    65: 3,
    66: 3,
    67: 2,
    68: 4,
    69: 2,
    70: 3,
    71: 3,
    72: 1,
    73: 4,
    74: 3,
    75: 2,
    76: 4,
    77: 4,
    78: 1,
    79: 3,
    80: 6,
    81: 4,
    82: 4,
    83: 4,
    84: 2,
    85: 6,
    86: 4,
    87: 3,
    88: 4,
    89: 3,
    90: 5,
    91: 5,
    92: 1,
    93: 3,
    94: 1,
    95: 4,
    96: 3,
    97: 3,
    98: 1,
    99: 2,
    100: 4,
    101: 3,
    102: 2,
    103: 1,
    104: 3,
    105: 3,
    106: 2,
    107: 4,
    108: 3,
    109: 4,
    110: 4,
    111: 3,
    112: 1,
    113: 4,
    114: 3,
    115: 5,
    116: 4,
    117: 4,
    118: 2,
    119: 2,
    120: 5,
    121: 4,
    122: 3,
    123: 1,
    124: 5,
}

# SMI v1.1 mode mapping from the results sheet
# Mode code -> list of question numbers
# Read from the Excel results sheet earlier:
# Item, Response, Mode Code
mode_items = {
    1: "BA",
    2: "CC",
    3: "PP",
    4: "VC",
    5: "PP",
    6: "VC",
    7: "DPa",
    8: "CS",
    9: "PP",
    10: "SA",
    11: "SA",
    12: "IC",
    13: "UC",
    14: "EC",
    15: "IC",
    16: "PP",
    17: "CC",
    18: "CS",
    19: "CC",
    20: "HA",
    21: "UC",
    22: "AC",
    23: "DPa",
    24: "BA",
    25: "EC",
    26: "EC",
    27: "SA",
    28: "DP",
    29: "DPa",
    30: "VC",
    31: "IC",
    32: "DS",
    33: "BA",
    34: "UC",
    35: "DP",
    36: "PP",
    37: "VC",
    38: "DPa",
    39: "CS",
    40: "AC",
    41: "DPa",
    42: "CS",
    43: "EC",
    44: "CC",
    45: "HA",
    46: "SA",
    47: "IC",
    48: "DS",
    49: "UC",
    50: "DP",
    51: "DPa",
    52: "PP",
    53: "BA",
    54: "VC",
    55: "HA",
    56: "AC",
    57: "DS",
    58: "CC",
    59: "IC",
    60: "EC",
    61: "UC",
    62: "CS",
    63: "DP",
    64: "SA",
    65: "AC",
    66: "DS",
    67: "VC",
    68: "HA",
    69: "BA",
    70: "PP",
    71: "CC",
    72: "AC",
    73: "DPa",
    74: "IC",
    75: "DP",
    76: "CS",
    77: "DS",
    78: "EC",
    79: "UC",
    80: "DPa",
    81: "BA",
    82: "SA",
    83: "HA",
    84: "VC",
    85: "DPa",
    86: "CC",
    87: "AC",
    88: "CS",
    89: "DP",
    90: "DPa",
    91: "DS",
    92: "EC",
    93: "IC",
    94: "VC",
    95: "HA",
    96: "UC",
    97: "BA",
    98: "AC",
    99: "CC",
    100: "DP",
    101: "DS",
    102: "IC",
    103: "EC",
    104: "SA",
    105: "CS",
    106: "VC",
    107: "HA",
    108: "PP",
    109: "CC",
    110: "BA",
    111: "UC",
    112: "AC",
    113: "DP",
    114: "SA",
    115: "DPa",
    116: "HA",
    117: "DS",
    118: "IC",
    119: "VC",
    120: "DPa",
    121: "CS",
    122: "CC",
    123: "EC",
    124: "HA",
}

# Group items by mode
modes = {}
for item, code in mode_items.items():
    modes.setdefault(code, []).append(item)

# Mode definitions with Russian names and norms
# Norms from the results sheet: Low, Reduced, Moderate, Elevated, High cutoffs
mode_info = {
    "VC": {
        "ru": "Уязвимый ребенок",
        "cat": "Детские режимы",
        "norms": [1.0, 1.47, 1.98, 3.36, 4.47],
        "reverse": False,
    },
    "AC": {
        "ru": "Рассерженный ребенок",
        "cat": "Детские режимы",
        "norms": [1.0, 1.81, 2.29, 3.09, 4.03],
        "reverse": False,
    },
    "EC": {
        "ru": "Яростный ребенок",
        "cat": "Детские режимы",
        "norms": [1.0, 1.20, 1.49, 2.05, 2.97],
        "reverse": False,
    },
    "IC": {
        "ru": "Импульсивный ребенок",
        "cat": "Детские режимы",
        "norms": [1.0, 2.15, 2.68, 3.05, 4.12],
        "reverse": False,
    },
    "UC": {
        "ru": "Недисциплинированный ребенок",
        "cat": "Детские режимы",
        "norms": [1.0, 2.27, 2.87, 3.47, 3.89],
        "reverse": False,
    },
    "CC": {
        "ru": "Счастливый ребенок",
        "cat": "Детские режимы",
        "norms": [6.0, 5.06, 4.52, 2.88, 2.11],
        "reverse": True,
    },
    "CS": {
        "ru": "Покорный капитулянт",
        "cat": "Избегающие режимы",
        "norms": [1.0, 2.51, 3.07, 3.63, 4.27],
        "reverse": False,
    },
    "DP": {
        "ru": "Отстраняющийся защитник",
        "cat": "Избегающие режимы",
        "norms": [1.0, 1.59, 2.11, 2.95, 3.89],
        "reverse": False,
    },
    "DS": {
        "ru": "Отстраненное самоуспокоение",
        "cat": "Избегающие режимы",
        "norms": [1.0, 1.93, 2.58, 3.32, 4.30],
        "reverse": False,
    },
    "SA": {
        "ru": "Самовозвеличение",
        "cat": "Режимы гиперкомпенсации",
        "norms": [1.0, 2.31, 2.90, 3.49, 4.08],
        "reverse": False,
    },
    "BA": {
        "ru": "Угрозы и нападение",
        "cat": "Режимы гиперкомпенсации",
        "norms": [1.0, 1.72, 2.23, 2.74, 3.25],
        "reverse": False,
    },
    "PP": {
        "ru": "Карающий родитель",
        "cat": "Родительские режимы",
        "norms": [1.0, 1.47, 1.86, 2.75, 3.72],
        "reverse": False,
    },
    "DPa": {
        "ru": "Требовательный родитель",
        "cat": "Родительские режимы",
        "norms": [1.0, 3.06, 3.66, 4.26, 4.86],
        "reverse": False,
    },
    "HA": {
        "ru": "Здоровый взрослый",
        "cat": "Режимы здорового взрослого",
        "norms": [6.0, 5.16, 4.60, 3.60, 2.77],
        "reverse": True,
    },
}


def get_level(score, norms, reverse):
    """Determine level based on normative cutoffs."""
    if reverse:
        # For reverse scales (CC, HA): high score = healthy = low level
        if score >= norms[0]:
            return "низкий"
        elif score >= norms[1]:
            return "пониженный"
        elif score >= norms[2]:
            return "умеренный"
        elif score >= norms[3]:
            return "повышенный"
        elif score >= norms[4]:
            return "высокий"
        else:
            return "оч. высокий"
    else:
        if score <= norms[0]:
            return "низкий"
        elif score <= norms[1]:
            return "пониженный"
        elif score <= norms[2]:
            return "умеренный"
        elif score <= norms[3]:
            return "повышенный"
        elif score <= norms[4]:
            return "высокий"
        else:
            return "оч. высокий"


print("=" * 85)
print("SMI v1.1 RESULTS")
print("=" * 85)

results = {}
for code, items in sorted(modes.items(), key=lambda x: x[0]):
    scores = [answers[i] for i in items]
    mean = sum(scores) / len(scores)
    info = mode_info[code]
    level = get_level(mean, info["norms"], info["reverse"])
    high_count = sum(1 for s in scores if s >= 5)
    results[code] = {
        "ru": info["ru"],
        "cat": info["cat"],
        "mean": mean,
        "level": level,
        "items": items,
        "scores": scores,
        "count": len(items),
        "high_count": high_count,
        "reverse": info["reverse"],
    }

# Print by category
current_cat = None
for code in [
    "VC",
    "AC",
    "EC",
    "IC",
    "UC",
    "CC",
    "CS",
    "DP",
    "DS",
    "SA",
    "BA",
    "PP",
    "DPa",
    "HA",
]:
    r = results[code]
    if r["cat"] != current_cat:
        current_cat = r["cat"]
        print(f"\n  {current_cat}")
        print(f"  {'─' * 80}")

    bar_len = int(r["mean"])
    bar = "█" * bar_len + "░" * (6 - bar_len)
    reverse_mark = " (обр.)" if r["reverse"] else ""
    print(
        f"  {code:4s} {r['ru'][:45]:45s} {r['mean']:.2f}  {bar}  {r['level']}{reverse_mark}"
    )
    print(
        f"       ({r['count']} items) Scores: {r['scores']}  High(5-6): {r['high_count']}"
    )

# Summary: sorted by clinical significance
print(f"\n{'=' * 85}")
print("SORTED BY CLINICAL SIGNIFICANCE (highest concern first)")
print(f"{'=' * 85}")


# For reverse-scored modes, invert the ranking
def clinical_score(code, r):
    if r["reverse"]:
        return 7 - r["mean"]  # invert: low CC/HA score = high concern
    return r["mean"]


sorted_modes = sorted(
    results.items(), key=lambda x: clinical_score(x[0], x[1]), reverse=True
)
for code, r in sorted_modes:
    marker = (
        " *** "
        if (not r["reverse"] and r["mean"] >= 3.5)
        or (r["reverse"] and r["mean"] <= 3.5)
        else "     "
    )
    display_note = " (low = concern)" if r["reverse"] else ""
    print(
        f"{marker}{code:4s} {r['ru'][:45]:45s} {r['mean']:.2f}  ({r['level']}){display_note}"
    )

# Write to Excel
# xlrd can't write .xls, so we just report. The .xls format is read-only in openpyxl too.
# We'll note that scores need manual entry or we convert.
print(f"\n{'=' * 85}")
print("NOTE: SMI file is .xls format (old Excel). Scores displayed above.")
print("The .xls file cannot be written by openpyxl. Results saved to results.json.")
print(f"{'=' * 85}")
