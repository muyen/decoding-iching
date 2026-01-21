#!/usr/bin/env python3
"""
深度模式搜尋 - 測試更多數學規律

測試的模式：
1. 質數 (Prime numbers)
2. 2的冪次 (Powers of 2)
3. 三角數 (Triangular numbers)
4. Lucas數列
5. 完美數 (Perfect numbers)
6. 音樂比例 (Musical ratios)
7. King Wen序對 (覆卦/綜卦)
8. Gray碼變化
9. 自相關 (Autocorrelation)
10. Markov轉移概率
11. 熵/資訊量
12. 差分序列
13. 傅立葉分析（週期檢測）
14. XOR模式
15. 二進制漢明距離
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

def get_labels_and_distances(data):
    """獲取標籤序列和變化距離"""
    sorted_data = sorted(data, key=lambda x: (x['hex_num'], x['position']))
    labels = [d['label'] for d in sorted_data]

    change_points = []
    for i in range(1, len(labels)):
        if labels[i] != labels[i-1]:
            change_points.append(i)

    distances = [change_points[i] - change_points[i-1] for i in range(1, len(change_points))]
    return labels, change_points, distances

# ============================================================
# 數列生成器
# ============================================================

def primes_up_to(n):
    """質數"""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return set(i for i in range(n + 1) if sieve[i])

def powers_of_2(n):
    """2的冪次"""
    result = set()
    p = 1
    while p <= n:
        result.add(p)
        p *= 2
    return result

def triangular_numbers(n):
    """三角數: 1, 3, 6, 10, 15..."""
    result = set()
    t = 0
    i = 1
    while t <= n:
        t += i
        if t <= n:
            result.add(t)
        i += 1
    return result

def lucas_numbers(n):
    """Lucas數列: 2, 1, 3, 4, 7, 11..."""
    result = {2, 1}
    a, b = 2, 1
    while True:
        c = a + b
        if c > n:
            break
        result.add(c)
        a, b = b, c
    return result

def perfect_numbers(n):
    """完美數: 6, 28, 496..."""
    return {6, 28, 496} & set(range(n + 1))

def catalan_numbers(n):
    """Catalan數: 1, 1, 2, 5, 14, 42..."""
    result = set()
    for i in range(20):
        c = math.comb(2*i, i) // (i + 1)
        if c <= n:
            result.add(c)
        else:
            break
    return result

# ============================================================
# 模式測試
# ============================================================

def test_number_sequences(distances):
    """測試各種數列"""
    print("=" * 70)
    print("數列匹配測試")
    print("=" * 70)

    if not distances:
        print("無距離數據")
        return

    max_d = max(distances) + 10

    sequences = {
        'Fibonacci': {1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89},
        '質數 (Prime)': primes_up_to(max_d),
        '2的冪次': powers_of_2(max_d),
        '三角數': triangular_numbers(max_d),
        'Lucas數': lucas_numbers(max_d),
        '完美數': perfect_numbers(max_d),
        'Catalan數': catalan_numbers(max_d),
        '6的倍數': set(range(6, max_d + 1, 6)),
        '8的倍數': set(range(8, max_d + 1, 8)),
        '偶數': set(range(2, max_d + 1, 2)),
        '奇數': set(range(1, max_d + 1, 2)),
    }

    print(f"\n距離數據: {len(distances)} 個")
    print(f"距離範圍: {min(distances)} - {max(distances)}")
    print(f"\n{'數列':<20} {'匹配數':<10} {'匹配率':<10} {'評價'}")
    print("-" * 55)

    for name, seq in sequences.items():
        matches = sum(1 for d in distances if d in seq)
        rate = matches / len(distances) * 100

        # 計算期望匹配率（隨機情況）
        coverage = len(seq & set(range(1, max_d + 1))) / max_d
        expected = coverage * 100

        # 評價
        if rate > expected * 1.5:
            eval_str = "*** 顯著高於隨機 ***"
        elif rate > expected * 1.2:
            eval_str = "* 略高於隨機 *"
        elif rate < expected * 0.5:
            eval_str = "顯著低於隨機"
        else:
            eval_str = "接近隨機"

        print(f"{name:<20} {matches:<10} {rate:>6.1f}%    {eval_str}")

def test_musical_ratios(distances):
    """測試音樂比例"""
    print("\n" + "=" * 70)
    print("音樂比例測試")
    print("=" * 70)

    if len(distances) < 2:
        return

    # 相鄰距離的比例
    ratios = []
    for i in range(1, len(distances)):
        if distances[i-1] > 0:
            ratios.append(distances[i] / distances[i-1])

    # 音樂比例
    musical = {
        '八度 (2:1)': 2.0,
        '五度 (3:2)': 1.5,
        '四度 (4:3)': 1.333,
        '大三度 (5:4)': 1.25,
        '小三度 (6:5)': 1.2,
        '大二度 (9:8)': 1.125,
        '黃金比例': 1.618,
    }

    tolerance = 0.1

    print(f"\n相鄰距離比例數: {len(ratios)}")
    print(f"\n{'比例名稱':<20} {'目標值':<10} {'匹配數':<10} {'匹配率'}")
    print("-" * 55)

    for name, target in musical.items():
        matches = sum(1 for r in ratios if abs(r - target) < tolerance or abs(1/r - target) < tolerance)
        rate = matches / len(ratios) * 100
        print(f"{name:<20} {target:<10.3f} {matches:<10} {rate:>6.1f}%")

def test_autocorrelation(labels):
    """自相關分析"""
    print("\n" + "=" * 70)
    print("自相關分析 (週期性檢測)")
    print("=" * 70)

    n = len(labels)
    mean = sum(labels) / n
    var = sum((l - mean) ** 2 for l in labels) / n

    if var == 0:
        print("方差為0，無法計算自相關")
        return

    print(f"\n標籤均值: {mean:.3f}")
    print(f"標籤方差: {var:.3f}")
    print(f"\n{'滯後':<10} {'自相關係數':<15} {'解釋'}")
    print("-" * 50)

    significant_lags = []

    for lag in [1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32, 64]:
        if lag >= n:
            continue

        # 計算自相關
        autocorr = sum((labels[i] - mean) * (labels[i + lag] - mean)
                       for i in range(n - lag)) / ((n - lag) * var)

        # 顯著性閾值（約2/sqrt(n)）
        threshold = 2 / math.sqrt(n)

        if abs(autocorr) > threshold:
            significance = "*** 顯著 ***"
            significant_lags.append((lag, autocorr))
        else:
            significance = ""

        print(f"{lag:<10} {autocorr:>+.4f}         {significance}")

    if significant_lags:
        print(f"\n發現顯著自相關的滯後: {[l for l, _ in significant_lags]}")
        # 檢查是否對應6爻或8卦
        for lag, corr in significant_lags:
            if lag == 6:
                print("  → 滯後6對應每卦的6爻結構！")
            if lag == 8:
                print("  → 滯後8可能對應八卦？")
            if lag % 6 == 0:
                print(f"  → 滯後{lag}是6的倍數（{lag//6}卦）")

def test_markov_transitions(labels):
    """Markov轉移概率"""
    print("\n" + "=" * 70)
    print("Markov 轉移概率矩陣")
    print("=" * 70)

    label_names = {1: '吉', 0: '中', -1: '凶'}

    # 計算轉移次數
    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(1, len(labels)):
        transitions[labels[i-1]][labels[i]] += 1

    # 計算轉移概率
    print("\n轉移概率矩陣 (從→到):")
    print("       吉      中      凶")
    print("-" * 30)

    for from_label in [1, 0, -1]:
        total = sum(transitions[from_label].values())
        if total > 0:
            probs = [transitions[from_label][to_label] / total * 100
                     for to_label in [1, 0, -1]]
            print(f"{label_names[from_label]}    {probs[0]:>5.1f}%  {probs[1]:>5.1f}%  {probs[2]:>5.1f}%")

    # 檢查對稱性
    print("\n對稱性檢查 (A→B vs B→A):")
    for (a, b) in [(1, 0), (1, -1), (0, -1)]:
        ab = transitions[a][b]
        ba = transitions[b][a]
        diff = abs(ab - ba)
        total = ab + ba
        if total > 0:
            print(f"  {label_names[a]}→{label_names[b]}: {ab}, {label_names[b]}→{label_names[a]}: {ba}, 差異: {diff}")

def test_entropy(labels, window_sizes=[6, 12, 24, 48]):
    """熵分析"""
    print("\n" + "=" * 70)
    print("熵分析 (資訊量)")
    print("=" * 70)

    def calculate_entropy(seq):
        if not seq:
            return 0
        counter = Counter(seq)
        n = len(seq)
        return -sum((c/n) * math.log2(c/n) for c in counter.values() if c > 0)

    # 全局熵
    global_entropy = calculate_entropy(labels)
    max_entropy = math.log2(3)  # 3個標籤

    print(f"\n全局熵: {global_entropy:.4f} (最大: {max_entropy:.4f})")
    print(f"熵比例: {global_entropy/max_entropy*100:.1f}%")

    # 滑動窗口熵
    print(f"\n滑動窗口熵分析:")
    print(f"{'窗口大小':<12} {'平均熵':<12} {'熵變異':<12} {'意義'}")
    print("-" * 55)

    for window in window_sizes:
        entropies = []
        for i in range(len(labels) - window + 1):
            e = calculate_entropy(labels[i:i+window])
            entropies.append(e)

        avg_e = sum(entropies) / len(entropies)
        var_e = math.sqrt(sum((e - avg_e)**2 for e in entropies) / len(entropies))

        meaning = ""
        if window == 6:
            meaning = "(每卦)"
        elif window == 12:
            meaning = "(兩卦)"
        elif window == 48:
            meaning = "(八卦)"

        print(f"{window:<12} {avg_e:<12.4f} {var_e:<12.4f} {meaning}")

def test_difference_sequences(labels):
    """差分序列分析"""
    print("\n" + "=" * 70)
    print("差分序列分析")
    print("=" * 70)

    # 一階差分
    diff1 = [labels[i] - labels[i-1] for i in range(1, len(labels))]

    # 二階差分
    diff2 = [diff1[i] - diff1[i-1] for i in range(1, len(diff1))]

    print("\n一階差分分布 (相鄰標籤之差):")
    diff1_counter = Counter(diff1)
    for d in sorted(diff1_counter.keys()):
        count = diff1_counter[d]
        pct = count / len(diff1) * 100
        meaning = ""
        if d == 0:
            meaning = "不變"
        elif d > 0:
            meaning = "變好"
        else:
            meaning = "變壞"
        print(f"  {d:+d}: {count:3d} ({pct:5.1f}%) {meaning}")

    print("\n二階差分分布 (變化的變化):")
    diff2_counter = Counter(diff2)
    for d in sorted(diff2_counter.keys()):
        count = diff2_counter[d]
        pct = count / len(diff2) * 100
        meaning = ""
        if d == 0:
            meaning = "趨勢不變"
        elif d > 0:
            meaning = "加速變好"
        else:
            meaning = "加速變壞"
        print(f"  {d:+d}: {count:3d} ({pct:5.1f}%) {meaning}")

def test_xor_patterns(data, struct_data):
    """XOR模式分析"""
    print("\n" + "=" * 70)
    print("XOR 模式分析 (二進制差異)")
    print("=" * 70)

    hex_to_binary = {}
    for hex_num, info in struct_data.items():
        hex_to_binary[int(hex_num)] = info['binary']

    # 計算每卦的淨分
    hex_scores = defaultdict(int)
    for d in data:
        hex_scores[d['hex_num']] += d['label']

    # XOR分析：比較二進制差異與吉凶差異
    hex_nums = sorted(hex_scores.keys())

    xor_vs_diff = []
    for i in range(len(hex_nums)):
        for j in range(i+1, len(hex_nums)):
            h1, h2 = hex_nums[i], hex_nums[j]
            if h1 not in hex_to_binary or h2 not in hex_to_binary:
                continue

            b1 = hex_to_binary[h1]
            b2 = hex_to_binary[h2]

            # 計算漢明距離（不同bit數）
            hamming = sum(a != b for a, b in zip(b1, b2))

            # 吉凶差異
            score_diff = abs(hex_scores[h1] - hex_scores[h2])

            xor_vs_diff.append((hamming, score_diff))

    # 按漢明距離分組
    print("\n漢明距離 vs 吉凶差異:")
    print(f"{'漢明距離':<12} {'平均吉凶差':<15} {'樣本數'}")
    print("-" * 40)

    hamming_groups = defaultdict(list)
    for h, d in xor_vs_diff:
        hamming_groups[h].append(d)

    for hamming in sorted(hamming_groups.keys()):
        diffs = hamming_groups[hamming]
        avg_diff = sum(diffs) / len(diffs)
        print(f"{hamming:<12} {avg_diff:<15.2f} {len(diffs)}")

    # 計算相關性
    if xor_vs_diff:
        n = len(xor_vs_diff)
        mean_h = sum(h for h, _ in xor_vs_diff) / n
        mean_d = sum(d for _, d in xor_vs_diff) / n

        cov = sum((h - mean_h) * (d - mean_d) for h, d in xor_vs_diff) / n
        std_h = math.sqrt(sum((h - mean_h)**2 for h, _ in xor_vs_diff) / n)
        std_d = math.sqrt(sum((d - mean_d)**2 for _, d in xor_vs_diff) / n)

        if std_h > 0 and std_d > 0:
            correlation = cov / (std_h * std_d)
            print(f"\n漢明距離與吉凶差異的相關係數: {correlation:.4f}")
            if abs(correlation) > 0.3:
                print("→ 中等相關！二進制差異與吉凶有關聯")
            elif abs(correlation) > 0.1:
                print("→ 弱相關")
            else:
                print("→ 幾乎無相關")

def test_king_wen_pairs(data, struct_data):
    """King Wen 序對分析"""
    print("\n" + "=" * 70)
    print("King Wen 序對分析 (覆卦/綜卦)")
    print("=" * 70)

    # 計算每卦的淨分
    hex_scores = defaultdict(int)
    for d in data:
        hex_scores[d['hex_num']] += d['label']

    # 獲取覆卦和對卦關係
    hex_to_info = {}
    for hex_num, info in struct_data.items():
        hex_to_info[int(hex_num)] = {
            'inverse': info.get('inverse_hexagram'),
            'complement': info.get('complement_hexagram'),
            'is_symmetric': info.get('is_symmetric', False)
        }

    # 分析相鄰對（King Wen序中1-2, 3-4等）
    print("\n相鄰卦對分析 (1-2, 3-4, ...):")
    pair_diffs = []
    for i in range(1, 64, 2):
        if i in hex_scores and i+1 in hex_scores:
            diff = abs(hex_scores[i] - hex_scores[i+1])
            pair_diffs.append(diff)

    avg_pair_diff = sum(pair_diffs) / len(pair_diffs) if pair_diffs else 0
    print(f"  相鄰卦對的平均分數差: {avg_pair_diff:.2f}")

    # 隨機對比
    import random
    random_diffs = []
    all_scores = list(hex_scores.values())
    for _ in range(1000):
        i, j = random.sample(range(len(all_scores)), 2)
        random_diffs.append(abs(all_scores[i] - all_scores[j]))

    avg_random_diff = sum(random_diffs) / len(random_diffs)
    print(f"  隨機卦對的平均分數差: {avg_random_diff:.2f}")

    if avg_pair_diff < avg_random_diff * 0.8:
        print("  → King Wen 相鄰對比隨機更相似！")
    elif avg_pair_diff > avg_random_diff * 1.2:
        print("  → King Wen 相鄰對比隨機更不同！")
    else:
        print("  → 無顯著差異")

def test_position_within_hexagram_correlation(data):
    """爻位與吉凶的相關性"""
    print("\n" + "=" * 70)
    print("爻位吉凶相關性深入分析")
    print("=" * 70)

    # 按爻位分組
    pos_labels = defaultdict(list)
    for d in data:
        pos_labels[d['position']].append(d['label'])

    # 計算爻位之間的相關性
    print("\n爻位間吉凶相關係數:")
    print("     1     2     3     4     5     6")

    for p1 in range(1, 7):
        print(f"{p1}", end="  ")
        for p2 in range(1, 7):
            if p1 == p2:
                print(" 1.00", end="")
            else:
                # 對應卦的爻位值
                correlations = []
                hex_groups = defaultdict(dict)
                for d in data:
                    hex_groups[d['hex_num']][d['position']] = d['label']

                pairs = []
                for hex_num, positions in hex_groups.items():
                    if p1 in positions and p2 in positions:
                        pairs.append((positions[p1], positions[p2]))

                if pairs:
                    n = len(pairs)
                    mean1 = sum(a for a, _ in pairs) / n
                    mean2 = sum(b for _, b in pairs) / n

                    cov = sum((a - mean1) * (b - mean2) for a, b in pairs) / n
                    std1 = math.sqrt(sum((a - mean1)**2 for a, _ in pairs) / n)
                    std2 = math.sqrt(sum((b - mean2)**2 for _, b in pairs) / n)

                    if std1 > 0 and std2 > 0:
                        corr = cov / (std1 * std2)
                        print(f" {corr:+.2f}", end="")
                    else:
                        print("  N/A", end="")
                else:
                    print("  N/A", end="")
        print()

    print("\n解讀：正相關=傾向同吉同凶，負相關=傾向一吉一凶")

def main():
    data = load_corrected_data()
    struct_data = load_structure()

    labels, change_points, distances = get_labels_and_distances(data)

    # 各種測試
    test_number_sequences(distances)
    test_musical_ratios(distances)
    test_autocorrelation(labels)
    test_markov_transitions(labels)
    test_entropy(labels)
    test_difference_sequences(labels)
    test_xor_patterns(data, struct_data)
    test_king_wen_pairs(data, struct_data)
    test_position_within_hexagram_correlation(data)

if __name__ == "__main__":
    main()
