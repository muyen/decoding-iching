#!/usr/bin/env python3
"""
繪製吉凶波動圖 - 視覺化「起伏」模式

1. 累積分數線圖 (吉=+1, 中=0, 凶=-1)
2. 波動圖 - 顯示區域覆蓋
3. ASCII 視覺化
"""

import json
import os
from collections import defaultdict

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

def create_ascii_wave(data, width=80):
    """創建ASCII波動圖"""
    print("=" * 70)
    print("吉凶波動圖 (ASCII)")
    print("=" * 70)

    # 按卦序和爻位排序
    sorted_data = sorted(data, key=lambda x: (x['hex_num'], x['position']))
    labels = [d['label'] for d in sorted_data]

    # 計算累積分數
    cumulative = []
    score = 0
    for label in labels:
        score += label
        cumulative.append(score)

    min_score = min(cumulative)
    max_score = max(cumulative)

    print(f"\n累積分數範圍: {min_score} 到 {max_score}")
    print(f"最終分數: {cumulative[-1]}")

    # ASCII 圖 - 每卦一列，6爻
    print("\n" + "-" * 70)
    print("每卦的吉凶模式 (吉=█, 中=░, 凶=▓)")
    print("-" * 70)

    hex_groups = defaultdict(list)
    for d in sorted_data:
        hex_groups[d['hex_num']].append(d['label'])

    char_map = {1: '█', 0: '░', -1: '▓'}

    # 每行顯示8卦
    hex_nums = sorted(hex_groups.keys())
    for row_start in range(0, len(hex_nums), 8):
        row_hexes = hex_nums[row_start:row_start+8]

        # 打印卦號
        print("\n卦:", end="")
        for hex_num in row_hexes:
            print(f" {hex_num:2d}    ", end="")
        print()

        # 打印6爻 (從下到上)
        for pos in range(6):
            print(f"爻{pos+1}", end="")
            for hex_num in row_hexes:
                labels_in_hex = hex_groups[hex_num]
                if pos < len(labels_in_hex):
                    label = labels_in_hex[pos]
                    char = char_map[label]
                    print(f"  {char*4} ", end="")
                else:
                    print("       ", end="")
            print()

    return cumulative

def create_cumulative_chart(data):
    """創建累積分數的ASCII圖表"""
    print("\n" + "=" * 70)
    print("累積分數波動 (每6爻取樣)")
    print("=" * 70)

    sorted_data = sorted(data, key=lambda x: (x['hex_num'], x['position']))

    # 計算累積分數
    cumulative = []
    score = 0
    for d in sorted_data:
        score += d['label']
        cumulative.append(score)

    # 每6爻（每卦）取一個樣本
    samples = cumulative[5::6]  # 每卦結束時的累積分數

    min_val = min(samples)
    max_val = max(samples)
    range_val = max_val - min_val if max_val != min_val else 1

    # ASCII 圖
    height = 20
    width = len(samples)

    print(f"\n橫軸: 卦序 (1-64), 縱軸: 累積分數 ({min_val} 到 {max_val})")
    print()

    # 創建圖表
    chart = [[' ' for _ in range(width)] for _ in range(height)]

    for i, val in enumerate(samples):
        # 將值映射到高度
        normalized = (val - min_val) / range_val
        row = int((1 - normalized) * (height - 1))
        chart[row][i] = '█'

        # 填充下方區域
        for r in range(row + 1, height):
            if val >= 0:
                chart[r][i] = '▒'

    # 打印圖表
    for row in chart:
        print(''.join(row))

    # X軸標籤
    print("+" + "-" * (width-1))
    labels_line = ""
    for i in range(0, width, 8):
        labels_line += f"{i+1:<8}"
    print(labels_line)

    return samples

def analyze_wave_pattern(data):
    """分析波動模式"""
    print("\n" + "=" * 70)
    print("波動模式分析")
    print("=" * 70)

    sorted_data = sorted(data, key=lambda x: (x['hex_num'], x['position']))

    # 計算累積分數
    cumulative = []
    score = 0
    for d in sorted_data:
        score += d['label']
        cumulative.append(score)

    # 找出局部最大值和最小值（峰值和谷值）
    peaks = []
    valleys = []

    for i in range(1, len(cumulative) - 1):
        if cumulative[i] > cumulative[i-1] and cumulative[i] > cumulative[i+1]:
            peaks.append((i, cumulative[i]))
        if cumulative[i] < cumulative[i-1] and cumulative[i] < cumulative[i+1]:
            valleys.append((i, cumulative[i]))

    print(f"\n峰值數量: {len(peaks)}")
    print(f"谷值數量: {len(valleys)}")

    # 峰值之間的距離
    if len(peaks) > 1:
        peak_distances = [peaks[i][0] - peaks[i-1][0] for i in range(1, len(peaks))]
        print(f"\n峰值間距: 平均 {sum(peak_distances)/len(peak_distances):.1f}, 範圍 {min(peak_distances)}-{max(peak_distances)}")

    if len(valleys) > 1:
        valley_distances = [valleys[i][0] - valleys[i-1][0] for i in range(1, len(valleys))]
        print(f"谷值間距: 平均 {sum(valley_distances)/len(valley_distances):.1f}, 範圍 {min(valley_distances)}-{max(valley_distances)}")

    # 上升和下降區間
    rising = 0
    falling = 0
    flat = 0

    for i in range(1, len(cumulative)):
        if cumulative[i] > cumulative[i-1]:
            rising += 1
        elif cumulative[i] < cumulative[i-1]:
            falling += 1
        else:
            flat += 1

    total = rising + falling + flat
    print(f"\n上升: {rising} ({rising/total*100:.1f}%)")
    print(f"下降: {falling} ({falling/total*100:.1f}%)")
    print(f"持平: {flat} ({flat/total*100:.1f}%)")

    # 最大上升區間和最大下降區間
    max_rise = 0
    max_fall = 0
    current_rise = 0
    current_fall = 0
    rise_start = 0
    fall_start = 0
    best_rise = (0, 0, 0)
    best_fall = (0, 0, 0)

    for i in range(1, len(cumulative)):
        if cumulative[i] > cumulative[i-1]:
            if current_rise == 0:
                rise_start = i - 1
            current_rise += 1
            current_fall = 0
            if current_rise > max_rise:
                max_rise = current_rise
                best_rise = (rise_start, i, current_rise)
        elif cumulative[i] < cumulative[i-1]:
            if current_fall == 0:
                fall_start = i - 1
            current_fall += 1
            current_rise = 0
            if current_fall > max_fall:
                max_fall = current_fall
                best_fall = (fall_start, i, current_fall)
        else:
            current_rise = 0
            current_fall = 0

    print(f"\n最長連續上升: {max_rise} 爻 (位置 {best_rise[0]}-{best_rise[1]}, 卦{best_rise[0]//6+1}-{best_rise[1]//6+1})")
    print(f"最長連續下降: {max_fall} 爻 (位置 {best_fall[0]}-{best_fall[1]}, 卦{best_fall[0]//6+1}-{best_fall[1]//6+1})")

    # 計算「區域」- 正區域和負區域
    positive_area = sum(c for c in cumulative if c > 0)
    negative_area = sum(abs(c) for c in cumulative if c < 0)
    print(f"\n正區域（累積分數>0）: {positive_area}")
    print(f"負區域（累積分數<0）: {negative_area}")
    print(f"淨區域: {positive_area - negative_area}")

    return peaks, valleys

def create_hexagram_wave_map(data, struct_data):
    """創建卦象波動地圖"""
    print("\n" + "=" * 70)
    print("8×8 波動地圖")
    print("=" * 70)

    TRIGRAM_NAMES = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']

    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 計算每卦的淨分數
    hex_scores = defaultdict(int)
    for d in data:
        hex_scores[d['hex_num']] += d['label']

    # 8×8 網格
    print("\n每卦淨分數 (下卦→, 上卦↓):")
    print("     ", end="")
    for lower in TRIGRAM_NAMES:
        print(f"  {lower} ", end="")
    print()
    print("     " + "-" * 40)

    # 找出每個組合的卦
    grid = defaultdict(int)
    for hex_num, (lower, upper) in hex_to_trigrams.items():
        grid[(lower, upper)] = hex_scores[hex_num]

    for upper in TRIGRAM_NAMES:
        print(f" {upper} |", end="")
        for lower in TRIGRAM_NAMES:
            score = grid[(lower, upper)]
            if score > 0:
                print(f" +{score:2d}", end="")
            elif score < 0:
                print(f" {score:3d}", end="")
            else:
                print(f"   0", end="")
        print()

    # 找出最高和最低
    scores_list = [(k, v) for k, v in grid.items()]
    scores_list.sort(key=lambda x: -x[1])

    print("\n最高分卦:")
    for (lower, upper), score in scores_list[:5]:
        print(f"  {upper}/{lower}: {score:+d}")

    print("\n最低分卦:")
    for (lower, upper), score in scores_list[-5:]:
        print(f"  {upper}/{lower}: {score:+d}")

def main():
    data = load_corrected_data()
    struct_data = load_structure()

    # ASCII 波動圖
    cumulative = create_ascii_wave(data)

    # 累積分數圖
    samples = create_cumulative_chart(data)

    # 波動模式分析
    peaks, valleys = analyze_wave_pattern(data)

    # 8×8 波動地圖
    create_hexagram_wave_map(data, struct_data)

if __name__ == "__main__":
    main()
