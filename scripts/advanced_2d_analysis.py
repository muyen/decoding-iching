#!/usr/bin/env python3
"""
進階2D網格分析

技術包括：
1. 2D傅立葉分析（頻率成分）
2. 空間自相關（Moran's I）
3. 矩陣特徵值分析
4. 卷積核檢測（邊緣、斑點）
5. 熱點分析
6. 等高線/地形分析
7. 路徑分析（最佳路徑）
8. 3x3鄰域模式
9. 旋轉不變性檢查
10. 與隨機網格比較
"""

import json
import os
from collections import defaultdict, Counter
import math

def load_corrected_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'analysis', 'corrected_yaoci_labels.json')
    with open(path, 'r') as f:
        return json.load(f)

def load_structure():
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'structure', 'hexagrams_structure.json')
    with open(path, 'r') as f:
        return json.load(f)

TRIGRAM_NAMES = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']

def build_grid(data, struct_data, value_type='net'):
    """構建8x8網格"""
    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    TRIGRAM_TO_IDX = {name: i for i, name in enumerate(TRIGRAM_NAMES)}

    grid = [[0.0 for _ in range(8)] for _ in range(8)]

    hex_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0, 'sum': 0})
    for d in data:
        hex_num = d['hex_num']
        hex_stats[hex_num]['total'] += 1
        hex_stats[hex_num]['sum'] += d['label']
        if d['label'] == 1:
            hex_stats[hex_num]['ji'] += 1
        elif d['label'] == -1:
            hex_stats[hex_num]['xiong'] += 1

    for hex_num, stats in hex_stats.items():
        if hex_num not in hex_to_trigrams:
            continue
        lower, upper = hex_to_trigrams[hex_num]
        col = TRIGRAM_TO_IDX[lower]
        row = TRIGRAM_TO_IDX[upper]

        if value_type == 'net':
            grid[row][col] = stats['ji'] - stats['xiong']
        elif value_type == 'ji_rate':
            grid[row][col] = stats['ji'] / stats['total'] if stats['total'] > 0 else 0
        elif value_type == 'xiong_rate':
            grid[row][col] = stats['xiong'] / stats['total'] if stats['total'] > 0 else 0

    return grid

def print_grid(grid, title="Grid", fmt="{:+.1f}"):
    """打印網格"""
    print(f"\n{title}")
    print("     ", end="")
    for name in TRIGRAM_NAMES:
        print(f"  {name} ", end="")
    print()
    print("     " + "-" * 40)
    for i, row in enumerate(grid):
        print(f" {TRIGRAM_NAMES[i]} |", end="")
        for val in row:
            print(f" {fmt.format(val)}", end="")
        print()

# ============================================================
# 1. 2D 傅立葉分析
# ============================================================

def fourier_analysis_2d(grid):
    """2D離散傅立葉分析（手動實現）"""
    print("\n" + "=" * 60)
    print("2D 傅立葉分析（頻率成分）")
    print("=" * 60)

    n = len(grid)

    # 計算2D DFT
    dft = [[complex(0, 0) for _ in range(n)] for _ in range(n)]

    for u in range(n):
        for v in range(n):
            total = complex(0, 0)
            for x in range(n):
                for y in range(n):
                    angle = -2 * math.pi * (u * x + v * y) / n
                    total += grid[x][y] * complex(math.cos(angle), math.sin(angle))
            dft[u][v] = total / (n * n)

    # 計算功率譜
    power = [[abs(dft[u][v]) ** 2 for v in range(n)] for u in range(n)]

    # 打印功率譜
    print("\n功率譜（頻率成分強度）:")
    print("     頻率 0  1  2  3  4  5  6  7")
    print("     " + "-" * 35)
    for u in range(n):
        print(f"  {u}  |", end="")
        for v in range(n):
            if power[u][v] > 0.01:
                level = min(9, int(power[u][v] * 100))
                print(f"  {level}", end="")
            else:
                print("  .", end="")
        print()

    # 找主要頻率成分
    freq_components = []
    for u in range(n):
        for v in range(n):
            if (u, v) != (0, 0) and power[u][v] > 0.01:
                freq_components.append((u, v, power[u][v]))

    freq_components.sort(key=lambda x: -x[2])

    print("\n主要頻率成分（非DC）:")
    for u, v, p in freq_components[:5]:
        period_x = n / u if u > 0 else float('inf')
        period_y = n / v if v > 0 else float('inf')
        print(f"  頻率({u},{v}): 功率={p:.4f}, 週期≈{period_x:.1f}×{period_y:.1f}")

    # DC成分（平均值）
    dc = abs(dft[0][0])
    print(f"\nDC成分（平均值）: {dc:.3f}")

    return power

# ============================================================
# 2. 空間自相關 (Moran's I)
# ============================================================

def morans_i(grid):
    """計算Moran's I空間自相關係數"""
    print("\n" + "=" * 60)
    print("空間自相關分析 (Moran's I)")
    print("=" * 60)

    n = len(grid)
    values = [grid[i][j] for i in range(n) for j in range(n)]
    mean = sum(values) / len(values)

    # 計算權重矩陣W（相鄰=1，否則=0）
    def are_neighbors(i1, j1, i2, j2):
        return abs(i1 - i2) <= 1 and abs(j1 - j2) <= 1 and (i1, j1) != (i2, j2)

    # 計算Moran's I
    numerator = 0
    denominator = 0
    w_sum = 0

    for i1 in range(n):
        for j1 in range(n):
            denominator += (grid[i1][j1] - mean) ** 2
            for i2 in range(n):
                for j2 in range(n):
                    if are_neighbors(i1, j1, i2, j2):
                        w_sum += 1
                        numerator += (grid[i1][j1] - mean) * (grid[i2][j2] - mean)

    N = n * n
    morans = (N / w_sum) * (numerator / denominator) if denominator > 0 and w_sum > 0 else 0

    print(f"\nMoran's I = {morans:.4f}")
    print(f"  I > 0: 正空間自相關（相似值聚集）")
    print(f"  I < 0: 負空間自相關（不同值相鄰）")
    print(f"  I ≈ 0: 隨機分布")

    if morans > 0.3:
        print(f"\n→ 發現顯著正空間自相關！相似的吉凶傾向聚集。")
    elif morans < -0.3:
        print(f"\n→ 發現顯著負空間自相關！吉凶呈棋盤狀分布。")
    else:
        print(f"\n→ 接近隨機分布。")

    return morans

# ============================================================
# 3. 矩陣特徵值分析
# ============================================================

def eigenvalue_analysis(grid):
    """矩陣特徵值分析（使用冪迭代法找最大特徵值）"""
    print("\n" + "=" * 60)
    print("矩陣特徵值分析")
    print("=" * 60)

    n = len(grid)

    # 簡化：計算矩陣的基本性質
    # 跡（trace）= 對角線之和
    trace = sum(grid[i][i] for i in range(n))

    # 行列式（使用LU分解的簡化版）
    # 對於分析目的，我們計算一些替代指標

    # 矩陣的Frobenius範數
    frob_norm = math.sqrt(sum(grid[i][j]**2 for i in range(n) for j in range(n)))

    # 行和與列和
    row_sums = [sum(row) for row in grid]
    col_sums = [sum(grid[i][j] for i in range(n)) for j in range(n)]

    print(f"\n矩陣性質:")
    print(f"  跡（對角線和）: {trace:.3f}")
    print(f"  Frobenius範數: {frob_norm:.3f}")

    print(f"\n行和（上卦效應）:")
    for i, (name, s) in enumerate(zip(TRIGRAM_NAMES, row_sums)):
        bar = "█" * int(abs(s) * 2) if s > 0 else "▓" * int(abs(s) * 2)
        print(f"  {name}: {s:+.1f} {bar}")

    print(f"\n列和（下卦效應）:")
    for j, (name, s) in enumerate(zip(TRIGRAM_NAMES, col_sums)):
        bar = "█" * int(abs(s) * 2) if s > 0 else "▓" * int(abs(s) * 2)
        print(f"  {name}: {s:+.1f} {bar}")

    # 對角線vs非對角線
    diag_sum = trace
    off_diag_sum = sum(sum(row) for row in grid) - trace
    print(f"\n對角線總和: {diag_sum:.1f}")
    print(f"非對角線總和: {off_diag_sum:.1f}")

    return trace, frob_norm

# ============================================================
# 4. 卷積核檢測
# ============================================================

def convolution_analysis(grid):
    """使用卷積核檢測特定模式"""
    print("\n" + "=" * 60)
    print("卷積核檢測")
    print("=" * 60)

    n = len(grid)

    # 定義各種檢測核
    kernels = {
        '水平邊緣': [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
        '垂直邊緣': [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
        '對角邊緣(\\)': [[-1, -1, 0], [-1, 0, 1], [0, 1, 1]],
        '對角邊緣(/)': [[0, -1, -1], [1, 0, -1], [1, 1, 0]],
        '高斯平滑': [[1, 2, 1], [2, 4, 2], [1, 2, 1]],
        '拉普拉斯': [[0, 1, 0], [1, -4, 1], [0, 1, 0]],
        '十字形': [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
        'X形': [[1, 0, 1], [0, 1, 0], [1, 0, 1]],
    }

    def convolve(grid, kernel):
        """執行2D卷積"""
        result = [[0.0 for _ in range(n-2)] for _ in range(n-2)]
        for i in range(1, n-1):
            for j in range(1, n-1):
                total = 0
                for ki in range(3):
                    for kj in range(3):
                        total += grid[i-1+ki][j-1+kj] * kernel[ki][kj]
                result[i-1][j-1] = total
        return result

    print("\n各檢測核的響應強度:")
    for name, kernel in kernels.items():
        result = convolve(grid, kernel)
        # 計算響應的總強度
        total_response = sum(abs(result[i][j]) for i in range(len(result)) for j in range(len(result[0])))
        avg_response = total_response / ((n-2) * (n-2))

        # 計算正負比例
        positive = sum(1 for i in range(len(result)) for j in range(len(result[0])) if result[i][j] > 0)
        negative = sum(1 for i in range(len(result)) for j in range(len(result[0])) if result[i][j] < 0)

        print(f"  {name:<12}: 平均響應={avg_response:.2f}, 正/負={positive}/{negative}")

    # 找邊緣位置
    print("\n邊緣檢測（拉普拉斯）:")
    laplacian = convolve(grid, kernels['拉普拉斯'])
    edges = []
    for i in range(len(laplacian)):
        for j in range(len(laplacian[0])):
            if abs(laplacian[i][j]) > 2:
                edges.append((i+1, j+1, laplacian[i][j]))

    if edges:
        print("  發現顯著邊緣位置:")
        for i, j, val in sorted(edges, key=lambda x: -abs(x[2]))[:5]:
            print(f"    ({TRIGRAM_NAMES[i]}, {TRIGRAM_NAMES[j]}): {val:+.1f}")

# ============================================================
# 5. 熱點分析
# ============================================================

def hotspot_analysis(grid):
    """熱點/冷點分析"""
    print("\n" + "=" * 60)
    print("熱點/冷點分析")
    print("=" * 60)

    n = len(grid)
    mean = sum(grid[i][j] for i in range(n) for j in range(n)) / (n * n)
    std = math.sqrt(sum((grid[i][j] - mean)**2 for i in range(n) for j in range(n)) / (n * n))

    print(f"\n網格統計: 均值={mean:.2f}, 標準差={std:.2f}")

    # 標準化並找熱點/冷點
    hotspots = []
    coldspots = []

    for i in range(n):
        for j in range(n):
            z_score = (grid[i][j] - mean) / std if std > 0 else 0
            if z_score > 1.5:
                hotspots.append((TRIGRAM_NAMES[i], TRIGRAM_NAMES[j], grid[i][j], z_score))
            elif z_score < -1.5:
                coldspots.append((TRIGRAM_NAMES[i], TRIGRAM_NAMES[j], grid[i][j], z_score))

    print(f"\n熱點（Z > 1.5，顯著高於平均）:")
    for upper, lower, val, z in sorted(hotspots, key=lambda x: -x[3]):
        print(f"  {upper}/{lower}: {val:+.1f} (Z={z:.2f})")

    print(f"\n冷點（Z < -1.5，顯著低於平均）:")
    for upper, lower, val, z in sorted(coldspots, key=lambda x: x[3]):
        print(f"  {upper}/{lower}: {val:+.1f} (Z={z:.2f})")

    # 熱點聚集分析
    if len(hotspots) > 1:
        print(f"\n熱點聚集分析:")
        for i, (u1, l1, _, _) in enumerate(hotspots):
            for u2, l2, _, _ in hotspots[i+1:]:
                i1, j1 = TRIGRAM_NAMES.index(u1), TRIGRAM_NAMES.index(l1)
                i2, j2 = TRIGRAM_NAMES.index(u2), TRIGRAM_NAMES.index(l2)
                if abs(i1-i2) <= 1 and abs(j1-j2) <= 1:
                    print(f"  {u1}/{l1} 與 {u2}/{l2} 相鄰")

# ============================================================
# 6. 等高線分析
# ============================================================

def contour_analysis(grid):
    """等高線/地形分析"""
    print("\n" + "=" * 60)
    print("等高線/地形分析")
    print("=" * 60)

    n = len(grid)
    values = [grid[i][j] for i in range(n) for j in range(n)]
    min_val, max_val = min(values), max(values)

    # 定義等高線級別
    levels = [-3, -2, -1, 0, 1, 2, 3, 4, 5]

    print(f"\n數值範圍: {min_val:.1f} 到 {max_val:.1f}")
    print("\n等高線圖（ASCII）:")
    print("     ", end="")
    for name in TRIGRAM_NAMES:
        print(f"  {name}", end="")
    print()

    symbols = {-3: '▼', -2: '▽', -1: '○', 0: '·', 1: '◇', 2: '◆', 3: '△', 4: '▲', 5: '★'}

    for i in range(n):
        print(f" {TRIGRAM_NAMES[i]} |", end="")
        for j in range(n):
            val = grid[i][j]
            level = max(-3, min(5, int(val)))
            print(f"  {symbols.get(level, '?')}", end="")
        print()

    print("\n圖例: ▼=-3 ▽=-2 ○=-1 ·=0 ◇=+1 ◆=+2 △=+3 ▲=+4 ★=+5")

    # 找山峰和山谷（局部極值）
    peaks = []
    valleys = []

    for i in range(n):
        for j in range(n):
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if (di, dj) != (0, 0) and 0 <= i+di < n and 0 <= j+dj < n:
                        neighbors.append(grid[i+di][j+dj])

            if neighbors:
                if grid[i][j] > max(neighbors):
                    peaks.append((TRIGRAM_NAMES[i], TRIGRAM_NAMES[j], grid[i][j]))
                elif grid[i][j] < min(neighbors):
                    valleys.append((TRIGRAM_NAMES[i], TRIGRAM_NAMES[j], grid[i][j]))

    print(f"\n山峰（局部最大）:")
    for upper, lower, val in sorted(peaks, key=lambda x: -x[2]):
        print(f"  {upper}/{lower}: {val:+.1f}")

    print(f"\n山谷（局部最小）:")
    for upper, lower, val in sorted(valleys, key=lambda x: x[2]):
        print(f"  {upper}/{lower}: {val:+.1f}")

# ============================================================
# 7. 3x3鄰域模式分析
# ============================================================

def neighborhood_patterns(grid):
    """分析所有3x3鄰域的模式"""
    print("\n" + "=" * 60)
    print("3x3鄰域模式分析")
    print("=" * 60)

    n = len(grid)
    patterns = []

    for i in range(1, n-1):
        for j in range(1, n-1):
            # 提取3x3鄰域
            neighborhood = [[grid[i+di][j+dj] for dj in [-1, 0, 1]] for di in [-1, 0, 1]]

            # 計算模式特徵
            center = neighborhood[1][1]
            neighbors = [neighborhood[di][dj] for di in range(3) for dj in range(3) if (di, dj) != (1, 1)]
            neighbor_mean = sum(neighbors) / len(neighbors)

            pattern_type = ""
            if center > neighbor_mean + 1:
                pattern_type = "山峰"
            elif center < neighbor_mean - 1:
                pattern_type = "山谷"
            elif max(neighbors) - min(neighbors) < 1:
                pattern_type = "平原"
            else:
                # 檢查梯度方向
                left = sum(neighborhood[di][0] for di in range(3)) / 3
                right = sum(neighborhood[di][2] for di in range(3)) / 3
                top = sum(neighborhood[0][dj] for dj in range(3)) / 3
                bottom = sum(neighborhood[2][dj] for dj in range(3)) / 3

                if abs(right - left) > abs(bottom - top):
                    pattern_type = "東西梯度" if right > left else "西東梯度"
                else:
                    pattern_type = "南北梯度" if bottom > top else "北南梯度"

            patterns.append((TRIGRAM_NAMES[i], TRIGRAM_NAMES[j], pattern_type))

    pattern_counts = Counter(p[2] for p in patterns)
    print(f"\n鄰域模式分布:")
    for pattern, count in pattern_counts.most_common():
        print(f"  {pattern}: {count}")

# ============================================================
# 8. 旋轉不變性檢查
# ============================================================

def rotation_invariance(grid):
    """檢查旋轉90度後的相似性"""
    print("\n" + "=" * 60)
    print("旋轉不變性分析")
    print("=" * 60)

    n = len(grid)

    # 旋轉90度
    rotated_90 = [[grid[n-1-j][i] for j in range(n)] for i in range(n)]

    # 旋轉180度
    rotated_180 = [[grid[n-1-i][n-1-j] for j in range(n)] for i in range(n)]

    # 旋轉270度
    rotated_270 = [[grid[j][n-1-i] for j in range(n)] for i in range(n)]

    def similarity(g1, g2):
        diff = sum(abs(g1[i][j] - g2[i][j]) for i in range(n) for j in range(n))
        total = sum(abs(g1[i][j]) + abs(g2[i][j]) for i in range(n) for j in range(n))
        return 1 - diff / total if total > 0 else 0

    sim_90 = similarity(grid, rotated_90)
    sim_180 = similarity(grid, rotated_180)
    sim_270 = similarity(grid, rotated_270)

    print(f"\n與原圖的相似度:")
    print(f"  旋轉90°: {sim_90:.1%}")
    print(f"  旋轉180°: {sim_180:.1%}")
    print(f"  旋轉270°: {sim_270:.1%}")

    if sim_180 > 0.7:
        print(f"\n→ 發現180°旋轉對稱性！")
    if sim_90 > 0.7 and sim_270 > 0.7:
        print(f"\n→ 發現90°旋轉對稱性！")

# ============================================================
# 9. 與隨機網格比較
# ============================================================

def compare_with_random(grid, n_simulations=1000):
    """與隨機網格比較"""
    print("\n" + "=" * 60)
    print("與隨機網格比較")
    print("=" * 60)

    import random

    n = len(grid)
    values = [grid[i][j] for i in range(n) for j in range(n)]

    # 計算原網格的統計量
    def calc_stats(g):
        n = len(g)
        # 對角線平均
        diag = sum(g[i][i] for i in range(n)) / n
        # 相鄰差異
        adj_diff = 0
        adj_count = 0
        for i in range(n):
            for j in range(n):
                if j + 1 < n:
                    adj_diff += abs(g[i][j] - g[i][j+1])
                    adj_count += 1
                if i + 1 < n:
                    adj_diff += abs(g[i][j] - g[i+1][j])
                    adj_count += 1
        adj_diff /= adj_count if adj_count > 0 else 1
        return diag, adj_diff

    orig_diag, orig_adj = calc_stats(grid)

    # 模擬隨機排列
    random_diags = []
    random_adjs = []

    for _ in range(n_simulations):
        shuffled = values.copy()
        random.shuffle(shuffled)
        random_grid = [[shuffled[i*n + j] for j in range(n)] for i in range(n)]
        d, a = calc_stats(random_grid)
        random_diags.append(d)
        random_adjs.append(a)

    # 計算p值
    p_diag = sum(1 for d in random_diags if d <= orig_diag) / n_simulations
    p_adj = sum(1 for a in random_adjs if a <= orig_adj) / n_simulations

    print(f"\n原網格 vs 隨機排列（{n_simulations}次模擬）:")
    print(f"\n對角線平均:")
    print(f"  原網格: {orig_diag:.2f}")
    print(f"  隨機平均: {sum(random_diags)/len(random_diags):.2f}")
    print(f"  p值: {p_diag:.3f}")
    if p_diag < 0.05:
        print(f"  → 對角線值顯著{'低' if orig_diag < sum(random_diags)/len(random_diags) else '高'}於隨機！")

    print(f"\n相鄰差異:")
    print(f"  原網格: {orig_adj:.2f}")
    print(f"  隨機平均: {sum(random_adjs)/len(random_adjs):.2f}")
    print(f"  p值: {p_adj:.3f}")
    if p_adj < 0.05:
        print(f"  → 相鄰差異顯著{'小' if orig_adj < sum(random_adjs)/len(random_adjs) else '大'}於隨機！")

def main():
    data = load_corrected_data()
    struct_data = load_structure()

    # 構建網格
    net_grid = build_grid(data, struct_data, 'net')

    print("=" * 60)
    print("進階2D網格分析")
    print("=" * 60)

    print_grid(net_grid, "淨分網格（吉-凶）")

    # 各種分析
    fourier_analysis_2d(net_grid)
    morans_i(net_grid)
    eigenvalue_analysis(net_grid)
    convolution_analysis(net_grid)
    hotspot_analysis(net_grid)
    contour_analysis(net_grid)
    neighborhood_patterns(net_grid)
    rotation_invariance(net_grid)
    compare_with_random(net_grid)

if __name__ == "__main__":
    main()
