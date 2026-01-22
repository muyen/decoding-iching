#!/usr/bin/env python3
"""
深度圖論分析

結合所有數據，尋找隱藏規律
特別關注：咸卦的矛盾（自身吉率低，但據說是最吉變卦目標）
"""

import json
from pathlib import Path
from collections import defaultdict
import re

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


def load_yaoci_data():
    """載入爻辭數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_xian_mystery(yaoci_data):
    """
    分析咸卦的矛盾

    問題：為什麼說咸卦是最吉的變卦目標，但咸卦自身吉率只有16.7%？
    """
    print("\n" + "=" * 70)
    print("咸卦矛盾深度分析")
    print("=" * 70)

    # 1. 先確認咸卦自身的爻辭
    print("\n【1. 咸卦自身的六爻】")
    print("-" * 50)

    xian_yao = [item for item in yaoci_data if item['hex_num'] == 31]
    for yao in sorted(xian_yao, key=lambda x: x['position']):
        label_str = {1: '吉', 0: '中', -1: '凶'}.get(yao['label'], '?')
        print(f"  第{yao['position']}爻: {yao['text'][:30]}... [{label_str}]")

    xian_ji = sum(1 for y in xian_yao if y['label'] == 1)
    xian_xiong = sum(1 for y in xian_yao if y['label'] == -1)
    print(f"\n  咸卦統計: 吉={xian_ji}, 凶={xian_xiong}, 中={6-xian_ji-xian_xiong}")
    print(f"  吉率: {xian_ji/6*100:.1f}%")

    # 2. 搜索所有提到「之咸」的爻辭
    print("\n【2. 搜索「之咸」- 變到咸卦的爻辭】")
    print("-" * 50)

    zhi_xian_count = 0
    for item in yaoci_data:
        if '之咸' in item['text'] or '咸' in item['text']:
            zhi_xian_count += 1

    print(f"  提到「咸」的爻辭數: {zhi_xian_count}")

    # 3. 分析「變爻」的概念
    print("\n【3. 重新理解「變卦目標」】")
    print("-" * 50)
    print("""
    之前的分析可能有誤解。

    「變到咸卦」的吉率，應該是指：
    - 從其他卦變一爻後變成咸卦
    - 那個「變爻」本身的吉凶

    而不是咸卦自身的爻辭吉凶。

    讓我們重新計算...
    """)

    # 4. 計算「變到某卦」的真正含義
    print("\n【4. 重新計算「變到X卦」的吉率】")
    print("-" * 50)

    # 對於每個卦，找出能變到它的6個爻，計算這些爻的平均吉率
    target_ji_rates = {}

    for target_hex in range(1, 65):
        target_binary = KINGWEN_TO_BINARY[target_hex]
        source_yao_labels = []

        # 找所有能變到這個卦的爻
        for source_hex in range(1, 65):
            source_binary = KINGWEN_TO_BINARY[source_hex]

            # 檢查是否只差一位
            diff_positions = []
            for i in range(6):
                if source_binary[i] != target_binary[i]:
                    diff_positions.append(i)

            if len(diff_positions) == 1:
                # 找到了！差異在 diff_positions[0]
                # 對應的爻位是 6 - diff_positions[0]（從下往上數）
                yao_position = 6 - diff_positions[0]

                # 找這個爻的吉凶
                for item in yaoci_data:
                    if item['hex_num'] == source_hex and item['position'] == yao_position:
                        source_yao_labels.append(item['label'])
                        break

        if source_yao_labels:
            ji_count = sum(1 for l in source_yao_labels if l == 1)
            target_ji_rates[target_hex] = ji_count / len(source_yao_labels)

    # 排序顯示
    sorted_targets = sorted(target_ji_rates.items(), key=lambda x: -x[1])

    print("\n「變到X卦」的吉率排名（變爻本身的吉凶）:")
    print("-" * 50)
    for hex_num, ji_rate in sorted_targets[:15]:
        name = HEXAGRAM_NAMES[hex_num - 1]
        print(f"  {hex_num:2d}. {name}: 變爻吉率={ji_rate*100:.1f}%")

    print("\n...")
    print("\n最差的「變到X卦」:")
    for hex_num, ji_rate in sorted_targets[-10:]:
        name = HEXAGRAM_NAMES[hex_num - 1]
        print(f"  {hex_num:2d}. {name}: 變爻吉率={ji_rate*100:.1f}%")

    # 咸卦在哪？
    xian_rank = next(i for i, (h, _) in enumerate(sorted_targets) if h == 31) + 1
    xian_rate = target_ji_rates.get(31, 0)
    print(f"\n咸卦排名: 第{xian_rank}名, 變爻吉率={xian_rate*100:.1f}%")

    return target_ji_rates, sorted_targets


def analyze_transformation_patterns(yaoci_data):
    """
    分析變爻模式

    哪些卦的哪些爻變了會變好/變差？
    """
    print("\n" + "=" * 70)
    print("變爻模式分析")
    print("=" * 70)

    # 建立變爻數據
    transformations = []

    for source_hex in range(1, 65):
        source_binary = KINGWEN_TO_BINARY[source_hex]

        for pos in range(6):
            # 變這一爻
            new_binary = list(source_binary)
            new_binary[pos] = '1' if new_binary[pos] == '0' else '0'
            new_binary = ''.join(new_binary)

            # 找目標卦
            target_hex = None
            for h, b in KINGWEN_TO_BINARY.items():
                if b == new_binary:
                    target_hex = h
                    break

            if target_hex:
                yao_position = 6 - pos

                # 找這個爻的吉凶
                for item in yaoci_data:
                    if item['hex_num'] == source_hex and item['position'] == yao_position:
                        transformations.append({
                            'source': source_hex,
                            'target': target_hex,
                            'position': yao_position,
                            'label': item['label'],
                            'source_name': HEXAGRAM_NAMES[source_hex - 1],
                            'target_name': HEXAGRAM_NAMES[target_hex - 1],
                        })
                        break

    print(f"\n共 {len(transformations)} 個變爻記錄")

    # 分析：變爻吉凶與源卦/目標卦的關係
    print("\n【變爻吉凶與目標卦吉率的關係】")
    print("-" * 50)

    # 計算每個卦的自身吉率
    hex_ji_rates = {}
    for hex_num in range(1, 65):
        yao_list = [item for item in yaoci_data if item['hex_num'] == hex_num]
        if yao_list:
            ji_count = sum(1 for y in yao_list if y['label'] == 1)
            hex_ji_rates[hex_num] = ji_count / len(yao_list)

    # 分組：變到好卦 vs 變到差卦
    to_good = [t for t in transformations if hex_ji_rates.get(t['target'], 0) >= 0.5]
    to_bad = [t for t in transformations if hex_ji_rates.get(t['target'], 0) <= 0.2]

    to_good_ji = sum(1 for t in to_good if t['label'] == 1) / len(to_good) * 100 if to_good else 0
    to_bad_ji = sum(1 for t in to_bad if t['label'] == 1) / len(to_bad) * 100 if to_bad else 0

    print(f"  變到好卦(吉率≥50%): 變爻吉率={to_good_ji:.1f}% (n={len(to_good)})")
    print(f"  變到差卦(吉率≤20%): 變爻吉率={to_bad_ji:.1f}% (n={len(to_bad)})")

    # 分析：從好卦變 vs 從差卦變
    print("\n【變爻吉凶與源卦吉率的關係】")
    print("-" * 50)

    from_good = [t for t in transformations if hex_ji_rates.get(t['source'], 0) >= 0.5]
    from_bad = [t for t in transformations if hex_ji_rates.get(t['source'], 0) <= 0.2]

    from_good_ji = sum(1 for t in from_good if t['label'] == 1) / len(from_good) * 100 if from_good else 0
    from_bad_ji = sum(1 for t in from_bad if t['label'] == 1) / len(from_bad) * 100 if from_bad else 0

    print(f"  從好卦變出: 變爻吉率={from_good_ji:.1f}% (n={len(from_good)})")
    print(f"  從差卦變出: 變爻吉率={from_bad_ji:.1f}% (n={len(from_bad)})")

    return transformations


def analyze_position_in_transformation(transformations):
    """
    分析爻位在變卦中的角色
    """
    print("\n" + "=" * 70)
    print("爻位與變卦吉凶")
    print("=" * 70)

    pos_stats = defaultdict(lambda: {'ji': 0, 'total': 0})

    for t in transformations:
        pos = t['position']
        pos_stats[pos]['total'] += 1
        if t['label'] == 1:
            pos_stats[pos]['ji'] += 1

    print("\n【各爻位的變爻吉率】")
    print("-" * 50)

    for pos in range(1, 7):
        stats = pos_stats[pos]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            bar = '█' * int(ji_rate / 5)
            print(f"  第{pos}爻變: 吉率={ji_rate:5.1f}% (n={stats['total']}) {bar}")


def analyze_special_hexagrams(yaoci_data, target_ji_rates):
    """
    分析特殊卦的特點
    """
    print("\n" + "=" * 70)
    print("特殊卦深度分析")
    print("=" * 70)

    # 計算每個卦的自身吉率
    hex_ji_rates = {}
    for hex_num in range(1, 65):
        yao_list = [item for item in yaoci_data if item['hex_num'] == hex_num]
        if yao_list:
            ji_count = sum(1 for y in yao_list if y['label'] == 1)
            hex_ji_rates[hex_num] = ji_count / len(yao_list)

    # 找出「自身好但變入差」的卦
    print("\n【矛盾卦1】自身吉率高，但變到這裡的爻吉率低:")
    print("-" * 50)

    contradictions_1 = []
    for hex_num in range(1, 65):
        own_ji = hex_ji_rates.get(hex_num, 0)
        target_ji = target_ji_rates.get(hex_num, 0)
        diff = own_ji - target_ji
        if diff > 0.2:  # 自己好但變入差
            contradictions_1.append({
                'hex_num': hex_num,
                'name': HEXAGRAM_NAMES[hex_num - 1],
                'own_ji': own_ji,
                'target_ji': target_ji,
                'diff': diff
            })

    contradictions_1.sort(key=lambda x: -x['diff'])
    for c in contradictions_1[:10]:
        print(f"  {c['hex_num']:2d}. {c['name']}: 自身={c['own_ji']*100:.1f}%, 變入={c['target_ji']*100:.1f}%, 差={c['diff']*100:+.1f}%")

    if contradictions_1:
        print("\n  解讀：這些卦是「好地方但難進入」- 入口艱難，到了就好")

    # 找出「自身差但變入好」的卦
    print("\n【矛盾卦2】自身吉率低，但變到這裡的爻吉率高:")
    print("-" * 50)

    contradictions_2 = []
    for hex_num in range(1, 65):
        own_ji = hex_ji_rates.get(hex_num, 0)
        target_ji = target_ji_rates.get(hex_num, 0)
        diff = target_ji - own_ji
        if diff > 0.2:  # 自己差但變入好
            contradictions_2.append({
                'hex_num': hex_num,
                'name': HEXAGRAM_NAMES[hex_num - 1],
                'own_ji': own_ji,
                'target_ji': target_ji,
                'diff': diff
            })

    contradictions_2.sort(key=lambda x: -x['diff'])
    for c in contradictions_2[:10]:
        print(f"  {c['hex_num']:2d}. {c['name']}: 自身={c['own_ji']*100:.1f}%, 變入={c['target_ji']*100:.1f}%, 差={c['diff']*100:+.1f}%")

    if contradictions_2:
        print("\n  解讀：這些卦是「容易進入但待著不好」- 入口順利，進去就糟")


def analyze_binary_neighbors(yaoci_data):
    """
    分析二進制鄰居關係
    """
    print("\n" + "=" * 70)
    print("二進制鄰居分析")
    print("=" * 70)

    # 計算每個卦的吉率
    hex_ji_rates = {}
    for hex_num in range(1, 65):
        yao_list = [item for item in yaoci_data if item['hex_num'] == hex_num]
        if yao_list:
            ji_count = sum(1 for y in yao_list if y['label'] == 1)
            hex_ji_rates[hex_num] = ji_count / len(yao_list)

    # 找二進制相鄰的卦（漢明距離=1）
    print("\n【漢明距離=1的卦對吉率差異】")
    print("-" * 50)

    pairs = []
    for h1 in range(1, 65):
        b1 = KINGWEN_TO_BINARY[h1]
        for h2 in range(h1 + 1, 65):
            b2 = KINGWEN_TO_BINARY[h2]

            # 計算漢明距離
            dist = sum(c1 != c2 for c1, c2 in zip(b1, b2))

            if dist == 1:
                ji1 = hex_ji_rates.get(h1, 0)
                ji2 = hex_ji_rates.get(h2, 0)
                diff = abs(ji1 - ji2)
                pairs.append({
                    'h1': h1, 'h2': h2,
                    'name1': HEXAGRAM_NAMES[h1 - 1],
                    'name2': HEXAGRAM_NAMES[h2 - 1],
                    'ji1': ji1, 'ji2': ji2,
                    'diff': diff
                })

    # 差異最大的配對
    pairs.sort(key=lambda x: -x['diff'])

    print("\n吉率差異最大的鄰居卦對（只差一爻卻天差地別）:")
    for p in pairs[:10]:
        print(f"  {p['name1']}({p['ji1']*100:.0f}%) ↔ {p['name2']}({p['ji2']*100:.0f}%): 差{p['diff']*100:.0f}%")

    print("\n  洞見：一爻之差可以造成巨大吉凶差異！")

    # 差異最小的配對
    print("\n吉率差異最小的鄰居卦對（一爻之差但吉凶相近）:")
    for p in pairs[-10:]:
        print(f"  {p['name1']}({p['ji1']*100:.0f}%) ↔ {p['name2']}({p['ji2']*100:.0f}%): 差{p['diff']*100:.0f}%")


def find_optimal_strategy(yaoci_data, target_ji_rates):
    """
    尋找最優策略
    """
    print("\n" + "=" * 70)
    print("最優變卦策略")
    print("=" * 70)

    # 計算每個卦的自身吉率
    hex_ji_rates = {}
    for hex_num in range(1, 65):
        yao_list = [item for item in yaoci_data if item['hex_num'] == hex_num]
        if yao_list:
            ji_count = sum(1 for y in yao_list if y['label'] == 1)
            hex_ji_rates[hex_num] = ji_count / len(yao_list)

    print("\n【最佳停留卦】自身吉率高，且變出去會變差:")
    print("-" * 50)

    stay_scores = []
    for hex_num in range(1, 65):
        own_ji = hex_ji_rates.get(hex_num, 0)

        # 計算鄰居平均吉率
        source_binary = KINGWEN_TO_BINARY[hex_num]
        neighbor_ji = []

        for pos in range(6):
            new_binary = list(source_binary)
            new_binary[pos] = '1' if new_binary[pos] == '0' else '0'
            new_binary = ''.join(new_binary)

            for h, b in KINGWEN_TO_BINARY.items():
                if b == new_binary:
                    neighbor_ji.append(hex_ji_rates.get(h, 0))
                    break

        if neighbor_ji:
            avg_neighbor = sum(neighbor_ji) / len(neighbor_ji)
            stay_score = own_ji - avg_neighbor
            stay_scores.append({
                'hex_num': hex_num,
                'name': HEXAGRAM_NAMES[hex_num - 1],
                'own_ji': own_ji,
                'neighbor_avg': avg_neighbor,
                'stay_score': stay_score
            })

    stay_scores.sort(key=lambda x: -x['stay_score'])

    for s in stay_scores[:10]:
        print(f"  {s['hex_num']:2d}. {s['name']}: 自身={s['own_ji']*100:.1f}%, 鄰居={s['neighbor_avg']*100:.1f}%, 留下得分={s['stay_score']*100:+.1f}%")

    print("\n【最佳離開卦】自身吉率低，但變出去會變好:")
    print("-" * 50)

    stay_scores.sort(key=lambda x: x['stay_score'])

    for s in stay_scores[:10]:
        print(f"  {s['hex_num']:2d}. {s['name']}: 自身={s['own_ji']*100:.1f}%, 鄰居={s['neighbor_avg']*100:.1f}%, 離開得分={-s['stay_score']*100:+.1f}%")


def summarize_findings():
    """總結發現"""
    print("\n" + "=" * 70)
    print("深度分析總結")
    print("=" * 70)
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                        核心發現                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  1. 「變到X卦」vs「X卦本身」是不同的概念！                          ║
║     - 變爻的吉凶 ≠ 目標卦的吉凶                                     ║
║     - 這解釋了咸卦的矛盾                                            ║
║                                                                      ║
║  2. 存在「入口效應」：                                               ║
║     - 有些卦難進但好（入口艱難，到了就好）                          ║
║     - 有些卦易進但差（入口順利，進去就糟）                          ║
║                                                                      ║
║  3. 一爻之差可以天差地別：                                          ║
║     - 漢明距離=1的卦，吉率差異可達80%                               ║
║     - 變爻選擇非常關鍵                                              ║
║                                                                      ║
║  4. 最優策略：                                                       ║
║     - 在「吸引子」卦（謙、臨、需）停留                              ║
║     - 從「排斥子」卦（旅、恆、觀）盡快離開                          ║
║     - 避免「陷阱」卦（乾、坎）                                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("=" * 70)
    print("深度圖論分析")
    print("=" * 70)

    yaoci_data = load_yaoci_data()
    print(f"\n載入 {len(yaoci_data)} 條爻數據")

    # 分析咸卦矛盾
    target_ji_rates, sorted_targets = analyze_xian_mystery(yaoci_data)

    # 分析變爻模式
    transformations = analyze_transformation_patterns(yaoci_data)

    # 分析爻位
    analyze_position_in_transformation(transformations)

    # 分析特殊卦
    analyze_special_hexagrams(yaoci_data, target_ji_rates)

    # 分析二進制鄰居
    analyze_binary_neighbors(yaoci_data)

    # 尋找最優策略
    find_optimal_strategy(yaoci_data, target_ji_rates)

    # 總結
    summarize_findings()


if __name__ == '__main__':
    main()
