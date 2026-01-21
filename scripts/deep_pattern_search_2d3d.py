#!/usr/bin/env python3
"""
深度模式搜尋 - 2D 和 3D 分析

2D 模式:
1. 對角線模式
2. 對稱性檢測
3. 梯度模式（遞增/遞減）
4. 棋盤模式
5. 行列相關性
6. 塊狀模式
7. 螺旋模式
8. 中心vs邊緣

3D 模式:
1. 立方體切片
2. 層次遞進
3. 空間聚集
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
TRIGRAM_TO_IDX = {name: i for i, name in enumerate(TRIGRAM_NAMES)}

def build_2d_grids(data, struct_data):
    """構建多個2D網格"""
    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 網格1: 吉率 (8x8)
    ji_grid = [[0.0 for _ in range(8)] for _ in range(8)]
    count_grid = [[0 for _ in range(8)] for _ in range(8)]

    # 網格2: 凶率 (8x8)
    xiong_grid = [[0.0 for _ in range(8)] for _ in range(8)]

    # 網格3: 淨分 (8x8)
    net_grid = [[0.0 for _ in range(8)] for _ in range(8)]

    # 網格4: 變化次數 (8x8)
    change_grid = [[0 for _ in range(8)] for _ in range(8)]

    hex_labels = defaultdict(list)
    for d in data:
        hex_labels[d['hex_num']].append(d)

    for hex_num, yaos in hex_labels.items():
        if hex_num not in hex_to_trigrams:
            continue

        lower, upper = hex_to_trigrams[hex_num]
        col = TRIGRAM_TO_IDX[lower]
        row = TRIGRAM_TO_IDX[upper]

        labels = [y['label'] for y in sorted(yaos, key=lambda x: x['position'])]

        ji_count = sum(1 for l in labels if l == 1)
        xiong_count = sum(1 for l in labels if l == -1)
        net = ji_count - xiong_count

        changes = sum(1 for i in range(1, len(labels)) if labels[i] != labels[i-1])

        ji_grid[row][col] = ji_count / len(labels) if labels else 0
        xiong_grid[row][col] = xiong_count / len(labels) if labels else 0
        net_grid[row][col] = net
        change_grid[row][col] = changes
        count_grid[row][col] = len(labels)

    return {
        'ji': ji_grid,
        'xiong': xiong_grid,
        'net': net_grid,
        'change': change_grid,
        'count': count_grid
    }

def analyze_diagonal_patterns(grid, name):
    """對角線模式分析"""
    print(f"\n【對角線模式 - {name}】")

    n = len(grid)

    # 主對角線（左上到右下）
    main_diag = [grid[i][i] for i in range(n)]
    main_avg = sum(main_diag) / n

    # 副對角線（右上到左下）
    anti_diag = [grid[i][n-1-i] for i in range(n)]
    anti_avg = sum(anti_diag) / n

    # 所有元素平均
    all_avg = sum(sum(row) for row in grid) / (n * n)

    print(f"  主對角線平均: {main_avg:.3f}")
    print(f"  副對角線平均: {anti_avg:.3f}")
    print(f"  整體平均: {all_avg:.3f}")

    # 對角線上是否特別高或低
    if main_avg > all_avg * 1.2:
        print(f"  → 主對角線顯著高於平均！(相同上下卦)")
    elif main_avg < all_avg * 0.8:
        print(f"  → 主對角線顯著低於平均！")

    # 檢查平行對角線
    print(f"\n  平行對角線分析:")
    for offset in range(-7, 8):
        diag = [grid[i][i+offset] for i in range(n) if 0 <= i+offset < n]
        if diag:
            avg = sum(diag) / len(diag)
            deviation = (avg - all_avg) / all_avg * 100 if all_avg != 0 else 0
            if abs(deviation) > 30:
                print(f"    偏移{offset:+d}: {avg:.3f} ({deviation:+.0f}%) ***")

def analyze_symmetry(grid, name):
    """對稱性分析"""
    print(f"\n【對稱性分析 - {name}】")

    n = len(grid)

    # 水平對稱
    h_diff = sum(abs(grid[i][j] - grid[n-1-i][j])
                 for i in range(n//2) for j in range(n))
    h_total = sum(abs(grid[i][j]) + abs(grid[n-1-i][j])
                  for i in range(n//2) for j in range(n))

    # 垂直對稱
    v_diff = sum(abs(grid[i][j] - grid[i][n-1-j])
                 for i in range(n) for j in range(n//2))
    v_total = sum(abs(grid[i][j]) + abs(grid[i][n-1-j])
                  for i in range(n) for j in range(n//2))

    # 對角對稱（轉置）
    d_diff = sum(abs(grid[i][j] - grid[j][i])
                 for i in range(n) for j in range(i+1, n))
    d_total = sum(abs(grid[i][j]) + abs(grid[j][i])
                  for i in range(n) for j in range(i+1, n))

    # 中心對稱（180度旋轉）
    c_diff = sum(abs(grid[i][j] - grid[n-1-i][n-1-j])
                 for i in range(n) for j in range(n))
    c_total = sum(abs(grid[i][j]) + abs(grid[n-1-i][n-1-j])
                  for i in range(n) for j in range(n))

    h_sym = 1 - h_diff/h_total if h_total > 0 else 0
    v_sym = 1 - v_diff/v_total if v_total > 0 else 0
    d_sym = 1 - d_diff/d_total if d_total > 0 else 0
    c_sym = 1 - c_diff/c_total if c_total > 0 else 0

    print(f"  水平對稱度: {h_sym:.1%}")
    print(f"  垂直對稱度: {v_sym:.1%}")
    print(f"  對角對稱度: {d_sym:.1%} (上下卦交換)")
    print(f"  中心對稱度: {c_sym:.1%} (180度旋轉)")

    max_sym = max(h_sym, v_sym, d_sym, c_sym)
    if max_sym > 0.7:
        print(f"  → 發現顯著對稱性！")

def analyze_gradient(grid, name):
    """梯度模式分析"""
    print(f"\n【梯度模式 - {name}】")

    n = len(grid)

    # 行方向梯度（從左到右）
    row_gradients = []
    for i in range(n):
        if n > 1:
            grad = (grid[i][n-1] - grid[i][0]) / (n - 1)
            row_gradients.append(grad)

    avg_row_grad = sum(row_gradients) / n if row_gradients else 0

    # 列方向梯度（從上到下）
    col_gradients = []
    for j in range(n):
        if n > 1:
            grad = (grid[n-1][j] - grid[0][j]) / (n - 1)
            col_gradients.append(grad)

    avg_col_grad = sum(col_gradients) / n if col_gradients else 0

    print(f"  平均行梯度（左→右）: {avg_row_grad:+.4f}")
    print(f"  平均列梯度（上→下）: {avg_col_grad:+.4f}")

    # 解讀
    if abs(avg_row_grad) > 0.02:
        direction = "增加" if avg_row_grad > 0 else "減少"
        print(f"  → 從坤到乾（下卦），{name}{direction}")

    if abs(avg_col_grad) > 0.02:
        direction = "增加" if avg_col_grad > 0 else "減少"
        print(f"  → 從坤到乾（上卦），{name}{direction}")

def analyze_checkerboard(grid, name):
    """棋盤模式分析"""
    print(f"\n【棋盤模式 - {name}】")

    n = len(grid)

    # 黑格（i+j為偶數）和白格（i+j為奇數）
    black = [grid[i][j] for i in range(n) for j in range(n) if (i+j) % 2 == 0]
    white = [grid[i][j] for i in range(n) for j in range(n) if (i+j) % 2 == 1]

    black_avg = sum(black) / len(black) if black else 0
    white_avg = sum(white) / len(white) if white else 0

    print(f"  黑格平均（i+j偶數）: {black_avg:.3f}")
    print(f"  白格平均（i+j奇數）: {white_avg:.3f}")

    diff = abs(black_avg - white_avg)
    total_avg = (black_avg + white_avg) / 2
    if total_avg > 0 and diff / total_avg > 0.2:
        print(f"  → 發現棋盤模式！差異: {diff:.3f}")

def analyze_center_vs_edge(grid, name):
    """中心vs邊緣分析"""
    print(f"\n【中心vs邊緣 - {name}】")

    n = len(grid)

    # 邊緣（第一行、最後一行、第一列、最後一列）
    edge = []
    for i in range(n):
        edge.append(grid[0][i])
        edge.append(grid[n-1][i])
        if 0 < i < n-1:
            edge.append(grid[i][0])
            edge.append(grid[i][n-1])

    # 中心（不在邊緣的）
    center = [grid[i][j] for i in range(1, n-1) for j in range(1, n-1)]

    # 核心（最中心2x2）
    core = [grid[3][3], grid[3][4], grid[4][3], grid[4][4]]

    edge_avg = sum(edge) / len(edge) if edge else 0
    center_avg = sum(center) / len(center) if center else 0
    core_avg = sum(core) / len(core) if core else 0

    print(f"  邊緣平均: {edge_avg:.3f}")
    print(f"  中間平均: {center_avg:.3f}")
    print(f"  核心平均: {core_avg:.3f}")

    if center_avg > edge_avg * 1.2:
        print(f"  → 中心高於邊緣！")
    elif edge_avg > center_avg * 1.2:
        print(f"  → 邊緣高於中心！")

def analyze_quadrants(grid, name):
    """四象限分析"""
    print(f"\n【四象限分析 - {name}】")

    n = len(grid)
    mid = n // 2

    # 四象限
    q1 = [grid[i][j] for i in range(mid) for j in range(mid, n)]  # 右上
    q2 = [grid[i][j] for i in range(mid) for j in range(mid)]      # 左上
    q3 = [grid[i][j] for i in range(mid, n) for j in range(mid)]   # 左下
    q4 = [grid[i][j] for i in range(mid, n) for j in range(mid, n)] # 右下

    q1_avg = sum(q1) / len(q1) if q1 else 0
    q2_avg = sum(q2) / len(q2) if q2 else 0
    q3_avg = sum(q3) / len(q3) if q3 else 0
    q4_avg = sum(q4) / len(q4) if q4 else 0

    print(f"  左上（坤艮坎巽/坤艮坎巽）: {q2_avg:.3f}")
    print(f"  右上（震離兌乾/坤艮坎巽）: {q1_avg:.3f}")
    print(f"  左下（坤艮坎巽/震離兌乾）: {q3_avg:.3f}")
    print(f"  右下（震離兌乾/震離兌乾）: {q4_avg:.3f}")

    # 陰陽分析（坤艮坎巽為陰系，震離兌乾為陽系）
    yin_yin = q2_avg
    yin_yang = q1_avg
    yang_yin = q3_avg
    yang_yang = q4_avg

    print(f"\n  陰下陰上: {yin_yin:.3f}")
    print(f"  陰下陽上: {yang_yin:.3f}")
    print(f"  陽下陰上: {yin_yang:.3f}")
    print(f"  陽下陽上: {yang_yang:.3f}")

def analyze_row_col_correlation(grid, name):
    """行列相關性"""
    print(f"\n【行列相關性 - {name}】")

    n = len(grid)

    # 行平均
    row_avgs = [sum(grid[i]) / n for i in range(n)]

    # 列平均
    col_avgs = [sum(grid[i][j] for i in range(n)) / n for j in range(n)]

    print(f"\n  行平均（上卦，坤→乾）:")
    for i, (name_t, avg) in enumerate(zip(TRIGRAM_NAMES, row_avgs)):
        bar = "█" * int(avg * 20) if avg > 0 else ""
        print(f"    {name_t}: {avg:+.3f} {bar}")

    print(f"\n  列平均（下卦，坤→乾）:")
    for j, (name_t, avg) in enumerate(zip(TRIGRAM_NAMES, col_avgs)):
        bar = "█" * int(avg * 20) if avg > 0 else ""
        print(f"    {name_t}: {avg:+.3f} {bar}")

    # 行列相關性
    mean_r = sum(row_avgs) / n
    mean_c = sum(col_avgs) / n

    cov = sum((row_avgs[i] - mean_r) * (col_avgs[i] - mean_c) for i in range(n)) / n
    std_r = math.sqrt(sum((r - mean_r)**2 for r in row_avgs) / n)
    std_c = math.sqrt(sum((c - mean_c)**2 for c in col_avgs) / n)

    if std_r > 0 and std_c > 0:
        corr = cov / (std_r * std_c)
        print(f"\n  行列相關係數: {corr:.3f}")
        if abs(corr) > 0.5:
            print(f"  → 上下卦對{name}有相似影響！")

def analyze_special_positions(grid, name):
    """特殊位置分析"""
    print(f"\n【特殊位置分析 - {name}】")

    # 八卦屬性
    attributes = {
        '乾': ('陽', '天', '剛'),
        '坤': ('陰', '地', '柔'),
        '震': ('陽', '雷', '動'),
        '巽': ('陰', '風', '入'),
        '坎': ('陽', '水', '險'),
        '離': ('陰', '火', '麗'),
        '艮': ('陽', '山', '止'),
        '兌': ('陰', '澤', '悅'),
    }

    # 檢查各種組合
    print("\n  特殊組合檢查:")

    # 相錯卦（陰陽完全相反）
    opposite_pairs = [('乾', '坤'), ('震', '巽'), ('坎', '離'), ('艮', '兌')]
    for t1, t2 in opposite_pairs:
        i1, i2 = TRIGRAM_TO_IDX[t1], TRIGRAM_TO_IDX[t2]
        val1 = grid[i1][i1]  # t1上t1下
        val2 = grid[i2][i2]  # t2上t2下
        val3 = grid[i1][i2]  # t1上t2下
        val4 = grid[i2][i1]  # t2上t1下
        print(f"    {t1}配對{t2}: 同{t1}={val1:.2f}, 同{t2}={val2:.2f}, {t1}上{t2}下={val3:.2f}, {t2}上{t1}下={val4:.2f}")

def build_3d_cube(data, struct_data):
    """構建3D立方體（下卦×上卦×爻位）"""
    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 8x8x6 立方體
    cube = [[[[] for _ in range(6)] for _ in range(8)] for _ in range(8)]

    for d in data:
        hex_num = d['hex_num']
        if hex_num not in hex_to_trigrams:
            continue

        lower, upper = hex_to_trigrams[hex_num]
        col = TRIGRAM_TO_IDX[lower]
        row = TRIGRAM_TO_IDX[upper]
        depth = d['position'] - 1

        cube[row][col][depth].append(d['label'])

    return cube

def analyze_3d_patterns(cube):
    """3D模式分析"""
    print("\n" + "=" * 70)
    print("3D 立方體模式分析")
    print("=" * 70)

    # 計算每個cell的平均值
    avg_cube = [[[
        sum(cube[i][j][k]) / len(cube[i][j][k]) if cube[i][j][k] else 0
        for k in range(6)] for j in range(8)] for i in range(8)]

    # 按層切片
    print("\n【層切片分析（爻位1-6）】")
    for layer in range(6):
        layer_vals = [avg_cube[i][j][layer] for i in range(8) for j in range(8)]
        layer_avg = sum(layer_vals) / len(layer_vals) if layer_vals else 0
        print(f"  爻位{layer+1}: 平均 {layer_avg:+.3f}")

    # 3D梯度
    print("\n【3D梯度分析】")

    # Z方向梯度（爻位方向）
    z_gradients = []
    for i in range(8):
        for j in range(8):
            if avg_cube[i][j][5] != 0 or avg_cube[i][j][0] != 0:
                grad = (avg_cube[i][j][5] - avg_cube[i][j][0]) / 5
                z_gradients.append(grad)

    avg_z_grad = sum(z_gradients) / len(z_gradients) if z_gradients else 0
    print(f"  Z梯度（爻1→爻6）: {avg_z_grad:+.4f}")

    # 3D對稱性
    print("\n【3D對稱性】")

    # 關於中心層(3-4)的對稱
    z_sym_diff = 0
    z_sym_total = 0
    for i in range(8):
        for j in range(8):
            for k in range(3):
                z_sym_diff += abs(avg_cube[i][j][k] - avg_cube[i][j][5-k])
                z_sym_total += abs(avg_cube[i][j][k]) + abs(avg_cube[i][j][5-k])

    z_sym = 1 - z_sym_diff / z_sym_total if z_sym_total > 0 else 0
    print(f"  Z軸對稱度（爻1-3 vs 爻4-6）: {z_sym:.1%}")

def main():
    print("=" * 70)
    print("深度2D/3D模式搜尋")
    print("=" * 70)

    data = load_corrected_data()
    struct_data = load_structure()

    # 構建2D網格
    grids = build_2d_grids(data, struct_data)

    # 對每個網格進行分析
    for grid_name, grid in [('吉率', grids['ji']),
                             ('淨分', grids['net']),
                             ('變化次數', grids['change'])]:

        print("\n" + "=" * 70)
        print(f"分析: {grid_name}")
        print("=" * 70)

        analyze_diagonal_patterns(grid, grid_name)
        analyze_symmetry(grid, grid_name)
        analyze_gradient(grid, grid_name)
        analyze_checkerboard(grid, grid_name)
        analyze_center_vs_edge(grid, grid_name)
        analyze_quadrants(grid, grid_name)
        analyze_row_col_correlation(grid, grid_name)
        analyze_special_positions(grid, grid_name)

    # 3D分析
    cube = build_3d_cube(data, struct_data)
    analyze_3d_patterns(cube)

if __name__ == "__main__":
    main()
