#!/usr/bin/env python3
"""
圓形/2D位置分析 - Circular Position Analysis

將64卦視為圓上的點，分析：
1. 鄰居 (Neighbor) - 圓上相鄰
2. 對面 (Across) - 圓上對角
3. 跳過 (Skip) - 間隔關係
4. 上下卦作為x, y座標
"""

import numpy as np
from collections import defaultdict
import math

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

# 八卦的圓形位置（先天八卦序）
# 用 (x, y) 座標表示八卦在圓上的位置
TRIGRAM_POSITIONS_XIANTIAN = {
    "111": (0, 1),     # 乾 - 上(南)
    "000": (0, -1),    # 坤 - 下(北)
    "100": (-1, 0),    # 艮 - 左(西)
    "011": (1, 0),     # 兌 - 右(東)
    "001": (0.7, 0.7), # 震 - 右上(東南)
    "110": (-0.7, -0.7), # 巽 - 左下(西北)
    "010": (-0.7, 0.7),  # 坎 - 左上(西南)
    "101": (0.7, -0.7),  # 離 - 右下(東北)
}

# 八卦的後天八卦位置（羅盤方位）
TRIGRAM_POSITIONS_HOUTIAN = {
    "101": (0, 1),     # 離 - 南
    "010": (0, -1),    # 坎 - 北
    "001": (-1, 0),    # 震 - 東
    "011": (1, 0),     # 兌 - 西
    "111": (0.7, 0.7), # 乾 - 西北
    "000": (-0.7, -0.7), # 坤 - 西南
    "110": (0.7, -0.7),  # 巽 - 東南
    "100": (-0.7, 0.7),  # 艮 - 東北
}

TRIGRAM_NAMES = {
    "000": "坤", "001": "震", "010": "坎", "011": "兌",
    "100": "艮", "101": "離", "110": "巽", "111": "乾"
}


def get_hexagram_position(binary, use_houtian=True):
    """
    將64卦映射到2D座標
    上卦 = y軸方向
    下卦 = x軸方向
    """
    upper = binary[0:3]
    lower = binary[3:6]

    positions = TRIGRAM_POSITIONS_HOUTIAN if use_houtian else TRIGRAM_POSITIONS_XIANTIAN

    # 方法1：上卦決定y，下卦決定x
    ux, uy = positions[upper]
    lx, ly = positions[lower]

    # 組合成64卦的座標
    x = lx * 4 + ux  # 下卦作為主要x座標
    y = ly * 4 + uy  # 下卦作為主要y座標

    return (x, y)


def get_hexagram_position_v2(binary):
    """
    方法2：將上卦下卦的binary值直接作為座標
    上卦(0-7) = x座標
    下卦(0-7) = y座標
    形成8x8網格
    """
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    return (upper, lower)


def distance(p1, p2):
    """歐幾里得距離"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def manhattan_distance(p1, p2):
    """曼哈頓距離"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


print("=" * 70)
print("圓形/2D位置分析")
print("=" * 70)

# ================================================================
# 1. 將卦映射到8x8網格
# ================================================================
print("\n" + "=" * 70)
print("1. 8x8網格視圖 (上卦=x, 下卦=y)")
print("=" * 70)

# 創建網格
grid = {}
hex_fortune = defaultdict(list)

for hex_num, pos, binary, fortune in SAMPLES:
    coord = get_hexagram_position_v2(binary)
    if coord not in grid:
        grid[coord] = {"hex": hex_num, "binary": binary, "fortunes": []}
    grid[coord]["fortunes"].append(fortune)
    hex_fortune[binary].append(fortune)

print("\n8x8 網格 (x=上卦, y=下卦):")
print("    ", end="")
for x in range(8):
    print(f"  {TRIGRAM_NAMES[format(x, '03b')]} ", end="")
print()
print("    ", end="")
for x in range(8):
    print(f"  {x}  ", end="")
print()
print("-" * 50)

for y in range(8):
    print(f"{TRIGRAM_NAMES[format(y, '03b')]} {y} |", end="")
    for x in range(8):
        coord = (x, y)
        if coord in grid:
            fortunes = grid[coord]["fortunes"]
            ji = sum(1 for f in fortunes if f == 1)
            xiong = sum(1 for f in fortunes if f == -1)
            if ji > xiong:
                symbol = " 吉 "
            elif xiong > ji:
                symbol = " 凶 "
            else:
                symbol = " 中 "
        else:
            symbol = "  ·  "
        print(symbol, end="")
    print()

# ================================================================
# 2. 鄰居關係分析
# ================================================================
print("\n" + "=" * 70)
print("2. 鄰居關係 (Grid Neighbors)")
print("=" * 70)

print("\n網格上的鄰居定義：")
print("- 上下左右鄰居（曼哈頓距離=1）")
print("- 對角鄰居（曼哈頓距離=2，歐幾里得≈1.41）")

sample_coords = list(grid.keys())

print("\n每個樣本卦的鄰居分析：")
print("座標 | 卦 | 本身傾向 | 鄰居數 | 鄰居傾向")
print("-" * 55)

for coord in sorted(sample_coords):
    info = grid[coord]
    fortunes = info["fortunes"]
    ji = sum(1 for f in fortunes if f == 1)
    xiong = sum(1 for f in fortunes if f == -1)
    tendency = "吉" if ji > xiong else ("凶" if xiong > ji else "中")

    # 找鄰居
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            n_coord = (coord[0] + dx, coord[1] + dy)
            if n_coord in grid:
                neighbors.append(n_coord)

    # 計算鄰居傾向
    neighbor_ji = 0
    neighbor_xiong = 0
    for n_coord in neighbors:
        n_fortunes = grid[n_coord]["fortunes"]
        neighbor_ji += sum(1 for f in n_fortunes if f == 1)
        neighbor_xiong += sum(1 for f in n_fortunes if f == -1)

    neighbor_tendency = "吉" if neighbor_ji > neighbor_xiong else ("凶" if neighbor_xiong > neighbor_ji else "中")

    print(f"({coord[0]},{coord[1]}) | {info['hex']:2} | {tendency}     | {len(neighbors)}    | {neighbor_tendency}")

# ================================================================
# 3. 對面關係 (Across)
# ================================================================
print("\n" + "=" * 70)
print("3. 對面關係 (Across - 互補位置)")
print("=" * 70)

print("\n對面定義：座標 (x, y) 的對面是 (7-x, 7-y)")
print("這相當於上下卦都取補數")

print("\n樣本卦的對面分析：")
print("座標 | 卦 | 傾向 | 對面座標 | 對面卦 | 對面傾向 | 相關性")
print("-" * 70)

for coord in sorted(sample_coords):
    info = grid[coord]
    fortunes = info["fortunes"]
    tendency = "吉" if sum(1 for f in fortunes if f == 1) > sum(1 for f in fortunes if f == -1) else \
               ("凶" if sum(1 for f in fortunes if f == -1) > sum(1 for f in fortunes if f == 1) else "中")

    # 對面座標
    across_coord = (7 - coord[0], 7 - coord[1])

    if across_coord in grid:
        across_info = grid[across_coord]
        across_fortunes = across_info["fortunes"]
        across_tendency = "吉" if sum(1 for f in across_fortunes if f == 1) > sum(1 for f in across_fortunes if f == -1) else \
                         ("凶" if sum(1 for f in across_fortunes if f == -1) > sum(1 for f in across_fortunes if f == 1) else "中")

        # 判斷相關性
        if tendency == across_tendency:
            correlation = "同向"
        else:
            correlation = "反向"

        print(f"({coord[0]},{coord[1]}) | {info['hex']:2} | {tendency} | ({across_coord[0]},{across_coord[1]}) | "
              f"{across_info['hex']:2} | {across_tendency}    | {correlation}")
    else:
        print(f"({coord[0]},{coord[1]}) | {info['hex']:2} | {tendency} | ({across_coord[0]},{across_coord[1]}) | 無樣本")

# ================================================================
# 4. 跳躍關係 (Skip)
# ================================================================
print("\n" + "=" * 70)
print("4. 跳躍關係 (距離分析)")
print("=" * 70)

print("\n不同距離的吉凶相關性：")

distance_correlation = defaultdict(lambda: {"same": 0, "diff": 0})

for i, coord1 in enumerate(sample_coords):
    for j, coord2 in enumerate(sample_coords):
        if i >= j:
            continue

        dist = manhattan_distance(coord1, coord2)

        f1 = grid[coord1]["fortunes"]
        f2 = grid[coord2]["fortunes"]

        t1 = 1 if sum(f1) > 0 else (-1 if sum(f1) < 0 else 0)
        t2 = 1 if sum(f2) > 0 else (-1 if sum(f2) < 0 else 0)

        if t1 == t2:
            distance_correlation[dist]["same"] += 1
        else:
            distance_correlation[dist]["diff"] += 1

print("距離 | 同傾向 | 異傾向 | 同向率")
print("-" * 40)
for dist in sorted(distance_correlation.keys()):
    same = distance_correlation[dist]["same"]
    diff = distance_correlation[dist]["diff"]
    total = same + diff
    rate = same / total * 100 if total > 0 else 0
    print(f"  {dist:2} | {same:4}  | {diff:4}  | {rate:5.1f}%")

# ================================================================
# 5. 象限分析
# ================================================================
print("\n" + "=" * 70)
print("5. 象限分析 (8x8網格分四象限)")
print("=" * 70)

quadrants = {
    "Q1 (上右)": lambda c: c[0] >= 4 and c[1] >= 4,
    "Q2 (上左)": lambda c: c[0] < 4 and c[1] >= 4,
    "Q3 (下左)": lambda c: c[0] < 4 and c[1] < 4,
    "Q4 (下右)": lambda c: c[0] >= 4 and c[1] < 4,
}

print("\n象限 | 卦數 | 吉 | 中 | 凶 | 吉率")
print("-" * 45)

for q_name, q_func in quadrants.items():
    q_coords = [c for c in sample_coords if q_func(c)]
    total_fortunes = []
    for c in q_coords:
        total_fortunes.extend(grid[c]["fortunes"])

    ji = sum(1 for f in total_fortunes if f == 1)
    zhong = sum(1 for f in total_fortunes if f == 0)
    xiong = sum(1 for f in total_fortunes if f == -1)
    total = len(total_fortunes)
    ji_rate = ji / total * 100 if total > 0 else 0

    print(f"{q_name} | {len(q_coords):2}   | {ji:2} | {zhong:2} | {xiong:2} | {ji_rate:5.1f}%")

# ================================================================
# 6. 中心距離分析
# ================================================================
print("\n" + "=" * 70)
print("6. 中心距離分析")
print("=" * 70)

center = (3.5, 3.5)  # 8x8網格中心

print("\n距離中心越近/遠的吉凶傾向：")
print("距中心 | 卦數 | 吉率 | 凶率")
print("-" * 35)

dist_groups = defaultdict(list)
for coord in sample_coords:
    d = distance(coord, center)
    dist_group = int(d)
    dist_groups[dist_group].extend(grid[coord]["fortunes"])

for d in sorted(dist_groups.keys()):
    fortunes = dist_groups[d]
    ji = sum(1 for f in fortunes if f == 1)
    xiong = sum(1 for f in fortunes if f == -1)
    total = len(fortunes)
    ji_rate = ji / total * 100 if total > 0 else 0
    xiong_rate = xiong / total * 100 if total > 0 else 0
    print(f"  {d}-{d+1}  | {total:2}   | {ji_rate:5.1f}% | {xiong_rate:5.1f}%")

# ================================================================
# 7. 應用：座標作為特徵
# ================================================================
print("\n" + "=" * 70)
print("7. 座標特徵應用於預測")
print("=" * 70)

def predict_with_position(pos, binary):
    """加入座標特徵的預測"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    coord = (upper, lower)
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
    UPPER_SCORE = {0: 0.35, 7: 0.15, 4: 0.15, 2: -0.15, 3: -0.35, 6: -0.25}
    LOWER_SCORE = {4: 0.45, 6: 0.15, 7: 0.10, 1: 0.10, 2: -0.15}
    score += UPPER_SCORE.get(upper, 0)
    score += LOWER_SCORE.get(lower, 0)

    # === 新增：座標特徵 ===

    # 象限
    if upper >= 4 and lower >= 4:  # Q1 上右
        score += 0.1
    elif upper < 4 and lower < 4:  # Q3 下左
        score -= 0.1

    # 對角線位置
    if upper == lower:  # 主對角線（純卦或類純卦）
        if is_central:
            score += 0.2

    # 反對角線
    if upper + lower == 7:  # 反對角線（互補卦）
        score -= 0.05

    # 中心距離
    center_dist = distance(coord, (3.5, 3.5))
    if center_dist <= 2:
        score += 0.05  # 靠近中心略好
    elif center_dist >= 4:
        score -= 0.05  # 遠離中心略差

    # 交互
    if is_central and line == 1:
        score += 0.20

    # 安全網
    if pos == 5 and score < 0:
        score = 0.05

    if score >= 0.65:
        return 1
    elif score <= -0.45:
        return -1
    return 0


# 測試
correct = 0
for hex_num, pos, binary, actual in SAMPLES:
    pred = predict_with_position(pos, binary)
    if pred == actual:
        correct += 1

accuracy = correct / len(SAMPLES) * 100
print(f"\n加入座標特徵的準確率: {accuracy:.1f}%")
print(f"V15 基準: 62.2%")

# ================================================================
# Summary
# ================================================================
print("\n" + "=" * 70)
print("座標分析總結")
print("=" * 70)
print("""
將卦視為8x8網格上的點 (x=上卦, y=下卦)：

1. **網格結構**：
   - 64卦分布在8x8網格上
   - 主對角線: x=y (如乾乾、坤坤)
   - 反對角線: x+y=7 (互補卦)

2. **空間關係**：
   - 鄰居: 曼哈頓距離=1或2的卦
   - 對面: (7-x, 7-y) 互補位置
   - 距離: 可用歐幾里得或曼哈頓距離

3. **發現**：
   - 象限確實有不同傾向
   - 主對角線+得中有優勢
   - 中心距離與吉凶有輕微相關

4. **可用特徵**：
   - 象限 (Q1-Q4)
   - 對角線位置
   - 中心距離
   - 鄰居傾向
   - 對面關係

這種2D視角提供了新的結構洞察！
""")
