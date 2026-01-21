#!/usr/bin/env python3
"""
分析吉凶變化的距離模式

核心問題：吉凶標籤的「變化點」有沒有規律？
- 1D: 在384爻序列中，變化點之間的距離
- 2D: 在8x8網格中，變化點的位置
- 3D: 變化點與卦結構的關係
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

def analyze_1d_transitions(data):
    """1D分析：標籤變化的距離模式"""
    print("=" * 70)
    print("1D 變化距離分析")
    print("=" * 70)

    # 按卦序和爻位排序
    sorted_data = sorted(data, key=lambda x: (x['hex_num'], x['position']))

    # 提取標籤序列
    labels = [d['label'] for d in sorted_data]

    # 找出變化點（標籤從一個值變到另一個值的位置）
    change_points = []
    for i in range(1, len(labels)):
        if labels[i] != labels[i-1]:
            change_points.append(i)

    print(f"\n總爻數: {len(labels)}")
    print(f"變化點數量: {len(change_points)}")
    print(f"平均每 {len(labels)/len(change_points):.1f} 爻發生一次變化")

    # 計算變化點之間的距離
    distances = []
    for i in range(1, len(change_points)):
        dist = change_points[i] - change_points[i-1]
        distances.append(dist)

    # 距離統計
    dist_counter = Counter(distances)
    print(f"\n變化距離分布:")
    print("距離  次數  佔比")
    print("-" * 30)
    for dist in sorted(dist_counter.keys()):
        count = dist_counter[dist]
        pct = count / len(distances) * 100
        bar = "█" * int(pct / 2)
        print(f"  {dist:2d}   {count:3d}  {pct:5.1f}% {bar}")

    # 統計量
    if distances:
        avg_dist = sum(distances) / len(distances)
        max_dist = max(distances)
        min_dist = min(distances)
        print(f"\n平均距離: {avg_dist:.2f}")
        print(f"最大距離: {max_dist}")
        print(f"最小距離: {min_dist}")

        # 檢查是否有週期性
        print("\n週期性檢查:")
        for period in [6, 8, 12, 64]:
            matches = sum(1 for d in distances if d % period == 0)
            print(f"  距離為 {period} 的倍數: {matches} ({matches/len(distances)*100:.1f}%)")

    # 分析變化類型
    print("\n變化類型分析:")
    transition_types = defaultdict(int)
    for i in range(1, len(labels)):
        if labels[i] != labels[i-1]:
            key = f"{labels[i-1]} → {labels[i]}"
            transition_types[key] += 1

    label_names = {1: '吉', 0: '中', -1: '凶'}
    for (trans, count) in sorted(transition_types.items(), key=lambda x: -x[1]):
        parts = trans.split(' → ')
        from_l = label_names[int(parts[0])]
        to_l = label_names[int(parts[1])]
        print(f"  {from_l} → {to_l}: {count}")

    return change_points, distances

def analyze_within_hexagram_transitions(data):
    """分析卦內變化模式"""
    print("\n" + "=" * 70)
    print("卦內變化分析 (每卦6爻內的變化)")
    print("=" * 70)

    # 按卦分組
    hex_groups = defaultdict(list)
    for d in data:
        hex_groups[d['hex_num']].append(d)

    # 統計每卦的變化次數
    changes_per_hex = []
    change_positions = defaultdict(int)  # 變化發生在哪個爻位

    for hex_num in sorted(hex_groups.keys()):
        yaos = sorted(hex_groups[hex_num], key=lambda x: x['position'])
        labels = [y['label'] for y in yaos]

        changes = 0
        for i in range(1, len(labels)):
            if labels[i] != labels[i-1]:
                changes += 1
                # 記錄變化發生的位置 (從爻i-1到爻i)
                change_positions[i] += 1  # i是爻位2-6

        changes_per_hex.append(changes)

    # 每卦變化次數分布
    change_counter = Counter(changes_per_hex)
    print("\n每卦變化次數分布:")
    print("變化次數  卦數  佔比")
    print("-" * 30)
    for changes in sorted(change_counter.keys()):
        count = change_counter[changes]
        pct = count / len(changes_per_hex) * 100
        print(f"   {changes}       {count:2d}   {pct:5.1f}%")

    print(f"\n平均每卦變化: {sum(changes_per_hex)/len(changes_per_hex):.2f} 次")

    # 變化最常發生的爻位
    print("\n變化最常發生的爻位邊界:")
    print("爻位邊界  變化次數")
    print("-" * 25)
    for pos in range(2, 7):
        count = change_positions[pos]
        bar = "█" * (count // 2)
        print(f"  {pos-1}→{pos}      {count:3d}  {bar}")

    return changes_per_hex, change_positions

def analyze_2d_transition_pattern(data, struct_data):
    """2D分析：在8x8網格中，哪些位置變化最多"""
    print("\n" + "=" * 70)
    print("2D 變化熱力圖 (8×8網格)")
    print("=" * 70)

    TRIGRAM_NAMES = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']

    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 按卦分組，計算每卦內的變化次數
    hex_groups = defaultdict(list)
    for d in data:
        hex_groups[d['hex_num']].append(d)

    # 計算每個上下卦組合的變化強度
    grid_changes = defaultdict(lambda: {'total_yaos': 0, 'changes': 0})

    for hex_num in sorted(hex_groups.keys()):
        if hex_num not in hex_to_trigrams:
            continue

        lower, upper = hex_to_trigrams[hex_num]
        yaos = sorted(hex_groups[hex_num], key=lambda x: x['position'])
        labels = [y['label'] for y in yaos]

        changes = sum(1 for i in range(1, len(labels)) if labels[i] != labels[i-1])

        grid_changes[(lower, upper)]['total_yaos'] += len(labels)
        grid_changes[(lower, upper)]['changes'] += changes

    # 打印變化強度網格
    print("\n卦內變化次數 (下卦→, 上卦↓):")
    print("     ", end="")
    for lower in TRIGRAM_NAMES:
        print(f"  {lower} ", end="")
    print()
    print("     " + "-" * 40)

    for upper in TRIGRAM_NAMES:
        print(f" {upper} |", end="")
        for lower in TRIGRAM_NAMES:
            key = (lower, upper)
            if grid_changes[key]['total_yaos'] > 0:
                changes = grid_changes[key]['changes']
                print(f"  {changes:2d}", end="")
            else:
                print("   -", end="")
        print()

    # 找出變化最多和最少的組合
    combos = [(k, v['changes']) for k, v in grid_changes.items() if v['total_yaos'] > 0]
    combos.sort(key=lambda x: -x[1])

    print("\n變化最多的組合 (不穩定):")
    for (lower, upper), changes in combos[:5]:
        print(f"  {upper}/{lower}: {changes} 次變化")

    print("\n變化最少的組合 (穩定):")
    for (lower, upper), changes in combos[-5:]:
        print(f"  {upper}/{lower}: {changes} 次變化")

    return grid_changes

def analyze_cross_hexagram_transitions(data, struct_data):
    """分析卦與卦之間的變化模式"""
    print("\n" + "=" * 70)
    print("卦間變化分析 (相鄰卦之間)")
    print("=" * 70)

    # 按卦序排序
    hex_groups = defaultdict(list)
    for d in data:
        hex_groups[d['hex_num']].append(d)

    hex_nums = sorted(hex_groups.keys())

    # 計算相鄰卦最後一爻和第一爻的變化
    cross_changes = []
    for i in range(1, len(hex_nums)):
        prev_hex = hex_nums[i-1]
        curr_hex = hex_nums[i]

        prev_yaos = sorted(hex_groups[prev_hex], key=lambda x: x['position'])
        curr_yaos = sorted(hex_groups[curr_hex], key=lambda x: x['position'])

        if prev_yaos and curr_yaos:
            last_label = prev_yaos[-1]['label']  # 上一卦的上爻
            first_label = curr_yaos[0]['label']   # 下一卦的初爻

            cross_changes.append({
                'from_hex': prev_hex,
                'to_hex': curr_hex,
                'last_label': last_label,
                'first_label': first_label,
                'changed': last_label != first_label
            })

    # 統計
    changed_count = sum(1 for c in cross_changes if c['changed'])
    print(f"\n卦間變化率: {changed_count}/{len(cross_changes)} ({changed_count/len(cross_changes)*100:.1f}%)")

    # 分析特定的卦對
    print("\n分析King Wen序的卦對變化:")
    # King Wen序是成對的（如1-2, 3-4等）
    pair_changes = []
    for i in range(0, len(cross_changes), 2):
        if i < len(cross_changes):
            pair_changes.append(cross_changes[i])

    pair_changed = sum(1 for c in pair_changes if c['changed'])
    print(f"  奇數→偶數卦變化率: {pair_changed}/{len(pair_changes)} ({pair_changed/len(pair_changes)*100:.1f}%)")

    return cross_changes

def analyze_label_run_lengths(data):
    """分析連續相同標籤的長度（Run Length）"""
    print("\n" + "=" * 70)
    print("連續相同標籤分析 (Run Length)")
    print("=" * 70)

    # 按卦序和爻位排序
    sorted_data = sorted(data, key=lambda x: (x['hex_num'], x['position']))
    labels = [d['label'] for d in sorted_data]

    # 計算run lengths
    runs = []
    current_label = labels[0]
    current_length = 1

    for i in range(1, len(labels)):
        if labels[i] == current_label:
            current_length += 1
        else:
            runs.append((current_label, current_length))
            current_label = labels[i]
            current_length = 1
    runs.append((current_label, current_length))

    # 按標籤分類統計
    label_names = {1: '吉', 0: '中', -1: '凶'}

    for label in [1, 0, -1]:
        label_runs = [length for (l, length) in runs if l == label]
        if label_runs:
            print(f"\n【{label_names[label]}】的連續長度:")
            run_counter = Counter(label_runs)
            print("長度  次數")
            for length in sorted(run_counter.keys()):
                count = run_counter[length]
                bar = "█" * count
                print(f"  {length:2d}   {count:2d}  {bar}")
            print(f"  平均: {sum(label_runs)/len(label_runs):.2f}, 最長: {max(label_runs)}")

    # 找出最長的連續序列
    print("\n最長連續序列 (Top 5):")
    sorted_runs = sorted([(l, length, i) for i, (l, length) in enumerate(runs)],
                         key=lambda x: -x[1])

    for label, length, run_idx in sorted_runs[:5]:
        # 計算這個run在哪個卦
        start_pos = sum(runs[j][1] for j in range(run_idx))
        start_hex = start_pos // 6 + 1
        end_hex = (start_pos + length - 1) // 6 + 1
        print(f"  {label_names[label]} 連續 {length} 爻 (卦{start_hex}-{end_hex})")

    return runs

def check_fibonacci_pattern(distances):
    """檢查距離是否符合Fibonacci模式"""
    print("\n" + "=" * 70)
    print("Fibonacci 模式檢查")
    print("=" * 70)

    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    fib_set = set(fib)

    fib_matches = sum(1 for d in distances if d in fib_set)
    print(f"\n距離為Fibonacci數的比例: {fib_matches}/{len(distances)} ({fib_matches/len(distances)*100:.1f}%)")

    # 檢查距離差是否為Fibonacci
    diff_distances = [abs(distances[i] - distances[i-1]) for i in range(1, len(distances))]
    diff_fib_matches = sum(1 for d in diff_distances if d in fib_set)
    print(f"距離差為Fibonacci數的比例: {diff_fib_matches}/{len(diff_distances)} ({diff_fib_matches/len(diff_distances)*100:.1f}%)")

    # 黃金比例檢查
    phi = 1.618
    ratios = [distances[i]/distances[i-1] for i in range(1, len(distances)) if distances[i-1] > 0]
    phi_matches = sum(1 for r in ratios if 0.9 < r/phi < 1.1 or 0.9 < phi/r < 1.1)
    print(f"相鄰距離比接近黃金比例: {phi_matches}/{len(ratios)} ({phi_matches/len(ratios)*100:.1f}%)")

def analyze_modular_patterns(distances):
    """檢查模數模式（如mod 6, mod 8）"""
    print("\n" + "=" * 70)
    print("模數模式分析")
    print("=" * 70)

    for mod in [2, 3, 4, 5, 6, 8]:
        remainders = [d % mod for d in distances]
        remainder_counter = Counter(remainders)

        print(f"\n距離 mod {mod}:")
        for r in range(mod):
            count = remainder_counter.get(r, 0)
            pct = count / len(distances) * 100
            bar = "█" * int(pct / 5)
            print(f"  餘數 {r}: {count:3d} ({pct:5.1f}%) {bar}")

        # 計算熵來衡量均勻程度
        probs = [remainder_counter.get(r, 0) / len(distances) for r in range(mod)]
        entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probs)
        max_entropy = math.log2(mod)
        print(f"  均勻度: {entropy/max_entropy*100:.1f}% (100%=完全均勻)")

def main():
    data = load_corrected_data()
    struct_data = load_structure()

    # 1D 變化距離分析
    change_points, distances = analyze_1d_transitions(data)

    # 卦內變化分析
    analyze_within_hexagram_transitions(data)

    # 2D 變化熱力圖
    analyze_2d_transition_pattern(data, struct_data)

    # 卦間變化分析
    analyze_cross_hexagram_transitions(data, struct_data)

    # Run Length 分析
    analyze_label_run_lengths(data)

    # Fibonacci 模式
    if distances:
        check_fibonacci_pattern(distances)

        # 模數模式
        analyze_modular_patterns(distances)

if __name__ == "__main__":
    main()
