#!/usr/bin/env python3
"""
字符-詞語方法 (Character-Word Approach)

核心思想：
1. 八卦 = 字符 (Character) - 8個基本符號
2. 卦 = 詞語 (Word) - 上下兩個字符組成
3. 爻 = 詞中位置 (Position in word)
4. 吉凶 = 詞義 (Word meaning)

這就像：
- 中文字：偏旁 + 偏旁 = 新意義
- 英文：letter + letter = word
- DNA：codon (3 bases) = amino acid

探索：
- 哪些字符組合產生「吉詞」？
- 哪些組合產生「凶詞」？
- 位置如何改變詞義？
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

# ============================================================
# 定義八卦字符系統
# ============================================================

# 用0-7表示八卦，類似hex字符
TRIGRAM_TO_CHAR = {
    "000": "0",  # 坤
    "001": "1",  # 震
    "010": "2",  # 坎
    "011": "3",  # 兌
    "100": "4",  # 艮
    "101": "5",  # 離
    "110": "6",  # 巽
    "111": "7",  # 乾
}

CHAR_TO_NAME = {
    "0": "坤(地)",
    "1": "震(雷)",
    "2": "坎(水)",
    "3": "兌(澤)",
    "4": "艮(山)",
    "5": "離(火)",
    "6": "巽(風)",
    "7": "乾(天)",
}

def binary_to_word(binary):
    """
    將六爻binary轉為「詞」
    格式：上卦字符 + 下卦字符
    """
    upper = binary[0:3]
    lower = binary[3:6]
    return TRIGRAM_TO_CHAR[upper] + TRIGRAM_TO_CHAR[lower]

def get_nuclear_word(binary):
    """互卦的詞"""
    nuc_upper = binary[1:4]
    nuc_lower = binary[2:5]
    return TRIGRAM_TO_CHAR[nuc_upper] + TRIGRAM_TO_CHAR[nuc_lower]

print("=" * 70)
print("字符-詞語方法：八卦 = 字符，卦 = 詞")
print("=" * 70)
print()

# ============================================================
# 建立詞典
# ============================================================

print("八卦字符對照表：")
print("-" * 30)
for char, name in CHAR_TO_NAME.items():
    print(f"  {char} = {name}")

print()
print("=" * 70)
print("卦 → 詞的轉換")
print("=" * 70)
print()

words_data = defaultdict(list)

for hex_num, pos, binary, actual in SAMPLES:
    word = binary_to_word(binary)
    nuclear = get_nuclear_word(binary)
    words_data[word].append({
        "hex": hex_num,
        "pos": pos,
        "binary": binary,
        "actual": actual,
        "nuclear": nuclear,
    })

print("詞 | 上卦 | 下卦 | 卦號 | 各爻吉凶分布")
print("-" * 70)

for word in sorted(words_data.keys()):
    data = words_data[word]
    hex_num = data[0]["hex"]
    upper_char = word[0]
    lower_char = word[1]
    upper_name = CHAR_TO_NAME[upper_char]
    lower_name = CHAR_TO_NAME[lower_char]

    # 計算吉凶分布
    results = [d["actual"] for d in sorted(data, key=lambda x: x["pos"])]
    result_str = "".join(["吉" if r == 1 else ("凶" if r == -1 else "中") for r in results])

    print(f" {word}  | {upper_name:8} | {lower_name:8} | {hex_num:2} | {result_str}")

# ============================================================
# 分析：字符出現時的整體傾向
# ============================================================

print()
print("=" * 70)
print("分析1：每個字符的吉凶傾向")
print("=" * 70)
print()

# 統計每個字符作為上卦或下卦時的吉凶
char_stats = defaultdict(lambda: {
    "upper_ji": 0, "upper_zhong": 0, "upper_xiong": 0,
    "lower_ji": 0, "lower_zhong": 0, "lower_xiong": 0,
})

for word, data in words_data.items():
    upper_char = word[0]
    lower_char = word[1]

    for d in data:
        if d["actual"] == 1:
            char_stats[upper_char]["upper_ji"] += 1
            char_stats[lower_char]["lower_ji"] += 1
        elif d["actual"] == 0:
            char_stats[upper_char]["upper_zhong"] += 1
            char_stats[lower_char]["lower_zhong"] += 1
        else:
            char_stats[upper_char]["upper_xiong"] += 1
            char_stats[lower_char]["lower_xiong"] += 1

print("字符 | 名稱 | 作上卦 (吉/中/凶) | 作下卦 (吉/中/凶)")
print("-" * 70)
for char in sorted(char_stats.keys()):
    s = char_stats[char]
    name = CHAR_TO_NAME[char]
    upper_total = s["upper_ji"] + s["upper_zhong"] + s["upper_xiong"]
    lower_total = s["lower_ji"] + s["lower_zhong"] + s["lower_xiong"]

    upper_ji_rate = s["upper_ji"] / upper_total * 100 if upper_total else 0
    lower_ji_rate = s["lower_ji"] / lower_total * 100 if lower_total else 0

    print(f"  {char}  | {name:8} | {s['upper_ji']:2}/{s['upper_zhong']:2}/{s['upper_xiong']:2} ({upper_ji_rate:4.0f}% 吉) | "
          f"{s['lower_ji']:2}/{s['lower_zhong']:2}/{s['lower_xiong']:2} ({lower_ji_rate:4.0f}% 吉)")

# ============================================================
# 分析2：字符組合（詞）的傾向
# ============================================================

print()
print("=" * 70)
print("分析2：詞（字符組合）的整體傾向")
print("=" * 70)
print()

word_tendencies = []

for word, data in words_data.items():
    ji = sum(1 for d in data if d["actual"] == 1)
    zhong = sum(1 for d in data if d["actual"] == 0)
    xiong = sum(1 for d in data if d["actual"] == -1)
    total = len(data)

    word_tendencies.append({
        "word": word,
        "upper": CHAR_TO_NAME[word[0]],
        "lower": CHAR_TO_NAME[word[1]],
        "ji": ji,
        "zhong": zhong,
        "xiong": xiong,
        "ji_rate": ji / total * 100,
        "xiong_rate": xiong / total * 100,
    })

print("詞 | 上 | 下 | 吉 | 中 | 凶 | 傾向")
print("-" * 70)
for w in sorted(word_tendencies, key=lambda x: x["ji_rate"], reverse=True):
    tendency = "吉詞" if w["ji_rate"] > 40 else ("凶詞" if w["xiong_rate"] > 30 else "中性")
    print(f" {w['word']} | {w['upper']:8} | {w['lower']:8} | "
          f"{w['ji']} | {w['zhong']} | {w['xiong']} | {tendency}")

# ============================================================
# 分析3：互卦（隱藏詞）的影響
# ============================================================

print()
print("=" * 70)
print("分析3：互卦（隱藏詞）的影響")
print("=" * 70)
print()

# 互卦分析
nuclear_stats = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for word, data in words_data.items():
    for d in data:
        nuclear = d["nuclear"]
        if d["actual"] == 1:
            nuclear_stats[nuclear]["ji"] += 1
        elif d["actual"] == 0:
            nuclear_stats[nuclear]["zhong"] += 1
        else:
            nuclear_stats[nuclear]["xiong"] += 1

print("互卦詞 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 55)
for nuc in sorted(nuclear_stats.keys()):
    s = nuclear_stats[nuc]
    total = s["ji"] + s["zhong"] + s["xiong"]
    if total > 0:
        ji_rate = s["ji"] / total * 100
        xiong_rate = s["xiong"] / total * 100
        upper_name = CHAR_TO_NAME[nuc[0]][:2]
        lower_name = CHAR_TO_NAME[nuc[1]][:2]
        print(f"  {nuc} ({upper_name}/{lower_name}) | {s['ji']:2} | {s['zhong']:2} | {s['xiong']:2} | "
              f"{ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 分析4：字符的「語法」規則
# ============================================================

print()
print("=" * 70)
print("分析4：發現詞法規則")
print("=" * 70)
print()

# 規則1：哪些字符在上位好？
print("上位字符排名（按吉率）：")
upper_ranking = []
for char in char_stats:
    s = char_stats[char]
    total = s["upper_ji"] + s["upper_zhong"] + s["upper_xiong"]
    if total > 0:
        ji_rate = s["upper_ji"] / total * 100
        upper_ranking.append((char, CHAR_TO_NAME[char], ji_rate, total))

for char, name, rate, n in sorted(upper_ranking, key=lambda x: -x[2]):
    print(f"  {char} {name}: {rate:.0f}% 吉 (n={n})")

print()
print("下位字符排名（按吉率）：")
lower_ranking = []
for char in char_stats:
    s = char_stats[char]
    total = s["lower_ji"] + s["lower_zhong"] + s["lower_xiong"]
    if total > 0:
        ji_rate = s["lower_ji"] / total * 100
        lower_ranking.append((char, CHAR_TO_NAME[char], ji_rate, total))

for char, name, rate, n in sorted(lower_ranking, key=lambda x: -x[2]):
    print(f"  {char} {name}: {rate:.0f}% 吉 (n={n})")

# ============================================================
# 分析5：位置×字符的深層規則
# ============================================================

print()
print("=" * 70)
print("分析5：位置×詞的交互")
print("=" * 70)
print()

# 每個位置在不同詞中的表現
pos_word_matrix = defaultdict(lambda: defaultdict(list))

for word, data in words_data.items():
    for d in data:
        pos_word_matrix[d["pos"]][word].append(d["actual"])

print("哪些詞在特定位置表現異常？")
print()

for pos in [2, 5]:  # 中位
    print(f"爻{pos}（得中）：")
    for word in sorted(pos_word_matrix[pos].keys()):
        results = pos_word_matrix[pos][word]
        if results:
            avg = sum(results) / len(results)
            if avg >= 0.5:
                print(f"  詞'{word}' → 吉")
            elif avg <= -0.5:
                print(f"  詞'{word}' → 凶 (異常！)")

# ============================================================
# 最終洞察
# ============================================================

print()
print("=" * 70)
print("字符-詞語方法的核心洞察")
print("=" * 70)
print("""
發現：
1. 八卦可視為8個基本「字符」(0-7)
2. 卦 = 上字符 + 下字符 = 兩字詞
3. 互卦 = 隱藏在詞中的另一個詞

詞法規則假設：
- 某些字符在上位好（如坤0 = 順從在上）
- 某些字符在下位好（如艮4 = 止在下）
- 某些組合產生特定「詞義」

下一步：
1. 建立「詞義表」- 每個詞的基本傾向
2. 位置修正 - 位置如何改變詞義
3. 互卦修正 - 隱藏詞的影響

這類似於：
- 中文：「日+月=明」→ 組合產生新義
- 化學：H + O = H2O → 元素組合產生新物質
""")
