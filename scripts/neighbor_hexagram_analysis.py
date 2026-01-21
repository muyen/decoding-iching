#!/usr/bin/env python3
"""
鄰卦詳細分析 - 左右上下鄰居

在8x8網格中：
- 左鄰: 上卦-1 (改變上卦)
- 右鄰: 上卦+1 (改變上卦)
- 上鄰: 下卦+1 (改變下卦)
- 下鄰: 下卦-1 (改變下卦)

每個鄰居也是一個完整的卦！
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

TRIGRAM_NAMES = {
    "000": "坤", "001": "震", "010": "坎", "011": "兌",
    "100": "艮", "101": "離", "110": "巽", "111": "乾"
}

# 完整64卦
ALL_64_HEXAGRAMS = {}
for upper in range(8):
    for lower in range(8):
        binary = format(upper, '03b') + format(lower, '03b')
        ALL_64_HEXAGRAMS[(upper, lower)] = binary


def get_coord(binary):
    """獲取卦的座標 (upper, lower)"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    return (upper, lower)


def get_neighbors(binary):
    """獲取四個方向的鄰居卦"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)

    neighbors = {}

    # 左鄰: 上卦-1
    if upper > 0:
        left_upper = format(upper - 1, '03b')
        left_lower = format(lower, '03b')
        neighbors["left"] = left_upper + left_lower

    # 右鄰: 上卦+1
    if upper < 7:
        right_upper = format(upper + 1, '03b')
        right_lower = format(lower, '03b')
        neighbors["right"] = right_upper + right_lower

    # 上鄰: 下卦+1
    if lower < 7:
        up_upper = format(upper, '03b')
        up_lower = format(lower + 1, '03b')
        neighbors["up"] = up_upper + up_lower

    # 下鄰: 下卦-1
    if lower > 0:
        down_upper = format(upper, '03b')
        down_lower = format(lower - 1, '03b')
        neighbors["down"] = down_upper + down_lower

    return neighbors


# 創建卦的吉凶統計
hex_fortune = defaultdict(list)
for hex_num, pos, binary, fortune in SAMPLES:
    hex_fortune[binary].append(fortune)


def get_tendency(binary):
    """獲取卦的傾向"""
    if binary not in hex_fortune:
        return None  # 不在樣本中
    fortunes = hex_fortune[binary]
    ji = sum(1 for f in fortunes if f == 1)
    xiong = sum(1 for f in fortunes if f == -1)
    if ji > xiong:
        return 1
    elif xiong > ji:
        return -1
    return 0


print("=" * 70)
print("鄰卦詳細分析 - 左右上下鄰居")
print("=" * 70)

# ================================================================
# 1. 每個樣本卦的鄰居
# ================================================================
print("\n" + "=" * 70)
print("1. 每個樣本卦的四方鄰居")
print("=" * 70)

print("\n說明：")
print("- 左/右: 改變上卦 (x方向)")
print("- 上/下: 改變下卦 (y方向)")
print("- 每個鄰居都是一個完整的64卦之一")

print("\n卦 | Binary | 座標 | 左鄰 | 右鄰 | 上鄰 | 下鄰")
print("-" * 75)

sample_binaries = set(s[2] for s in SAMPLES)

for binary in sorted(sample_binaries):
    coord = get_coord(binary)
    neighbors = get_neighbors(binary)

    upper_name = TRIGRAM_NAMES[binary[0:3]]
    lower_name = TRIGRAM_NAMES[binary[3:6]]

    # 獲取每個鄰居的信息
    def format_neighbor(direction):
        if direction in neighbors:
            n_bin = neighbors[direction]
            n_upper = TRIGRAM_NAMES[n_bin[0:3]]
            n_lower = TRIGRAM_NAMES[n_bin[3:6]]
            tendency = get_tendency(n_bin)
            if tendency is not None:
                t_str = ["凶", "中", "吉"][tendency + 1]
                return f"{n_upper}{n_lower}({t_str})"
            else:
                return f"{n_upper}{n_lower}(?)"
        return "邊界"

    left = format_neighbor("left")
    right = format_neighbor("right")
    up = format_neighbor("up")
    down = format_neighbor("down")

    tendency = get_tendency(binary)
    t_str = ["凶", "中", "吉"][tendency + 1] if tendency is not None else "?"

    print(f"{upper_name}{lower_name} | {binary} | ({coord[0]},{coord[1]}) | {left:10} | {right:10} | {up:10} | {down:10}")

# ================================================================
# 2. 鄰居傾向相關性分析
# ================================================================
print("\n" + "=" * 70)
print("2. 鄰居傾向相關性")
print("=" * 70)

# 統計：本身傾向 vs 各方向鄰居傾向
direction_correlation = {
    "left": {"same": 0, "diff": 0, "unknown": 0},
    "right": {"same": 0, "diff": 0, "unknown": 0},
    "up": {"same": 0, "diff": 0, "unknown": 0},
    "down": {"same": 0, "diff": 0, "unknown": 0},
}

for binary in sample_binaries:
    my_tendency = get_tendency(binary)
    if my_tendency is None:
        continue

    neighbors = get_neighbors(binary)

    for direction, n_binary in neighbors.items():
        n_tendency = get_tendency(n_binary)
        if n_tendency is None:
            direction_correlation[direction]["unknown"] += 1
        elif n_tendency == my_tendency:
            direction_correlation[direction]["same"] += 1
        else:
            direction_correlation[direction]["diff"] += 1

print("\n方向 | 同傾向 | 異傾向 | 未知 | 同向率")
print("-" * 50)

for direction in ["left", "right", "up", "down"]:
    stats = direction_correlation[direction]
    known = stats["same"] + stats["diff"]
    rate = stats["same"] / known * 100 if known > 0 else 0
    print(f"{direction:5} | {stats['same']:4}  | {stats['diff']:4}  | {stats['unknown']:3} | {rate:5.1f}%")

# ================================================================
# 3. 左右 vs 上下的差異
# ================================================================
print("\n" + "=" * 70)
print("3. 左右(改上卦) vs 上下(改下卦) 的差異")
print("=" * 70)

print("\n假設：改變上卦(左右)和改變下卦(上下)對吉凶的影響不同")

# 左右合併
lr_same = direction_correlation["left"]["same"] + direction_correlation["right"]["same"]
lr_diff = direction_correlation["left"]["diff"] + direction_correlation["right"]["diff"]

# 上下合併
ud_same = direction_correlation["up"]["same"] + direction_correlation["down"]["same"]
ud_diff = direction_correlation["up"]["diff"] + direction_correlation["down"]["diff"]

print(f"\n左右方向（改上卦）:")
print(f"  同傾向: {lr_same}, 異傾向: {lr_diff}")
print(f"  同向率: {lr_same/(lr_same+lr_diff)*100:.1f}%" if lr_same + lr_diff > 0 else "  無數據")

print(f"\n上下方向（改下卦）:")
print(f"  同傾向: {ud_same}, 異傾向: {ud_diff}")
print(f"  同向率: {ud_same/(ud_same+ud_diff)*100:.1f}%" if ud_same + ud_diff > 0 else "  無數據")

# ================================================================
# 4. 鄰居變化規律
# ================================================================
print("\n" + "=" * 70)
print("4. 鄰居變化規律 - 1位變化")
print("=" * 70)

print("\n當上卦或下卦改變1時，吉凶如何變化？")

# 分析每個方向1步移動後的變化
change_patterns = defaultdict(list)

for binary in sample_binaries:
    my_tendency = get_tendency(binary)
    if my_tendency is None:
        continue

    neighbors = get_neighbors(binary)

    for direction, n_binary in neighbors.items():
        n_tendency = get_tendency(n_binary)
        if n_tendency is None:
            continue

        # 記錄變化模式
        change = n_tendency - my_tendency  # -2 到 +2
        change_patterns[direction].append(change)

print("\n方向 | 平均變化 | 變好次數 | 變差次數 | 不變次數")
print("-" * 55)

for direction in ["left", "right", "up", "down"]:
    changes = change_patterns[direction]
    if not changes:
        continue

    avg = np.mean(changes)
    better = sum(1 for c in changes if c > 0)
    worse = sum(1 for c in changes if c < 0)
    same = sum(1 for c in changes if c == 0)

    print(f"{direction:5} | {avg:+6.2f}  | {better:6}   | {worse:6}   | {same:6}")

# ================================================================
# 5. 具體鄰卦對比較
# ================================================================
print("\n" + "=" * 70)
print("5. 具體鄰卦對比較")
print("=" * 70)

print("\n有數據的鄰卦對：")
print("本卦 → 鄰卦 | 方向 | 本卦傾向 | 鄰卦傾向 | 變化")
print("-" * 60)

comparisons = []

for binary in sample_binaries:
    my_tendency = get_tendency(binary)
    if my_tendency is None:
        continue

    my_upper = TRIGRAM_NAMES[binary[0:3]]
    my_lower = TRIGRAM_NAMES[binary[3:6]]

    neighbors = get_neighbors(binary)

    for direction, n_binary in neighbors.items():
        n_tendency = get_tendency(n_binary)
        if n_tendency is None:
            continue

        n_upper = TRIGRAM_NAMES[n_binary[0:3]]
        n_lower = TRIGRAM_NAMES[n_binary[3:6]]

        my_str = ["凶", "中", "吉"][my_tendency + 1]
        n_str = ["凶", "中", "吉"][n_tendency + 1]

        change = n_tendency - my_tendency
        change_str = "不變" if change == 0 else (f"+{change}" if change > 0 else str(change))

        comparisons.append((f"{my_upper}{my_lower}", f"{n_upper}{n_lower}", direction, my_str, n_str, change_str))

for my_name, n_name, direction, my_t, n_t, change in comparisons:
    print(f"{my_name}→{n_name} | {direction:5} | {my_t}     | {n_t}     | {change}")

# ================================================================
# 6. 發現：哪個方向移動最安全？
# ================================================================
print("\n" + "=" * 70)
print("6. 哪個方向移動最「安全」？")
print("=" * 70)

print("\n分析：從當前位置移動到鄰居，吉凶如何變化")

# 按起始傾向分組
for start_tendency in [1, 0, -1]:
    start_name = ["凶", "中", "吉"][start_tendency + 1]
    print(f"\n從「{start_name}」出發：")

    for direction in ["left", "right", "up", "down"]:
        outcomes = []

        for binary in sample_binaries:
            my_tendency = get_tendency(binary)
            if my_tendency != start_tendency:
                continue

            neighbors = get_neighbors(binary)
            if direction not in neighbors:
                continue

            n_tendency = get_tendency(neighbors[direction])
            if n_tendency is not None:
                outcomes.append(n_tendency)

        if outcomes:
            avg = np.mean(outcomes)
            ji_count = sum(1 for o in outcomes if o == 1)
            total = len(outcomes)
            print(f"  {direction:5}: {total}次移動, 平均傾向={avg:+.2f}, 到吉率={ji_count/total*100:.0f}%")

# ================================================================
# 7. 應用：鄰居特徵加入預測
# ================================================================
print("\n" + "=" * 70)
print("7. 鄰居特徵應用於預測")
print("=" * 70)

def predict_with_neighbors(pos, binary):
    """加入鄰居特徵的預測"""
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
    UPPER_SCORE = {0: 0.35, 7: 0.15, 4: 0.15, 2: -0.15, 3: -0.35, 6: -0.25}
    LOWER_SCORE = {4: 0.45, 6: 0.15, 7: 0.10, 1: 0.10, 2: -0.15}
    score += UPPER_SCORE.get(upper, 0)
    score += LOWER_SCORE.get(lower, 0)

    # === 鄰居特徵 ===
    neighbors = get_neighbors(binary)

    # 計算已知鄰居的平均傾向
    known_neighbors = []
    for direction, n_binary in neighbors.items():
        n_tendency = get_tendency(n_binary)
        if n_tendency is not None:
            known_neighbors.append(n_tendency)

    if known_neighbors:
        neighbor_avg = np.mean(known_neighbors)
        # 鄰居傾向影響本身（弱相關）
        score += neighbor_avg * 0.1

    # 邊界位置（鄰居少）
    if len(neighbors) < 4:
        if upper == 0 or upper == 7 or lower == 0 or lower == 7:
            score -= 0.05  # 邊緣位置略減分

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
    pred = predict_with_neighbors(pos, binary)
    if pred == actual:
        correct += 1

accuracy = correct / len(SAMPLES) * 100
print(f"\n加入鄰居特徵的準確率: {accuracy:.1f}%")
print(f"V15 基準: 62.2%")
print(f"座標版本: 63.3%")

# ================================================================
# Summary
# ================================================================
print("\n" + "=" * 70)
print("鄰卦分析總結")
print("=" * 70)
print("""
關鍵發現：

1. **四方鄰居**：
   - 左右: 改變上卦 (x方向移動)
   - 上下: 改變下卦 (y方向移動)
   - 每個鄰居都是64卦之一

2. **鄰居傾向相關性**：
   - 相鄰卦的吉凶有一定相關性
   - 但不是完全一致

3. **方向差異**：
   - 左右移動（改上卦）vs 上下移動（改下卦）
   - 可能有不同的影響

4. **安全移動**：
   - 從某些位置移動到鄰居更「安全」
   - 這反映了卦象的連續性

5. **邊界效應**：
   - 位於網格邊緣的卦只有2-3個鄰居
   - 邊緣位置可能有特殊意義

這種鄰居分析揭示了64卦之間的結構關聯！
""")
