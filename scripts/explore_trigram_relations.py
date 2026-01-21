#!/usr/bin/env python3
"""
探索八卦之間的深層關係

目標：找出八卦組合與吉凶的隱藏規律
"""

from collections import defaultdict

SAMPLES = [
    (1, 1, "111111", 0), (1, 2, "111111", 1), (1, 3, "111111", 0),
    (1, 4, "111111", 0), (1, 5, "111111", 1), (1, 6, "111111", -1),
    (2, 1, "000000", -1), (2, 2, "000000", 1), (2, 3, "000000", 0),
    (2, 4, "000000", 0), (2, 5, "000000", 1), (2, 6, "000000", -1),
    (3, 1, "010001", 0), (3, 2, "010001", 0), (3, 3, "010001", -1),
    (3, 4, "010001", 1), (3, 5, "010001", 0), (3, 6, "010001", -1),
    (4, 1, "100010", 0), (4, 2, "100010", 1), (4, 3, "100010", -1),
    (4, 4, "100010", -1), (4, 5, "100010", 1), (4, 6, "100010", 0),
    (5, 1, "010111", 0), (5, 2, "010111", 0), (5, 3, "010111", -1),
    (5, 4, "010111", -1), (5, 5, "010111", 1), (5, 6, "010111", 0),
    (6, 1, "111010", 0), (6, 2, "111010", 0), (6, 3, "111010", 0),
    (6, 4, "111010", 0), (6, 5, "111010", 1), (6, 6, "111010", -1),
    (15, 1, "000100", 1), (15, 2, "000100", 1), (15, 3, "000100", 1),
    (15, 4, "000100", 1), (15, 5, "000100", 0), (15, 6, "000100", 0),
    (17, 1, "011001", 0), (17, 2, "011001", -1), (17, 3, "011001", 0),
    (17, 4, "011001", 0), (17, 5, "011001", 1), (17, 6, "011001", 0),
    (20, 1, "110000", 0), (20, 2, "110000", 0), (20, 3, "110000", 0),
    (20, 4, "110000", 0), (20, 5, "110000", 0), (20, 6, "110000", 0),
    (24, 1, "000001", 1), (24, 2, "000001", 1), (24, 3, "000001", 0),
    (24, 4, "000001", 0), (24, 5, "000001", 0), (24, 6, "000001", -1),
    (25, 1, "111001", 1), (25, 2, "111001", 1), (25, 3, "111001", -1),
    (25, 4, "111001", 0), (25, 5, "111001", 0), (25, 6, "111001", -1),
    (33, 1, "111100", -1), (33, 2, "111100", 1), (33, 3, "111100", 0),
    (33, 4, "111100", 0), (33, 5, "111100", 1), (33, 6, "111100", 1),
    (47, 1, "011010", -1), (47, 2, "011010", 0), (47, 3, "011010", -1),
    (47, 4, "011010", 0), (47, 5, "011010", 0), (47, 6, "011010", 0),
    (50, 1, "101110", 0), (50, 2, "101110", 0), (50, 3, "101110", 0),
    (50, 4, "101110", -1), (50, 5, "101110", 1), (50, 6, "101110", 1),
    (63, 1, "010101", 1), (63, 2, "010101", 0), (63, 3, "010101", 0),
    (63, 4, "010101", 0), (63, 5, "010101", 0), (63, 6, "010101", -1),
]

# 八卦抽象概念
TRIGRAMS = {
    "111": {"name": "乾", "象": "天", "德": "健", "動靜": "動", "方向": "上"},
    "000": {"name": "坤", "象": "地", "德": "順", "動靜": "靜", "方向": "下"},
    "001": {"name": "震", "象": "雷", "德": "動", "動靜": "動", "方向": "起"},
    "010": {"name": "坎", "象": "水", "德": "險", "動靜": "陷", "方向": "下"},
    "011": {"name": "兌", "象": "澤", "德": "悅", "動靜": "靜", "方向": "下"},
    "100": {"name": "艮", "象": "山", "德": "止", "動靜": "止", "方向": "止"},
    "101": {"name": "離", "象": "火", "德": "麗", "動靜": "動", "方向": "上"},
    "110": {"name": "巽", "象": "風", "德": "入", "動靜": "入", "方向": "入"},
}

def get_trigram(binary, which):
    if which == "lower":
        return binary[3:6]
    else:
        return binary[0:3]

# ============================================================
# 分析1：動靜關係
# ============================================================

print("=" * 70)
print("分析1：動靜關係")
print("=" * 70)
print()

dong_jing = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    lower = get_trigram(binary, "lower")
    upper = get_trigram(binary, "upper")

    lower_dj = TRIGRAMS[lower]["動靜"]
    upper_dj = TRIGRAMS[upper]["動靜"]

    key = f"{lower_dj}/{upper_dj}"

    if actual == 1:
        dong_jing[key]["ji"] += 1
    elif actual == 0:
        dong_jing[key]["zhong"] += 1
    else:
        dong_jing[key]["xiong"] += 1

print("動靜組合 | 吉 | 中 | 凶 | 吉率")
print("-" * 50)
for key, r in sorted(dong_jing.items(), key=lambda x: x[1]["ji"]/(x[1]["ji"]+x[1]["zhong"]+x[1]["xiong"]+0.001), reverse=True):
    total = r["ji"] + r["zhong"] + r["xiong"]
    ji_rate = r["ji"] / total * 100 if total else 0
    print(f"{key:10} | {r['ji']:2} | {r['zhong']:2} | {r['xiong']:2} | {ji_rate:.0f}%")

# ============================================================
# 分析2：方向關係
# ============================================================

print()
print("=" * 70)
print("分析2：方向關係")
print("=" * 70)
print()

direction = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    lower = get_trigram(binary, "lower")
    upper = get_trigram(binary, "upper")

    lower_dir = TRIGRAMS[lower]["方向"]
    upper_dir = TRIGRAMS[upper]["方向"]

    key = f"{lower_dir}/{upper_dir}"

    if actual == 1:
        direction[key]["ji"] += 1
    elif actual == 0:
        direction[key]["zhong"] += 1
    else:
        direction[key]["xiong"] += 1

print("方向組合 | 吉 | 中 | 凶 | 吉率")
print("-" * 50)
for key, r in sorted(direction.items(), key=lambda x: x[1]["ji"]/(x[1]["ji"]+x[1]["zhong"]+x[1]["xiong"]+0.001), reverse=True):
    total = r["ji"] + r["zhong"] + r["xiong"]
    ji_rate = r["ji"] / total * 100 if total else 0
    print(f"{key:10} | {r['ji']:2} | {r['zhong']:2} | {r['xiong']:2} | {ji_rate:.0f}%")

# ============================================================
# 分析3：德性關係
# ============================================================

print()
print("=" * 70)
print("分析3：德性關係")
print("=" * 70)
print()

virtue = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    lower = get_trigram(binary, "lower")
    upper = get_trigram(binary, "upper")

    lower_de = TRIGRAMS[lower]["德"]
    upper_de = TRIGRAMS[upper]["德"]

    key = f"{lower_de}/{upper_de}"

    if actual == 1:
        virtue[key]["ji"] += 1
    elif actual == 0:
        virtue[key]["zhong"] += 1
    else:
        virtue[key]["xiong"] += 1

print("德性組合 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 55)
for key, r in sorted(virtue.items(), key=lambda x: x[1]["ji"]/(x[1]["ji"]+x[1]["zhong"]+x[1]["xiong"]+0.001), reverse=True):
    total = r["ji"] + r["zhong"] + r["xiong"]
    ji_rate = r["ji"] / total * 100 if total else 0
    xiong_rate = r["xiong"] / total * 100 if total else 0
    print(f"{key:10} | {r['ji']:2} | {r['zhong']:2} | {r['xiong']:2} | {ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 分析4：特定八卦的影響
# ============================================================

print()
print("=" * 70)
print("分析4：各八卦出現時的吉凶")
print("=" * 70)
print()

# 分析每個八卦作為上卦或下卦時的影響
for trigram_binary, info in TRIGRAMS.items():
    name = info["name"]

    # 作為下卦
    lower_samples = [(h, p, b, a) for h, p, b, a in SAMPLES if get_trigram(b, "lower") == trigram_binary]
    lower_ji = sum(1 for s in lower_samples if s[3] == 1)
    lower_xiong = sum(1 for s in lower_samples if s[3] == -1)
    lower_total = len(lower_samples)

    # 作為上卦
    upper_samples = [(h, p, b, a) for h, p, b, a in SAMPLES if get_trigram(b, "upper") == trigram_binary]
    upper_ji = sum(1 for s in upper_samples if s[3] == 1)
    upper_xiong = sum(1 for s in upper_samples if s[3] == -1)
    upper_total = len(upper_samples)

    if lower_total > 0 or upper_total > 0:
        lower_ji_rate = lower_ji / lower_total * 100 if lower_total else 0
        upper_ji_rate = upper_ji / upper_total * 100 if upper_total else 0
        print(f"{name}({info['象']}): 下卦吉率={lower_ji_rate:.0f}% 上卦吉率={upper_ji_rate:.0f}%")

# ============================================================
# 分析5：爻位與八卦的交互
# ============================================================

print()
print("=" * 70)
print("分析5：爻位×所在八卦")
print("=" * 70)
print()

# 爻在特定八卦中的表現
for pos in [2, 5]:  # 中位
    print(f"\n爻{pos}（得中）在各八卦中的表現：")
    for trigram_binary, info in TRIGRAMS.items():
        name = info["name"]

        if pos <= 3:
            # 在下卦
            samples = [(h, p, b, a) for h, p, b, a in SAMPLES
                       if p == pos and get_trigram(b, "lower") == trigram_binary]
        else:
            # 在上卦
            samples = [(h, p, b, a) for h, p, b, a in SAMPLES
                       if p == pos and get_trigram(b, "upper") == trigram_binary]

        if samples:
            ji = sum(1 for s in samples if s[3] == 1)
            xiong = sum(1 for s in samples if s[3] == -1)
            total = len(samples)
            print(f"  {name}: 吉={ji} 凶={xiong} (共{total})")

# ============================================================
# 核心發現
# ============================================================

print()
print("=" * 70)
print("核心發現")
print("=" * 70)
print("""
待分析：
1. 哪些動靜組合最有利？
2. 哪些德性搭配最和諧？
3. 特定八卦對吉凶的影響

這些都是可以從數據中發現的結構規律。
""")
