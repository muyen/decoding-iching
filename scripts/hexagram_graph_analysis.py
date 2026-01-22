#!/usr/bin/env python3
"""
易經六十四卦圖論分析

把64卦視為圖的節點，變爻關係視為邊
分析網絡結構，尋找隱藏規律
"""

import json
from pathlib import Path
from collections import defaultdict

# 64卦名稱
HEXAGRAM_NAMES = [
    "乾", "坤", "屯", "蒙", "需", "訟", "師", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "謙", "豫",
    "隨", "蠱", "臨", "觀", "噬嗑", "賁", "剝", "復",
    "無妄", "大畜", "頤", "大過", "坎", "離", "咸", "恆",
    "遯", "大壯", "晉", "明夷", "家人", "睽", "蹇", "解",
    "損", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "漸", "歸妹", "豐", "旅",
    "巽", "兌", "渙", "節", "中孚", "小過", "既濟", "未濟"
]

# 卦序到二進制的映射（King Wen序）
def get_hexagram_binary(hex_num):
    """獲取卦的二進制表示"""
    # 這是標準的King Wen序對應的二進制
    KINGWEN_TO_BINARY = {
        1: '111111', 2: '000000', 3: '100010', 4: '010001',
        5: '111010', 6: '010111', 7: '010000', 8: '000010',
        9: '111011', 10: '110111', 11: '111000', 12: '000111',
        13: '101111', 14: '111101', 15: '001000', 16: '000100',
        17: '100110', 18: '011001', 19: '110000', 20: '000011',
        21: '100101', 22: '101001', 23: '000001', 24: '100000',
        25: '100111', 26: '111001', 27: '100001', 28: '011110',
        29: '010010', 30: '101101', 31: '001110', 32: '011100',
        33: '001111', 34: '111100', 35: '000101', 36: '101000',
        37: '101011', 38: '110101', 39: '001010', 40: '010100',
        41: '110001', 42: '100011', 43: '111110', 44: '011111',
        45: '000110', 46: '011000', 47: '010110', 48: '011010',
        49: '101110', 50: '011101', 51: '100100', 52: '001001',
        53: '001011', 54: '110100', 55: '101100', 56: '001101',
        57: '011011', 58: '110110', 59: '010011', 60: '110010',
        61: '110011', 62: '001100', 63: '101010', 64: '010101',
    }
    return KINGWEN_TO_BINARY.get(hex_num, '000000')


def binary_to_hexnum(binary):
    """二進制轉卦序"""
    BINARY_TO_KINGWEN = {
        '111111': 1, '000000': 2, '100010': 3, '010001': 4,
        '111010': 5, '010111': 6, '010000': 7, '000010': 8,
        '111011': 9, '110111': 10, '111000': 11, '000111': 12,
        '101111': 13, '111101': 14, '001000': 15, '000100': 16,
        '100110': 17, '011001': 18, '110000': 19, '000011': 20,
        '100101': 21, '101001': 22, '000001': 23, '100000': 24,
        '100111': 25, '111001': 26, '100001': 27, '011110': 28,
        '010010': 29, '101101': 30, '001110': 31, '011100': 32,
        '001111': 33, '111100': 34, '000101': 35, '101000': 36,
        '101011': 37, '110101': 38, '001010': 39, '010100': 40,
        '110001': 41, '100011': 42, '111110': 43, '011111': 44,
        '000110': 45, '011000': 46, '010110': 47, '011010': 48,
        '101110': 49, '011101': 50, '100100': 51, '001001': 52,
        '001011': 53, '110100': 54, '101100': 55, '001101': 56,
        '011011': 57, '110110': 58, '010011': 59, '110010': 60,
        '110011': 61, '001100': 62, '101010': 63, '010101': 64,
    }
    return BINARY_TO_KINGWEN.get(binary, 0)


def flip_bit(binary, position):
    """翻轉指定位置的bit（模擬變爻）"""
    bits = list(binary)
    bits[position] = '0' if bits[position] == '1' else '1'
    return ''.join(bits)


def load_yaoci_data():
    """載入爻辭數據獲取吉凶信息"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_hexagram_ji_rate(yaoci_data):
    """計算每卦的吉率"""
    hex_stats = defaultdict(lambda: {'ji': 0, 'total': 0})

    for item in yaoci_data:
        hex_num = item['hex_num']
        label = item['label']
        hex_stats[hex_num]['total'] += 1
        if label == 1:
            hex_stats[hex_num]['ji'] += 1

    result = {}
    for hex_num, stats in hex_stats.items():
        if stats['total'] > 0:
            result[hex_num] = stats['ji'] / stats['total']

    return result


def build_transformation_graph():
    """
    建立變卦圖

    節點：64卦
    邊：變爻關係（每卦可變到6個其他卦）
    """
    graph = defaultdict(list)

    for hex_num in range(1, 65):
        binary = get_hexagram_binary(hex_num)

        # 每個爻都可以變
        for pos in range(6):
            new_binary = flip_bit(binary, pos)
            target_hex = binary_to_hexnum(new_binary)

            if target_hex > 0:
                graph[hex_num].append({
                    'target': target_hex,
                    'changed_position': 6 - pos,  # 轉換為爻位（從下往上）
                    'from_binary': binary,
                    'to_binary': new_binary
                })

    return graph


def analyze_graph_structure(graph):
    """分析圖結構"""
    print("\n" + "=" * 70)
    print("圖結構基本分析")
    print("=" * 70)

    # 節點數和邊數
    nodes = len(graph)
    edges = sum(len(targets) for targets in graph.values())

    print(f"\n節點數（卦數）: {nodes}")
    print(f"邊數（變爻關係）: {edges}")
    print(f"平均度數: {edges / nodes:.1f}")

    # 這是一個6-正則圖（每個節點都有6條邊）
    print("\n結構特徵：6-正則圖（每卦恰好連接6個其他卦）")


def analyze_centrality(graph, ji_rates):
    """
    分析中心性

    問題：哪些卦是「中心」？中心性與吉率有關嗎？
    """
    print("\n" + "=" * 70)
    print("中心性分析")
    print("=" * 70)

    # 由於是6-正則圖，度中心性相同
    # 我們計算「鄰居吉率」- 你能變到的卦的平均吉率

    neighbor_ji = {}

    for hex_num, targets in graph.items():
        target_ji_rates = []
        for t in targets:
            target_hex = t['target']
            if target_hex in ji_rates:
                target_ji_rates.append(ji_rates[target_hex])

        if target_ji_rates:
            neighbor_ji[hex_num] = sum(target_ji_rates) / len(target_ji_rates)

    # 排序
    sorted_by_neighbor = sorted(neighbor_ji.items(), key=lambda x: -x[1])

    print("\n【發現】鄰居平均吉率最高的卦（變到哪都好）:")
    print("-" * 50)
    for hex_num, avg_ji in sorted_by_neighbor[:10]:
        name = HEXAGRAM_NAMES[hex_num - 1]
        own_ji = ji_rates.get(hex_num, 0) * 100
        print(f"  {hex_num:2d}. {name}: 鄰居平均吉率={avg_ji*100:.1f}%, 自身吉率={own_ji:.1f}%")

    print("\n【發現】鄰居平均吉率最低的卦（變到哪都差）:")
    print("-" * 50)
    for hex_num, avg_ji in sorted_by_neighbor[-10:]:
        name = HEXAGRAM_NAMES[hex_num - 1]
        own_ji = ji_rates.get(hex_num, 0) * 100
        print(f"  {hex_num:2d}. {name}: 鄰居平均吉率={avg_ji*100:.1f}%, 自身吉率={own_ji:.1f}%")

    return neighbor_ji


def analyze_xian_hexagram(graph, ji_rates):
    """
    特別分析咸卦

    咸卦是最吉的變卦目標，為什麼？
    """
    print("\n" + "=" * 70)
    print("咸卦特殊性分析")
    print("=" * 70)

    xian_num = 31  # 咸卦
    xian_binary = get_hexagram_binary(xian_num)

    print(f"\n咸卦 (第31卦)")
    print(f"二進制: {xian_binary}")
    print(f"結構: 澤山咸 (☱ over ☶)")
    print(f"自身吉率: {ji_rates.get(xian_num, 0)*100:.1f}%")

    # 誰能變到咸卦？
    print("\n【誰能變到咸卦】")
    sources = []
    for hex_num, targets in graph.items():
        for t in targets:
            if t['target'] == xian_num:
                sources.append({
                    'hex_num': hex_num,
                    'name': HEXAGRAM_NAMES[hex_num - 1],
                    'position': t['changed_position'],
                    'ji_rate': ji_rates.get(hex_num, 0)
                })

    print(f"共有 {len(sources)} 個卦可以變到咸卦:")
    for s in sources:
        print(f"  {s['hex_num']:2d}. {s['name']} (第{s['position']}爻變) - 原卦吉率: {s['ji_rate']*100:.1f}%")

    # 咸卦能變到哪？
    print("\n【咸卦能變到哪】")
    for t in graph[xian_num]:
        target_name = HEXAGRAM_NAMES[t['target'] - 1]
        target_ji = ji_rates.get(t['target'], 0) * 100
        print(f"  → {t['target']:2d}. {target_name} (第{t['changed_position']}爻變) - 目標吉率: {target_ji:.1f}%")

    # 咸卦的結構特殊性
    print("\n【咸卦結構分析】")
    print(f"  二進制: {xian_binary}")
    print(f"  陽爻數: {xian_binary.count('1')}")
    print(f"  陰爻數: {xian_binary.count('0')}")

    # 計算與其他卦的漢明距離分布
    hamming_dist = defaultdict(list)
    for hex_num in range(1, 65):
        if hex_num == xian_num:
            continue
        other_binary = get_hexagram_binary(hex_num)
        dist = sum(a != b for a, b in zip(xian_binary, other_binary))
        hamming_dist[dist].append(hex_num)

    print("\n【咸卦與其他卦的漢明距離】")
    for dist in sorted(hamming_dist.keys()):
        count = len(hamming_dist[dist])
        print(f"  距離={dist}: {count}個卦")


def analyze_attractors_and_traps(graph, ji_rates):
    """
    分析吸引子和陷阱

    吸引子：大家都想變過去的卦（鄰居吉率低，自己吉率高）
    陷阱：變進去就出不來（自己吉率低，鄰居吉率也低）
    """
    print("\n" + "=" * 70)
    print("吸引子與陷阱分析")
    print("=" * 70)

    # 計算每個卦的「吸引力」= 自身吉率 - 鄰居平均吉率
    attraction = {}

    for hex_num, targets in graph.items():
        own_ji = ji_rates.get(hex_num, 0)

        neighbor_rates = []
        for t in targets:
            target_hex = t['target']
            if target_hex in ji_rates:
                neighbor_rates.append(ji_rates[target_hex])

        if neighbor_rates:
            avg_neighbor = sum(neighbor_rates) / len(neighbor_rates)
            attraction[hex_num] = own_ji - avg_neighbor

    sorted_attraction = sorted(attraction.items(), key=lambda x: -x[1])

    print("\n【吸引子】自己比鄰居好很多（值得留在這裡）:")
    print("-" * 50)
    for hex_num, attr in sorted_attraction[:10]:
        name = HEXAGRAM_NAMES[hex_num - 1]
        own_ji = ji_rates.get(hex_num, 0) * 100
        print(f"  {hex_num:2d}. {name}: 吸引力={attr*100:+.1f}%, 自身吉率={own_ji:.1f}%")

    print("\n【排斥子】自己比鄰居差很多（應該離開）:")
    print("-" * 50)
    for hex_num, attr in sorted_attraction[-10:]:
        name = HEXAGRAM_NAMES[hex_num - 1]
        own_ji = ji_rates.get(hex_num, 0) * 100
        print(f"  {hex_num:2d}. {name}: 吸引力={attr*100:+.1f}%, 自身吉率={own_ji:.1f}%")

    # 陷阱：自己差，鄰居也差
    print("\n【陷阱】自己差，變到哪也差:")
    print("-" * 50)

    traps = []
    for hex_num in range(1, 65):
        own_ji = ji_rates.get(hex_num, 0)

        neighbor_rates = []
        for t in graph[hex_num]:
            target_hex = t['target']
            if target_hex in ji_rates:
                neighbor_rates.append(ji_rates[target_hex])

        if neighbor_rates:
            avg_neighbor = sum(neighbor_rates) / len(neighbor_rates)
            if own_ji < 0.25 and avg_neighbor < 0.35:
                traps.append({
                    'hex_num': hex_num,
                    'name': HEXAGRAM_NAMES[hex_num - 1],
                    'own_ji': own_ji,
                    'neighbor_avg': avg_neighbor
                })

    traps.sort(key=lambda x: x['own_ji'])
    for trap in traps[:10]:
        print(f"  {trap['hex_num']:2d}. {trap['name']}: 自身={trap['own_ji']*100:.1f}%, 鄰居平均={trap['neighbor_avg']*100:.1f}%")


def analyze_binary_patterns(ji_rates):
    """
    分析二進制模式與吉率的關係
    """
    print("\n" + "=" * 70)
    print("二進制模式分析")
    print("=" * 70)

    # 按陽爻數分組
    yang_count_stats = defaultdict(list)

    for hex_num in range(1, 65):
        binary = get_hexagram_binary(hex_num)
        yang_count = binary.count('1')
        ji_rate = ji_rates.get(hex_num, 0)
        yang_count_stats[yang_count].append((hex_num, ji_rate))

    print("\n【陽爻數與卦吉率】")
    print("-" * 50)
    for yang_count in sorted(yang_count_stats.keys()):
        hexagrams = yang_count_stats[yang_count]
        avg_ji = sum(ji for _, ji in hexagrams) / len(hexagrams) * 100
        count = len(hexagrams)
        bar = '█' * int(avg_ji / 5)
        print(f"  {yang_count}陽爻 ({count:2d}卦): 平均吉率={avg_ji:5.1f}% {bar}")


def find_optimal_paths(graph, ji_rates):
    """
    尋找最優變卦路徑

    從差的卦出發，找到通往好卦的最短路徑
    """
    print("\n" + "=" * 70)
    print("最優變卦路徑")
    print("=" * 70)

    # 找吉率最低的5個卦
    sorted_ji = sorted(ji_rates.items(), key=lambda x: x[1])
    worst_5 = [h for h, _ in sorted_ji[:5]]

    # 找吉率最高的5個卦
    best_5 = [h for h, _ in sorted_ji[-5:]]

    print(f"\n最差的卦: {[HEXAGRAM_NAMES[h-1] for h in worst_5]}")
    print(f"最好的卦: {[HEXAGRAM_NAMES[h-1] for h in best_5]}")

    # BFS找最短路徑
    def find_path(start, targets, graph):
        from collections import deque

        visited = {start}
        queue = deque([(start, [start])])

        while queue:
            node, path = queue.popleft()

            if node in targets:
                return path

            for t in graph[node]:
                next_node = t['target']
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))

        return None

    print("\n【從最差卦到最好卦的最短路徑】")
    print("-" * 50)

    for worst in worst_5[:3]:
        path = find_path(worst, set(best_5), graph)
        if path:
            path_names = [HEXAGRAM_NAMES[h-1] for h in path]
            path_ji = [f"{ji_rates.get(h, 0)*100:.0f}%" for h in path]
            print(f"\n  {HEXAGRAM_NAMES[worst-1]} → {HEXAGRAM_NAMES[path[-1]-1]}")
            print(f"  路徑: {' → '.join(path_names)}")
            print(f"  吉率: {' → '.join(path_ji)}")
            print(f"  步數: {len(path)-1}")


def analyze_clusters(graph, ji_rates):
    """
    分析卦的聚類

    哪些卦形成「好卦群」？哪些形成「差卦群」？
    """
    print("\n" + "=" * 70)
    print("卦群聚類分析")
    print("=" * 70)

    # 把卦分成好/中/差三類
    good_hex = [h for h, ji in ji_rates.items() if ji >= 0.4]
    bad_hex = [h for h, ji in ji_rates.items() if ji <= 0.2]

    print(f"\n好卦 (吉率≥40%): {len(good_hex)}個")
    print(f"差卦 (吉率≤20%): {len(bad_hex)}個")

    # 計算好卦之間的連接密度
    good_to_good = 0
    good_edges = 0

    for hex_num in good_hex:
        for t in graph[hex_num]:
            good_edges += 1
            if t['target'] in good_hex:
                good_to_good += 1

    good_density = good_to_good / good_edges * 100 if good_edges > 0 else 0

    # 計算差卦之間的連接密度
    bad_to_bad = 0
    bad_edges = 0

    for hex_num in bad_hex:
        for t in graph[hex_num]:
            bad_edges += 1
            if t['target'] in bad_hex:
                bad_to_bad += 1

    bad_density = bad_to_bad / bad_edges * 100 if bad_edges > 0 else 0

    print(f"\n好卦互連密度: {good_density:.1f}% (好卦變到好卦的比例)")
    print(f"差卦互連密度: {bad_density:.1f}% (差卦變到差卦的比例)")

    if bad_density > good_density:
        print("\n⚠️ 發現：差卦更容易形成「陷阱群」- 變來變去還是差")
    else:
        print("\n✓ 發現：好卦形成連通群 - 一旦進入好卦區域容易保持")


def main():
    print("=" * 70)
    print("易經六十四卦圖論分析")
    print("=" * 70)

    # 載入數據
    yaoci_data = load_yaoci_data()
    ji_rates = calculate_hexagram_ji_rate(yaoci_data)

    print(f"\n載入 {len(yaoci_data)} 條爻數據")
    print(f"計算了 {len(ji_rates)} 個卦的吉率")

    # 建立圖
    graph = build_transformation_graph()

    # 各種分析
    analyze_graph_structure(graph)
    analyze_binary_patterns(ji_rates)
    neighbor_ji = analyze_centrality(graph, ji_rates)
    analyze_xian_hexagram(graph, ji_rates)
    analyze_attractors_and_traps(graph, ji_rates)
    analyze_clusters(graph, ji_rates)
    find_optimal_paths(graph, ji_rates)

    # 總結
    print("\n" + "=" * 70)
    print("圖論分析總結")
    print("=" * 70)
    print("""
核心發現：

1. 六十四卦形成一個6-正則圖（每卦連接6個其他卦）

2. 「吸引子」卦：自身吉率高，鄰居吉率低
   → 值得停留的位置

3. 「陷阱」卦：自身吉率低，鄰居吉率也低
   → 難以逃脫的困境

4. 咸卦的特殊性：
   → 結構上的特點待進一步分析

5. 好卦/差卦形成聚類
   → 變卦有路徑依賴性
""")


if __name__ == '__main__':
    main()
