#!/usr/bin/env python3
"""
進階2D和3D位置分析

基於Web搜索發現:
- King Wen序列有3:1的偶/奇變化比
- 與黃金分割(Golden Section)相關
- 與Fibonacci序列相關
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
from scipy.fft import fft, fftfreq
from collections import defaultdict
from pathlib import Path

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 八卦二進制編碼
TRIGRAM_BINARY = {
    '乾': '111', '兌': '011', '離': '101', '震': '001',
    '巽': '110', '坎': '010', '艮': '100', '坤': '000'
}

TRIGRAM_INDEX = {
    '乾': 7, '兌': 3, '離': 5, '震': 1,
    '巽': 6, '坎': 2, '艮': 4, '坤': 0
}

# 八卦先天八卦順序 (伏羲序)
FUXI_ORDER = ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤']

# 八卦後天八卦順序 (文王序)
WENWANG_ORDER = ['坎', '坤', '震', '巽', '乾', '兌', '艮', '離']  # 北→西南→東...

def load_analysis_data():
    """載入分析數據"""
    with open('data/analysis/full_64_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_hexagram_data():
    """載入64卦數據"""
    with open('data/zhouyi-64gua/zhouyi_64gua.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['hexagrams']

def create_3d_cube_visualization(data, hexagrams):
    """創建3D立方體可視化 - 使用八卦作為坐標"""
    fig = plt.figure(figsize=(16, 12))

    # 準備數據
    special_positions = set(data['pattern_analysis']['positions'])

    # 建立3D坐標：X=上卦(0-7), Y=下卦(0-7), Z=爻位(1-6)
    xs, ys, zs = [], [], []
    colors = []
    sizes = []

    for gua in hexagrams:
        gua_index = gua['number']
        upper = gua.get('trigrams', {}).get('upper', '')
        lower = gua.get('trigrams', {}).get('lower', '')

        if upper not in TRIGRAM_INDEX or lower not in TRIGRAM_INDEX:
            continue

        x = TRIGRAM_INDEX[upper]
        y = TRIGRAM_INDEX[lower]

        for yao_pos in range(1, 7):
            global_pos = (gua_index - 1) * 6 + yao_pos

            xs.append(x)
            ys.append(y)
            zs.append(yao_pos)

            is_special = global_pos in special_positions
            colors.append('#F44336' if is_special else '#4CAF50')
            sizes.append(100 if is_special else 30)

    # 子圖1：標準3D散點圖
    ax1 = fig.add_subplot(221, projection='3d')
    ax1.scatter(xs, ys, zs, c=colors, s=sizes, alpha=0.6)
    ax1.set_xlabel('上卦 (0-7)')
    ax1.set_ylabel('下卦 (0-7)')
    ax1.set_zlabel('爻位 (1-6)')
    ax1.set_title('3D立方體視圖：紅=特殊爻，綠=可預測')

    # 子圖2：XY平面投影（上卦 vs 下卦）
    ax2 = fig.add_subplot(222)
    # 計算每個(x,y)組合的特殊爻比例
    xy_special = defaultdict(lambda: {'special': 0, 'total': 0})
    for i, (x, y) in enumerate(zip(xs, ys)):
        xy_special[(x, y)]['total'] += 1
        if colors[i] == '#F44336':
            xy_special[(x, y)]['special'] += 1

    heatmap_data = np.zeros((8, 8))
    for (x, y), counts in xy_special.items():
        heatmap_data[y, x] = counts['special'] / counts['total'] * 100

    im = ax2.imshow(heatmap_data, cmap='RdYlGn_r', aspect='equal', vmin=0, vmax=100)
    ax2.set_xticks(range(8))
    ax2.set_yticks(range(8))
    ax2.set_xticklabels([f'{t}({i})' for t, i in sorted(TRIGRAM_INDEX.items(), key=lambda x: x[1])])
    ax2.set_yticklabels([f'{t}({i})' for t, i in sorted(TRIGRAM_INDEX.items(), key=lambda x: x[1])])
    ax2.set_xlabel('上卦')
    ax2.set_ylabel('下卦')
    ax2.set_title('XY投影：特殊爻比例熱力圖')
    plt.colorbar(im, ax=ax2, label='特殊爻比例 (%)')

    # 添加數值
    for i in range(8):
        for j in range(8):
            ax2.text(j, i, f'{heatmap_data[i, j]:.0f}%', ha='center', va='center', fontsize=8)

    # 子圖3：XZ平面投影（上卦 vs 爻位）
    ax3 = fig.add_subplot(223)
    xz_special = defaultdict(lambda: {'special': 0, 'total': 0})
    for i, (x, z) in enumerate(zip(xs, zs)):
        xz_special[(x, z)]['total'] += 1
        if colors[i] == '#F44336':
            xz_special[(x, z)]['special'] += 1

    heatmap_xz = np.zeros((6, 8))
    for (x, z), counts in xz_special.items():
        heatmap_xz[z-1, x] = counts['special'] / counts['total'] * 100

    im3 = ax3.imshow(heatmap_xz, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
    ax3.set_xticks(range(8))
    ax3.set_yticks(range(6))
    ax3.set_xticklabels([f'{t}' for t, i in sorted(TRIGRAM_INDEX.items(), key=lambda x: x[1])])
    ax3.set_yticklabels([f'第{i+1}爻' for i in range(6)])
    ax3.set_xlabel('上卦')
    ax3.set_ylabel('爻位')
    ax3.set_title('XZ投影：上卦×爻位 特殊爻比例')
    plt.colorbar(im3, ax=ax3, label='%')

    # 子圖4：YZ平面投影（下卦 vs 爻位）
    ax4 = fig.add_subplot(224)
    yz_special = defaultdict(lambda: {'special': 0, 'total': 0})
    for i, (y, z) in enumerate(zip(ys, zs)):
        yz_special[(y, z)]['total'] += 1
        if colors[i] == '#F44336':
            yz_special[(y, z)]['special'] += 1

    heatmap_yz = np.zeros((6, 8))
    for (y, z), counts in yz_special.items():
        heatmap_yz[z-1, y] = counts['special'] / counts['total'] * 100

    im4 = ax4.imshow(heatmap_yz, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
    ax4.set_xticks(range(8))
    ax4.set_yticks(range(6))
    ax4.set_xticklabels([f'{t}' for t, i in sorted(TRIGRAM_INDEX.items(), key=lambda x: x[1])])
    ax4.set_yticklabels([f'第{i+1}爻' for i in range(6)])
    ax4.set_xlabel('下卦')
    ax4.set_ylabel('爻位')
    ax4.set_title('YZ投影：下卦×爻位 特殊爻比例')
    plt.colorbar(im4, ax=ax4, label='%')

    plt.tight_layout()
    plt.savefig('docs/figures/3d_cube_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("已保存: docs/figures/3d_cube_analysis.png")

def get_hexagram_binary(gua):
    """從八卦獲取卦的二進制表示"""
    upper = gua.get('trigrams', {}).get('upper', '')
    lower = gua.get('trigrams', {}).get('lower', '')
    if upper in TRIGRAM_BINARY and lower in TRIGRAM_BINARY:
        return TRIGRAM_BINARY[upper] + TRIGRAM_BINARY[lower]
    return ''

def analyze_king_wen_transitions(hexagrams):
    """分析King Wen序列的過渡特性 - 驗證3:1比例"""
    print("\n" + "=" * 70)
    print(" King Wen 序列過渡分析")
    print("=" * 70)

    transitions = []

    for i in range(len(hexagrams) - 1):
        gua1 = hexagrams[i]
        gua2 = hexagrams[i + 1]

        # 計算漢明距離（變化的爻數）
        bin1 = get_hexagram_binary(gua1)
        bin2 = get_hexagram_binary(gua2)

        if len(bin1) == 6 and len(bin2) == 6:
            hamming = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
            transitions.append({
                'from': gua1['name'],
                'to': gua2['name'],
                'hamming': hamming,
                'is_even': hamming % 2 == 0
            })

    # 統計
    even_count = sum(1 for t in transitions if t['is_even'])
    odd_count = len(transitions) - even_count

    print(f"\n過渡總數: {len(transitions)}")
    print(f"偶數變化: {even_count} ({even_count/len(transitions)*100:.1f}%)")
    print(f"奇數變化: {odd_count} ({odd_count/len(transitions)*100:.1f}%)")
    print(f"偶/奇比例: {even_count/odd_count:.2f}:1")

    # 按漢明距離分組
    hamming_dist = defaultdict(int)
    for t in transitions:
        hamming_dist[t['hamming']] += 1

    print("\n漢明距離分布:")
    for dist, count in sorted(hamming_dist.items()):
        parity = "偶" if dist % 2 == 0 else "奇"
        print(f"  {dist}爻變化({parity}): {count}次 ({count/len(transitions)*100:.1f}%)")

    return transitions

def analyze_golden_ratio_patterns(data):
    """分析黃金比例相關模式"""
    print("\n" + "=" * 70)
    print(" 黃金比例模式分析")
    print("=" * 70)

    phi = (1 + np.sqrt(5)) / 2  # 黃金比例 ≈ 1.618
    psi = phi - 1  # ≈ 0.618

    special_positions = data['pattern_analysis']['positions']

    # 測試1：位置是否落在黃金分割點附近
    golden_points_384 = [int(384 * psi), int(384 * psi * psi), int(384 * (1 - psi))]
    golden_points_64 = [int(64 * psi), int(64 * psi * psi), int(64 * (1 - psi))]

    print(f"\n384爻的黃金分割點: {golden_points_384}")
    print(f"64卦的黃金分割點: {golden_points_64}")

    # 測試2：間距比例是否接近黃金比例
    intervals = [special_positions[i+1] - special_positions[i]
                 for i in range(len(special_positions)-1)]

    # 計算連續間距的比例
    ratios = []
    for i in range(len(intervals) - 1):
        if intervals[i] > 0:
            ratio = intervals[i+1] / intervals[i]
            ratios.append(ratio)

    # 找接近phi或1/phi的比例
    phi_matches = sum(1 for r in ratios if abs(r - phi) < 0.1 or abs(r - 1/phi) < 0.1)

    print(f"\n間距比例接近φ或1/φ的數量: {phi_matches}/{len(ratios)} ({phi_matches/len(ratios)*100:.1f}%)")

    # 測試3：Fibonacci位置
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    fib_set = set(fib)

    fib_positions = [p for p in special_positions if p in fib_set]
    print(f"\n特殊爻在Fibonacci位置: {fib_positions}")

    # 測試4：Lucas數列
    lucas = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
    lucas_set = set(lucas)
    lucas_positions = [p for p in special_positions if p in lucas_set]
    print(f"特殊爻在Lucas位置: {lucas_positions}")

    return phi_matches, len(ratios)

def fourier_analysis(data):
    """對特殊爻序列進行傅里葉分析"""
    print("\n" + "=" * 70)
    print(" 傅里葉分析 - 尋找隱藏週期")
    print("=" * 70)

    # 創建384長度的二進制序列（1=特殊，0=普通）
    special_set = set(data['pattern_analysis']['positions'])
    sequence = np.array([1 if i in special_set else 0 for i in range(1, 385)])

    # 執行FFT
    fft_result = fft(sequence)
    frequencies = fftfreq(384, d=1)

    # 取正頻率部分
    positive_freq_idx = frequencies > 0
    magnitudes = np.abs(fft_result[positive_freq_idx])
    freqs = frequencies[positive_freq_idx]

    # 找主要頻率成分
    top_indices = np.argsort(magnitudes)[-10:][::-1]

    print("\n主要頻率成分（Top 10）:")
    print(f"{'頻率':>10} {'週期':>10} {'幅度':>10}")
    print("-" * 35)
    for idx in top_indices:
        freq = freqs[idx]
        period = 1 / freq if freq > 0 else float('inf')
        mag = magnitudes[idx]
        print(f"{freq:>10.4f} {period:>10.2f} {mag:>10.2f}")

    # 繪製頻譜圖
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    # 原始序列
    ax1 = axes[0]
    ax1.fill_between(range(1, 385), sequence, alpha=0.5, color='#2196F3')
    ax1.set_xlabel('爻位置')
    ax1.set_ylabel('特殊爻 (1/0)')
    ax1.set_title('特殊爻分布序列')
    ax1.set_xlim(1, 384)

    # 標記卦邊界
    for i in range(0, 385, 6):
        ax1.axvline(x=i, color='gray', linewidth=0.3, alpha=0.5)

    # 頻譜
    ax2 = axes[1]
    ax2.plot(freqs, magnitudes, color='#F44336', linewidth=0.8)
    ax2.fill_between(freqs, magnitudes, alpha=0.3, color='#F44336')
    ax2.set_xlabel('頻率')
    ax2.set_ylabel('幅度')
    ax2.set_title('傅里葉頻譜 - 尋找週期性')
    ax2.set_xlim(0, 0.2)  # 關注低頻部分

    # 標記關鍵週期
    key_periods = [6, 8, 12, 64]  # 6爻/卦, 8卦, 12月, 64卦
    for period in key_periods:
        freq = 1 / period
        ax2.axvline(x=freq, color='green', linestyle='--', alpha=0.7)
        ax2.text(freq, ax2.get_ylim()[1] * 0.9, f'T={period}', rotation=90, va='top')

    plt.tight_layout()
    plt.savefig('docs/figures/fourier_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n已保存: docs/figures/fourier_analysis.png")

    return freqs, magnitudes

def autocorrelation_analysis(data):
    """自相關分析"""
    print("\n" + "=" * 70)
    print(" 自相關分析")
    print("=" * 70)

    # 創建序列
    special_set = set(data['pattern_analysis']['positions'])
    sequence = np.array([1 if i in special_set else 0 for i in range(1, 385)])

    # 計算自相關
    n = len(sequence)
    mean = np.mean(sequence)
    var = np.var(sequence)

    max_lag = 100
    autocorr = []

    for lag in range(max_lag):
        if var > 0:
            corr = np.sum((sequence[lag:] - mean) * (sequence[:n-lag] - mean)) / ((n - lag) * var)
        else:
            corr = 0
        autocorr.append(corr)

    # 找顯著的lag
    significant_lags = [(lag, corr) for lag, corr in enumerate(autocorr) if abs(corr) > 0.1 and lag > 0]

    print("\n顯著自相關 (|r| > 0.1):")
    for lag, corr in significant_lags[:15]:
        interpretation = ""
        if lag == 6:
            interpretation = "← 1卦"
        elif lag == 12:
            interpretation = "← 2卦"
        elif lag == 8:
            interpretation = "← 八卦週期?"
        elif lag % 6 == 0:
            interpretation = f"← {lag//6}卦"
        print(f"  Lag {lag}: r = {corr:.3f} {interpretation}")

    # 繪圖
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(max_lag), autocorr, color='#2196F3', alpha=0.7)
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.axhline(y=0.1, color='red', linestyle='--', alpha=0.5)
    ax.axhline(y=-0.1, color='red', linestyle='--', alpha=0.5)

    # 標記關鍵lag
    for lag in [6, 12, 18, 24, 48, 64]:
        if lag < max_lag:
            ax.axvline(x=lag, color='green', linestyle=':', alpha=0.5)
            ax.text(lag, ax.get_ylim()[1] * 0.95, str(lag), ha='center', fontsize=8)

    ax.set_xlabel('Lag')
    ax.set_ylabel('自相關係數')
    ax.set_title('特殊爻序列自相關分析')
    ax.set_xlim(0, max_lag)

    plt.tight_layout()
    plt.savefig('docs/figures/autocorrelation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n已保存: docs/figures/autocorrelation.png")

    return autocorr

def analyze_2d_bagua_arrangement(data, hexagrams):
    """2D八卦排列分析 - 使用先天/後天八卦"""
    print("\n" + "=" * 70)
    print(" 2D八卦排列分析")
    print("=" * 70)

    special_set = set(data['pattern_analysis']['positions'])

    # 計算每個卦的特殊爻數
    hexagram_special_count = {}
    for gua in hexagrams:
        idx = gua['number']
        special_count = sum(1 for yao in range(1, 7)
                          if (idx - 1) * 6 + yao in special_set)
        hexagram_special_count[gua['name']] = {
            'count': special_count,
            'upper': gua.get('trigrams', {}).get('upper', ''),
            'lower': gua.get('trigrams', {}).get('lower', '')
        }

    # 先天八卦方位（伏羲）
    # 乾南(上), 坤北(下), 離東(右), 坎西(左)
    fuxi_positions = {
        '乾': (0, 2),   # 南/上
        '兌': (1, 3),   # 東南
        '離': (2, 3),   # 東
        '震': (3, 3),   # 東北
        '巽': (3, 1),   # 西南
        '坎': (2, 0),   # 西
        '艮': (1, 0),   # 西北
        '坤': (0, 1),   # 北/下
    }

    # 後天八卦方位（文王）
    # 離南, 坎北, 震東, 兌西
    wenwang_positions = {
        '離': (0, 2),   # 南
        '坤': (1, 3),   # 西南
        '兌': (2, 3),   # 西
        '乾': (3, 3),   # 西北
        '坎': (3, 1),   # 北
        '艮': (2, 0),   # 東北
        '震': (1, 0),   # 東
        '巽': (0, 1),   # 東南
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, (title, positions) in zip(axes, [
        ('先天八卦 (伏羲) - 上卦分布', fuxi_positions),
        ('後天八卦 (文王) - 上卦分布', wenwang_positions)
    ]):
        # 計算每個位置的平均特殊爻數
        position_counts = defaultdict(list)

        for gua_name, info in hexagram_special_count.items():
            upper = info['upper']
            if upper in positions:
                pos = positions[upper]
                position_counts[pos].append(info['count'])

        # 創建8x8網格用於64卦
        grid = np.zeros((8, 8))

        for gua in hexagrams:
            upper = gua.get('trigrams', {}).get('upper', '')
            lower = gua.get('trigrams', {}).get('lower', '')
            if upper in TRIGRAM_INDEX and lower in TRIGRAM_INDEX:
                x = TRIGRAM_INDEX[upper]
                y = TRIGRAM_INDEX[lower]
                idx = gua['number']
                special_count = sum(1 for yao in range(1, 7)
                                  if (idx - 1) * 6 + yao in special_set)
                grid[y, x] = special_count

        im = ax.imshow(grid, cmap='YlOrRd', aspect='equal')

        # 設置標籤
        trigram_labels = [t for t, i in sorted(TRIGRAM_INDEX.items(), key=lambda x: x[1])]
        ax.set_xticks(range(8))
        ax.set_yticks(range(8))
        ax.set_xticklabels(trigram_labels)
        ax.set_yticklabels(trigram_labels)
        ax.set_xlabel('上卦')
        ax.set_ylabel('下卦')
        ax.set_title(title)

        # 添加數值
        for i in range(8):
            for j in range(8):
                ax.text(j, i, f'{int(grid[i, j])}', ha='center', va='center', fontsize=9)

        plt.colorbar(im, ax=ax, label='特殊爻數量')

    plt.tight_layout()
    plt.savefig('docs/figures/2d_bagua_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n已保存: docs/figures/2d_bagua_analysis.png")

def main():
    """主函數"""
    print("=" * 70)
    print(" 進階2D/3D位置分析")
    print("=" * 70)

    # 確保目錄存在
    Path('docs/figures').mkdir(parents=True, exist_ok=True)

    # 載入數據
    data = load_analysis_data()
    hexagrams = load_hexagram_data()

    # 執行分析
    create_3d_cube_visualization(data, hexagrams)
    transitions = analyze_king_wen_transitions(hexagrams)
    phi_matches, total_ratios = analyze_golden_ratio_patterns(data)
    freqs, mags = fourier_analysis(data)
    autocorr = autocorrelation_analysis(data)
    analyze_2d_bagua_arrangement(data, hexagrams)

    print("\n" + "=" * 70)
    print(" 分析完成！")
    print("=" * 70)
    print("\n生成的圖表:")
    print("  - docs/figures/3d_cube_analysis.png")
    print("  - docs/figures/fourier_analysis.png")
    print("  - docs/figures/autocorrelation.png")
    print("  - docs/figures/2d_bagua_analysis.png")

if __name__ == "__main__":
    main()
