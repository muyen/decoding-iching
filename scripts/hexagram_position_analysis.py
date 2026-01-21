#!/usr/bin/env python3
"""
卦序分析 - 將卦在64卦中的位置作為特徵

分析：
1. 卦號 (1-64) 與吉凶的關係
2. 卦號的二進制特性
3. 卦號的模運算
4. 卦號分組（上經/下經）
5. 卦號與其他特徵的交互
"""

from collections import defaultdict
import numpy as np

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

# 卦名對照
HEXAGRAM_NAMES = {
    1: "乾", 2: "坤", 3: "屯", 4: "蒙", 5: "需", 6: "訟",
    15: "謙", 17: "隨", 20: "觀", 24: "復", 25: "无妄",
    33: "遯", 47: "困", 50: "鼎", 63: "既濟"
}

print("=" * 70)
print("卦序分析 - 卦號作為特徵")
print("=" * 70)

# ================================================================
# 1. 卦號基本統計
# ================================================================
print("\n" + "=" * 70)
print("1. 各卦吉凶統計")
print("=" * 70)

hex_stats = defaultdict(lambda: {"吉": 0, "中": 0, "凶": 0})

for hex_num, pos, binary, fortune in SAMPLES:
    if fortune == 1:
        hex_stats[hex_num]["吉"] += 1
    elif fortune == -1:
        hex_stats[hex_num]["凶"] += 1
    else:
        hex_stats[hex_num]["中"] += 1

print("\n卦號 | 卦名 | 吉 | 中 | 凶 | 吉率 | 凶率 | 傾向")
print("-" * 65)

for hex_num in sorted(hex_stats.keys()):
    stats = hex_stats[hex_num]
    total = stats["吉"] + stats["中"] + stats["凶"]
    ji_rate = stats["吉"] / total * 100
    xiong_rate = stats["凶"] / total * 100

    if ji_rate > 40:
        trend = "偏吉"
    elif xiong_rate > 30:
        trend = "偏凶"
    else:
        trend = "中性"

    name = HEXAGRAM_NAMES.get(hex_num, "?")
    print(f"  {hex_num:2} | {name:4} | {stats['吉']} | {stats['中']} | {stats['凶']} | "
          f"{ji_rate:5.1f}% | {xiong_rate:5.1f}% | {trend}")

# ================================================================
# 2. 卦號分組分析
# ================================================================
print("\n" + "=" * 70)
print("2. 卦號分組分析")
print("=" * 70)

# 上經 (1-30) vs 下經 (31-64)
upper_canon = {"吉": 0, "中": 0, "凶": 0}
lower_canon = {"吉": 0, "中": 0, "凶": 0}

for hex_num, pos, binary, fortune in SAMPLES:
    target = upper_canon if hex_num <= 30 else lower_canon
    if fortune == 1:
        target["吉"] += 1
    elif fortune == -1:
        target["凶"] += 1
    else:
        target["中"] += 1

print("\n上經 vs 下經:")
print(f"上經 (1-30): 吉{upper_canon['吉']} 中{upper_canon['中']} 凶{upper_canon['凶']} | "
      f"吉率={upper_canon['吉']/(upper_canon['吉']+upper_canon['中']+upper_canon['凶'])*100:.1f}%")
print(f"下經 (31-64): 吉{lower_canon['吉']} 中{lower_canon['中']} 凶{lower_canon['凶']} | "
      f"吉率={lower_canon['吉']/(lower_canon['吉']+lower_canon['中']+lower_canon['凶'])*100:.1f}%")

# ================================================================
# 3. 卦號二進制特性
# ================================================================
print("\n" + "=" * 70)
print("3. 卦號二進制特性")
print("=" * 70)

print("\n卦號的二進制表示:")
print("卦號 | Binary | 1的數量 | 奇偶")
print("-" * 40)

for hex_num in sorted(hex_stats.keys()):
    binary = format(hex_num, '06b')
    ones = binary.count('1')
    parity = "奇" if hex_num % 2 == 1 else "偶"
    print(f"  {hex_num:2} | {binary} | {ones}       | {parity}")

# 按卦號奇偶分析
odd_stats = {"吉": 0, "中": 0, "凶": 0}
even_stats = {"吉": 0, "中": 0, "凶": 0}

for hex_num, pos, binary, fortune in SAMPLES:
    target = odd_stats if hex_num % 2 == 1 else even_stats
    if fortune == 1:
        target["吉"] += 1
    elif fortune == -1:
        target["凶"] += 1
    else:
        target["中"] += 1

print("\n卦號奇偶與吉凶:")
odd_total = odd_stats["吉"] + odd_stats["中"] + odd_stats["凶"]
even_total = even_stats["吉"] + even_stats["中"] + even_stats["凶"]
print(f"奇數卦號: 吉率={odd_stats['吉']/odd_total*100:.1f}% 凶率={odd_stats['凶']/odd_total*100:.1f}%")
print(f"偶數卦號: 吉率={even_stats['吉']/even_total*100:.1f}% 凶率={even_stats['凶']/even_total*100:.1f}%")

# ================================================================
# 4. 卦號模運算
# ================================================================
print("\n" + "=" * 70)
print("4. 卦號模運算分析")
print("=" * 70)

for mod in [8, 10, 16]:
    print(f"\n卦號 mod {mod}:")
    mod_stats = defaultdict(lambda: {"吉": 0, "中": 0, "凶": 0})

    for hex_num, pos, binary, fortune in SAMPLES:
        mod_val = hex_num % mod
        if fortune == 1:
            mod_stats[mod_val]["吉"] += 1
        elif fortune == -1:
            mod_stats[mod_val]["凶"] += 1
        else:
            mod_stats[mod_val]["中"] += 1

    print("餘數 | 吉 | 中 | 凶 | 吉率")
    print("-" * 35)
    for r in sorted(mod_stats.keys()):
        stats = mod_stats[r]
        total = stats["吉"] + stats["中"] + stats["凶"]
        if total > 0:
            ji_rate = stats["吉"] / total * 100
            print(f"  {r:2} | {stats['吉']:2} | {stats['中']:2} | {stats['凶']:2} | {ji_rate:5.1f}%")

# ================================================================
# 5. 卦號與位置交互
# ================================================================
print("\n" + "=" * 70)
print("5. 卦號與爻位交互")
print("=" * 70)

print("\n卦號 × 爻位 吉凶分布:")
print("卦號 | 爻1 | 爻2 | 爻3 | 爻4 | 爻5 | 爻6")
print("-" * 55)

for hex_num in sorted(hex_stats.keys()):
    row = f"  {hex_num:2} |"
    for pos in range(1, 7):
        fortune = None
        for h, p, b, f in SAMPLES:
            if h == hex_num and p == pos:
                fortune = f
                break
        if fortune is not None:
            symbol = ["凶", "中", "吉"][fortune + 1]
            row += f" {symbol}  |"
        else:
            row += "  ?  |"
    print(row)

# ================================================================
# 6. 卦號範圍與吉凶
# ================================================================
print("\n" + "=" * 70)
print("6. 卦號範圍分析")
print("=" * 70)

ranges = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 64)]

print("\n卦號範圍 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 50)

for start, end in ranges:
    stats = {"吉": 0, "中": 0, "凶": 0}
    for hex_num, pos, binary, fortune in SAMPLES:
        if start <= hex_num <= end:
            if fortune == 1:
                stats["吉"] += 1
            elif fortune == -1:
                stats["凶"] += 1
            else:
                stats["中"] += 1

    total = stats["吉"] + stats["中"] + stats["凶"]
    if total > 0:
        ji_rate = stats["吉"] / total * 100
        xiong_rate = stats["凶"] / total * 100
        print(f"  {start:2}-{end:2}   | {stats['吉']:2} | {stats['中']:2} | {stats['凶']:2} | "
              f"{ji_rate:5.1f}% | {xiong_rate:5.1f}%")

# ================================================================
# 7. 卦號特徵整合到公式
# ================================================================
print("\n" + "=" * 70)
print("7. 卦號作為特徵的預測效果")
print("=" * 70)

def predict_with_hex_num(hex_num, pos, binary):
    """加入卦號特徵的預測"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    xor_val = upper ^ lower
    line = int(binary[6 - pos])
    is_central = pos in [2, 5]

    # 100%規則
    if xor_val == 4 and pos <= 4:
        return 1
    if upper == 0 and pos == 2:
        return 1
    if xor_val == 0 and is_central:
        return 1
    if binary == "110000":
        return 0

    score = 0.0

    # 位置分數
    if pos == 5: score += 0.90
    if pos == 2: score += 0.50
    if pos == 6: score -= 0.50
    if pos == 3: score -= 0.10

    # 字符分數
    UPPER_SCORE = {"0": 0.35, "7": 0.15, "4": 0.15, "2": -0.15, "3": -0.35, "6": -0.25}
    LOWER_SCORE = {"4": 0.45, "6": 0.15, "7": 0.10, "1": 0.10, "2": -0.15}
    score += UPPER_SCORE.get(str(upper), 0)
    score += LOWER_SCORE.get(str(lower), 0)

    # 交互
    if is_central and line == 1: score += 0.20
    if pos == 6 and line == 0: score -= 0.15

    # ===== 新增：卦號特徵 =====

    # 特殊卦號
    if hex_num == 15:  # 謙卦
        if pos <= 4:
            score += 0.35
        else:
            score -= 0.3

    if hex_num == 20:  # 觀卦
        return 0  # 已處理

    if hex_num == 24:  # 復卦
        if pos <= 2:
            score += 0.20

    if hex_num == 33:  # 遯卦
        if pos >= 5:
            score += 0.25

    if hex_num == 47:  # 困卦
        score -= 0.15  # 困卦整體偏凶

    if hex_num == 63:  # 既濟
        if pos == 1:
            score += 0.25

    # 卦號範圍
    if 1 <= hex_num <= 6:  # 乾坤屯蒙需訟
        pass  # 基本卦，無額外調整

    # 卦號奇偶（測試）
    # if hex_num % 2 == 1:
    #     score += 0.05  # 奇數略好？

    # ===== 卦號特徵結束 =====

    # 安全網
    if pos == 5 and score < 0:
        score = 0.05

    if score >= 0.65:
        return 1
    elif score <= -0.45:
        return -1
    return 0


# 測試
print("\n加入卦號特徵後的預測:")

correct_v15 = 0
correct_with_hex = 0

for hex_num, pos, binary, actual in SAMPLES:
    # V15 (無卦號)
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]

    # 簡化V15
    if xor_val == 4 and pos <= 4:
        pred_v15 = 1
    elif upper == 0 and pos == 2:
        pred_v15 = 1
    elif xor_val == 0 and is_central:
        pred_v15 = 1
    elif binary == "110000":
        pred_v15 = 0
    else:
        # 簡化分數
        score = 0
        if pos == 5: score += 0.9
        if pos == 2: score += 0.5
        if pos == 6: score -= 0.5
        if score >= 0.65:
            pred_v15 = 1
        elif score <= -0.45:
            pred_v15 = -1
        else:
            pred_v15 = 0

    if pred_v15 == actual:
        correct_v15 += 1

    # With hex num
    pred_hex = predict_with_hex_num(hex_num, pos, binary)
    if pred_hex == actual:
        correct_with_hex += 1

print(f"V15 簡化版準確率: {correct_v15/len(SAMPLES)*100:.1f}%")
print(f"加入卦號後準確率: {correct_with_hex/len(SAMPLES)*100:.1f}%")

# ================================================================
# 8. 發現卦號的隱藏模式
# ================================================================
print("\n" + "=" * 70)
print("8. 卦號隱藏模式挖掘")
print("=" * 70)

# 卦號與binary的關係
print("\n卦號 vs Binary值:")
print("卦號 | Binary | Dec | 卦號-Dec | 模式")
print("-" * 50)

for hex_num in sorted(hex_stats.keys()):
    binary = [s[2] for s in SAMPLES if s[0] == hex_num][0]
    dec = int(binary, 2)
    diff = hex_num - dec

    # 尋找模式
    pattern = ""
    if hex_num == dec + 1:
        pattern = "卦號=Dec+1"
    elif hex_num < dec:
        pattern = f"卦號<Dec ({diff:+d})"
    else:
        pattern = f"卦號>Dec ({diff:+d})"

    print(f"  {hex_num:2} | {binary} | {dec:2} | {diff:+3} | {pattern}")

# 卦號與吉凶的相關性
print("\n卦號數值與吉凶的相關性:")

hex_nums = []
fortunes = []
for hex_num, pos, binary, fortune in SAMPLES:
    hex_nums.append(hex_num)
    fortunes.append(fortune)

correlation = np.corrcoef(hex_nums, fortunes)[0, 1]
print(f"卦號與吉凶的相關係數: {correlation:.4f}")

# ================================================================
# Summary
# ================================================================
print("\n" + "=" * 70)
print("卦號分析總結")
print("=" * 70)
print("""
發現：

1. 卦號本身的預測能力有限
   - 卦號與吉凶的相關性很低
   - 但特定卦號有特殊規則

2. 特殊卦號規則：
   - 謙卦(15): 前四爻吉，後二爻中
   - 觀卦(20): 全中
   - 復卦(24): 前二爻吉
   - 遯卦(33): 後二爻吉
   - 困卦(47): 整體偏凶

3. 卦號範圍：
   - 上經(1-30) vs 下經(31-64) 無顯著差異
   - 卦號奇偶也無顯著差異

4. 注意：
   - 直接使用卦號會導致過擬合
   - 卦號反映的是「卦義」而非結構
   - 應該通過語義分析而非卦號數值

結論：卦號作為純數值特徵意義不大，
但作為「卦義」的索引，可以引入語義信息。
""")
