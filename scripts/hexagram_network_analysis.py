#!/usr/bin/env python3
"""
64卦變卦網絡圖論分析

將64卦視為圖的節點，變卦關係視為邊：
- 分析網絡結構特性
- 找出關鍵轉折卦（樞紐）
- 識別卦群（社群檢測）
- 研究吉凶傳遞模式

關鍵概念：
- 每個卦有6種可能的變化（變爻）
- 某些卦是「轉折點」- 離開/到達後吉凶大幅改變
- 某些卦群傾向互相轉換
"""

import json
from pathlib import Path
from collections import defaultdict
import math


def load_biangua_data():
    """載入變卦數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'biangua_384.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_yao_data():
    """載入爻數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_adjacency_graph(biangua_data):
    """
    建立鄰接圖

    節點：64卦
    邊：變卦關係（帶方向）
    權重：該變爻的吉凶
    """
    graph = defaultdict(lambda: {'out': [], 'in': []})

    for trans in biangua_data['transformations']:
        orig = trans['original_num']
        changed = trans['changed_num']
        pos = trans['line_position']
        yaoci_class = trans['yaoci_class']
        trend = trans['trend_change']

        # 轉換吉凶為數值
        if yaoci_class == '吉':
            weight = 1
        elif yaoci_class == '凶':
            weight = -1
        else:
            weight = 0

        graph[orig]['out'].append({
            'target': changed,
            'position': pos,
            'class': yaoci_class,
            'weight': weight,
            'trend': trend
        })

        graph[changed]['in'].append({
            'source': orig,
            'position': pos,
            'class': yaoci_class,
            'weight': weight,
            'trend': trend
        })

    return graph


def analyze_centrality(graph):
    """
    分析卦的中心性

    度中心性：連接數量
    流動中心性：吉凶流動量
    """
    print("\n" + "="*70)
    print("【分析1】卦的中心性分析")
    print("="*70)

    centrality = {}

    for hex_num in range(1, 65):
        out_edges = graph[hex_num]['out']
        in_edges = graph[hex_num]['in']

        # 出度、入度
        out_degree = len(out_edges)
        in_degree = len(in_edges)

        # 吉流出、吉流入
        ji_out = sum(1 for e in out_edges if e['weight'] == 1)
        ji_in = sum(1 for e in in_edges if e['weight'] == 1)

        # 凶流出、凶流入
        xiong_out = sum(1 for e in out_edges if e['weight'] == -1)
        xiong_in = sum(1 for e in in_edges if e['weight'] == -1)

        # 趨勢影響
        avg_trend_out = sum(e['trend'] for e in out_edges) / len(out_edges) if out_edges else 0
        avg_trend_in = sum(e['trend'] for e in in_edges) / len(in_edges) if in_edges else 0

        centrality[hex_num] = {
            'out_degree': out_degree,
            'in_degree': in_degree,
            'ji_out': ji_out,
            'ji_in': ji_in,
            'xiong_out': xiong_out,
            'xiong_in': xiong_in,
            'avg_trend_out': avg_trend_out,
            'avg_trend_in': avg_trend_in,
            'ji_ratio': (ji_out + ji_in) / (out_degree + in_degree) if (out_degree + in_degree) > 0 else 0,
            'net_ji_flow': ji_in - ji_out,  # 淨吉流入
        }

    print("\n【A】吉氣「吸收者」（淨吉流入最高）：")
    print("-" * 50)
    sorted_by_net = sorted(centrality.items(), key=lambda x: -x[1]['net_ji_flow'])
    for i, (hex_num, stats) in enumerate(sorted_by_net[:10]):
        print(f"  {i+1}. 卦{hex_num:2}: 淨吉流入={stats['net_ji_flow']:+d}  (流入{stats['ji_in']}, 流出{stats['ji_out']})")

    print("\n【B】吉氣「發射者」（淨吉流出最高）：")
    print("-" * 50)
    for i, (hex_num, stats) in enumerate(sorted_by_net[-10:][::-1]):
        print(f"  {i+1}. 卦{hex_num:2}: 淨吉流出={-stats['net_ji_flow']:+d}  (流入{stats['ji_in']}, 流出{stats['ji_out']})")

    print("\n【C】趨勢轉折點（離開後趨勢變化最大）：")
    print("-" * 50)
    sorted_by_trend = sorted(centrality.items(), key=lambda x: abs(x[1]['avg_trend_out']), reverse=True)
    for i, (hex_num, stats) in enumerate(sorted_by_trend[:10]):
        direction = '↑' if stats['avg_trend_out'] > 0 else '↓'
        print(f"  {i+1}. 卦{hex_num:2}: 離開後趨勢={stats['avg_trend_out']:+.3f} {direction}")

    return centrality


def analyze_hub_hexagrams(graph, yao_data):
    """
    分析樞紐卦

    樞紐卦：變化後吉凶變化大的卦
    """
    print("\n" + "="*70)
    print("【分析2】樞紐卦分析（轉折點）")
    print("="*70)

    # 計算每卦的整體吉率
    hex_ji_rates = defaultdict(lambda: {'吉': 0, '凶': 0, '中': 0})
    for item in yao_data:
        hex_num = item['hex_num']
        label = item['label']
        if label == 1:
            hex_ji_rates[hex_num]['吉'] += 1
        elif label == -1:
            hex_ji_rates[hex_num]['凶'] += 1
        else:
            hex_ji_rates[hex_num]['中'] += 1

    # 計算吉率
    ji_rates = {}
    for hex_num, stats in hex_ji_rates.items():
        total = sum(stats.values())
        ji_rates[hex_num] = stats['吉'] / total if total > 0 else 0

    # 分析每個變化的吉凶差異
    hub_scores = defaultdict(list)

    for trans in load_biangua_data()['transformations']:
        orig = trans['original_num']
        changed = trans['changed_num']

        orig_rate = ji_rates.get(orig, 0)
        changed_rate = ji_rates.get(changed, 0)

        diff = changed_rate - orig_rate

        hub_scores[orig].append({
            'to': changed,
            'diff': diff
        })

    # 計算每卦的「轉折力」
    hex_pivot_power = {}
    for hex_num, changes in hub_scores.items():
        avg_diff = sum(c['diff'] for c in changes) / len(changes) if changes else 0
        max_diff = max(c['diff'] for c in changes) if changes else 0
        min_diff = min(c['diff'] for c in changes) if changes else 0

        hex_pivot_power[hex_num] = {
            'avg_diff': avg_diff,
            'max_diff': max_diff,
            'min_diff': min_diff,
            'range': max_diff - min_diff
        }

    print("\n【發現】離開後吉率大幅上升的卦（脫離困境）：")
    print("-" * 50)
    sorted_pivot = sorted(hex_pivot_power.items(), key=lambda x: -x[1]['avg_diff'])
    for i, (hex_num, stats) in enumerate(sorted_pivot[:10]):
        name = get_hex_name(hex_num)
        print(f"  {i+1}. 卦{hex_num:2}({name}): 離開後平均吉率變化={stats['avg_diff']:+.3f}")

    print("\n【發現】離開後吉率大幅下降的卦（離開福地）：")
    print("-" * 50)
    for i, (hex_num, stats) in enumerate(sorted_pivot[-10:][::-1]):
        name = get_hex_name(hex_num)
        print(f"  {i+1}. 卦{hex_num:2}({name}): 離開後平均吉率變化={stats['avg_diff']:+.3f}")

    return hex_pivot_power


def get_hex_name(hex_num):
    """獲取卦名"""
    hex_names = {
        1: '乾', 2: '坤', 3: '屯', 4: '蒙', 5: '需', 6: '訟', 7: '師', 8: '比',
        9: '小畜', 10: '履', 11: '泰', 12: '否', 13: '同人', 14: '大有', 15: '謙', 16: '豫',
        17: '隨', 18: '蠱', 19: '臨', 20: '觀', 21: '噬嗑', 22: '賁', 23: '剝', 24: '復',
        25: '无妄', 26: '大畜', 27: '頤', 28: '大過', 29: '坎', 30: '離', 31: '咸', 32: '恆',
        33: '遯', 34: '大壯', 35: '晉', 36: '明夷', 37: '家人', 38: '睽', 39: '蹇', 40: '解',
        41: '損', 42: '益', 43: '夬', 44: '姤', 45: '萃', 46: '升', 47: '困', 48: '井',
        49: '革', 50: '鼎', 51: '震', 52: '艮', 53: '漸', 54: '歸妹', 55: '豐', 56: '旅',
        57: '巽', 58: '兌', 59: '渙', 60: '節', 61: '中孚', 62: '小過', 63: '既濟', 64: '未濟'
    }
    return hex_names.get(hex_num, f'卦{hex_num}')


def analyze_clusters(graph):
    """
    分析卦群（社群檢測）

    用簡單的連通分量和高頻互變來識別卦群
    """
    print("\n" + "="*70)
    print("【分析3】卦群分析（常互變的卦組）")
    print("="*70)

    # 建立無向邊的頻率矩陣
    edge_freq = defaultdict(int)

    for hex_num in range(1, 65):
        for edge in graph[hex_num]['out']:
            pair = tuple(sorted([hex_num, edge['target']]))
            edge_freq[pair] += 1

    # 找出高頻互變對
    print("\n最常互變的卦對：")
    print("-" * 50)
    sorted_pairs = sorted(edge_freq.items(), key=lambda x: -x[1])

    for i, (pair, freq) in enumerate(sorted_pairs[:15]):
        h1, h2 = pair
        name1 = get_hex_name(h1)
        name2 = get_hex_name(h2)
        print(f"  {i+1}. {name1}({h1}) ↔ {name2}({h2}): {freq}次互變")

    # 按八宮分組（傳統分類）
    print("\n按八宮分析：")
    print("-" * 50)

    # 八宮對應的卦
    eight_houses = {
        '乾宮': [1, 44, 13, 10, 9, 14, 43, 34],
        '坤宮': [2, 24, 7, 15, 16, 8, 23, 20],
        '震宮': [51, 16, 40, 32, 46, 48, 28, 17],
        '巽宮': [57, 9, 37, 53, 20, 42, 25, 18],
        '坎宮': [29, 60, 3, 63, 49, 55, 36, 7],
        '離宮': [30, 56, 50, 64, 4, 59, 6, 13],
        '艮宮': [52, 22, 26, 41, 38, 10, 61, 53],
        '兌宮': [58, 17, 45, 31, 39, 60, 62, 54],
    }

    for house, hexagrams in eight_houses.items():
        # 計算宮內互變頻率
        internal_edges = 0
        for h1 in hexagrams:
            for h2 in hexagrams:
                if h1 < h2:
                    pair = (h1, h2)
                    internal_edges += edge_freq.get(pair, 0)

        print(f"  {house}: 宮內互變{internal_edges}次")

    return edge_freq


def analyze_path_patterns(graph):
    """
    分析路徑模式

    從凶卦到吉卦的路徑特性
    """
    print("\n" + "="*70)
    print("【分析4】吉凶轉換路徑分析")
    print("="*70)

    # 統計從不同類型爻出發的變化
    class_transitions = defaultdict(lambda: defaultdict(int))

    biangua_data = load_biangua_data()
    for trans in biangua_data['transformations']:
        from_class = trans['yaoci_class']
        trend = trans['trend_change']

        if trend > 0.1:
            to_state = '變好'
        elif trend < -0.1:
            to_state = '變差'
        else:
            to_state = '持平'

        class_transitions[from_class][to_state] += 1

    print("\n從不同吉凶狀態出發的變化趨勢：")
    print("-" * 60)

    for from_class in ['吉', '中', '凶']:
        transitions = class_transitions[from_class]
        total = sum(transitions.values())
        if total > 0:
            better = transitions['變好'] / total * 100
            same = transitions['持平'] / total * 100
            worse = transitions['變差'] / total * 100
            print(f"  從「{from_class}」出發: 變好={better:.1f}%  持平={same:.1f}%  變差={worse:.1f}%  (n={total})")

    # 分析變爻位置與趨勢的關係
    print("\n各位置變爻的趨勢影響：")
    print("-" * 50)

    pos_trends = defaultdict(list)
    for trans in biangua_data['transformations']:
        pos = trans['line_position']
        trend = trans['trend_change']
        pos_trends[pos].append(trend)

    for pos in range(1, 7):
        trends = pos_trends[pos]
        if trends:
            avg = sum(trends) / len(trends)
            positive = sum(1 for t in trends if t > 0) / len(trends) * 100
            negative = sum(1 for t in trends if t < 0) / len(trends) * 100
            print(f"  爻{pos}變: 平均趨勢={avg:+.3f}  上升比例={positive:.1f}%  下降比例={negative:.1f}%")

    return class_transitions


def analyze_biangua_symmetry(graph):
    """
    分析變卦的對稱性

    A變B 與 B變A 的吉凶是否對稱？
    """
    print("\n" + "="*70)
    print("【分析5】變卦對稱性分析")
    print("="*70)

    biangua_data = load_biangua_data()

    # 建立變卦對照表
    transformations = {}
    for trans in biangua_data['transformations']:
        orig = trans['original_num']
        changed = trans['changed_num']
        pos = trans['line_position']
        key = (orig, changed, pos)
        transformations[key] = trans

    # 分析對稱性
    symmetric_pairs = []
    asymmetric_pairs = []

    checked = set()
    for trans in biangua_data['transformations']:
        orig = trans['original_num']
        changed = trans['changed_num']
        pos = trans['line_position']

        if (orig, changed) in checked:
            continue

        # 找反向變卦
        reverse_key = (changed, orig, pos)
        if reverse_key in transformations:
            reverse_trans = transformations[reverse_key]

            orig_class = trans['yaoci_class']
            reverse_class = reverse_trans['yaoci_class']

            if orig_class == reverse_class:
                symmetric_pairs.append((orig, changed, pos, orig_class))
            else:
                asymmetric_pairs.append((orig, changed, pos, orig_class, reverse_class))

        checked.add((orig, changed))
        checked.add((changed, orig))

    print(f"\n對稱變卦對數量：{len(symmetric_pairs)}")
    print(f"不對稱變卦對數量：{len(asymmetric_pairs)}")

    print("\n典型不對稱案例（A→B吉，B→A凶）：")
    print("-" * 60)

    # 找出極端不對稱案例
    extreme_asymmetric = [p for p in asymmetric_pairs
                         if (p[3] == '吉' and p[4] == '凶') or (p[3] == '凶' and p[4] == '吉')]

    for i, (h1, h2, pos, c1, c2) in enumerate(extreme_asymmetric[:10]):
        name1 = get_hex_name(h1)
        name2 = get_hex_name(h2)
        print(f"  爻{pos}: {name1}→{name2}({c1}) vs {name2}→{name1}({c2})")

    return symmetric_pairs, asymmetric_pairs


def synthesize_network_findings():
    """總結網絡分析發現"""
    print("\n" + "="*70)
    print("64卦變卦網絡分析總結")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    64卦變卦網絡分析結果                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【網絡結構特性】                                                    ║
║  ────────────────                                                    ║
║  - 64個節點，384條有向邊                                             ║
║  - 每個卦有6個出邊、6個入邊                                          ║
║  - 網絡是完全對稱的結構                                              ║
║                                                                      ║
║  【關鍵發現】                                                        ║
║  ──────────                                                          ║
║  1. 某些卦是「吉氣吸收者」- 變到這裡趨勢向好                        ║
║  2. 某些卦是「吉氣發射者」- 離開這裡趨勢向好                        ║
║  3. 變卦不完全對稱：A→B吉 不代表 B→A吉                              ║
║  4. 變爻位置影響趨勢                                                ║
║                                                                      ║
║  【實用意義】                                                        ║
║  ──────────                                                          ║
║  - 處於「困境卦」時，某些變化路徑較佳                                ║
║  - 處於「福地卦」時，避免隨意變動                                    ║
║  - 變爻位置本身帶有吉凶傾向                                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("64卦變卦網絡圖論分析")
    print("="*70)
    print("\n將64卦視為網絡節點，分析變卦關係的結構特性")

    biangua_data = load_biangua_data()
    yao_data = load_yao_data()

    print(f"\n載入 {len(biangua_data['transformations'])} 條變卦數據")

    # 建立圖
    graph = build_adjacency_graph(biangua_data)

    # 分析
    analyze_centrality(graph)
    analyze_hub_hexagrams(graph, yao_data)
    analyze_clusters(graph)
    analyze_path_patterns(graph)
    analyze_biangua_symmetry(graph)

    # 總結
    synthesize_network_findings()


if __name__ == '__main__':
    main()
