#!/usr/bin/env python3
"""
生成64卦策略速查表

為每個卦提供：
1. 吉率
2. 類型（吸引子/排斥子/陷阱/一般）
3. 行動建議
4. 最佳變爻位置
5. 推薦路徑
"""

import json
from pathlib import Path
from collections import defaultdict

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

BINARY_TO_KINGWEN = {v: k for k, v in KINGWEN_TO_BINARY.items()}


def load_yaoci_data():
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_hex_stats(yaoci_data):
    """計算每個卦的統計數據"""
    hex_stats = {}

    for hex_num in range(1, 65):
        yao_list = [item for item in yaoci_data if item['hex_num'] == hex_num]

        if yao_list:
            ji_count = sum(1 for y in yao_list if y['label'] == 1)
            xiong_count = sum(1 for y in yao_list if y['label'] == -1)

            # 每個爻位的吉凶
            yao_labels = {}
            for y in yao_list:
                yao_labels[y['position']] = y['label']

            hex_stats[hex_num] = {
                'name': HEXAGRAM_NAMES[hex_num - 1],
                'ji_rate': ji_count / 6,
                'ji_count': ji_count,
                'xiong_count': xiong_count,
                'yao_labels': yao_labels
            }

    return hex_stats


def calculate_neighbors(hex_num):
    """計算鄰居卦（變一爻可達）"""
    binary = KINGWEN_TO_BINARY[hex_num]
    neighbors = []

    for pos in range(6):
        new_binary = list(binary)
        new_binary[pos] = '1' if new_binary[pos] == '0' else '0'
        new_binary = ''.join(new_binary)

        if new_binary in BINARY_TO_KINGWEN:
            target = BINARY_TO_KINGWEN[new_binary]
            yao_pos = 6 - pos  # 爻位從下往上
            neighbors.append({
                'target': target,
                'yao_position': yao_pos
            })

    return neighbors


def find_best_path(start_hex, hex_stats, max_steps=3):
    """找到通往好卦的最短路徑"""
    from collections import deque

    # 定義「好卦」：吉率 >= 50%
    good_hexes = {h for h, s in hex_stats.items() if s['ji_rate'] >= 0.5}

    if start_hex in good_hexes:
        return None  # 已經在好卦了

    visited = {start_hex}
    queue = deque([(start_hex, [start_hex])])

    while queue:
        node, path = queue.popleft()

        if len(path) > max_steps + 1:
            break

        neighbors = calculate_neighbors(node)
        for n in neighbors:
            next_node = n['target']

            if next_node in good_hexes:
                return path + [next_node]

            if next_node not in visited:
                visited.add(next_node)
                queue.append((next_node, path + [next_node]))

    return None


def classify_hexagram(hex_num, hex_stats):
    """分類卦的類型"""
    own_ji = hex_stats[hex_num]['ji_rate']

    # 計算鄰居平均吉率
    neighbors = calculate_neighbors(hex_num)
    neighbor_ji = [hex_stats[n['target']]['ji_rate'] for n in neighbors if n['target'] in hex_stats]
    avg_neighbor = sum(neighbor_ji) / len(neighbor_ji) if neighbor_ji else 0

    diff = own_ji - avg_neighbor

    if own_ji >= 0.5 and diff > 0.2:
        return "吸引子", "留", "自己好，變出去會差，建議停留"
    elif own_ji <= 0.2 and diff < -0.2:
        return "排斥子", "走", "自己差，變出去會好，建議離開"
    elif own_ji <= 0.2 and avg_neighbor <= 0.35:
        return "陷阱", "慎", "自己差，鄰居也不好，需謹慎選擇"
    elif own_ji >= 0.5:
        return "福地", "守", "吉率高，可維持現狀"
    elif own_ji <= 0.2:
        return "困境", "變", "吉率低，需要改變"
    else:
        return "一般", "觀", "中等，視情況而定"


def get_best_yao_to_change(hex_num, hex_stats):
    """找出最佳變爻位置"""
    neighbors = calculate_neighbors(hex_num)

    yao_scores = []
    for n in neighbors:
        target_ji = hex_stats[n['target']]['ji_rate']
        yao_scores.append({
            'position': n['yao_position'],
            'target': n['target'],
            'target_name': HEXAGRAM_NAMES[n['target'] - 1],
            'target_ji': target_ji
        })

    # 按目標吉率排序
    yao_scores.sort(key=lambda x: -x['target_ji'])

    return yao_scores


def generate_guide():
    """生成策略指南"""
    yaoci_data = load_yaoci_data()
    hex_stats = calculate_hex_stats(yaoci_data)

    guide = []

    for hex_num in range(1, 65):
        stats = hex_stats[hex_num]
        category, action, description = classify_hexagram(hex_num, hex_stats)
        best_yao = get_best_yao_to_change(hex_num, hex_stats)
        path = find_best_path(hex_num, hex_stats)

        neighbors = calculate_neighbors(hex_num)
        neighbor_ji = [hex_stats[n['target']]['ji_rate'] for n in neighbors]
        avg_neighbor = sum(neighbor_ji) / len(neighbor_ji)

        entry = {
            'hex_num': hex_num,
            'name': stats['name'],
            'ji_rate': stats['ji_rate'],
            'ji_count': stats['ji_count'],
            'xiong_count': stats['xiong_count'],
            'category': category,
            'action': action,
            'description': description,
            'neighbor_avg': avg_neighbor,
            'best_yao': best_yao[:3],  # 前3個最佳
            'worst_yao': best_yao[-1] if best_yao else None,
            'path_to_good': path
        }

        guide.append(entry)

    return guide


def print_guide(guide):
    """打印策略指南"""

    # 按類型分組
    categories = defaultdict(list)
    for entry in guide:
        categories[entry['category']].append(entry)

    print("=" * 80)
    print("六十四卦策略速查表")
    print("=" * 80)

    # 先打印吸引子
    print("\n" + "─" * 80)
    print("【吸引子】應該停留的卦")
    print("─" * 80)
    for entry in sorted(categories['吸引子'], key=lambda x: -x['ji_rate']):
        print(f"\n{entry['hex_num']:2d}. {entry['name']}卦  吉率:{entry['ji_rate']*100:.0f}%  建議:{entry['action']}")
        print(f"   說明：{entry['description']}")
        print(f"   鄰居平均：{entry['neighbor_avg']*100:.0f}%")

    # 排斥子
    print("\n" + "─" * 80)
    print("【排斥子】應該離開的卦")
    print("─" * 80)
    for entry in sorted(categories['排斥子'], key=lambda x: x['ji_rate']):
        print(f"\n{entry['hex_num']:2d}. {entry['name']}卦  吉率:{entry['ji_rate']*100:.0f}%  建議:{entry['action']}")
        print(f"   說明：{entry['description']}")
        if entry['path_to_good']:
            path_names = [HEXAGRAM_NAMES[h-1] for h in entry['path_to_good']]
            print(f"   推薦路徑：{' → '.join(path_names)}")
        if entry['best_yao']:
            best = entry['best_yao'][0]
            print(f"   最佳變爻：第{best['position']}爻 → {best['target_name']}({best['target_ji']*100:.0f}%)")

    # 陷阱
    print("\n" + "─" * 80)
    print("【陷阱】需要謹慎的卦")
    print("─" * 80)
    for entry in sorted(categories['陷阱'], key=lambda x: x['ji_rate']):
        print(f"\n{entry['hex_num']:2d}. {entry['name']}卦  吉率:{entry['ji_rate']*100:.0f}%  建議:{entry['action']}")
        print(f"   說明：{entry['description']}")
        if entry['path_to_good']:
            path_names = [HEXAGRAM_NAMES[h-1] for h in entry['path_to_good']]
            print(f"   推薦路徑：{' → '.join(path_names)}")

    # 福地
    print("\n" + "─" * 80)
    print("【福地】吉率高的卦")
    print("─" * 80)
    for entry in sorted(categories['福地'], key=lambda x: -x['ji_rate']):
        print(f"\n{entry['hex_num']:2d}. {entry['name']}卦  吉率:{entry['ji_rate']*100:.0f}%  建議:{entry['action']}")
        print(f"   說明：{entry['description']}")

    # 困境
    print("\n" + "─" * 80)
    print("【困境】吉率低的卦")
    print("─" * 80)
    for entry in sorted(categories['困境'], key=lambda x: x['ji_rate']):
        print(f"\n{entry['hex_num']:2d}. {entry['name']}卦  吉率:{entry['ji_rate']*100:.0f}%  建議:{entry['action']}")
        print(f"   說明：{entry['description']}")
        if entry['path_to_good']:
            path_names = [HEXAGRAM_NAMES[h-1] for h in entry['path_to_good']]
            print(f"   推薦路徑：{' → '.join(path_names)}")
        if entry['best_yao']:
            best = entry['best_yao'][0]
            print(f"   最佳變爻：第{best['position']}爻 → {best['target_name']}({best['target_ji']*100:.0f}%)")

    # 一般
    print("\n" + "─" * 80)
    print("【一般】中等的卦")
    print("─" * 80)
    for entry in sorted(categories['一般'], key=lambda x: -x['ji_rate']):
        print(f"\n{entry['hex_num']:2d}. {entry['name']}卦  吉率:{entry['ji_rate']*100:.0f}%  建議:{entry['action']}")

    return guide


def export_markdown(guide):
    """導出為 Markdown 格式"""

    lines = []
    lines.append("# 六十四卦策略速查表")
    lines.append("")
    lines.append("*根據384爻數據分析生成*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 使用方法")
    lines.append("")
    lines.append("1. 占卦後，找到你的卦")
    lines.append("2. 查看類型和建議")
    lines.append("3. 如果需要變，參考推薦路徑")
    lines.append("")
    lines.append("## 類型說明")
    lines.append("")
    lines.append("| 類型 | 意義 | 建議 |")
    lines.append("|------|------|------|")
    lines.append("| 吸引子 | 自己好，變出去差 | 留下，不要動 |")
    lines.append("| 排斥子 | 自己差，變出去好 | 趕快離開 |")
    lines.append("| 陷阱 | 自己差，鄰居也差 | 謹慎選擇方向 |")
    lines.append("| 福地 | 吉率高 | 維持現狀 |")
    lines.append("| 困境 | 吉率低 | 需要改變 |")
    lines.append("| 一般 | 中等 | 視情況而定 |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 按類型分組
    categories = defaultdict(list)
    for entry in guide:
        categories[entry['category']].append(entry)

    category_order = ['吸引子', '排斥子', '陷阱', '福地', '困境', '一般']

    for cat in category_order:
        if cat not in categories:
            continue

        lines.append(f"## {cat}")
        lines.append("")

        entries = categories[cat]
        if cat in ['吸引子', '福地']:
            entries = sorted(entries, key=lambda x: -x['ji_rate'])
        else:
            entries = sorted(entries, key=lambda x: x['ji_rate'])

        for entry in entries:
            lines.append(f"### {entry['hex_num']}. {entry['name']}卦")
            lines.append("")
            lines.append(f"- **吉率**：{entry['ji_rate']*100:.0f}%（{entry['ji_count']}吉 {entry['xiong_count']}凶）")
            lines.append(f"- **鄰居平均**：{entry['neighbor_avg']*100:.0f}%")
            lines.append(f"- **建議**：{entry['action']} - {entry['description']}")

            if entry['path_to_good']:
                path_names = [HEXAGRAM_NAMES[h-1] for h in entry['path_to_good']]
                path_str = ' → '.join(path_names)
                lines.append(f"- **推薦路徑**：{path_str}")

            if entry['best_yao'] and entry['ji_rate'] < 0.5:
                lines.append("- **變爻建議**：")
                for yao in entry['best_yao']:
                    lines.append(f"  - 第{yao['position']}爻 → {yao['target_name']}（{yao['target_ji']*100:.0f}%）")

            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 速查總表")
    lines.append("")
    lines.append("| 卦序 | 卦名 | 吉率 | 類型 | 建議 |")
    lines.append("|------|------|------|------|------|")

    for entry in sorted(guide, key=lambda x: x['hex_num']):
        lines.append(f"| {entry['hex_num']} | {entry['name']} | {entry['ji_rate']*100:.0f}% | {entry['category']} | {entry['action']} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*生成日期：2026-01-21*")

    return '\n'.join(lines)


def main():
    guide = generate_guide()
    print_guide(guide)

    # 導出 Markdown
    md_content = export_markdown(guide)
    output_path = Path(__file__).parent.parent / 'docs' / 'HEXAGRAM_STRATEGY_GUIDE.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n\n已導出到: {output_path}")


if __name__ == '__main__':
    main()
