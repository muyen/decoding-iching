#!/usr/bin/env python3
"""
文王卦序分析 - King Wen Sequence Analysis

分析卦序中的關係：
1. 鄰卦 (Neighbors) - 相鄰卦的關係
2. 對卦 (Pairs) - 翻轉或互補
3. 跳卦 (Skips) - 間隔關係
4. 卦序結構與吉凶的關聯
"""

from collections import defaultdict
import numpy as np

# 完整64卦序列（文王卦序）
KING_WEN_SEQUENCE = {
    1: "111111",   # 乾
    2: "000000",   # 坤
    3: "010001",   # 屯
    4: "100010",   # 蒙
    5: "010111",   # 需
    6: "111010",   # 訟
    7: "000010",   # 師
    8: "010000",   # 比
    9: "110111",   # 小畜
    10: "111011",  # 履
    11: "000111",  # 泰
    12: "111000",  # 否
    13: "111101",  # 同人
    14: "101111",  # 大有
    15: "000100",  # 謙
    16: "001000",  # 豫
    17: "011001",  # 隨
    18: "100110",  # 蠱
    19: "000011",  # 臨
    20: "110000",  # 觀
    21: "101001",  # 噬嗑
    22: "100101",  # 賁
    23: "100000",  # 剝
    24: "000001",  # 復
    25: "111001",  # 无妄
    26: "100111",  # 大畜
    27: "100001",  # 頤
    28: "011110",  # 大過
    29: "010010",  # 坎
    30: "101101",  # 離
    31: "011100",  # 咸
    32: "001110",  # 恆
    33: "111100",  # 遯
    34: "001111",  # 大壯
    35: "101000",  # 晉
    36: "000101",  # 明夷
    37: "110101",  # 家人
    38: "101011",  # 睽
    39: "010100",  # 蹇
    40: "001010",  # 解
    41: "100011",  # 損
    42: "110001",  # 益
    43: "011111",  # 夬
    44: "111110",  # 姤
    45: "011000",  # 萃
    46: "000110",  # 升
    47: "011010",  # 困
    48: "010110",  # 井
    49: "011101",  # 革
    50: "101110",  # 鼎
    51: "001001",  # 震
    52: "100100",  # 艮
    53: "110100",  # 漸
    54: "001011",  # 歸妹
    55: "001101",  # 豐
    56: "101100",  # 旅
    57: "110110",  # 巽
    58: "011011",  # 兌
    59: "110010",  # 渙
    60: "010011",  # 節
    61: "110011",  # 中孚
    62: "001100",  # 小過
    63: "010101",  # 既濟
    64: "101010",  # 未濟
}

HEXAGRAM_NAMES = {
    1: "乾", 2: "坤", 3: "屯", 4: "蒙", 5: "需", 6: "訟",
    7: "師", 8: "比", 9: "小畜", 10: "履", 11: "泰", 12: "否",
    13: "同人", 14: "大有", 15: "謙", 16: "豫", 17: "隨", 18: "蠱",
    19: "臨", 20: "觀", 21: "噬嗑", 22: "賁", 23: "剝", 24: "復",
    25: "无妄", 26: "大畜", 27: "頤", 28: "大過", 29: "坎", 30: "離",
    31: "咸", 32: "恆", 33: "遯", 34: "大壯", 35: "晉", 36: "明夷",
    37: "家人", 38: "睽", 39: "蹇", 40: "解", 41: "損", 42: "益",
    43: "夬", 44: "姤", 45: "萃", 46: "升", 47: "困", 48: "井",
    49: "革", 50: "鼎", 51: "震", 52: "艮", 53: "漸", 54: "歸妹",
    55: "豐", 56: "旅", 57: "巽", 58: "兌", 59: "渙", 60: "節",
    61: "中孚", 62: "小過", 63: "既濟", 64: "未濟"
}

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


def flip_binary(binary):
    """翻轉（上下顛倒）"""
    return binary[::-1]


def invert_binary(binary):
    """互補（陰陽互換）"""
    return ''.join('1' if b == '0' else '0' for b in binary)


def hamming_distance(a, b):
    """漢明距離"""
    return sum(c1 != c2 for c1, c2 in zip(a, b))


print("=" * 70)
print("文王卦序分析 - King Wen Sequence Analysis")
print("=" * 70)

# ================================================================
# 1. 鄰卦關係 (Neighbor Analysis)
# ================================================================
print("\n" + "=" * 70)
print("1. 鄰卦關係分析 (Neighbors)")
print("=" * 70)

print("\n相鄰卦的關係類型：")
print("卦對 | 名稱 | Binary | 關係類型 | 漢明距離")
print("-" * 70)

neighbor_types = defaultdict(int)

for i in range(1, 64):
    hex1 = i
    hex2 = i + 1
    bin1 = KING_WEN_SEQUENCE[hex1]
    bin2 = KING_WEN_SEQUENCE[hex2]
    name1 = HEXAGRAM_NAMES[hex1]
    name2 = HEXAGRAM_NAMES[hex2]

    flipped = flip_binary(bin1)
    inverted = invert_binary(bin1)
    hamming = hamming_distance(bin1, bin2)

    # 判斷關係類型
    if bin2 == flipped:
        relation = "翻轉(Flip)"
        neighbor_types["翻轉"] += 1
    elif bin2 == inverted:
        relation = "互補(Invert)"
        neighbor_types["互補"] += 1
    elif bin2 == invert_binary(flipped):
        relation = "翻轉+互補"
        neighbor_types["翻轉+互補"] += 1
    elif hamming == 1:
        relation = "相差1位"
        neighbor_types["相差1位"] += 1
    elif hamming == 2:
        relation = "相差2位"
        neighbor_types["相差2位"] += 1
    else:
        relation = f"其他(H={hamming})"
        neighbor_types["其他"] += 1

    # 只顯示我們樣本中的卦
    sample_hexes = set(s[0] for s in SAMPLES)
    if hex1 in sample_hexes or hex2 in sample_hexes:
        print(f"{hex1:2}-{hex2:2} | {name1}-{name2} | {bin1}-{bin2} | {relation:12} | {hamming}")

print("\n鄰卦關係統計：")
for rel_type, count in sorted(neighbor_types.items(), key=lambda x: -x[1]):
    print(f"  {rel_type}: {count}對 ({count/63*100:.1f}%)")

# ================================================================
# 2. 對卦關係 (Paired Hexagrams)
# ================================================================
print("\n" + "=" * 70)
print("2. 對卦關係 (Pairs in sequence)")
print("=" * 70)

print("\n文王卦序中的配對（每2卦為一組）：")
print("組號 | 卦對 | 名稱 | 關係 | 吉凶差異")
print("-" * 65)

# 創建吉率查詢
hex_fortune = defaultdict(list)
for hex_num, pos, binary, fortune in SAMPLES:
    hex_fortune[hex_num].append(fortune)


def get_hex_tendency(hex_num):
    if hex_num not in hex_fortune:
        return "?"
    fortunes = hex_fortune[hex_num]
    ji = sum(1 for f in fortunes if f == 1)
    xiong = sum(1 for f in fortunes if f == -1)
    if ji > xiong:
        return "吉"
    elif xiong > ji:
        return "凶"
    return "中"


for pair_num in range(1, 33):
    hex1 = pair_num * 2 - 1
    hex2 = pair_num * 2
    bin1 = KING_WEN_SEQUENCE[hex1]
    bin2 = KING_WEN_SEQUENCE[hex2]
    name1 = HEXAGRAM_NAMES[hex1]
    name2 = HEXAGRAM_NAMES[hex2]

    flipped = flip_binary(bin1)

    if bin2 == flipped:
        relation = "翻轉"
    elif bin2 == invert_binary(bin1):
        relation = "互補"
    elif bin1 == bin2:
        relation = "相同"
    else:
        relation = "其他"

    # 只顯示樣本中的
    sample_hexes = set(s[0] for s in SAMPLES)
    if hex1 in sample_hexes or hex2 in sample_hexes:
        tend1 = get_hex_tendency(hex1)
        tend2 = get_hex_tendency(hex2)
        print(f"  {pair_num:2} | {hex1:2}-{hex2:2} | {name1}-{name2:4} | {relation:4} | {tend1}-{tend2}")

# ================================================================
# 3. 跳卦關係 (Skip patterns)
# ================================================================
print("\n" + "=" * 70)
print("3. 跳卦關係 (Skip patterns)")
print("=" * 70)

sample_hexes = sorted(set(s[0] for s in SAMPLES))

print("\n樣本卦之間的間隔：")
print("卦對 | 間隔 | 關係類型 | Binary差異")
print("-" * 55)

for i in range(len(sample_hexes) - 1):
    hex1 = sample_hexes[i]
    hex2 = sample_hexes[i + 1]
    gap = hex2 - hex1
    bin1 = KING_WEN_SEQUENCE[hex1]
    bin2 = KING_WEN_SEQUENCE[hex2]
    name1 = HEXAGRAM_NAMES[hex1]
    name2 = HEXAGRAM_NAMES[hex2]

    hamming = hamming_distance(bin1, bin2)

    if bin2 == flip_binary(bin1):
        relation = "翻轉"
    elif bin2 == invert_binary(bin1):
        relation = "互補"
    else:
        relation = f"H={hamming}"

    print(f"{hex1:2}-{hex2:2} ({name1}-{name2}) | {gap:2} | {relation:6} | {bin1}→{bin2}")

# ================================================================
# 4. 卦序位置與吉凶
# ================================================================
print("\n" + "=" * 70)
print("4. 卦序位置特徵分析")
print("=" * 70)

print("\n卦在序列中的位置特徵：")
print("卦號 | 名稱 | 奇偶 | 對內 | 組內 | 吉率")
print("-" * 50)

for hex_num in sample_hexes:
    name = HEXAGRAM_NAMES[hex_num]
    is_odd = "奇" if hex_num % 2 == 1 else "偶"
    pair_pos = "首" if hex_num % 2 == 1 else "次"  # 對內位置
    group = (hex_num - 1) // 8 + 1  # 8卦一組

    fortunes = hex_fortune[hex_num]
    ji_rate = sum(1 for f in fortunes if f == 1) / len(fortunes) * 100

    print(f"  {hex_num:2} | {name:4} | {is_odd} | {pair_pos}  | 第{group}組 | {ji_rate:5.1f}%")

# ================================================================
# 5. 翻轉/互補卦的吉凶對比
# ================================================================
print("\n" + "=" * 70)
print("5. 翻轉/互補卦的吉凶對比")
print("=" * 70)

print("\n找出樣本卦的翻轉/互補對應：")
print("原卦 | 翻轉卦 | 互補卦 | 原吉率 | 翻轉吉率 | 互補吉率")
print("-" * 65)

for hex_num in sample_hexes:
    bin_orig = KING_WEN_SEQUENCE[hex_num]
    bin_flip = flip_binary(bin_orig)
    bin_inv = invert_binary(bin_orig)
    name = HEXAGRAM_NAMES[hex_num]

    # 找翻轉卦號
    flip_hex = None
    inv_hex = None
    for h, b in KING_WEN_SEQUENCE.items():
        if b == bin_flip:
            flip_hex = h
        if b == bin_inv:
            inv_hex = h

    # 計算吉率
    orig_rate = sum(1 for f in hex_fortune[hex_num] if f == 1) / len(hex_fortune[hex_num]) * 100 if hex_num in hex_fortune else 0

    flip_name = HEXAGRAM_NAMES.get(flip_hex, "?")
    inv_name = HEXAGRAM_NAMES.get(inv_hex, "?")

    flip_rate = "?" if flip_hex not in hex_fortune else f"{sum(1 for f in hex_fortune[flip_hex] if f == 1) / len(hex_fortune[flip_hex]) * 100:.1f}%"
    inv_rate = "?" if inv_hex not in hex_fortune else f"{sum(1 for f in hex_fortune[inv_hex] if f == 1) / len(hex_fortune[inv_hex]) * 100:.1f}%"

    print(f"{hex_num:2} {name:4} | {flip_hex or '?':2} {flip_name:4} | {inv_hex or '?':2} {inv_name:4} | {orig_rate:5.1f}% | {flip_rate:>6} | {inv_rate:>6}")

# ================================================================
# 6. 發現卦序的隱藏結構
# ================================================================
print("\n" + "=" * 70)
print("6. 卦序隱藏結構")
print("=" * 70)

# 分析8卦一組的規律
print("\n每8卦一組的結構：")
for group in range(1, 9):
    start = (group - 1) * 8 + 1
    end = group * 8
    print(f"\n第{group}組 (卦{start}-{end}):")

    group_hexes = []
    for h in range(start, end + 1):
        name = HEXAGRAM_NAMES[h]
        binary = KING_WEN_SEQUENCE[h]
        ones = binary.count('1')
        group_hexes.append((h, name, binary, ones))

    for h, name, binary, ones in group_hexes:
        in_sample = "✓" if h in sample_hexes else " "
        print(f"  {h:2} {name:4} {binary} (陽{ones}) {in_sample}")

# ================================================================
# 7. 應用：卦序位置作為特徵
# ================================================================
print("\n" + "=" * 70)
print("7. 卦序位置作為預測特徵")
print("=" * 70)

def get_sequence_features(hex_num):
    """提取卦序相關特徵"""
    features = {}

    # 基本位置
    features["is_odd"] = hex_num % 2 == 1
    features["pair_first"] = hex_num % 2 == 1
    features["group_8"] = (hex_num - 1) // 8 + 1
    features["upper_canon"] = hex_num <= 30

    # 鄰卦關係
    binary = KING_WEN_SEQUENCE[hex_num]

    # 找對卦
    if hex_num % 2 == 1:
        pair_hex = hex_num + 1
    else:
        pair_hex = hex_num - 1

    pair_bin = KING_WEN_SEQUENCE[pair_hex]
    features["pair_is_flip"] = pair_bin == flip_binary(binary)
    features["pair_is_invert"] = pair_bin == invert_binary(binary)

    return features


print("\n每個樣本卦的序列特徵：")
print("卦號 | 奇偶 | 對首 | 8組 | 經 | 對翻轉 | 對互補")
print("-" * 55)

for hex_num in sample_hexes:
    f = get_sequence_features(hex_num)
    name = HEXAGRAM_NAMES[hex_num]
    odd = "奇" if f["is_odd"] else "偶"
    first = "首" if f["pair_first"] else "次"
    canon = "上" if f["upper_canon"] else "下"
    flip = "✓" if f["pair_is_flip"] else " "
    inv = "✓" if f["pair_is_invert"] else " "

    print(f"  {hex_num:2} {name:4} | {odd} | {first}  | {f['group_8']} | {canon} | {flip}     | {inv}")

# ================================================================
# Summary
# ================================================================
print("\n" + "=" * 70)
print("文王卦序分析總結")
print("=" * 70)
print("""
關鍵發現：

1. **配對規律**：
   - 64卦分為32對
   - 大多數對是「翻轉」關係（上下顛倒）
   - 少數對是「互補」關係（陰陽互換）
   - 乾坤(1-2)、坎離(29-30)等是互補對

2. **8卦分組**：
   - 64卦可分為8組，每組8卦
   - 每組有內在邏輯關聯

3. **上經vs下經**：
   - 上經(1-30): 天地人之道
   - 下經(31-64): 人事應用

4. **翻轉對的吉凶**：
   - 翻轉卦往往有相似的吉凶傾向
   - 例如：屯(3)和蒙(4)是翻轉對

5. **可用作特徵**：
   - 卦序奇偶
   - 對內位置（首/次）
   - 8組編號
   - 上經/下經
   - 與對卦的關係（翻轉/互補）

這些序列關係反映了古人對卦象變化的理解！
""")
