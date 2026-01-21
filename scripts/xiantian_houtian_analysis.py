#!/usr/bin/env python3
"""
先天八卦 vs 後天八卦 分析

先天八卦（伏羲）= 宇宙本體秩序
- 二進制自然順序
- 對立配對（乾↔坤）
- 代表「事物的本質」

後天八卦（文王）= 人事變化秩序
- 羅盤方位順序
- 代表「事物的變化」

關鍵問題：兩者的轉換關係是否影響吉凶？
"""

from collections import defaultdict

# ============================================================
# 先天八卦序（Fu Xi / Binary Order）
# ============================================================

# 先天八卦順序（按二進制值）
XIANTIAN_TRIGRAMS = {
    0: {"binary": "000", "name": "坤", "symbol": "地", "position": "北"},
    1: {"binary": "001", "name": "震", "symbol": "雷", "position": "東北"},
    2: {"binary": "010", "name": "坎", "symbol": "水", "position": "西"},
    3: {"binary": "011", "name": "兌", "symbol": "澤", "position": "東南"},
    4: {"binary": "100", "name": "艮", "symbol": "山", "position": "西北"},
    5: {"binary": "101", "name": "離", "symbol": "火", "position": "東"},
    6: {"binary": "110", "name": "巽", "symbol": "風", "position": "西南"},
    7: {"binary": "111", "name": "乾", "symbol": "天", "position": "南"},
}

# 先天八卦的對立關係（二進制互補）
XIANTIAN_OPPOSITES = {
    "000": "111",  # 坤↔乾
    "001": "110",  # 震↔巽
    "010": "101",  # 坎↔離
    "011": "100",  # 兌↔艮
    "100": "011",  # 艮↔兌
    "101": "010",  # 離↔坎
    "110": "001",  # 巽↔震
    "111": "000",  # 乾↔坤
}

# ============================================================
# 後天八卦序（King Wen / Compass Order）
# ============================================================

# 後天八卦順序（羅盤方位，順時針）
HOUTIAN_ORDER = [
    {"binary": "101", "name": "離", "direction": "南", "number": 9},
    {"binary": "000", "name": "坤", "direction": "西南", "number": 2},
    {"binary": "011", "name": "兌", "direction": "西", "number": 7},
    {"binary": "111", "name": "乾", "direction": "西北", "number": 6},
    {"binary": "010", "name": "坎", "direction": "北", "number": 1},
    {"binary": "100", "name": "艮", "direction": "東北", "number": 8},
    {"binary": "001", "name": "震", "direction": "東", "number": 3},
    {"binary": "110", "name": "巽", "direction": "東南", "number": 4},
]

# 先天數 vs 後天數的對應
XIANTIAN_NUMBER = {"000": 2, "001": 4, "010": 6, "011": 7, "100": 8, "101": 3, "110": 5, "111": 1}
HOUTIAN_NUMBER = {"000": 2, "001": 3, "010": 1, "011": 7, "100": 8, "101": 9, "110": 4, "111": 6}

# 我們的樣本
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

TRIGRAM_NAME = {
    "000": "坤", "001": "震", "010": "坎", "011": "兌",
    "100": "艮", "101": "離", "110": "巽", "111": "乾",
}

def get_upper_lower(binary):
    return binary[0:3], binary[3:6]

print("=" * 70)
print("先天八卦 vs 後天八卦 分析")
print("=" * 70)
print()

# ============================================================
# 1. 兩種序列對比
# ============================================================

print("1. 八卦在兩種系統中的位置對比")
print("-" * 70)
print()
print("八卦 | 先天數 | 先天位 | 後天數 | 後天位 | 差值")
print("-" * 55)

for binary, xt_num in XIANTIAN_NUMBER.items():
    ht_num = HOUTIAN_NUMBER[binary]
    name = TRIGRAM_NAME[binary]
    diff = ht_num - xt_num
    xt_info = XIANTIAN_TRIGRAMS[xt_num - 1 if xt_num <= 8 else 0]
    ht_info = next((h for h in HOUTIAN_ORDER if h["binary"] == binary), {})

    print(f" {name}  |   {xt_num}    | {xt_info.get('position', '?'):4} |   {ht_num}    | "
          f"{ht_info.get('direction', '?'):4} | {diff:+d}")

# ============================================================
# 2. 先天數之和與吉凶
# ============================================================

print()
print("=" * 70)
print("2. 先天數之和與吉凶的關係")
print("=" * 70)
print()

# 計算每卦的先天數之和
xiantian_sum_stats = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    upper, lower = get_upper_lower(binary)
    upper_xt = XIANTIAN_NUMBER[upper]
    lower_xt = XIANTIAN_NUMBER[lower]
    xt_sum = upper_xt + lower_xt

    if actual == 1:
        xiantian_sum_stats[xt_sum]["ji"] += 1
    elif actual == 0:
        xiantian_sum_stats[xt_sum]["zhong"] += 1
    else:
        xiantian_sum_stats[xt_sum]["xiong"] += 1

print("先天數之和 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 50)
for sum_val in sorted(xiantian_sum_stats.keys()):
    s = xiantian_sum_stats[sum_val]
    total = s["ji"] + s["zhong"] + s["xiong"]
    ji_rate = s["ji"] / total * 100 if total else 0
    xiong_rate = s["xiong"] / total * 100 if total else 0
    print(f"    {sum_val:2}      | {s['ji']:2} | {s['zhong']:2} | {s['xiong']:2} | "
          f"{ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 3. 後天數之和與吉凶
# ============================================================

print()
print("=" * 70)
print("3. 後天數之和與吉凶的關係")
print("=" * 70)
print()

houtian_sum_stats = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    upper, lower = get_upper_lower(binary)
    upper_ht = HOUTIAN_NUMBER[upper]
    lower_ht = HOUTIAN_NUMBER[lower]
    ht_sum = upper_ht + lower_ht

    if actual == 1:
        houtian_sum_stats[ht_sum]["ji"] += 1
    elif actual == 0:
        houtian_sum_stats[ht_sum]["zhong"] += 1
    else:
        houtian_sum_stats[ht_sum]["xiong"] += 1

print("後天數之和 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 50)
for sum_val in sorted(houtian_sum_stats.keys()):
    s = houtian_sum_stats[sum_val]
    total = s["ji"] + s["zhong"] + s["xiong"]
    ji_rate = s["ji"] / total * 100 if total else 0
    xiong_rate = s["xiong"] / total * 100 if total else 0
    print(f"    {sum_val:2}      | {s['ji']:2} | {s['zhong']:2} | {s['xiong']:2} | "
          f"{ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 4. 先天-後天轉換差異與吉凶
# ============================================================

print()
print("=" * 70)
print("4. 先天→後天的轉換差異")
print("=" * 70)
print()
print("轉換差異 = |後天數 - 先天數|")
print("這代表八卦從「本體」到「變化」的偏移程度")
print()

transform_stats = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    upper, lower = get_upper_lower(binary)

    upper_diff = abs(HOUTIAN_NUMBER[upper] - XIANTIAN_NUMBER[upper])
    lower_diff = abs(HOUTIAN_NUMBER[lower] - XIANTIAN_NUMBER[lower])
    total_diff = upper_diff + lower_diff

    if actual == 1:
        transform_stats[total_diff]["ji"] += 1
    elif actual == 0:
        transform_stats[total_diff]["zhong"] += 1
    else:
        transform_stats[total_diff]["xiong"] += 1

print("轉換差異 | 吉 | 中 | 凶 | 吉率 | 凶率 | 意義")
print("-" * 65)
for diff in sorted(transform_stats.keys()):
    s = transform_stats[diff]
    total = s["ji"] + s["zhong"] + s["xiong"]
    ji_rate = s["ji"] / total * 100 if total else 0
    xiong_rate = s["xiong"] / total * 100 if total else 0
    meaning = "穩定" if diff <= 4 else ("變動" if diff <= 8 else "劇變")
    print(f"   {diff:2}     | {s['ji']:2} | {s['zhong']:2} | {s['xiong']:2} | "
          f"{ji_rate:4.0f}% | {xiong_rate:4.0f}% | {meaning}")

# ============================================================
# 5. 對立卦分析（先天互補）
# ============================================================

print()
print("=" * 70)
print("5. 先天對立卦（二進制互補）分析")
print("=" * 70)
print()

# 計算是否上下卦互為對立
opposite_stats = {"opposite": {"ji": 0, "zhong": 0, "xiong": 0},
                  "same": {"ji": 0, "zhong": 0, "xiong": 0},
                  "other": {"ji": 0, "zhong": 0, "xiong": 0}}

for hex_num, pos, binary, actual in SAMPLES:
    upper, lower = get_upper_lower(binary)

    if XIANTIAN_OPPOSITES[upper] == lower:
        key = "opposite"
    elif upper == lower:
        key = "same"
    else:
        key = "other"

    if actual == 1:
        opposite_stats[key]["ji"] += 1
    elif actual == 0:
        opposite_stats[key]["zhong"] += 1
    else:
        opposite_stats[key]["xiong"] += 1

print("上下卦關係 | 吉 | 中 | 凶 | 吉率 | 凶率 | 說明")
print("-" * 70)
for relation in ["opposite", "same", "other"]:
    s = opposite_stats[relation]
    total = s["ji"] + s["zhong"] + s["xiong"]
    ji_rate = s["ji"] / total * 100 if total else 0
    xiong_rate = s["xiong"] / total * 100 if total else 0
    desc = {
        "opposite": "對立（如乾/坤）",
        "same": "同卦（如乾/乾）",
        "other": "其他組合",
    }
    print(f"  {relation:8} | {s['ji']:2} | {s['zhong']:2} | {s['xiong']:2} | "
          f"{ji_rate:4.0f}% | {xiong_rate:4.0f}% | {desc[relation]}")

# ============================================================
# 6. 河圖洛書數分析
# ============================================================

print()
print("=" * 70)
print("6. 河圖洛書數與吉凶")
print("=" * 70)
print()
print("河圖：1-6水，2-7火，3-8木，4-9金，5-10土")
print("洛書：載九履一，左三右七，二四為肩，六八為足")
print()

# 五行對應
WUXING = {
    1: "水", 6: "水",
    2: "火", 7: "火",
    3: "木", 8: "木",
    4: "金", 9: "金",
    5: "土", 0: "土", 10: "土",
}

# 計算後天數的五行
wuxing_stats = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    upper, lower = get_upper_lower(binary)
    upper_ht = HOUTIAN_NUMBER[upper]
    lower_ht = HOUTIAN_NUMBER[lower]

    upper_wx = WUXING.get(upper_ht, "?")
    lower_wx = WUXING.get(lower_ht, "?")

    key = f"{upper_wx}/{lower_wx}"

    if actual == 1:
        wuxing_stats[key]["ji"] += 1
    elif actual == 0:
        wuxing_stats[key]["zhong"] += 1
    else:
        wuxing_stats[key]["xiong"] += 1

print("五行組合 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 50)
for key in sorted(wuxing_stats.keys()):
    s = wuxing_stats[key]
    total = s["ji"] + s["zhong"] + s["xiong"]
    if total > 0:
        ji_rate = s["ji"] / total * 100
        xiong_rate = s["xiong"] / total * 100
        print(f"  {key:8} | {s['ji']:2} | {s['zhong']:2} | {s['xiong']:2} | "
              f"{ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 結論
# ============================================================

print()
print("=" * 70)
print("先天後天分析結論")
print("=" * 70)
print("""
關鍵發現：

1. 先天八卦 = 本體秩序（二進制自然）
   - 對立配對（乾↔坤，離↔坎）
   - 代表事物的本質結構

2. 後天八卦 = 變化秩序（羅盤方位）
   - 代表事物的變化發展
   - 與人事、時令相關

3. 轉換差異的意義
   - 差異小 = 本體與變化一致 = 穩定
   - 差異大 = 本體與變化不一致 = 變動

4. 這可能解釋：
   - 為何某些結構「應該吉」卻凶
   - 本體結構好，但在變化序列中位置不佳

下一步：
- 將先天後天數差作為新特徵
- 測試是否提升預測準確率
""")
