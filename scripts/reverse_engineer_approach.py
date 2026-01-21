#!/usr/bin/env python3
"""
逆向工程方法探索易經吉凶規律

專家諮詢：計算機科學 / 逆向工程技術

技術：
1. 位元模式分析 (Bit Pattern Analysis)
2. XOR 關係發現 (XOR Relationship)
3. 漢明距離 (Hamming Distance)
4. 頻率分析 (Frequency Analysis)
5. 差分分析 (Differential Analysis)
6. 壓縮相似性 (Compression-based Similarity)

核心思想：
- 把 6位binary + 6位position 視為 12位碼
- 或者把整個卦+爻編碼成特徵向量
- 尋找 吉/中/凶 之間的二進制規律
"""

from collections import defaultdict
import itertools

# 原始數據：(卦號, 爻位, 卦binary, 結果)
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

def pos_to_binary(pos):
    """位置轉換為3位binary (1-6 -> 000-101)"""
    return format(pos - 1, '03b')

def encode_sample(hex_binary, pos):
    """
    編碼方式1：9位碼
    - 6位卦binary + 3位位置binary
    """
    return hex_binary + pos_to_binary(pos)

def encode_sample_v2(hex_binary, pos):
    """
    編碼方式2：12位碼
    - 6位卦binary + 6位位置one-hot
    """
    pos_onehot = '0' * (pos - 1) + '1' + '0' * (6 - pos)
    return hex_binary + pos_onehot

def encode_sample_v3(hex_binary, pos):
    """
    編碼方式3：提取該爻的值
    - 6位卦binary + 1位該爻值 + 3位位置
    """
    line_value = hex_binary[6 - pos]
    return hex_binary + line_value + pos_to_binary(pos)

def hamming_distance(s1, s2):
    """計算漢明距離"""
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def xor_binary(s1, s2):
    """XOR 兩個二進制字符串"""
    return ''.join(str(int(a) ^ int(b)) for a, b in zip(s1, s2))

print("=" * 70)
print("逆向工程方法：純二進制模式分析")
print("=" * 70)
print()

# ============================================================
# 方法1：編碼並按結果分類
# ============================================================

print("=" * 70)
print("方法1：9位編碼 (6位卦 + 3位位置)")
print("=" * 70)
print()

ji_codes = []    # 吉
zhong_codes = [] # 中
xiong_codes = [] # 凶

for hex_num, pos, binary, actual in SAMPLES:
    code = encode_sample(binary, pos)
    if actual == 1:
        ji_codes.append((code, hex_num, pos))
    elif actual == 0:
        zhong_codes.append((code, hex_num, pos))
    else:
        xiong_codes.append((code, hex_num, pos))

print(f"吉 ({len(ji_codes)} 個):")
for code, h, p in sorted(ji_codes):
    print(f"  {code} (卦{h}爻{p})")

print(f"\n凶 ({len(xiong_codes)} 個):")
for code, h, p in sorted(xiong_codes):
    print(f"  {code} (卦{h}爻{p})")

# ============================================================
# 方法2：位元模式頻率分析
# ============================================================

print()
print("=" * 70)
print("方法2：各位元對吉凶的影響")
print("=" * 70)
print()

# 分析每個位元位置，當該位為1時的吉凶分布
for bit_pos in range(9):
    ji_with_1 = sum(1 for c, _, _ in ji_codes if c[bit_pos] == '1')
    ji_with_0 = sum(1 for c, _, _ in ji_codes if c[bit_pos] == '0')
    xiong_with_1 = sum(1 for c, _, _ in xiong_codes if c[bit_pos] == '1')
    xiong_with_0 = sum(1 for c, _, _ in xiong_codes if c[bit_pos] == '0')
    zhong_with_1 = sum(1 for c, _, _ in zhong_codes if c[bit_pos] == '1')
    zhong_with_0 = sum(1 for c, _, _ in zhong_codes if c[bit_pos] == '0')

    # 計算該位為1時的吉率和凶率
    total_1 = ji_with_1 + zhong_with_1 + xiong_with_1
    total_0 = ji_with_0 + zhong_with_0 + xiong_with_0

    if total_1 > 0:
        ji_rate_1 = ji_with_1 / total_1 * 100
        xiong_rate_1 = xiong_with_1 / total_1 * 100
    else:
        ji_rate_1 = xiong_rate_1 = 0

    if total_0 > 0:
        ji_rate_0 = ji_with_0 / total_0 * 100
        xiong_rate_0 = xiong_with_0 / total_0 * 100
    else:
        ji_rate_0 = xiong_rate_0 = 0

    bit_name = f"卦位{6-bit_pos}" if bit_pos < 6 else f"位置位{bit_pos-5}"
    print(f"位{bit_pos} ({bit_name}): "
          f"=1時(n={total_1}) 吉{ji_rate_1:4.0f}% 凶{xiong_rate_1:4.0f}% | "
          f"=0時(n={total_0}) 吉{ji_rate_0:4.0f}% 凶{xiong_rate_0:4.0f}%")

# ============================================================
# 方法3：XOR 差分分析
# ============================================================

print()
print("=" * 70)
print("方法3：吉與凶的 XOR 差分分析")
print("=" * 70)
print()

# 找出吉和凶之間的共同差異
xor_patterns = defaultdict(int)

for ji_code, _, _ in ji_codes:
    for xiong_code, _, _ in xiong_codes:
        diff = xor_binary(ji_code, xiong_code)
        xor_patterns[diff] += 1

print("吉↔凶 XOR 差異模式 (出現頻率最高):")
for pattern, count in sorted(xor_patterns.items(), key=lambda x: -x[1])[:10]:
    diff_bits = sum(1 for b in pattern if b == '1')
    print(f"  {pattern} (漢明距離={diff_bits}, 出現{count}次)")

# ============================================================
# 方法4：找出「必然規則」
# ============================================================

print()
print("=" * 70)
print("方法4：尋找必然規則 (100%成立)")
print("=" * 70)
print()

# 對於每個2位元組合，檢查是否完美區分
all_codes = [(encode_sample(b, p), a) for _, p, b, a in SAMPLES]

print("檢查所有2位元組合...")
for i in range(9):
    for j in range(i+1, 9):
        # 提取這兩位的模式
        patterns = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})
        for code, actual in all_codes:
            key = code[i] + code[j]
            if actual == 1:
                patterns[key]["ji"] += 1
            elif actual == 0:
                patterns[key]["zhong"] += 1
            else:
                patterns[key]["xiong"] += 1

        # 檢查是否有完美區分的模式
        for pat, counts in patterns.items():
            total = counts["ji"] + counts["zhong"] + counts["xiong"]
            if total >= 3:  # 至少3個樣本
                if counts["xiong"] == 0 and counts["ji"] >= 2:
                    print(f"  位{i},{j}='{pat}' → 從不凶 (吉{counts['ji']} 中{counts['zhong']})")
                if counts["ji"] == 0 and counts["xiong"] >= 2:
                    print(f"  位{i},{j}='{pat}' → 從不吉 (中{counts['zhong']} 凶{counts['xiong']})")

# ============================================================
# 方法5：3位元組合分析
# ============================================================

print()
print("=" * 70)
print("方法5：3位元組合的強規則")
print("=" * 70)
print()

strong_rules = []

for i in range(9):
    for j in range(i+1, 9):
        for k in range(j+1, 9):
            patterns = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})
            for code, actual in all_codes:
                key = code[i] + code[j] + code[k]
                if actual == 1:
                    patterns[key]["ji"] += 1
                elif actual == 0:
                    patterns[key]["zhong"] += 1
                else:
                    patterns[key]["xiong"] += 1

            for pat, counts in patterns.items():
                total = counts["ji"] + counts["zhong"] + counts["xiong"]
                if total >= 4:
                    ji_rate = counts["ji"] / total
                    xiong_rate = counts["xiong"] / total
                    if ji_rate >= 0.8:
                        strong_rules.append((f"位{i},{j},{k}='{pat}'", "高吉", ji_rate, total))
                    elif xiong_rate >= 0.7:
                        strong_rules.append((f"位{i},{j},{k}='{pat}'", "高凶", xiong_rate, total))

print("強規則 (吉率≥80% 或 凶率≥70%):")
for rule, typ, rate, n in sorted(strong_rules, key=lambda x: -x[2])[:15]:
    print(f"  {rule} → {typ} ({rate*100:.0f}%, n={n})")

# ============================================================
# 方法6：漢明距離聚類
# ============================================================

print()
print("=" * 70)
print("方法6：吉/凶樣本的漢明距離特徵")
print("=" * 70)
print()

# 吉樣本之間的平均漢明距離
ji_internal = []
for i in range(len(ji_codes)):
    for j in range(i+1, len(ji_codes)):
        ji_internal.append(hamming_distance(ji_codes[i][0], ji_codes[j][0]))

xiong_internal = []
for i in range(len(xiong_codes)):
    for j in range(i+1, len(xiong_codes)):
        xiong_internal.append(hamming_distance(xiong_codes[i][0], xiong_codes[j][0]))

ji_xiong_cross = []
for ji_code, _, _ in ji_codes:
    for xiong_code, _, _ in xiong_codes:
        ji_xiong_cross.append(hamming_distance(ji_code, xiong_code))

print(f"吉樣本內部平均距離: {sum(ji_internal)/len(ji_internal):.2f}")
print(f"凶樣本內部平均距離: {sum(xiong_internal)/len(xiong_internal):.2f}")
print(f"吉↔凶跨類平均距離: {sum(ji_xiong_cross)/len(ji_xiong_cross):.2f}")

# ============================================================
# 方法7：爻值與位置的交互分析
# ============================================================

print()
print("=" * 70)
print("方法7：爻值×位置的交互效應")
print("=" * 70)
print()

# 12位編碼：提取爻值
for pos in range(1, 7):
    for line_val in ['0', '1']:
        samples_subset = [(h, p, b, a) for h, p, b, a in SAMPLES
                          if p == pos and b[6-pos] == line_val]
        if samples_subset:
            ji = sum(1 for s in samples_subset if s[3] == 1)
            xiong = sum(1 for s in samples_subset if s[3] == -1)
            total = len(samples_subset)
            line_name = "陽" if line_val == '1' else "陰"
            print(f"爻{pos} {line_name}: 吉{ji}/{total} 凶{xiong}/{total}")

# ============================================================
# 核心發現總結
# ============================================================

print()
print("=" * 70)
print("逆向工程核心發現")
print("=" * 70)
print("""
待分析發現：
1. 位元模式頻率 → 哪些位元組合與吉凶強相關？
2. XOR差分 → 吉凶之間的結構性差異
3. 漢明距離 → 吉樣本是否比凶樣本更「聚集」？
4. 必然規則 → 哪些模式100%成立？

逆向工程的關鍵洞察：
- 如果找到一個位元組合能完美預測，說明這就是「編碼規則」
- 如果沒有，說明規則需要更高維度或非線性組合
""")
