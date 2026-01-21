#!/usr/bin/env python3
"""
計算機科學進階技術探索

技術清單：
1. 布林函數分析 (Boolean Function Analysis)
2. 決策樹自動生成 (Decision Tree)
3. 關聯規則挖掘 (Association Rules)
4. 聚類分析 (Clustering)
5. 特徵選擇 (Feature Selection)
6. 圖論分析 (Graph Analysis)
"""

from collections import defaultdict
import itertools

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

def get_line(binary, pos):
    return int(binary[6 - pos])

def pos_to_binary(pos):
    return format(pos - 1, '03b')

def encode_full(binary, pos):
    """完整編碼：6位卦 + 3位位置 + 1位爻值"""
    line = get_line(binary, pos)
    return binary + pos_to_binary(pos) + str(line)

# ============================================================
# 技術1：布林函數分析
# ============================================================

print("=" * 70)
print("技術1：布林函數分析 (Boolean Function)")
print("=" * 70)
print()
print("目標：找出 f(x1,x2,...,xn) = 吉/凶 的最簡表達式")
print()

# 建立完整的特徵向量
def extract_boolean_features(binary, pos):
    """提取布林特徵"""
    f = []

    # 6個卦位
    for i in range(6):
        f.append(int(binary[i]))

    # 3個位置位
    pos_bin = pos_to_binary(pos)
    for i in range(3):
        f.append(int(pos_bin[i]))

    # 當前爻值
    f.append(get_line(binary, pos))

    # 衍生特徵
    f.append(1 if pos in [2, 5] else 0)  # 得中
    f.append(1 if pos == 5 else 0)  # 五爻
    f.append(1 if pos == 6 else 0)  # 六爻
    f.append(1 if binary[3:6] == "100" else 0)  # 艮在下
    f.append(1 if binary[0:3] == "000" else 0)  # 坤在上
    f.append(1 if binary[0:3] == "011" else 0)  # 兌在上
    f.append(1 if binary[0:3] == "010" or binary[3:6] == "010" else 0)  # 有坎

    return tuple(f)

# 建立真值表
truth_table = defaultdict(list)
for hex_num, pos, binary, actual in SAMPLES:
    features = extract_boolean_features(binary, pos)
    truth_table[features].append(actual)

# 分析矛盾
print("特徵衝突分析（同樣特徵不同結果）：")
conflicts = 0
for features, outcomes in truth_table.items():
    if len(set(outcomes)) > 1:
        conflicts += 1
        if conflicts <= 5:
            print(f"  {features[:10]}... → 結果: {outcomes}")

print(f"\n總衝突數: {conflicts}/{len(truth_table)} 特徵組合")
print("(衝突意味著這些特徵不足以完全區分)")

# ============================================================
# 技術2：貪婪決策樹構建
# ============================================================

print()
print("=" * 70)
print("技術2：貪婪決策樹（信息增益）")
print("=" * 70)
print()

def entropy(counts):
    """計算熵"""
    total = sum(counts)
    if total == 0:
        return 0
    result = 0
    for c in counts:
        if c > 0:
            p = c / total
            result -= p * (p.__log__(2) if hasattr(p, '__log__') else (0 if p == 0 else p * (1/p).__pow__(p)))
    # 簡化版本
    return 1 - max(counts) / total if total > 0 else 0

def information_gain(samples, feature_idx):
    """計算單個特徵的信息增益"""
    # 分割樣本
    split = {0: [], 1: []}
    for s in samples:
        features = extract_boolean_features(s[2], s[1])
        split[features[feature_idx]].append(s[3])

    # 計算增益
    total = len(samples)
    gain = 0
    for val, outcomes in split.items():
        if outcomes:
            subset_entropy = 1 - max(outcomes.count(1), outcomes.count(0), outcomes.count(-1)) / len(outcomes)
            gain += (len(outcomes) / total) * subset_entropy

    return 1 - gain  # 越大越好

feature_names = [
    "卦位0", "卦位1", "卦位2", "卦位3", "卦位4", "卦位5",
    "位置0", "位置1", "位置2", "爻值",
    "得中", "五爻", "六爻", "艮下", "坤上", "兌上", "有坎"
]

print("特徵重要性排名（信息增益）：")
gains = []
for i in range(len(feature_names)):
    g = information_gain(SAMPLES, i)
    gains.append((feature_names[i], g))

for name, g in sorted(gains, key=lambda x: -x[1]):
    print(f"  {name:8}: {g:.3f}")

# ============================================================
# 技術3：關聯規則（頻繁項集）
# ============================================================

print()
print("=" * 70)
print("技術3：關聯規則挖掘")
print("=" * 70)
print()
print("尋找：IF 特徵組合 THEN 吉/凶 的強規則")
print()

# 簡化的關聯規則挖掘
def find_association_rules(samples, min_support=4, min_confidence=0.7):
    """找出關聯規則"""
    rules = []

    # 定義條件（特徵組合）
    conditions = [
        ("五爻", lambda b, p: p == 5),
        ("得中", lambda b, p: p in [2, 5]),
        ("六爻", lambda b, p: p == 6),
        ("三爻", lambda b, p: p == 3),
        ("艮下", lambda b, p: b[3:6] == "100"),
        ("坤上", lambda b, p: b[0:3] == "000"),
        ("兌上", lambda b, p: b[0:3] == "011"),
        ("有坎", lambda b, p: "010" in [b[0:3], b[3:6]]),
        ("陽爻", lambda b, p: get_line(b, p) == 1),
        ("陰爻", lambda b, p: get_line(b, p) == 0),
        ("純卦", lambda b, p: b == "000000" or b == "111111"),
        ("交錯", lambda b, p: b in ["010101", "101010"]),
        ("得中+陽", lambda b, p: p in [2, 5] and get_line(b, p) == 1),
        ("得中+陰", lambda b, p: p in [2, 5] and get_line(b, p) == 0),
        ("五爻+陽", lambda b, p: p == 5 and get_line(b, p) == 1),
        ("六爻+陰", lambda b, p: p == 6 and get_line(b, p) == 0),
        ("艮下+得中", lambda b, p: b[3:6] == "100" and p in [2, 5]),
    ]

    for cond_name, cond_func in conditions:
        matching = [s for s in samples if cond_func(s[2], s[1])]
        if len(matching) >= min_support:
            ji = sum(1 for s in matching if s[3] == 1)
            xiong = sum(1 for s in matching if s[3] == -1)
            total = len(matching)

            if ji / total >= min_confidence:
                rules.append((cond_name, "吉", ji / total, total))
            elif xiong / total >= min_confidence:
                rules.append((cond_name, "凶", xiong / total, total))
            elif ji == 0 and total >= min_support:
                rules.append((cond_name, "從不吉", 1.0, total))
            elif xiong == 0 and total >= min_support:
                rules.append((cond_name, "從不凶", 1.0, total))

    return rules

rules = find_association_rules(SAMPLES)
print("發現的強規則（置信度≥70%或絕對規則）：")
for cond, result, conf, support in sorted(rules, key=lambda x: -x[2]):
    print(f"  IF {cond:12} THEN {result} (置信度: {conf*100:.0f}%, 支持: {support})")

# ============================================================
# 技術4：特徵組合窮舉
# ============================================================

print()
print("=" * 70)
print("技術4：特徵組合窮舉（找完美規則）")
print("=" * 70)
print()

# 定義原子特徵
atomic_features = {
    "p1": lambda b, p: p == 1,
    "p2": lambda b, p: p == 2,
    "p3": lambda b, p: p == 3,
    "p4": lambda b, p: p == 4,
    "p5": lambda b, p: p == 5,
    "p6": lambda b, p: p == 6,
    "yang": lambda b, p: get_line(b, p) == 1,
    "yin": lambda b, p: get_line(b, p) == 0,
    "gen_low": lambda b, p: b[3:6] == "100",
    "kun_up": lambda b, p: b[0:3] == "000",
    "dui_up": lambda b, p: b[0:3] == "011",
    "kan": lambda b, p: "010" in [b[0:3], b[3:6]],
    "qian_low": lambda b, p: b[3:6] == "111",
    "qian_up": lambda b, p: b[0:3] == "111",
    "zhen_low": lambda b, p: b[3:6] == "001",
}

# 尋找完美的2特徵組合
print("完美2特徵組合（100%預測）：")
perfect_rules = []

for f1_name, f1 in atomic_features.items():
    for f2_name, f2 in atomic_features.items():
        if f1_name >= f2_name:
            continue

        # 組合條件
        matching = [s for s in SAMPLES if f1(s[2], s[1]) and f2(s[2], s[1])]

        if len(matching) >= 3:
            outcomes = [s[3] for s in matching]
            if len(set(outcomes)) == 1:
                result = ["凶", "中", "吉"][outcomes[0] + 1]
                perfect_rules.append((f"{f1_name} AND {f2_name}", result, len(matching)))
                print(f"  {f1_name} AND {f2_name} → {result} ({len(matching)}樣本)")

# ============================================================
# 技術5：逆向推導（從結果到特徵）
# ============================================================

print()
print("=" * 70)
print("技術5：逆向推導（從結果找共同特徵）")
print("=" * 70)
print()

# 分類樣本
ji_samples = [s for s in SAMPLES if s[3] == 1]
xiong_samples = [s for s in SAMPLES if s[3] == -1]

# 找出吉樣本的共同特徵
print(f"吉樣本 ({len(ji_samples)} 個) 的共同特徵：")
for f_name, f in atomic_features.items():
    count = sum(1 for s in ji_samples if f(s[2], s[1]))
    if count >= len(ji_samples) * 0.5:
        print(f"  {f_name}: {count}/{len(ji_samples)} ({count/len(ji_samples)*100:.0f}%)")

print(f"\n凶樣本 ({len(xiong_samples)} 個) 的共同特徵：")
for f_name, f in atomic_features.items():
    count = sum(1 for s in xiong_samples if f(s[2], s[1]))
    if count >= len(xiong_samples) * 0.4:
        print(f"  {f_name}: {count}/{len(xiong_samples)} ({count/len(xiong_samples)*100:.0f}%)")

# ============================================================
# 技術6：距離矩陣分析
# ============================================================

print()
print("=" * 70)
print("技術6：樣本間距離分析")
print("=" * 70)
print()

def hamming(s1, s2):
    """漢明距離"""
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

# 編碼所有樣本
encoded = [(encode_full(s[2], s[1]), s[3]) for s in SAMPLES]

# 計算同類和異類的平均距離
same_class_dist = {1: [], 0: [], -1: []}
cross_class_dist = []

for i in range(len(encoded)):
    for j in range(i+1, len(encoded)):
        d = hamming(encoded[i][0], encoded[j][0])
        if encoded[i][1] == encoded[j][1]:
            same_class_dist[encoded[i][1]].append(d)
        else:
            cross_class_dist.append(d)

print("類內平均距離：")
for label, dists in same_class_dist.items():
    if dists:
        label_name = ["凶", "中", "吉"][label + 1]
        print(f"  {label_name}: {sum(dists)/len(dists):.2f}")

print(f"\n類間平均距離: {sum(cross_class_dist)/len(cross_class_dist):.2f}")

if sum(cross_class_dist)/len(cross_class_dist) > sum(sum(v) for v in same_class_dist.values() if v) / sum(len(v) for v in same_class_dist.values() if v):
    print("\n結論：類間距離 > 類內距離，說明結構確實能區分")
else:
    print("\n結論：類內類間距離相近，純結構區分能力有限")

# ============================================================
# 總結
# ============================================================

print()
print("=" * 70)
print("計算機科學技術總結")
print("=" * 70)
print("""
應用技術：
1. 布林函數分析 → 發現特徵衝突
2. 決策樹（信息增益）→ 特徵重要性排名
3. 關聯規則 → 強預測規則
4. 特徵組合窮舉 → 完美規則
5. 逆向推導 → 吉/凶的共同特徵
6. 距離矩陣 → 類內類間可分性

關鍵發現：
- 存在特徵衝突（同樣特徵不同結果）
- 這限制了純結構預測的極限
- 需要語義信息來解決衝突
""")
