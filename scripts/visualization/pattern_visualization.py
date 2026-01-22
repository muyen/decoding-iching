#!/usr/bin/env python3
"""
爻辭特殊標記模式可視化

生成高質量圖表：
1. 1D線性位置分布圖
2. 2D八卦網格熱力圖
3. 數學模式分析圖
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager
import math
from collections import defaultdict
import json

# 嘗試設置中文字體
try:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

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

GUA_NAMES = {
    1: "乾", 2: "坤", 3: "屯", 4: "蒙", 5: "需", 6: "訟",
    15: "謙", 17: "隨", 20: "觀", 24: "復", 25: "無妄",
    33: "遯", 47: "困", 50: "鼎", 63: "既濟"
}

BAGUA_NAMES = ["坤", "震", "坎", "兌", "艮", "離", "巽", "乾"]

PHI = (1 + math.sqrt(5)) / 2  # 黃金比例
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

# ============================================================
# 輔助函數
# ============================================================

def binary_to_upper_lower(binary):
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    return upper, lower

def get_linear_position(gua_num, yao_pos):
    return (gua_num - 1) * 6 + yao_pos

def predict_by_structure(pos, binary):
    upper, lower = binary_to_upper_lower(binary)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]
    line = int(binary[6 - pos])

    if xor_val == 4 and pos <= 4:
        return 1
    if xor_val == 0 and is_central:
        return 1
    if upper == 0 and pos == 2:
        return 1

    score = 0.0
    pos_weights = {5: 0.7, 2: 0.5, 6: -0.7, 3: -0.1, 1: 0, 4: 0}
    score += pos_weights.get(pos, 0)
    upper_weights = {0: 0.35, 7: 0.15, 4: 0.2, 3: -0.35, 6: -0.3}
    score += upper_weights.get(upper, 0)
    lower_weights = {4: 0.45, 6: 0.2, 1: 0.1}
    score += lower_weights.get(lower, 0)

    if score >= 0.6:
        return 1
    elif score <= -0.3:
        return -1
    else:
        return 0

def analyze_samples():
    """分析所有樣本，返回可預測和特殊爻列表"""
    predictable = []
    special = []

    for gua_num, pos, binary, actual in SAMPLES:
        upper, lower = binary_to_upper_lower(binary)
        prediction = predict_by_structure(pos, binary)
        linear_pos = get_linear_position(gua_num, pos)

        data = {
            'gua_num': gua_num,
            'pos': pos,
            'binary': binary,
            'actual': actual,
            'prediction': prediction,
            'linear_pos': linear_pos,
            'grid_x': upper,
            'grid_y': lower,
            'is_predictable': prediction == actual
        }

        if prediction == actual:
            predictable.append(data)
        else:
            special.append(data)

    return predictable, special

# ============================================================
# 可視化函數
# ============================================================

def plot_1d_linear(predictable, special, save_path=None):
    """1D線性位置分布圖"""
    fig, axes = plt.subplots(2, 1, figsize=(16, 8))

    # 上圖：完整384位置分布
    ax1 = axes[0]
    all_positions = np.zeros(384)
    special_positions = [s['linear_pos'] for s in special]

    for pos in special_positions:
        if 1 <= pos <= 384:
            all_positions[pos - 1] = 1

    ax1.bar(range(1, 385), all_positions, width=1, color='red', alpha=0.7)

    # 標記黃金分割點
    golden_point = 384 / PHI
    ax1.axvline(x=golden_point, color='gold', linestyle='--', linewidth=2, label=f'Golden Point ({golden_point:.1f})')

    # 標記Fibonacci位置
    for fib in FIBONACCI:
        if fib <= 384:
            ax1.axvline(x=fib, color='green', linestyle=':', alpha=0.5)

    ax1.set_xlabel('Linear Position (1-384)')
    ax1.set_ylabel('Needs Yi Ci (1=Yes)')
    ax1.set_title('1D Linear Distribution of Special Yao (Needs 爻辭)')
    ax1.legend()
    ax1.set_xlim(0, 384)

    # 下圖：間距分布
    ax2 = axes[1]
    if len(special_positions) > 1:
        sorted_pos = sorted(special_positions)
        intervals = [sorted_pos[i+1] - sorted_pos[i] for i in range(len(sorted_pos)-1)]

        ax2.bar(range(len(intervals)), intervals, color='blue', alpha=0.7)
        ax2.axhline(y=PHI, color='gold', linestyle='--', label=f'φ = {PHI:.3f}')
        ax2.axhline(y=PHI * 10, color='orange', linestyle='--', alpha=0.5, label=f'10φ = {PHI*10:.1f}')

        # 標記Fibonacci間距
        for i, interval in enumerate(intervals):
            if interval in FIBONACCI:
                ax2.bar(i, interval, color='green', alpha=0.9)

        ax2.set_xlabel('Interval Index')
        ax2.set_ylabel('Interval Size')
        ax2.set_title('Intervals Between Special Yao Positions (Green = Fibonacci)')
        ax2.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_2d_bagua_heatmap(predictable, special, save_path=None):
    """2D八卦網格熱力圖"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # 建立網格
    total_grid = np.zeros((8, 8))
    special_grid = np.zeros((8, 8))

    for s in special:
        x, y = s['grid_x'], s['grid_y']
        special_grid[y, x] += 1

    for p in predictable:
        x, y = p['grid_x'], p['grid_y']
        total_grid[y, x] += 1

    for s in special:
        x, y = s['grid_x'], s['grid_y']
        total_grid[y, x] += 1

    # 左圖：特殊爻數量
    ax1 = axes[0]
    im1 = ax1.imshow(special_grid, cmap='Reds', origin='lower')
    ax1.set_xticks(range(8))
    ax1.set_yticks(range(8))
    ax1.set_xticklabels(BAGUA_NAMES)
    ax1.set_yticklabels(BAGUA_NAMES)
    ax1.set_xlabel('Upper Trigram (上卦)')
    ax1.set_ylabel('Lower Trigram (下卦)')
    ax1.set_title('Special Yao Count (Needs 爻辭)')

    # 添加數值標籤
    for i in range(8):
        for j in range(8):
            if special_grid[i, j] > 0:
                ax1.text(j, i, int(special_grid[i, j]), ha='center', va='center', color='white', fontsize=12, fontweight='bold')

    plt.colorbar(im1, ax=ax1, label='Count')

    # 右圖：特殊爻比例
    ax2 = axes[1]
    ratio_grid = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            if total_grid[i, j] > 0:
                ratio_grid[i, j] = special_grid[i, j] / total_grid[i, j]

    im2 = ax2.imshow(ratio_grid, cmap='RdYlGn_r', origin='lower', vmin=0, vmax=1)
    ax2.set_xticks(range(8))
    ax2.set_yticks(range(8))
    ax2.set_xticklabels(BAGUA_NAMES)
    ax2.set_yticklabels(BAGUA_NAMES)
    ax2.set_xlabel('Upper Trigram (上卦)')
    ax2.set_ylabel('Lower Trigram (下卦)')
    ax2.set_title('Ratio of Special Yao (Red = High)')

    # 添加比例標籤
    for i in range(8):
        for j in range(8):
            if total_grid[i, j] > 0:
                text = f'{ratio_grid[i, j]:.0%}'
                color = 'white' if ratio_grid[i, j] > 0.5 else 'black'
                ax2.text(j, i, text, ha='center', va='center', color=color, fontsize=10)

    plt.colorbar(im2, ax=ax2, label='Ratio')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_mathematical_patterns(special, save_path=None):
    """數學模式分析圖"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    positions = sorted([s['linear_pos'] for s in special])

    # 1. 位置分布直方圖
    ax1 = axes[0, 0]
    ax1.hist(positions, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(x=384/PHI, color='gold', linestyle='--', linewidth=2, label=f'φ point ({384/PHI:.1f})')
    ax1.set_xlabel('Linear Position')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Special Yao Positions')
    ax1.legend()

    # 2. 模運算分析
    ax2 = axes[0, 1]
    mods = [7, 8, 12, 24]
    mod_data = {}
    for m in mods:
        counts = defaultdict(int)
        for p in positions:
            counts[p % m] += 1
        mod_data[m] = counts

    x = np.arange(max(mods))
    width = 0.2
    for i, m in enumerate(mods):
        values = [mod_data[m].get(j, 0) for j in range(m)]
        ax2.bar(np.arange(m) + i*width, values, width, label=f'mod {m}', alpha=0.7)

    ax2.set_xlabel('Remainder')
    ax2.set_ylabel('Count')
    ax2.set_title('Modular Arithmetic Analysis')
    ax2.legend()

    # 3. Fibonacci間距匹配
    ax3 = axes[1, 0]
    if len(positions) > 1:
        intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        fib_matches = [i for i in intervals if i in FIBONACCI]
        non_fib = [i for i in intervals if i not in FIBONACCI]

        ax3.hist([non_fib, fib_matches], bins=15, label=['Non-Fibonacci', 'Fibonacci'],
                 color=['gray', 'green'], stacked=True, edgecolor='black')
        ax3.set_xlabel('Interval Size')
        ax3.set_ylabel('Frequency')
        ax3.set_title(f'Interval Distribution (Fibonacci matches: {len(fib_matches)}/{len(intervals)})')
        ax3.legend()

    # 4. 質數位置分析
    ax4 = axes[1, 1]
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    prime_positions = [p for p in positions if is_prime(p)]
    non_prime_positions = [p for p in positions if not is_prime(p)]

    ax4.scatter(non_prime_positions, [0]*len(non_prime_positions), c='gray', s=100, label='Non-prime', alpha=0.5)
    ax4.scatter(prime_positions, [0]*len(prime_positions), c='red', s=150, marker='*', label='Prime')

    ax4.set_xlabel('Linear Position')
    ax4.set_title(f'Prime Number Positions ({len(prime_positions)}/{len(positions)} = {len(prime_positions)/len(positions)*100:.1f}%)')
    ax4.legend()
    ax4.set_ylim(-1, 1)
    ax4.set_yticks([])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_solar_terms_analysis(special, save_path=None):
    """節氣對應分析圖"""
    SOLAR_TERMS_24 = [
        "立春", "雨水", "驚蟄", "春分", "清明", "穀雨",
        "立夏", "小滿", "芒種", "夏至", "小暑", "大暑",
        "立秋", "處暑", "白露", "秋分", "寒露", "霜降",
        "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"
    ]

    fig, ax = plt.subplots(figsize=(14, 6))

    # 統計每個節氣的特殊爻
    term_counts = defaultdict(int)
    term_total = defaultdict(int)

    for gua_num, pos, binary, actual in SAMPLES:
        term_index = ((gua_num - 1) // 3) % 24
        term_total[term_index] += 1

    for s in special:
        term_index = ((s['gua_num'] - 1) // 3) % 24
        term_counts[term_index] += 1

    # 繪製
    x = np.arange(24)
    totals = [term_total[i] for i in range(24)]
    specials = [term_counts[i] for i in range(24)]
    ratios = [specials[i]/totals[i] if totals[i] > 0 else 0 for i in range(24)]

    bars = ax.bar(x, ratios, color='steelblue', edgecolor='black')

    # 標記高比例節氣
    for i, ratio in enumerate(ratios):
        if ratio > 0.5:
            bars[i].set_color('red')

    ax.axhline(y=0.5, color='orange', linestyle='--', label='50% threshold')

    ax.set_xticks(x)
    ax.set_xticklabels(SOLAR_TERMS_24, rotation=45, ha='right')
    ax.set_xlabel('Solar Terms (節氣)')
    ax.set_ylabel('Ratio of Special Yao')
    ax.set_title('Special Yao Distribution by Solar Terms (Red > 50%)')
    ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

def plot_comprehensive_dashboard(predictable, special, save_path=None):
    """綜合儀表板"""
    fig = plt.figure(figsize=(20, 16))

    # 1. 1D分布 (頂部)
    ax1 = fig.add_subplot(3, 2, (1, 2))
    special_positions = [s['linear_pos'] for s in special]
    ax1.bar(special_positions, [1]*len(special_positions), width=3, color='red', alpha=0.7)
    ax1.axvline(x=384/PHI, color='gold', linestyle='--', linewidth=2, label=f'Golden Point')
    ax1.set_xlim(0, 384)
    ax1.set_xlabel('Linear Position (1-384)')
    ax1.set_title('1D Linear Distribution of Special Yao')
    ax1.legend()

    # 2. 2D熱力圖 (左中)
    ax2 = fig.add_subplot(3, 2, 3)
    special_grid = np.zeros((8, 8))
    for s in special:
        x, y = s['grid_x'], s['grid_y']
        special_grid[y, x] += 1
    im2 = ax2.imshow(special_grid, cmap='Reds', origin='lower')
    ax2.set_xticks(range(8))
    ax2.set_yticks(range(8))
    ax2.set_xticklabels(BAGUA_NAMES)
    ax2.set_yticklabels(BAGUA_NAMES)
    ax2.set_title('2D Bagua Heatmap')
    plt.colorbar(im2, ax=ax2)

    # 3. 象限分析 (右中)
    ax3 = fig.add_subplot(3, 2, 4)
    quadrants = {'Q1\n(上右)': 0, 'Q2\n(上左)': 0, 'Q3\n(下左)': 0, 'Q4\n(下右)': 0}
    quadrant_total = {'Q1\n(上右)': 0, 'Q2\n(上左)': 0, 'Q3\n(下左)': 0, 'Q4\n(下右)': 0}

    for s in special:
        x, y = s['grid_x'], s['grid_y']
        if x >= 4 and y >= 4:
            quadrants['Q1\n(上右)'] += 1
        elif x < 4 and y >= 4:
            quadrants['Q2\n(上左)'] += 1
        elif x < 4 and y < 4:
            quadrants['Q3\n(下左)'] += 1
        else:
            quadrants['Q4\n(下右)'] += 1

    for p in predictable:
        x, y = p['grid_x'], p['grid_y']
        if x >= 4 and y >= 4:
            quadrant_total['Q1\n(上右)'] += 1
        elif x < 4 and y >= 4:
            quadrant_total['Q2\n(上左)'] += 1
        elif x < 4 and y < 4:
            quadrant_total['Q3\n(下左)'] += 1
        else:
            quadrant_total['Q4\n(下右)'] += 1

    for s in special:
        x, y = s['grid_x'], s['grid_y']
        if x >= 4 and y >= 4:
            quadrant_total['Q1\n(上右)'] += 1
        elif x < 4 and y >= 4:
            quadrant_total['Q2\n(上左)'] += 1
        elif x < 4 and y < 4:
            quadrant_total['Q3\n(下左)'] += 1
        else:
            quadrant_total['Q4\n(下右)'] += 1

    ratios = [quadrants[q]/quadrant_total[q] if quadrant_total[q] > 0 else 0 for q in quadrants.keys()]
    colors = ['green' if r < 0.4 else 'red' for r in ratios]
    ax3.bar(quadrants.keys(), ratios, color=colors, edgecolor='black')
    ax3.axhline(y=0.4, color='orange', linestyle='--')
    ax3.set_ylabel('Special Yao Ratio')
    ax3.set_title('Quadrant Analysis')

    # 4. 間距分布 (左下)
    ax4 = fig.add_subplot(3, 2, 5)
    if len(special_positions) > 1:
        sorted_pos = sorted(special_positions)
        intervals = [sorted_pos[i+1] - sorted_pos[i] for i in range(len(sorted_pos)-1)]
        fib_intervals = [i for i in intervals if i in FIBONACCI]
        ax4.hist(intervals, bins=15, color='steelblue', edgecolor='black', alpha=0.7)
        ax4.set_xlabel('Interval Size')
        ax4.set_ylabel('Frequency')
        ax4.set_title(f'Interval Distribution (Fib matches: {len(fib_intervals)}/{len(intervals)})')

    # 5. 統計摘要 (右下)
    ax5 = fig.add_subplot(3, 2, 6)
    ax5.axis('off')
    summary_text = f"""
    === Pattern Analysis Summary ===

    Total Samples: {len(SAMPLES)}
    Predictable: {len(predictable)} ({len(predictable)/len(SAMPLES)*100:.1f}%)
    Needs 爻辭: {len(special)} ({len(special)/len(SAMPLES)*100:.1f}%)

    Mathematical Patterns:
    - Golden ratio point: {384/PHI:.1f}
    - Fibonacci interval matches: {len([i for i in intervals if i in FIBONACCI]) if len(special_positions) > 1 else 0}
    - Prime positions: {len([p for p in special_positions if all(p % i != 0 for i in range(2, int(p**0.5)+1)) and p > 1])}

    Spatial Distribution:
    - Lower-left quadrant: {quadrants['Q3\n(下左)']} special ({ratios[2]*100:.1f}%)
    - Upper-right quadrant: {quadrants['Q1\n(上右)']} special ({ratios[0]*100:.1f}%)
    """
    ax5.text(0.1, 0.9, summary_text, transform=ax5.transAxes, fontsize=12,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.suptitle('I Ching Special Yao Pattern Analysis Dashboard', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig

# ============================================================
# 主程序
# ============================================================

def main():
    print("Generating visualizations...\n")

    # 分析數據
    predictable, special = analyze_samples()
    print(f"Predictable: {len(predictable)}, Special: {len(special)}")

    # 生成圖表
    output_dir = "docs/figures"
    import os
    os.makedirs(output_dir, exist_ok=True)

    # 1D分布圖
    plot_1d_linear(predictable, special, f"{output_dir}/1d_linear_distribution.png")

    # 2D熱力圖
    plot_2d_bagua_heatmap(predictable, special, f"{output_dir}/2d_bagua_heatmap.png")

    # 數學模式
    plot_mathematical_patterns(special, f"{output_dir}/mathematical_patterns.png")

    # 節氣分析
    plot_solar_terms_analysis(special, f"{output_dir}/solar_terms_analysis.png")

    # 綜合儀表板
    plot_comprehensive_dashboard(predictable, special, f"{output_dir}/comprehensive_dashboard.png")

    print(f"\nAll figures saved to {output_dir}/")
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
