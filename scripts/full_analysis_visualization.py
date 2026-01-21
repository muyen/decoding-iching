#!/usr/bin/env python3
"""
完整384爻分析可視化
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """載入分析數據"""
    with open('data/analysis/full_64_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def plot_position_analysis(data):
    """爻位分析圖"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    positions = ['1', '2', '3', '4', '5', '6']
    pos_stats = data['by_position']

    # 吉凶率比較
    ax = axes[0]
    ji_rates = [pos_stats[p]['ji_rate'] for p in positions]
    xiong_rates = [pos_stats[p]['xiong_rate'] for p in positions]

    x = np.arange(len(positions))
    width = 0.35

    bars1 = ax.bar(x - width/2, ji_rates, width, label='吉率', color='#4CAF50', alpha=0.8)
    bars2 = ax.bar(x + width/2, xiong_rates, width, label='凶率', color='#F44336', alpha=0.8)

    ax.set_xlabel('爻位', fontsize=12)
    ax.set_ylabel('比率 (%)', fontsize=12)
    ax.set_title('各爻位吉凶率比較', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'第{p}爻' for p in positions])
    ax.legend()
    ax.axhline(y=33.3, color='gray', linestyle='--', alpha=0.5, label='平均線')

    # 添加數值標籤
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

    # 吉-凶淨值
    ax2 = axes[1]
    net_values = [ji_rates[i] - xiong_rates[i] for i in range(6)]
    colors = ['#4CAF50' if v > 0 else '#F44336' for v in net_values]

    bars = ax2.bar(positions, net_values, color=colors, alpha=0.8)
    ax2.set_xlabel('爻位', fontsize=12)
    ax2.set_ylabel('吉率 - 凶率 (%)', fontsize=12)
    ax2.set_title('各爻位吉凶淨值（正=偏吉，負=偏凶）', fontsize=14, fontweight='bold')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_xticklabels([f'第{p}爻' for p in positions])

    for bar, val in zip(bars, net_values):
        height = bar.get_height()
        ax2.annotate(f'{val:+.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3 if height > 0 else -12), textcoords="offset points",
                    ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/figures/position_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("已保存: docs/figures/position_analysis.png")

def plot_trigram_analysis(data):
    """八卦分析圖"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 上卦
    ax = axes[0]
    upper = data['by_trigram']['upper']
    trigrams = sorted(upper.keys(), key=lambda x: upper[x]['ji_rate'], reverse=True)
    ji_rates = [upper[t]['ji_rate'] for t in trigrams]

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(trigrams)))
    bars = ax.barh(trigrams, ji_rates, color=colors)
    ax.set_xlabel('吉率 (%)', fontsize=12)
    ax.set_title('上卦吉率排名', fontsize=14, fontweight='bold')
    ax.axvline(x=35.9, color='red', linestyle='--', alpha=0.7, label='平均')

    for bar, rate in zip(bars, ji_rates):
        ax.annotate(f'{rate:.1f}%', xy=(rate, bar.get_y() + bar.get_height()/2),
                   xytext=(3, 0), textcoords="offset points", va='center', fontsize=10)

    # 下卦
    ax2 = axes[1]
    lower = data['by_trigram']['lower']
    trigrams = sorted(lower.keys(), key=lambda x: lower[x]['ji_rate'], reverse=True)
    ji_rates = [lower[t]['ji_rate'] for t in trigrams]

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(trigrams)))
    bars = ax2.barh(trigrams, ji_rates, color=colors)
    ax2.set_xlabel('吉率 (%)', fontsize=12)
    ax2.set_title('下卦吉率排名', fontsize=14, fontweight='bold')
    ax2.axvline(x=35.9, color='red', linestyle='--', alpha=0.7, label='平均')

    for bar, rate in zip(bars, ji_rates):
        ax2.annotate(f'{rate:.1f}%', xy=(rate, bar.get_y() + bar.get_height()/2),
                   xytext=(3, 0), textcoords="offset points", va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('docs/figures/trigram_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("已保存: docs/figures/trigram_analysis.png")

def plot_interval_distribution(data):
    """間距分布圖"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 間距頻率
    ax = axes[0]
    interval_freq = data['pattern_analysis']['interval_distribution']
    # Sort by interval value
    sorted_items = sorted(interval_freq.items(), key=lambda x: int(x[0]))
    intervals = [int(k) for k, v in sorted_items]
    counts = [v for k, v in sorted_items]

    colors = ['#2196F3' if i <= 2 else '#FFC107' if i <= 5 else '#F44336' for i in intervals]
    bars = ax.bar(range(len(intervals)), counts, color=colors, alpha=0.8)
    ax.set_xlabel('間距', fontsize=12)
    ax.set_ylabel('出現次數', fontsize=12)
    ax.set_title('特殊爻間距頻率分布', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(intervals)))
    ax.set_xticklabels(intervals)

    # 標註主要值
    for bar, count in zip(bars[:3], counts[:3]):
        ax.annotate(f'{count}', xy=(bar.get_x() + bar.get_width()/2, count),
                   xytext=(0, 3), textcoords="offset points", ha='center', fontsize=11, fontweight='bold')

    # 累積分布
    ax2 = axes[1]
    cumsum = np.cumsum(counts)
    total = sum(counts)
    cum_pct = [c/total*100 for c in cumsum]

    ax2.plot(range(len(intervals)), cum_pct, 'bo-', markersize=8, linewidth=2)
    ax2.fill_between(range(len(intervals)), cum_pct, alpha=0.3)
    ax2.set_xlabel('間距 ≤', fontsize=12)
    ax2.set_ylabel('累積比例 (%)', fontsize=12)
    ax2.set_title('間距累積分布', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(intervals)))
    ax2.set_xticklabels(intervals)
    ax2.axhline(y=83, color='red', linestyle='--', alpha=0.7)
    ax2.axhline(y=95, color='green', linestyle='--', alpha=0.7)

    # 標註關鍵點
    for i, (intv, pct) in enumerate(zip(intervals[:4], cum_pct[:4])):
        ax2.annotate(f'{pct:.0f}%', xy=(i, pct), xytext=(5, 5),
                    textcoords="offset points", fontsize=10)

    plt.tight_layout()
    plt.savefig('docs/figures/interval_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("已保存: docs/figures/interval_distribution.png")

def plot_hexagram_heatmap(data):
    """64卦吉凶熱力圖"""
    fig, ax = plt.subplots(figsize=(12, 10))

    # 八卦名稱
    trigrams = ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤']

    # 從數據中提取每個卦的吉率
    hexagram_stats = data.get('hexagram_statistics', {})

    # 建立8x8矩陣
    matrix = np.zeros((8, 8))

    # 卦序到八卦的映射（簡化版）
    gua_to_trigram = {
        '乾': (0, 0), '姤': (0, 4), '遯': (0, 6), '否': (0, 7),
        '觀': (4, 7), '剝': (6, 7), '晉': (2, 7), '大有': (2, 0),
        # ... 需要完整映射
    }

    # 填充矩陣（使用上下卦組合）
    upper_stats = data['by_trigram']['upper']
    lower_stats = data['by_trigram']['lower']

    for i, upper in enumerate(trigrams):
        for j, lower in enumerate(trigrams):
            # 近似：使用上下卦吉率的組合
            if upper in upper_stats and lower in lower_stats:
                matrix[i, j] = (upper_stats[upper]['ji_rate'] + lower_stats[lower]['ji_rate']) / 2

    # 繪製熱力圖
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='equal')

    # 設置標籤
    ax.set_xticks(np.arange(8))
    ax.set_yticks(np.arange(8))
    ax.set_xticklabels([f'{t}\n(下卦)' for t in trigrams], fontsize=11)
    ax.set_yticklabels([f'{t}\n(上卦)' for t in trigrams], fontsize=11)

    # 添加數值
    for i in range(8):
        for j in range(8):
            text = ax.text(j, i, f'{matrix[i, j]:.0f}%',
                          ha="center", va="center", color="black", fontsize=9)

    ax.set_title('八卦組合吉率熱力圖\n（紅=凶，黃=中，綠=吉）', fontsize=14, fontweight='bold')

    # 顏色條
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.set_ylabel('吉率 (%)', rotation=-90, va="bottom", fontsize=11)

    plt.tight_layout()
    plt.savefig('docs/figures/trigram_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("已保存: docs/figures/trigram_heatmap.png")

def plot_special_yao_density():
    """特殊爻密度圖"""
    # 載入原始數據
    with open('data/analysis/full_64_analysis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    special_positions = data['pattern_analysis']['positions']

    fig, axes = plt.subplots(2, 1, figsize=(16, 8))

    # 上圖：384爻線性分布
    ax = axes[0]
    all_positions = range(1, 385)
    special_set = set(special_positions)
    colors = ['#F44336' if p in special_set else '#E0E0E0' for p in all_positions]

    ax.scatter(all_positions, [1]*384, c=colors, s=15, marker='|')
    ax.set_xlim(0, 385)
    ax.set_ylim(0.5, 1.5)
    ax.set_xlabel('爻位置（1-384）', fontsize=12)
    ax.set_title('特殊爻分布（紅色=需要爻辭，灰色=可預測）', fontsize=14, fontweight='bold')
    ax.set_yticks([])

    # 標記卦邊界
    for i in range(0, 385, 6):
        ax.axvline(x=i, color='#BDBDBD', linewidth=0.3, alpha=0.5)

    # 下圖：密度分布
    ax2 = axes[1]

    # 計算每個區間的特殊爻數量
    window = 12  # 2卦
    densities = []
    for i in range(0, 384 - window + 1):
        count = sum(1 for p in special_positions if i < p <= i + window)
        densities.append(count / window * 100)

    ax2.fill_between(range(len(densities)), densities, alpha=0.5, color='#2196F3')
    ax2.plot(densities, color='#1976D2', linewidth=1)
    ax2.set_xlim(0, len(densities))
    ax2.set_xlabel('位置', fontsize=12)
    ax2.set_ylabel('特殊爻密度 (%)', fontsize=12)
    ax2.set_title(f'特殊爻密度（滑動窗口={window}爻）', fontsize=14, fontweight='bold')
    ax2.axhline(y=60, color='red', linestyle='--', alpha=0.7, label='60%')

    plt.tight_layout()
    plt.savefig('docs/figures/special_yao_density.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("已保存: docs/figures/special_yao_density.png")

def main():
    """主函數"""
    print("=" * 60)
    print(" 生成完整分析可視化")
    print("=" * 60)

    # 確保目錄存在
    Path('docs/figures').mkdir(parents=True, exist_ok=True)

    data = load_data()

    plot_position_analysis(data)
    plot_trigram_analysis(data)
    plot_interval_distribution(data)
    plot_hexagram_heatmap(data)
    plot_special_yao_density()

    print("\n所有圖表已生成完畢！")

if __name__ == "__main__":
    main()
