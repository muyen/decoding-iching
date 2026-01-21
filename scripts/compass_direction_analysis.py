#!/usr/bin/env python3
"""
八卦方位分析 - 使用後天八卦的實際方位

後天八卦方位:
    坎(北)
巽(東南)    乾(西北)
震(東)          兌(西)
艮(東北)    坤(西南)
    離(南)

將64卦映射到方位座標進行分析
"""

import json
import os
from collections import defaultdict
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

# 後天八卦方位 (x, y) 座標
# 以中心為原點，北為上(+y)，東為右(+x)
LATER_HEAVEN_POS = {
    '坎': (0, 2),      # 北
    '離': (0, -2),     # 南
    '震': (2, 0),      # 東
    '兌': (-2, 0),     # 西
    '乾': (-1.4, 1.4),    # 西北
    '坤': (-1.4, -1.4),   # 西南
    '艮': (1.4, 1.4),     # 東北
    '巽': (1.4, -1.4),    # 東南
}

# 先天八卦方位（對比用）
EARLIER_HEAVEN_POS = {
    '乾': (0, 2),      # 南（先天）
    '坤': (0, -2),     # 北
    '離': (2, 0),      # 東
    '坎': (-2, 0),     # 西
    '兌': (1.4, 1.4),     # 東南
    '艮': (-1.4, -1.4),   # 西北
    '震': (1.4, -1.4),    # 東北
    '巽': (-1.4, 1.4),    # 西南
}

TRIGRAM_NAMES = ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']

def get_hexagram_position(lower, upper, positions):
    """計算卦的方位座標（下卦+上卦的中點）"""
    x1, y1 = positions[lower]
    x2, y2 = positions[upper]
    # 可以用不同的組合方式
    # 方式1: 平均位置
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def build_position_data(data, struct_data, positions):
    """建立位置到吉凶的映射"""
    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 計算每卦的吉凶
    hex_stats = defaultdict(lambda: {'ji': 0, 'zhong': 0, 'xiong': 0, 'total': 0})
    for d in data:
        hex_num = d['hex_num']
        hex_stats[hex_num]['total'] += 1
        if d['label'] == 1:
            hex_stats[hex_num]['ji'] += 1
        elif d['label'] == 0:
            hex_stats[hex_num]['zhong'] += 1
        else:
            hex_stats[hex_num]['xiong'] += 1

    # 映射到座標
    position_data = []
    for hex_num, stats in hex_stats.items():
        if hex_num not in hex_to_trigrams:
            continue

        lower, upper = hex_to_trigrams[hex_num]
        x, y = get_hexagram_position(lower, upper, positions)

        ji_rate = stats['ji'] / stats['total'] if stats['total'] > 0 else 0
        xiong_rate = stats['xiong'] / stats['total'] if stats['total'] > 0 else 0
        net = stats['ji'] - stats['xiong']

        position_data.append({
            'hex_num': hex_num,
            'lower': lower,
            'upper': upper,
            'x': x,
            'y': y,
            'ji_rate': ji_rate,
            'xiong_rate': xiong_rate,
            'net': net
        })

    return position_data

def plot_ascii_compass(position_data, value_key='net'):
    """ASCII方位圖"""
    print("\n" + "=" * 60)
    print(f"八卦方位圖 ({value_key})")
    print("=" * 60)

    # 建立網格
    grid_size = 9
    grid = [[' ' for _ in range(grid_size * 3)] for _ in range(grid_size)]

    # 標記方位
    directions = {
        (0, 2): '北(坎)',
        (0, -2): '南(離)',
        (2, 0): '東(震)',
        (-2, 0): '西(兌)',
    }

    # 歸一化位置到網格
    for pd in position_data:
        # 映射到網格座標
        gx = int((pd['x'] + 2) / 4 * (grid_size - 1))
        gy = int((2 - pd['y']) / 4 * (grid_size - 1))

        gx = max(0, min(grid_size - 1, gx))
        gy = max(0, min(grid_size - 1, gy))

        val = pd[value_key]
        if value_key == 'net':
            char = '+' if val > 0 else ('-' if val < 0 else '0')
        else:
            char = '*'

        grid[gy][gx * 3:gx * 3 + 2] = f'{char} '

    # 打印
    print("\n        北(坎)")
    print("         ↑")
    for row in grid:
        print(''.join(row))
    print("  西(兌) ← · → 東(震)")
    print("         ↓")
    print("        南(離)")

def analyze_directional_patterns(position_data):
    """方向性分析"""
    print("\n" + "=" * 60)
    print("方向性分析")
    print("=" * 60)

    # 按象限分組
    quadrants = {
        '東北': [],  # x>0, y>0
        '東南': [],  # x>0, y<0
        '西北': [],  # x<0, y>0
        '西南': [],  # x<0, y<0
        '中心': [],  # x≈0 or y≈0
    }

    for pd in position_data:
        x, y = pd['x'], pd['y']
        if abs(x) < 0.5 or abs(y) < 0.5:
            quadrants['中心'].append(pd)
        elif x > 0 and y > 0:
            quadrants['東北'].append(pd)
        elif x > 0 and y < 0:
            quadrants['東南'].append(pd)
        elif x < 0 and y > 0:
            quadrants['西北'].append(pd)
        else:
            quadrants['西南'].append(pd)

    print("\n象限分析:")
    print(f"{'象限':<8} {'卦數':<6} {'平均吉率':<10} {'平均凶率':<10} {'淨分'}")
    print("-" * 50)

    for qname in ['東北', '東南', '西南', '西北', '中心']:
        pds = quadrants[qname]
        if pds:
            avg_ji = sum(p['ji_rate'] for p in pds) / len(pds)
            avg_xiong = sum(p['xiong_rate'] for p in pds) / len(pds)
            avg_net = sum(p['net'] for p in pds) / len(pds)
            print(f"{qname:<8} {len(pds):<6} {avg_ji:<10.1%} {avg_xiong:<10.1%} {avg_net:+.1f}")

def analyze_distance_from_center(position_data):
    """距離中心的分析"""
    print("\n" + "=" * 60)
    print("距離中心分析")
    print("=" * 60)

    # 計算到中心的距離
    for pd in position_data:
        pd['distance'] = math.sqrt(pd['x']**2 + pd['y']**2)

    # 按距離分組
    close = [p for p in position_data if p['distance'] < 1.5]
    mid = [p for p in position_data if 1.5 <= p['distance'] < 2.5]
    far = [p for p in position_data if p['distance'] >= 2.5]

    print("\n按距離分組:")
    print(f"{'距離':<12} {'卦數':<6} {'平均吉率':<10} {'平均凶率':<10} {'淨分'}")
    print("-" * 55)

    for name, group in [('近(d<1.5)', close), ('中(1.5≤d<2.5)', mid), ('遠(d≥2.5)', far)]:
        if group:
            avg_ji = sum(p['ji_rate'] for p in group) / len(group)
            avg_xiong = sum(p['xiong_rate'] for p in group) / len(group)
            avg_net = sum(p['net'] for p in group) / len(group)
            print(f"{name:<12} {len(group):<6} {avg_ji:<10.1%} {avg_xiong:<10.1%} {avg_net:+.1f}")

    # 相關性分析
    distances = [p['distance'] for p in position_data]
    nets = [p['net'] for p in position_data]

    mean_d = sum(distances) / len(distances)
    mean_n = sum(nets) / len(nets)

    cov = sum((d - mean_d) * (n - mean_n) for d, n in zip(distances, nets)) / len(distances)
    std_d = math.sqrt(sum((d - mean_d)**2 for d in distances) / len(distances))
    std_n = math.sqrt(sum((n - mean_n)**2 for n in nets) / len(nets))

    if std_d > 0 and std_n > 0:
        corr = cov / (std_d * std_n)
        print(f"\n距離與淨分相關係數: {corr:.3f}")

def analyze_angle_patterns(position_data):
    """角度模式分析"""
    print("\n" + "=" * 60)
    print("角度模式分析")
    print("=" * 60)

    # 計算角度 (0度=東, 90度=北)
    for pd in position_data:
        pd['angle'] = math.degrees(math.atan2(pd['y'], pd['x']))
        if pd['angle'] < 0:
            pd['angle'] += 360

    # 按45度分組
    angle_groups = defaultdict(list)
    for pd in position_data:
        group = int(pd['angle'] / 45) * 45
        angle_groups[group].append(pd)

    print("\n按角度分組（45度區間）:")
    print(f"{'角度':<12} {'方向':<8} {'卦數':<6} {'平均吉率':<10} {'淨分'}")
    print("-" * 50)

    direction_names = {
        0: '東',
        45: '東北',
        90: '北',
        135: '西北',
        180: '西',
        225: '西南',
        270: '南',
        315: '東南',
    }

    for angle in sorted(angle_groups.keys()):
        group = angle_groups[angle]
        if group:
            avg_ji = sum(p['ji_rate'] for p in group) / len(group)
            avg_net = sum(p['net'] for p in group) / len(group)
            dir_name = direction_names.get(angle, '?')
            print(f"{angle:>3}°-{angle+45:<3}°  {dir_name:<8} {len(group):<6} {avg_ji:<10.1%} {avg_net:+.1f}")

def compare_heaven_arrangements(data, struct_data):
    """比較先天和後天八卦"""
    print("\n" + "=" * 60)
    print("先天 vs 後天八卦比較")
    print("=" * 60)

    later_data = build_position_data(data, struct_data, LATER_HEAVEN_POS)
    earlier_data = build_position_data(data, struct_data, EARLIER_HEAVEN_POS)

    # 計算在每種排列下的空間聚集性
    def spatial_autocorr(position_data):
        """計算空間自相關（相近位置的卦是否有相似吉凶）"""
        total_sim = 0
        count = 0
        for i, p1 in enumerate(position_data):
            for j, p2 in enumerate(position_data):
                if i >= j:
                    continue
                dist = math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
                if dist < 2:  # 鄰近
                    # 吉凶相似度
                    sim = 1 - abs(p1['ji_rate'] - p2['ji_rate'])
                    total_sim += sim
                    count += 1
        return total_sim / count if count > 0 else 0

    later_autocorr = spatial_autocorr(later_data)
    earlier_autocorr = spatial_autocorr(earlier_data)

    print(f"\n後天八卦空間自相關: {later_autocorr:.3f}")
    print(f"先天八卦空間自相關: {earlier_autocorr:.3f}")

    if later_autocorr > earlier_autocorr:
        print("→ 後天八卦排列更能捕捉吉凶的空間規律！")
    else:
        print("→ 先天八卦排列更能捕捉吉凶的空間規律！")

def print_trigram_map():
    """打印八卦方位對照圖"""
    print("\n" + "=" * 60)
    print("後天八卦方位圖")
    print("=" * 60)

    print("""
                    坎(北)
                      ↑
            乾(西北)     艮(東北)
                \\       /
        兌(西) ←   中    → 震(東)
                /       \\
            坤(西南)     巽(東南)
                      ↓
                    離(南)
    """)

def analyze_trigram_combination_by_direction(data, struct_data):
    """按方位分析八卦組合"""
    print("\n" + "=" * 60)
    print("八卦組合方位分析")
    print("=" * 60)

    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 計算每卦吉凶
    hex_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})
    for d in data:
        hex_num = d['hex_num']
        hex_stats[hex_num]['total'] += 1
        if d['label'] == 1:
            hex_stats[hex_num]['ji'] += 1
        elif d['label'] == -1:
            hex_stats[hex_num]['xiong'] += 1

    # 按下卦方位分組
    print("\n【下卦方位→吉率】")
    lower_by_pos = defaultdict(list)
    for hex_num, (lower, upper) in hex_to_trigrams.items():
        stats = hex_stats[hex_num]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total']
            lower_by_pos[lower].append(ji_rate)

    for trigram in TRIGRAM_NAMES:
        rates = lower_by_pos[trigram]
        if rates:
            avg = sum(rates) / len(rates)
            pos = LATER_HEAVEN_POS[trigram]
            print(f"  {trigram} ({pos[0]:+.1f}, {pos[1]:+.1f}): {avg:.1%}")

    # 按上卦方位分組
    print("\n【上卦方位→吉率】")
    upper_by_pos = defaultdict(list)
    for hex_num, (lower, upper) in hex_to_trigrams.items():
        stats = hex_stats[hex_num]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total']
            upper_by_pos[upper].append(ji_rate)

    for trigram in TRIGRAM_NAMES:
        rates = upper_by_pos[trigram]
        if rates:
            avg = sum(rates) / len(rates)
            pos = LATER_HEAVEN_POS[trigram]
            print(f"  {trigram} ({pos[0]:+.1f}, {pos[1]:+.1f}): {avg:.1%}")

def main():
    data = load_corrected_data()
    struct_data = load_structure()

    # 打印方位圖
    print_trigram_map()

    # 構建後天八卦位置數據
    position_data = build_position_data(data, struct_data, LATER_HEAVEN_POS)

    # ASCII 方位圖
    plot_ascii_compass(position_data, 'net')

    # 方向性分析
    analyze_directional_patterns(position_data)

    # 距離中心分析
    analyze_distance_from_center(position_data)

    # 角度模式
    analyze_angle_patterns(position_data)

    # 八卦組合方位分析
    analyze_trigram_combination_by_direction(data, struct_data)

    # 先天vs後天比較
    compare_heaven_arrangements(data, struct_data)

if __name__ == "__main__":
    main()
