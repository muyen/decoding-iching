#!/usr/bin/env python3
"""
3D 可視化分析

三個維度：
- X軸: 上卦 (0-7)
- Y軸: 下卦 (0-7)
- Z軸: 爻位 (1-6)

總共 8×8×6 = 384 個點，對應所有爻
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import defaultdict
import os

# ============================================================
# 數據
# ============================================================

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

BAGUA_NAMES = ["坤", "震", "坎", "兌", "艮", "離", "巽", "乾"]

def predict_structure(pos: int, binary: str) -> int:
    """純結構預測"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]

    if xor_val == 4 and pos <= 4:
        return 1
    if xor_val == 0 and is_central:
        return 1
    if upper == 0 and pos == 2:
        return 1

    score = 0.0
    pos_weights = {5: 0.7, 2: 0.5, 6: -0.7, 3: -0.1}
    score += pos_weights.get(pos, 0)
    upper_weights = {0: 0.35, 7: 0.15, 4: 0.2, 3: -0.35, 6: -0.3}
    score += upper_weights.get(upper, 0)
    lower_weights = {4: 0.45, 6: 0.2, 1: 0.1}
    score += lower_weights.get(lower, 0)

    if score >= 0.6:
        return 1
    elif score <= -0.3:
        return -1
    return 0

def prepare_3d_data():
    """準備3D數據"""
    predictable = []
    special = []

    for gua_num, pos, binary, actual in SAMPLES:
        upper = int(binary[0:3], 2)
        lower = int(binary[3:6], 2)
        prediction = predict_structure(pos, binary)

        point = {
            'x': upper,
            'y': lower,
            'z': pos,
            'gua_num': gua_num,
            'actual': actual,
            'prediction': prediction,
            'is_special': prediction != actual
        }

        if prediction == actual:
            predictable.append(point)
        else:
            special.append(point)

    return predictable, special

# ============================================================
# 3D 可視化
# ============================================================

def plot_3d_scatter(predictable, special, save_path=None):
    """3D散點圖"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 可預測點（綠色，較小）
    if predictable:
        px = [p['x'] for p in predictable]
        py = [p['y'] for p in predictable]
        pz = [p['z'] for p in predictable]
        ax.scatter(px, py, pz, c='green', alpha=0.3, s=30, label='Predictable')

    # 特殊點（紅色，較大）
    if special:
        sx = [p['x'] for p in special]
        sy = [p['y'] for p in special]
        sz = [p['z'] for p in special]
        ax.scatter(sx, sy, sz, c='red', alpha=0.8, s=100, marker='^', label='Needs 爻辭')

    # 設置軸標籤
    ax.set_xlabel('Upper Trigram (上卦)', fontsize=12)
    ax.set_ylabel('Lower Trigram (下卦)', fontsize=12)
    ax.set_zlabel('Yao Position (爻位)', fontsize=12)

    ax.set_xticks(range(8))
    ax.set_xticklabels(BAGUA_NAMES)
    ax.set_yticks(range(8))
    ax.set_yticklabels(BAGUA_NAMES)
    ax.set_zticks(range(1, 7))

    ax.set_title('3D Distribution of Special Yao in I Ching\n'
                 '(Red = Needs 爻辭, Green = Structure Predictable)', fontsize=14)
    ax.legend()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_3d_by_yao_position(predictable, special, save_path=None):
    """按爻位分層的3D視圖"""
    fig = plt.figure(figsize=(16, 10))

    for pos in range(1, 7):
        ax = fig.add_subplot(2, 3, pos, projection='3d')

        # 過濾該爻位的數據
        pred_pos = [p for p in predictable if p['z'] == pos]
        spec_pos = [p for p in special if p['z'] == pos]

        # 繪製
        if pred_pos:
            ax.scatter([p['x'] for p in pred_pos],
                      [p['y'] for p in pred_pos],
                      [0]*len(pred_pos),
                      c='green', alpha=0.5, s=50)

        if spec_pos:
            ax.scatter([p['x'] for p in spec_pos],
                      [p['y'] for p in spec_pos],
                      [0.5]*len(spec_pos),
                      c='red', alpha=0.8, s=100, marker='^')

        ax.set_xlabel('Upper')
        ax.set_ylabel('Lower')
        ax.set_title(f'Yao Position {pos}')
        ax.set_xticks(range(8))
        ax.set_yticks(range(8))
        ax.set_zlim(-0.5, 1)

        # 計算該爻位的特殊比例
        total = len(pred_pos) + len(spec_pos)
        if total > 0:
            ratio = len(spec_pos) / total * 100
            ax.text2D(0.05, 0.95, f"Special: {ratio:.0f}%", transform=ax.transAxes)

    plt.suptitle('Special Yao Distribution by Position (Layer View)', fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_3d_slices(predictable, special, save_path=None):
    """XY平面切片（每個Z層）"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for pos in range(1, 7):
        ax = axes[pos - 1]

        # 創建8x8網格
        grid = np.zeros((8, 8))
        special_grid = np.zeros((8, 8))

        for p in predictable:
            if p['z'] == pos:
                grid[p['y'], p['x']] += 1

        for p in special:
            if p['z'] == pos:
                grid[p['y'], p['x']] += 1
                special_grid[p['y'], p['x']] += 1

        # 計算比例
        ratio_grid = np.zeros((8, 8))
        for i in range(8):
            for j in range(8):
                if grid[i, j] > 0:
                    ratio_grid[i, j] = special_grid[i, j] / grid[i, j]

        im = ax.imshow(ratio_grid, cmap='RdYlGn_r', origin='lower', vmin=0, vmax=1)
        ax.set_xticks(range(8))
        ax.set_yticks(range(8))
        ax.set_xticklabels(BAGUA_NAMES, fontsize=8)
        ax.set_yticklabels(BAGUA_NAMES, fontsize=8)
        ax.set_xlabel('Upper')
        ax.set_ylabel('Lower')
        ax.set_title(f'Position {pos} (Z={pos})')

        # 添加數值標籤
        for i in range(8):
            for j in range(8):
                if grid[i, j] > 0:
                    text = f'{ratio_grid[i, j]:.0%}'
                    color = 'white' if ratio_grid[i, j] > 0.5 else 'black'
                    ax.text(j, i, text, ha='center', va='center', fontsize=7, color=color)

    plt.suptitle('Special Yao Ratio by XY Position at Each Z Layer\n'
                 '(Red = High Special Ratio, Green = Low)', fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_3d_projections(predictable, special, save_path=None):
    """三個投影面"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # XZ投影 (Upper vs Position)
    ax1 = axes[0]
    xz_grid = defaultdict(lambda: {'total': 0, 'special': 0})
    for p in predictable + special:
        key = (p['x'], p['z'])
        xz_grid[key]['total'] += 1
    for p in special:
        key = (p['x'], p['z'])
        xz_grid[key]['special'] += 1

    matrix_xz = np.zeros((6, 8))
    for (x, z), v in xz_grid.items():
        if v['total'] > 0:
            matrix_xz[z-1, x] = v['special'] / v['total']

    im1 = ax1.imshow(matrix_xz, cmap='RdYlGn_r', origin='lower', aspect='auto')
    ax1.set_xticks(range(8))
    ax1.set_xticklabels(BAGUA_NAMES)
    ax1.set_yticks(range(6))
    ax1.set_yticklabels(range(1, 7))
    ax1.set_xlabel('Upper Trigram (上卦)')
    ax1.set_ylabel('Yao Position')
    ax1.set_title('XZ Projection (Upper vs Position)')
    plt.colorbar(im1, ax=ax1, label='Special Ratio')

    # YZ投影 (Lower vs Position)
    ax2 = axes[1]
    yz_grid = defaultdict(lambda: {'total': 0, 'special': 0})
    for p in predictable + special:
        key = (p['y'], p['z'])
        yz_grid[key]['total'] += 1
    for p in special:
        key = (p['y'], p['z'])
        yz_grid[key]['special'] += 1

    matrix_yz = np.zeros((6, 8))
    for (y, z), v in yz_grid.items():
        if v['total'] > 0:
            matrix_yz[z-1, y] = v['special'] / v['total']

    im2 = ax2.imshow(matrix_yz, cmap='RdYlGn_r', origin='lower', aspect='auto')
    ax2.set_xticks(range(8))
    ax2.set_xticklabels(BAGUA_NAMES)
    ax2.set_yticks(range(6))
    ax2.set_yticklabels(range(1, 7))
    ax2.set_xlabel('Lower Trigram (下卦)')
    ax2.set_ylabel('Yao Position')
    ax2.set_title('YZ Projection (Lower vs Position)')
    plt.colorbar(im2, ax=ax2, label='Special Ratio')

    # XY投影 (Upper vs Lower) - 已經有了，但再做一次平均
    ax3 = axes[2]
    xy_grid = defaultdict(lambda: {'total': 0, 'special': 0})
    for p in predictable + special:
        key = (p['x'], p['y'])
        xy_grid[key]['total'] += 1
    for p in special:
        key = (p['x'], p['y'])
        xy_grid[key]['special'] += 1

    matrix_xy = np.zeros((8, 8))
    for (x, y), v in xy_grid.items():
        if v['total'] > 0:
            matrix_xy[y, x] = v['special'] / v['total']

    im3 = ax3.imshow(matrix_xy, cmap='RdYlGn_r', origin='lower')
    ax3.set_xticks(range(8))
    ax3.set_xticklabels(BAGUA_NAMES)
    ax3.set_yticks(range(8))
    ax3.set_yticklabels(BAGUA_NAMES)
    ax3.set_xlabel('Upper Trigram (上卦)')
    ax3.set_ylabel('Lower Trigram (下卦)')
    ax3.set_title('XY Projection (Upper vs Lower)')
    plt.colorbar(im3, ax=ax3, label='Special Ratio')

    plt.suptitle('3D Projections: Special Yao Distribution', fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_3d_analysis_summary(predictable, special, save_path=None):
    """3D分析總結圖"""
    fig = plt.figure(figsize=(18, 12))

    # 1. 主3D散點圖
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')

    if predictable:
        ax1.scatter([p['x'] for p in predictable],
                   [p['y'] for p in predictable],
                   [p['z'] for p in predictable],
                   c='green', alpha=0.3, s=30, label='Predictable')
    if special:
        ax1.scatter([p['x'] for p in special],
                   [p['y'] for p in special],
                   [p['z'] for p in special],
                   c='red', alpha=0.8, s=100, marker='^', label='Special')

    ax1.set_xlabel('Upper (X)')
    ax1.set_ylabel('Lower (Y)')
    ax1.set_zlabel('Position (Z)')
    ax1.set_title('3D Scatter: All Samples')
    ax1.legend()

    # 2. Z軸分布（爻位）
    ax2 = fig.add_subplot(2, 2, 2)
    z_counts = defaultdict(lambda: {'total': 0, 'special': 0})
    for p in predictable + special:
        z_counts[p['z']]['total'] += 1
    for p in special:
        z_counts[p['z']]['special'] += 1

    positions = list(range(1, 7))
    totals = [z_counts[z]['total'] for z in positions]
    specials = [z_counts[z]['special'] for z in positions]
    ratios = [s/t if t > 0 else 0 for s, t in zip(specials, totals)]

    x = np.arange(6)
    width = 0.35
    ax2.bar(x - width/2, totals, width, label='Total', alpha=0.7)
    ax2.bar(x + width/2, specials, width, label='Special', color='red', alpha=0.7)

    ax2.set_xticks(x)
    ax2.set_xticklabels(positions)
    ax2.set_xlabel('Yao Position')
    ax2.set_ylabel('Count')
    ax2.set_title('Distribution by Z (Yao Position)')
    ax2.legend()

    # 添加比例標籤
    for i, (r, t) in enumerate(zip(ratios, totals)):
        if t > 0:
            ax2.text(i, t + 0.5, f'{r:.0%}', ha='center', fontsize=10)

    # 3. X軸分布（上卦）
    ax3 = fig.add_subplot(2, 2, 3)
    x_counts = defaultdict(lambda: {'total': 0, 'special': 0})
    for p in predictable + special:
        x_counts[p['x']]['total'] += 1
    for p in special:
        x_counts[p['x']]['special'] += 1

    trigrams = list(range(8))
    totals_x = [x_counts[x]['total'] for x in trigrams]
    specials_x = [x_counts[x]['special'] for x in trigrams]
    ratios_x = [s/t if t > 0 else 0 for s, t in zip(specials_x, totals_x)]

    x = np.arange(8)
    ax3.bar(x - width/2, totals_x, width, label='Total', alpha=0.7)
    ax3.bar(x + width/2, specials_x, width, label='Special', color='red', alpha=0.7)

    ax3.set_xticks(x)
    ax3.set_xticklabels(BAGUA_NAMES)
    ax3.set_xlabel('Upper Trigram')
    ax3.set_ylabel('Count')
    ax3.set_title('Distribution by X (Upper Trigram)')
    ax3.legend()

    for i, (r, t) in enumerate(zip(ratios_x, totals_x)):
        if t > 0:
            ax3.text(i, t + 0.3, f'{r:.0%}', ha='center', fontsize=9)

    # 4. Y軸分布（下卦）
    ax4 = fig.add_subplot(2, 2, 4)
    y_counts = defaultdict(lambda: {'total': 0, 'special': 0})
    for p in predictable + special:
        y_counts[p['y']]['total'] += 1
    for p in special:
        y_counts[p['y']]['special'] += 1

    totals_y = [y_counts[y]['total'] for y in trigrams]
    specials_y = [y_counts[y]['special'] for y in trigrams]
    ratios_y = [s/t if t > 0 else 0 for s, t in zip(specials_y, totals_y)]

    ax4.bar(x - width/2, totals_y, width, label='Total', alpha=0.7)
    ax4.bar(x + width/2, specials_y, width, label='Special', color='red', alpha=0.7)

    ax4.set_xticks(x)
    ax4.set_xticklabels(BAGUA_NAMES)
    ax4.set_xlabel('Lower Trigram')
    ax4.set_ylabel('Count')
    ax4.set_title('Distribution by Y (Lower Trigram)')
    ax4.legend()

    for i, (r, t) in enumerate(zip(ratios_y, totals_y)):
        if t > 0:
            ax4.text(i, t + 0.3, f'{r:.0%}', ha='center', fontsize=9)

    plt.suptitle('3D Analysis Summary: Special Yao in I Ching Space', fontsize=16)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

# ============================================================
# 主程序
# ============================================================

def main():
    print("生成3D可視化...\n")

    predictable, special = prepare_3d_data()
    print(f"可預測: {len(predictable)}, 特殊: {len(special)}")

    output_dir = "docs/figures"
    os.makedirs(output_dir, exist_ok=True)

    # 生成所有圖表
    plot_3d_scatter(predictable, special, f"{output_dir}/3d_scatter.png")
    plot_3d_by_yao_position(predictable, special, f"{output_dir}/3d_by_position.png")
    plot_3d_slices(predictable, special, f"{output_dir}/3d_xy_slices.png")
    plot_3d_projections(predictable, special, f"{output_dir}/3d_projections.png")
    plot_3d_analysis_summary(predictable, special, f"{output_dir}/3d_analysis_summary.png")

    print(f"\n所有3D圖表已保存至 {output_dir}/")

    # 打印統計
    print("\n【3D空間統計】")
    print(f"  X軸（上卦）範圍: 0-7")
    print(f"  Y軸（下卦）範圍: 0-7")
    print(f"  Z軸（爻位）範圍: 1-6")
    print(f"  總空間大小: 8×8×6 = 384")
    print(f"  採樣點: {len(predictable) + len(special)}")
    print(f"  特殊點: {len(special)} ({len(special)/(len(predictable)+len(special))*100:.1f}%)")


if __name__ == "__main__":
    main()
