#!/usr/bin/env python3
"""
變卦路徑優化分析

核心問題：
1. 從困境卦（如觀、恆、旅）到福地卦（如謙、臨、需）的最短路徑？
2. 吉凶累積最優的路徑？
3. 哪些卦是「必經之路」（樞紐）？

方法：
- 將64卦視為圖節點
- 用BFS/Dijkstra找最短路徑
- 用加權路徑找最優吉凶累積

基於之前分析的發現：
- 福地卦（離開後吉率下降）：謙(-55.6%)、臨(-52.8%)、需(-50%)
- 困境卦（離開後吉率上升）：觀(+44.4%)、恆(+44.4%)、旅(+44.4%)
"""

import json
from pathlib import Path
from collections import defaultdict, deque
import heapq


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


# 卦名對照
HEX_NAMES = {
    1: '乾', 2: '坤', 3: '屯', 4: '蒙', 5: '需', 6: '訟', 7: '師', 8: '比',
    9: '小畜', 10: '履', 11: '泰', 12: '否', 13: '同人', 14: '大有', 15: '謙', 16: '豫',
    17: '隨', 18: '蠱', 19: '臨', 20: '觀', 21: '噬嗑', 22: '賁', 23: '剝', 24: '復',
    25: '无妄', 26: '大畜', 27: '頤', 28: '大過', 29: '坎', 30: '離', 31: '咸', 32: '恆',
    33: '遯', 34: '大壯', 35: '晉', 36: '明夷', 37: '家人', 38: '睽', 39: '蹇', 40: '解',
    41: '損', 42: '益', 43: '夬', 44: '姤', 45: '萃', 46: '升', 47: '困', 48: '井',
    49: '革', 50: '鼎', 51: '震', 52: '艮', 53: '漸', 54: '歸妹', 55: '豐', 56: '旅',
    57: '巽', 58: '兌', 59: '渙', 60: '節', 61: '中孚', 62: '小過', 63: '既濟', 64: '未濟'
}

# 反向對照
NAME_TO_NUM = {v: k for k, v in HEX_NAMES.items()}


def build_graph(biangua_data, yao_data):
    """
    建立加權圖

    邊權重選項：
    1. 單位權重（最短步數）
    2. 吉凶權重（最優吉凶累積）
    3. 趨勢權重（最大趨勢改善）
    """
    # 計算每卦的吉率
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

    ji_rates = {}
    for hex_num, stats in hex_ji_rates.items():
        total = sum(stats.values())
        ji_rates[hex_num] = stats['吉'] / total if total > 0 else 0

    # 建立鄰接表
    graph = defaultdict(list)  # graph[from] = [(to, weight, position, yaoci_class), ...]

    for trans in biangua_data['transformations']:
        orig = trans['original_num']
        changed = trans['changed_num']
        pos = trans['line_position']
        yaoci_class = trans['yaoci_class']
        trend = trans['trend_change']

        # 多種權重
        # 1. 單位權重
        unit_weight = 1

        # 2. 吉凶權重（吉=負權重更優，凶=正權重更差）
        if yaoci_class == '吉':
            ji_weight = -1  # 吉的路徑更優
        elif yaoci_class == '凶':
            ji_weight = 2   # 凶的路徑懲罰更重
        else:
            ji_weight = 0

        # 3. 趨勢權重（負趨勢=到更差的卦）
        trend_weight = -trend  # 趨勢越正（變好），權重越負（越優）

        graph[orig].append({
            'to': changed,
            'unit': unit_weight,
            'ji': ji_weight,
            'trend': trend_weight,
            'position': pos,
            'class': yaoci_class
        })

    return graph, ji_rates


def bfs_shortest_path(graph, start, end):
    """
    BFS找最短路徑（步數最少）
    """
    if start == end:
        return [start], 0

    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        current, path = queue.popleft()

        for edge in graph[current]:
            next_hex = edge['to']
            if next_hex == end:
                return path + [next_hex], len(path)

            if next_hex not in visited:
                visited.add(next_hex)
                queue.append((next_hex, path + [next_hex]))

    return None, float('inf')


def dijkstra_optimal_path(graph, start, end, weight_type='ji'):
    """
    Dijkstra找最優路徑

    weight_type:
    - 'ji': 吉凶最優
    - 'trend': 趨勢最優
    - 'unit': 最短步數
    """
    if start == end:
        return [start], 0, []

    # (累積權重, 當前節點, 路徑, 邊信息)
    heap = [(0, start, [start], [])]
    visited = set()

    while heap:
        cost, current, path, edges = heapq.heappop(heap)

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            return path, cost, edges

        for edge in graph[current]:
            next_hex = edge['to']
            if next_hex not in visited:
                weight = edge[weight_type]
                new_cost = cost + weight
                heapq.heappush(heap, (
                    new_cost,
                    next_hex,
                    path + [next_hex],
                    edges + [edge]
                ))

    return None, float('inf'), []


def find_all_paths_limited(graph, start, end, max_depth=4):
    """
    找出所有路徑（限制深度）
    """
    all_paths = []

    def dfs(current, path, edges, depth):
        if depth > max_depth:
            return

        if current == end:
            all_paths.append((path[:], edges[:]))
            return

        for edge in graph[current]:
            next_hex = edge['to']
            if next_hex not in path:  # 避免循環
                path.append(next_hex)
                edges.append(edge)
                dfs(next_hex, path, edges, depth + 1)
                path.pop()
                edges.pop()

    dfs(start, [start], [], 0)
    return all_paths


def analyze_escape_routes(graph, ji_rates):
    """
    分析「脫困路線」

    從困境卦出發，找到福地卦的最佳路徑
    """
    print("\n" + "="*70)
    print("【分析1】脫困路線（從困境卦到福地卦）")
    print("="*70)

    # 困境卦（離開後吉率大幅上升）
    trouble_hexs = [20, 32, 56, 43, 63]  # 觀、恆、旅、夬、既濟

    # 福地卦（離開後吉率大幅下降）
    fortune_hexs = [15, 19, 5, 50, 8]  # 謙、臨、需、鼎、比

    print("\n困境卦 → 福地卦 最短路徑：")
    print("-" * 60)

    for trouble in trouble_hexs[:3]:
        for fortune in fortune_hexs[:3]:
            path, steps, edges = dijkstra_optimal_path(graph, trouble, fortune, 'unit')

            if path:
                trouble_name = HEX_NAMES[trouble]
                fortune_name = HEX_NAMES[fortune]

                path_str = ' → '.join([HEX_NAMES[h] for h in path])

                # 計算路徑的吉凶分布
                ji_count = sum(1 for e in edges if e['class'] == '吉')
                xiong_count = sum(1 for e in edges if e['class'] == '凶')

                print(f"\n  {trouble_name}({trouble}) → {fortune_name}({fortune})")
                print(f"    路徑: {path_str}")
                print(f"    步數: {steps}, 吉爻: {ji_count}, 凶爻: {xiong_count}")


def analyze_optimal_routes(graph, ji_rates):
    """
    分析「吉凶最優路線」

    考慮過程中的吉凶累積，而不只是步數
    """
    print("\n" + "="*70)
    print("【分析2】吉凶最優路線（過程也重要）")
    print("="*70)

    # 選擇幾組起終點
    routes = [
        (20, 15, '觀→謙'),  # 困境到福地
        (47, 19, '困→臨'),  # 困難到良機
        (29, 11, '坎→泰'),  # 險難到通達
        (39, 42, '蹇→益'),  # 艱難到獲益
    ]

    for start, end, desc in routes:
        print(f"\n【{desc}】")
        print("-" * 50)

        # 最短路徑
        short_path, short_cost, short_edges = dijkstra_optimal_path(graph, start, end, 'unit')

        # 吉凶最優路徑
        ji_path, ji_cost, ji_edges = dijkstra_optimal_path(graph, start, end, 'ji')

        if short_path:
            print(f"  最短路徑 ({len(short_path)-1}步):")
            print(f"    {' → '.join([HEX_NAMES[h] for h in short_path])}")
            short_ji = sum(1 for e in short_edges if e['class'] == '吉')
            short_xiong = sum(1 for e in short_edges if e['class'] == '凶')
            print(f"    吉/凶爻: {short_ji}/{short_xiong}")

        if ji_path and ji_path != short_path:
            print(f"  吉凶最優路徑 ({len(ji_path)-1}步, 權重={ji_cost}):")
            print(f"    {' → '.join([HEX_NAMES[h] for h in ji_path])}")
            opt_ji = sum(1 for e in ji_edges if e['class'] == '吉')
            opt_xiong = sum(1 for e in ji_edges if e['class'] == '凶')
            print(f"    吉/凶爻: {opt_ji}/{opt_xiong}")


def analyze_hub_hexagrams(graph):
    """
    分析「樞紐卦」

    哪些卦是最多路徑的必經之地？
    """
    print("\n" + "="*70)
    print("【分析3】樞紐卦分析（必經之路）")
    print("="*70)

    # 統計每個卦被經過的次數
    pass_count = defaultdict(int)

    # 隨機抽樣一些起終點對
    sample_pairs = [
        (1, 2), (3, 64), (7, 58), (11, 12), (15, 16),
        (20, 19), (29, 30), (39, 40), (47, 48), (63, 64),
        (5, 50), (8, 35), (13, 14), (23, 24), (41, 42)
    ]

    for start, end in sample_pairs:
        path, _, _ = dijkstra_optimal_path(graph, start, end, 'unit')
        if path:
            for h in path[1:-1]:  # 排除起終點
                pass_count[h] += 1

    print("\n最常被經過的卦（樞紐）：")
    print("-" * 50)

    sorted_hubs = sorted(pass_count.items(), key=lambda x: -x[1])
    for i, (hex_num, count) in enumerate(sorted_hubs[:10]):
        name = HEX_NAMES[hex_num]
        bar = '█' * count
        print(f"  {i+1}. {name}({hex_num:2}): 被經過 {count} 次 {bar}")


def analyze_one_step_improvements(graph, ji_rates):
    """
    分析「一步改善」

    從當前卦出發，哪個變爻能帶來最大改善？
    """
    print("\n" + "="*70)
    print("【分析4】一步改善建議")
    print("="*70)

    # 選擇幾個常見的困境卦
    trouble_hexs = [47, 29, 39, 4, 36, 6]  # 困、坎、蹇、蒙、明夷、訟

    for hex_num in trouble_hexs:
        name = HEX_NAMES[hex_num]
        current_rate = ji_rates.get(hex_num, 0)

        print(f"\n【{name}卦】(當前吉率: {current_rate*100:.1f}%)")
        print("-" * 50)

        # 找出所有可能的變爻及其結果
        improvements = []
        for edge in graph[hex_num]:
            target = edge['to']
            target_name = HEX_NAMES[target]
            target_rate = ji_rates.get(target, 0)
            improvement = target_rate - current_rate
            improvements.append({
                'position': edge['position'],
                'target': target,
                'target_name': target_name,
                'improvement': improvement,
                'class': edge['class']
            })

        # 按改善程度排序
        improvements.sort(key=lambda x: -x['improvement'])

        print("  變爻建議（按改善程度）：")
        for imp in improvements:
            direction = '↑' if imp['improvement'] > 0 else '↓' if imp['improvement'] < 0 else '→'
            class_mark = '吉' if imp['class'] == '吉' else '凶' if imp['class'] == '凶' else '中'
            print(f"    爻{imp['position']}: → {imp['target_name']} ({imp['improvement']*100:+.1f}%) [{class_mark}] {direction}")


def analyze_recovery_patterns(graph, ji_rates):
    """
    分析「否極泰來」模式

    從最凶的狀態能多快恢復？
    """
    print("\n" + "="*70)
    print("【分析5】否極泰來分析")
    print("="*70)

    # 找出吉率最低和最高的卦
    sorted_rates = sorted(ji_rates.items(), key=lambda x: x[1])

    worst_hexs = sorted_rates[:5]
    best_hexs = sorted_rates[-5:]

    print("\n從最凶卦到最吉卦的最短路徑：")
    print("-" * 60)

    for worst_num, worst_rate in worst_hexs[:3]:
        for best_num, best_rate in best_hexs[-3:]:
            path, steps, edges = dijkstra_optimal_path(graph, worst_num, best_num, 'unit')

            if path:
                worst_name = HEX_NAMES[worst_num]
                best_name = HEX_NAMES[best_num]

                print(f"\n  {worst_name}({worst_rate*100:.0f}%) → {best_name}({best_rate*100:.0f}%)")
                print(f"    需要 {steps} 步")
                print(f"    路徑: {' → '.join([HEX_NAMES[h] for h in path])}")

                # 路徑上的吉率變化
                rates_on_path = [ji_rates.get(h, 0) for h in path]
                print(f"    吉率變化: {' → '.join([f'{r*100:.0f}%' for r in rates_on_path])}")


def print_practical_guide():
    """輸出實用指南"""
    print("\n" + "="*70)
    print("變卦路徑實用指南")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    變卦路徑優化指南                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【脫困策略】                                                        ║
║  ────────────                                                        ║
║  處於困境卦時，優先考慮：                                            ║
║  1. 找出到福地卦的最短路徑                                          ║
║  2. 每步選擇「吉」爻而非「凶」爻                                    ║
║  3. 避免經過其他困境卦                                              ║
║                                                                      ║
║  【福地保持】                                                        ║
║  ────────────                                                        ║
║  處於福地卦時：                                                      ║
║  1. 避免隨意變動（離開後吉率大幅下降）                              ║
║  2. 如需變動，選擇趨勢最小的變爻                                    ║
║  3. 特別注意：謙、臨、需離開後損失最大                              ║
║                                                                      ║
║  【樞紐利用】                                                        ║
║  ────────────                                                        ║
║  某些卦是「交通樞紐」，可作為中轉站：                                ║
║  1. 到達樞紐卦後重新評估方向                                        ║
║  2. 樞紐卦連接多種可能性                                            ║
║                                                                      ║
║  【一步改善】                                                        ║
║  ────────────                                                        ║
║  每個卦都有6種變化可能：                                             ║
║  1. 選擇吉率改善最大的變爻                                          ║
║  2. 避免選擇凶爻（即使目標卦看起來不錯）                            ║
║  3. 過程的吉凶與結果同樣重要                                        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("變卦路徑優化分析")
    print("="*70)
    print("\n尋找從困境卦到福地卦的最優路徑")

    biangua_data = load_biangua_data()
    yao_data = load_yao_data()

    print(f"\n載入 {len(biangua_data['transformations'])} 條變卦數據")

    # 建立圖
    graph, ji_rates = build_graph(biangua_data, yao_data)

    # 分析
    analyze_escape_routes(graph, ji_rates)
    analyze_optimal_routes(graph, ji_rates)
    analyze_hub_hexagrams(graph)
    analyze_one_step_improvements(graph, ji_rates)
    analyze_recovery_patterns(graph, ji_rates)

    # 實用指南
    print_practical_guide()


if __name__ == '__main__':
    main()
