#!/usr/bin/env python3
"""
Generate professional 8x8 hexagram heatmap for the book
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import json
import os

# Configure for high quality output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12

# Try to use a good Chinese font
chinese_fonts = [
    'PingFang TC',
    'Heiti TC',
    'STHeiti',
    'Arial Unicode MS',
    'Microsoft YaHei',
    'SimHei',
    'Noto Sans CJK TC'
]

for font in chinese_fonts:
    try:
        fm.findfont(font, fallback_to_default=False)
        plt.rcParams['font.sans-serif'] = [font]
        print(f"Using font: {font}")
        break
    except:
        continue

plt.rcParams['axes.unicode_minus'] = False

# Trigram names
TRIGRAM_NAMES = ["坤", "艮", "坎", "巽", "震", "離", "兌", "乾"]

# Load actual data or use sample data
# This is the 吉率 (fortune rate) for each hexagram
# Format: grid[lower_trigram][upper_trigram] = fortune_rate

# Sample data based on research findings
# Values are fortune rates (0-1 scale)
FORTUNE_RATES = np.array([
    # 坤  艮   坎   巽   震   離   兌   乾   <- Upper trigram
    [0.17, 0.50, 0.33, 0.17, 0.83, 0.33, 0.00, 0.00],  # 坤 lower
    [0.83, 0.33, 0.33, 0.50, 0.50, 0.17, 0.50, 0.33],  # 艮 lower
    [0.33, 0.17, 0.33, 0.33, 0.50, 0.17, 0.00, 0.17],  # 坎 lower
    [0.17, 0.17, 0.33, 0.17, 0.17, 0.17, 0.17, 0.17],  # 巽 lower
    [0.17, 0.33, 0.17, 0.33, 0.17, 0.33, 0.17, 0.17],  # 震 lower
    [0.33, 0.17, 0.17, 0.33, 0.33, 0.17, 0.17, 0.00],  # 離 lower
    [0.00, 0.33, 0.17, 0.17, 0.33, 0.50, 0.33, 0.33],  # 兌 lower
    [0.00, 0.33, 0.17, 0.17, 0.17, 0.17, 0.17, 0.00],  # 乾 lower
])

def create_heatmap():
    """Create a professional heatmap"""

    fig, ax = plt.subplots(figsize=(10, 10))

    # Use a professional color scheme
    # Green = good (吉), Red = bad (凶), Yellow = neutral
    cmap = plt.cm.RdYlGn  # Red-Yellow-Green

    # Create heatmap
    im = ax.imshow(FORTUNE_RATES, cmap=cmap, vmin=0, vmax=1, aspect='equal')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, label='吉率')
    cbar.ax.tick_params(labelsize=11)

    # Set ticks and labels
    ax.set_xticks(np.arange(8))
    ax.set_yticks(np.arange(8))
    ax.set_xticklabels(TRIGRAM_NAMES, fontsize=14)
    ax.set_yticklabels(TRIGRAM_NAMES, fontsize=14)

    # Labels
    ax.set_xlabel('上卦（外在環境）', fontsize=14, labelpad=10)
    ax.set_ylabel('下卦（內在狀態）', fontsize=14, labelpad=10)
    ax.set_title('64卦吉率熱力圖\n（每卦六爻中判定為「吉」的比例）', fontsize=16, pad=20, fontweight='bold')

    # Add text annotations with values
    for i in range(8):
        for j in range(8):
            value = FORTUNE_RATES[i, j]
            # Choose text color based on background
            text_color = 'white' if value < 0.3 or value > 0.7 else 'black'
            text = ax.text(j, i, f'{value:.0%}', ha='center', va='center',
                          color=text_color, fontsize=10, fontweight='bold')

    # Add grid lines
    ax.set_xticks(np.arange(-.5, 8, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 8, 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)

    # Remove minor tick marks
    ax.tick_params(which='minor', length=0)

    plt.tight_layout()

    # Save in multiple formats
    output_dir = 'images'
    os.makedirs(output_dir, exist_ok=True)

    # High-res PNG for ebook
    plt.savefig(f'{output_dir}/8x8_heatmap.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')

    # SVG for scalability
    plt.savefig(f'{output_dir}/8x8_heatmap.svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print(f"Saved: {output_dir}/8x8_heatmap.png (300 DPI)")
    print(f"Saved: {output_dir}/8x8_heatmap.svg")

    plt.close()

def create_quadrant_chart():
    """Create a professional quadrant analysis chart"""

    fig, ax = plt.subplots(figsize=(10, 11))  # Taller for title space

    # Quadrant data - clearer labels without Q1/Q2/Q3/Q4
    quadrants = {
        '左上': (0.25, 0.75, 33.3, '內強外弱', '穩健'),
        '右上': (0.75, 0.75, 38.9, '內外皆強', '最佳'),
        '左下': (0.25, 0.25, 20.0, '內外皆弱', '最差'),
        '右下': (0.75, 0.25, 20.8, '外強內弱', '不穩'),
    }

    # Colors based on fortune rate
    colors = {
        '左上': '#90EE90',  # Light green
        '右上': '#228B22',  # Forest green (best)
        '左下': '#FF6B6B',  # Red (worst)
        '右下': '#FFB347',  # Orange
    }

    # Draw quadrants
    for label, (x, y, rate, desc, status) in quadrants.items():
        # Draw rectangle
        rect = plt.Rectangle((x-0.24, y-0.24), 0.48, 0.48,
                             facecolor=colors[label], edgecolor='black', linewidth=2)
        ax.add_patch(rect)

        # Add labels
        ax.text(x, y+0.12, status, ha='center', va='center',
               fontsize=18, fontweight='bold')
        ax.text(x, y-0.02, f'{rate}% 吉', ha='center', va='center',
               fontsize=16, fontweight='bold')
        ax.text(x, y-0.15, desc, ha='center', va='center',
               fontsize=12, color='#333333')

    # Draw axes
    ax.axhline(y=0.5, color='black', linewidth=2)
    ax.axvline(x=0.5, color='black', linewidth=2)

    # Labels - top axis
    ax.text(0.5, 1.08, '上卦（外在環境）', ha='center', va='bottom', fontsize=14, fontweight='bold')
    ax.text(0.15, 1.02, '← 弱', ha='center', va='bottom', fontsize=11, color='gray')
    ax.text(0.85, 1.02, '強 →', ha='center', va='bottom', fontsize=11, color='gray')

    # Labels - left axis
    ax.text(-0.08, 0.5, '下卦\n（內在）', ha='right', va='center', fontsize=13, fontweight='bold')
    ax.text(-0.02, 0.85, '↑強', ha='right', va='center', fontsize=11, color='gray')
    ax.text(-0.02, 0.15, '↓弱', ha='right', va='center', fontsize=11, color='gray')

    ax.set_title('64卦四象限分析', fontsize=20, pad=30, fontweight='bold')

    ax.set_xlim(-0.15, 1.05)
    ax.set_ylim(-0.05, 1.15)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()

    # Save
    output_dir = 'images'
    plt.savefig(f'{output_dir}/quadrant_analysis.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.savefig(f'{output_dir}/quadrant_analysis.svg', bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print(f"Saved: {output_dir}/quadrant_analysis.png (300 DPI)")
    plt.close()


if __name__ == '__main__':
    create_heatmap()
    create_quadrant_chart()
    print("Done!")
