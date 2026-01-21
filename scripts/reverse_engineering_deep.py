#!/usr/bin/env python3
"""
深度逆向工程技術

技術清單：
1. 圖論分析 - 變卦連接圖
2. 馬可夫鏈 - 狀態轉移概率
3. 二元決策圖 (BDD) 簡化
4. 卡諾圖 (Karnaugh Map) 分析
5. 線性密碼分析
6. S-box 分析（八卦視為S-box）
7. 聚類分析 (Clustering)
8. 序列模式挖掘
9. 自動機建模
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

def flip_bit(binary, pos):
    """翻轉指定位置的位元"""
    b = list(binary)
    idx = 6 - pos
    b[idx] = '0' if b[idx] == '1' else '1'
    return ''.join(b)

def get_line(binary, pos):
    return int(binary[6 - pos])

def hamming_distance(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

# ============================================================
# 技術1：變卦連接圖分析
# ============================================================

print("=" * 70)
print("技術1：變卦連接圖 (Transformation Graph)")
print("=" * 70)
print()
print("每個卦是一個節點，變爻連接形成邊")
print("分析：哪些轉換路徑與吉凶相關？")
print()

# 建立圖
graph = defaultdict(list)
edge_fortune = {}  # 邊的吉凶

for hex_num, pos, binary, actual in SAMPLES:
    new_binary = flip_bit(binary, pos)
    edge = (binary, new_binary, pos)
    graph[binary].append((new_binary, pos, actual))
    edge_fortune[edge] = actual

# 分析出度（可變化數）
print("節點出度分析（樣本中的卦）：")
for binary in sorted(set(s[2] for s in SAMPLES)):
    edges = graph[binary]
    ji_edges = sum(1 for e in edges if e[2] == 1)
    xiong_edges = sum(1 for e in edges if e[2] == -1)
    print(f"  {binary}: {len(edges)}條邊, 吉{ji_edges} 凶{xiong_edges}")

# 找出吉凶路徑模式
print()
print("邊的吉凶分布（按變化位置）：")
for pos in range(1, 7):
    edges_at_pos = [(e, f) for e, f in edge_fortune.items() if e[2] == pos]
    if edges_at_pos:
        ji = sum(1 for e, f in edges_at_pos if f == 1)
        xiong = sum(1 for e, f in edges_at_pos if f == -1)
        print(f"  變爻{pos}: 吉{ji} 凶{xiong}")

# ============================================================
# 技術2：馬可夫鏈分析
# ============================================================

print()
print("=" * 70)
print("技術2：馬可夫鏈 - 狀態轉移")
print("=" * 70)
print()
print("把吉/中/凶視為狀態，分析轉移概率")
print()

# 建立轉移矩陣（基於爻位順序）
transitions = defaultdict(lambda: defaultdict(int))

for hex_num, pos, binary, actual in SAMPLES:
    if pos < 6:
        # 找下一爻的結果
        next_samples = [s for s in SAMPLES if s[0] == hex_num and s[1] == pos + 1]
        if next_samples:
            next_actual = next_samples[0][3]
            transitions[actual][next_actual] += 1

print("轉移矩陣（爻位i → 爻位i+1）：")
print("     | 吉  | 中  | 凶  |")
print("-" * 30)
for from_state in [1, 0, -1]:
    row = transitions[from_state]
    total = sum(row.values())
    if total > 0:
        probs = [row[1]/total, row[0]/total, row[-1]/total]
        from_name = ["凶", "中", "吉"][from_state + 1]
        print(f" {from_name}  | {probs[0]:.2f} | {probs[1]:.2f} | {probs[2]:.2f} |")

# ============================================================
# 技術3：位元影響力分析（類似差分密碼分析）
# ============================================================

print()
print("=" * 70)
print("技術3：位元影響力分析 (Differential Analysis)")
print("=" * 70)
print()
print("分析：改變某個位元對結果的影響程度")
print()

# 對於每個位元位置，計算其對吉凶的影響
for bit_pos in range(6):
    # 找出只在這個位元不同的樣本對
    bit_effect = {"same_result": 0, "diff_result": 0}

    for i, s1 in enumerate(SAMPLES):
        for s2 in SAMPLES[i+1:]:
            if s1[1] == s2[1]:  # 同樣的爻位
                # 檢查是否只有這個位元不同
                diff_bits = [j for j in range(6) if s1[2][j] != s2[2][j]]
                if len(diff_bits) == 1 and diff_bits[0] == bit_pos:
                    if s1[3] == s2[3]:
                        bit_effect["same_result"] += 1
                    else:
                        bit_effect["diff_result"] += 1

    total = bit_effect["same_result"] + bit_effect["diff_result"]
    if total > 0:
        influence = bit_effect["diff_result"] / total * 100
        bit_name = f"卦位{6-bit_pos}"
        print(f"  {bit_name}: 影響力 {influence:.0f}% "
              f"(改變{bit_effect['diff_result']}/{total}次導致結果變化)")

# ============================================================
# 技術4：S-box 分析（八卦視為8→8映射）
# ============================================================

print()
print("=" * 70)
print("技術4：S-box 分析（八卦作為置換）")
print("=" * 70)
print()
print("把八卦視為S-box，分析上卦→下卦的置換特性")
print()

TRIGRAM_TO_NUM = {
    "000": 0, "001": 1, "010": 2, "011": 3,
    "100": 4, "101": 5, "110": 6, "111": 7,
}

TRIGRAM_NAME = {
    "000": "坤", "001": "震", "010": "坎", "011": "兌",
    "100": "艮", "101": "離", "110": "巽", "111": "乾",
}

# 分析上下卦的XOR關係
print("上卦 XOR 下卦 與吉凶的關係：")
xor_results = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    upper = TRIGRAM_TO_NUM[binary[0:3]]
    lower = TRIGRAM_TO_NUM[binary[3:6]]
    xor_val = upper ^ lower

    if actual == 1:
        xor_results[xor_val]["ji"] += 1
    elif actual == 0:
        xor_results[xor_val]["zhong"] += 1
    else:
        xor_results[xor_val]["xiong"] += 1

print("XOR值 | 吉 | 中 | 凶 | 吉率 | 凶率 | 二進制")
print("-" * 55)
for xor_val in sorted(xor_results.keys()):
    r = xor_results[xor_val]
    total = r["ji"] + r["zhong"] + r["xiong"]
    if total > 0:
        ji_rate = r["ji"] / total * 100
        xiong_rate = r["xiong"] / total * 100
        xor_bin = format(xor_val, '03b')
        print(f"  {xor_val}   | {r['ji']:2} | {r['zhong']:2} | {r['xiong']:2} | "
              f"{ji_rate:4.0f}% | {xiong_rate:4.0f}% | {xor_bin}")

# ============================================================
# 技術5：線性分析（找線性關係）
# ============================================================

print()
print("=" * 70)
print("技術5：線性分析 (Linear Cryptanalysis)")
print("=" * 70)
print()
print("尋找：輸入位元的線性組合 與 結果的相關性")
print()

# 對每個可能的位元掩碼，計算與吉凶的相關性
best_masks = []

for mask in range(1, 64):  # 6位掩碼
    # 計算掩碼對應的奇偶性
    correlations = {"ji": 0, "zhong": 0, "xiong": 0}

    for hex_num, pos, binary, actual in SAMPLES:
        # 計算掩碼位元的XOR
        parity = 0
        for i in range(6):
            if mask & (1 << (5-i)):
                parity ^= int(binary[i])

        if actual == 1:
            correlations["ji"] += 1 if parity == 1 else -1
        elif actual == -1:
            correlations["xiong"] += 1 if parity == 1 else -1

    # 計算相關性強度
    ji_corr = abs(correlations["ji"])
    xiong_corr = abs(correlations["xiong"])

    if ji_corr >= 8 or xiong_corr >= 8:
        mask_bin = format(mask, '06b')
        best_masks.append((mask_bin, ji_corr, xiong_corr, correlations))

print("強線性相關（|相關|≥8）：")
for mask_bin, ji_corr, xiong_corr, corr in sorted(best_masks, key=lambda x: -(x[1]+x[2]))[:10]:
    bits = [f"位{5-i}" for i in range(6) if mask_bin[i] == '1']
    print(f"  {mask_bin} ({'+'.join(bits)}): 吉相關{corr['ji']:+d} 凶相關{corr['xiong']:+d}")

# ============================================================
# 技術6：聚類分析
# ============================================================

print()
print("=" * 70)
print("技術6：聚類分析 (Clustering)")
print("=" * 70)
print()
print("把樣本向量化並聚類，看自然分組")
print()

def vectorize(binary, pos):
    """將樣本轉為特徵向量"""
    v = []
    # 6個卦位
    for c in binary:
        v.append(int(c))
    # 爻位 one-hot
    for p in range(1, 7):
        v.append(1 if pos == p else 0)
    # 當前爻值
    v.append(get_line(binary, pos))
    return tuple(v)

# 簡單的層次聚類（基於漢明距離）
vectors = [(vectorize(s[2], s[1]), s[3]) for s in SAMPLES]

# 計算質心
centroids = {1: [], 0: [], -1: []}
for v, label in vectors:
    centroids[label].append(v)

print("各類別質心（平均特徵向量）：")
for label in [1, 0, -1]:
    if centroids[label]:
        vecs = centroids[label]
        n = len(vecs)
        dim = len(vecs[0])
        avg = [sum(v[i] for v in vecs) / n for i in range(dim)]
        label_name = ["凶", "中", "吉"][label + 1]
        # 只顯示前6個（卦位）和爻值
        print(f"  {label_name}: 卦位平均={[f'{a:.2f}' for a in avg[:6]]}")
        print(f"       爻值平均={avg[-1]:.2f}")

# ============================================================
# 技術7：自動機建模
# ============================================================

print()
print("=" * 70)
print("技術7：自動機建模 (Automata)")
print("=" * 70)
print()
print("把6爻視為6個狀態轉移，分析狀態序列模式")
print()

# 建立狀態轉移模式
patterns = defaultdict(int)

for hex_num in set(s[0] for s in SAMPLES):
    hex_samples = sorted([s for s in SAMPLES if s[0] == hex_num], key=lambda x: x[1])
    if len(hex_samples) == 6:
        # 提取吉凶序列
        sequence = tuple(s[3] for s in hex_samples)
        patterns[sequence] += 1

print("吉凶序列模式（爻1→爻6）：")
for seq, count in sorted(patterns.items(), key=lambda x: -x[1]):
    seq_str = "".join(["凶" if s == -1 else ("吉" if s == 1 else "中") for s in seq])
    print(f"  {seq_str}: {count}個卦")

# 分析序列的週期性
print()
print("序列週期性分析：")
for seq, count in patterns.items():
    # 檢查週期2 (如 吉凶吉凶...)
    period2 = all(seq[i] == seq[i % 2] for i in range(6))
    # 檢查週期3
    period3 = all(seq[i] == seq[i % 3] for i in range(6))
    # 檢查遞增
    increasing = all(seq[i] >= seq[i-1] for i in range(1, 6))
    # 檢查遞減
    decreasing = all(seq[i] <= seq[i-1] for i in range(1, 6))

    if period2 or period3 or increasing or decreasing:
        seq_str = "".join(["凶" if s == -1 else ("吉" if s == 1 else "中") for s in seq])
        props = []
        if period2: props.append("週期2")
        if period3: props.append("週期3")
        if increasing: props.append("遞增")
        if decreasing: props.append("遞減")
        print(f"  {seq_str}: {', '.join(props)}")

# ============================================================
# 技術8：對稱性分析
# ============================================================

print()
print("=" * 70)
print("技術8：對稱性分析 (Symmetry)")
print("=" * 70)
print()

# 分析二進制的對稱性
print("卦的對稱性與吉凶：")
symmetry_results = {"symmetric": {"ji": 0, "zhong": 0, "xiong": 0},
                    "asymmetric": {"ji": 0, "zhong": 0, "xiong": 0}}

for hex_num, pos, binary, actual in SAMPLES:
    is_symmetric = binary == binary[::-1]
    key = "symmetric" if is_symmetric else "asymmetric"
    if actual == 1:
        symmetry_results[key]["ji"] += 1
    elif actual == 0:
        symmetry_results[key]["zhong"] += 1
    else:
        symmetry_results[key]["xiong"] += 1

for sym_type, counts in symmetry_results.items():
    total = counts["ji"] + counts["zhong"] + counts["xiong"]
    if total > 0:
        ji_rate = counts["ji"] / total * 100
        xiong_rate = counts["xiong"] / total * 100
        print(f"  {sym_type:12}: 吉{ji_rate:.0f}% 凶{xiong_rate:.0f}% (n={total})")

# 分析上下卦的對稱
print()
print("上下卦對稱性與吉凶：")
ud_symmetry = {"same": {"ji": 0, "zhong": 0, "xiong": 0},
               "reverse": {"ji": 0, "zhong": 0, "xiong": 0},
               "other": {"ji": 0, "zhong": 0, "xiong": 0}}

for hex_num, pos, binary, actual in SAMPLES:
    upper = binary[0:3]
    lower = binary[3:6]

    if upper == lower:
        key = "same"
    elif upper == lower[::-1]:
        key = "reverse"
    else:
        key = "other"

    if actual == 1:
        ud_symmetry[key]["ji"] += 1
    elif actual == 0:
        ud_symmetry[key]["zhong"] += 1
    else:
        ud_symmetry[key]["xiong"] += 1

for sym_type, counts in ud_symmetry.items():
    total = counts["ji"] + counts["zhong"] + counts["xiong"]
    if total > 0:
        ji_rate = counts["ji"] / total * 100
        xiong_rate = counts["xiong"] / total * 100
        print(f"  {sym_type:8}: 吉{ji_rate:.0f}% 凶{xiong_rate:.0f}% (n={total})")

# ============================================================
# 技術9：互補分析
# ============================================================

print()
print("=" * 70)
print("技術9：互補/反轉分析")
print("=" * 70)
print()

# 分析反轉卦（二進制取反）的吉凶關係
print("卦與其反轉卦的關係：")
for hex_num, pos, binary, actual in SAMPLES:
    # 反轉卦
    inverted = ''.join('1' if c == '0' else '0' for c in binary)

    # 找反轉卦的同位置爻
    inv_samples = [s for s in SAMPLES if s[2] == inverted and s[1] == pos]

    if inv_samples:
        inv_actual = inv_samples[0][3]
        if actual != inv_actual:
            actual_str = ["凶", "中", "吉"][actual + 1]
            inv_str = ["凶", "中", "吉"][inv_actual + 1]
            print(f"  {binary} 爻{pos}({actual_str}) ↔ {inverted} 爻{pos}({inv_str})")

# ============================================================
# 總結
# ============================================================

print()
print("=" * 70)
print("深度逆向工程總結")
print("=" * 70)
print("""
應用技術：
1. 變卦連接圖 - 分析轉換路徑
2. 馬可夫鏈 - 爻位間的狀態轉移
3. 差分分析 - 位元對結果的影響力
4. S-box分析 - 上下卦XOR關係
5. 線性分析 - 位元組合與結果相關性
6. 聚類分析 - 自然分組
7. 自動機建模 - 序列模式
8. 對稱性分析 - 二進制對稱
9. 互補分析 - 反轉卦關係

這些是密碼學和機器學習中的標準逆向工程技術。
""")
