#!/usr/bin/env python3
"""
檢查是否有遺漏的模式和規則

額外分析：
1. 對稱卦 vs 非對稱卦
2. 核卦 (Nuclear hexagram) 效應
3. 五行相生相剋
4. 特殊100%規則搜尋
"""

import json
import os
from collections import defaultdict, Counter
from itertools import combinations

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

# 五行相生相剋
ELEMENTS = {
    '乾': '金', '坤': '土', '震': '木', '巽': '木',
    '坎': '水', '離': '火', '艮': '土', '兌': '金'
}

SHENG = [('木', '火'), ('火', '土'), ('土', '金'), ('金', '水'), ('水', '木')]  # 相生
KE = [('木', '土'), ('土', '水'), ('水', '火'), ('火', '金'), ('金', '木')]     # 相剋

def get_wuxing_relation(lower, upper):
    """判斷上下卦的五行關係"""
    e1 = ELEMENTS.get(lower)
    e2 = ELEMENTS.get(upper)
    if not e1 or not e2:
        return '未知'
    if e1 == e2:
        return '比和'
    if (e1, e2) in SHENG:
        return '下生上'
    if (e2, e1) in SHENG:
        return '上生下'
    if (e1, e2) in KE:
        return '下剋上'
    if (e2, e1) in KE:
        return '上剋下'
    return '未知'

def analysis_wuxing(data, struct_data):
    """五行分析"""
    print("=" * 70)
    print("五行相生相剋分析")
    print("=" * 70)

    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    wuxing_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})

    for yao in data:
        hex_num = yao['hex_num']
        if hex_num not in hex_to_trigrams:
            continue
        lower, upper = hex_to_trigrams[hex_num]
        relation = get_wuxing_relation(lower, upper)

        wuxing_stats[relation]['total'] += 1
        if yao['label'] == 1:
            wuxing_stats[relation]['ji'] += 1
        elif yao['label'] == -1:
            wuxing_stats[relation]['xiong'] += 1

    print("\n五行關係   總數   吉率    凶率")
    print("-" * 45)
    for relation in ['比和', '下生上', '上生下', '下剋上', '上剋下']:
        s = wuxing_stats[relation]
        if s['total'] > 0:
            ji_r = s['ji'] / s['total'] * 100
            xi_r = s['xiong'] / s['total'] * 100
            print(f" {relation}    {s['total']:3d}   {ji_r:5.1f}%  {xi_r:5.1f}%")

def analysis_symmetry(data, struct_data):
    """對稱卦分析"""
    print("\n" + "=" * 70)
    print("對稱卦 vs 非對稱卦分析")
    print("=" * 70)

    hex_is_symmetric = {}
    for hex_num, info in struct_data.items():
        hex_is_symmetric[int(hex_num)] = info.get('is_symmetric', False)

    sym_stats = {'對稱卦': {'total': 0, 'ji': 0, 'xiong': 0},
                 '非對稱卦': {'total': 0, 'ji': 0, 'xiong': 0}}

    for yao in data:
        hex_num = yao['hex_num']
        is_sym = hex_is_symmetric.get(hex_num, False)
        key = '對稱卦' if is_sym else '非對稱卦'

        sym_stats[key]['total'] += 1
        if yao['label'] == 1:
            sym_stats[key]['ji'] += 1
        elif yao['label'] == -1:
            sym_stats[key]['xiong'] += 1

    print("\n類型       總數   吉率    凶率")
    print("-" * 40)
    for key, s in sym_stats.items():
        if s['total'] > 0:
            ji_r = s['ji'] / s['total'] * 100
            xi_r = s['xiong'] / s['total'] * 100
            print(f" {key}   {s['total']:3d}   {ji_r:5.1f}%  {xi_r:5.1f}%")

def search_100_percent_rules(data, struct_data):
    """搜尋100%準確率規則"""
    print("\n" + "=" * 70)
    print("搜尋100%準確率規則")
    print("=" * 70)

    hex_to_info = {}
    for hex_num, info in struct_data.items():
        hex_to_info[int(hex_num)] = {
            'lower': info['lower_trigram']['name'],
            'upper': info['upper_trigram']['name'],
            'lower_element': info['lower_trigram']['element'],
            'upper_element': info['upper_trigram']['element'],
            'is_symmetric': info.get('is_symmetric', False),
            'yang_count': info.get('yang_count', 3)
        }

    # 檢查各種條件組合
    conditions_results = []

    # 條件1: 特定爻位 + 特定卦
    for pos in range(1, 7):
        for upper in ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']:
            for lower in ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']:
                matches = [y for y in data
                          if y['position'] == pos
                          and y['hex_num'] in hex_to_info
                          and hex_to_info[y['hex_num']]['upper'] == upper
                          and hex_to_info[y['hex_num']]['lower'] == lower]
                if matches and len(matches) >= 1:
                    labels = [y['label'] for y in matches]
                    if all(l == 1 for l in labels):
                        conditions_results.append(f"爻{pos} + 上卦{upper}/下卦{lower} = 100%吉 ({len(matches)}個)")
                    if all(l == -1 for l in labels):
                        conditions_results.append(f"爻{pos} + 上卦{upper}/下卦{lower} = 100%凶 ({len(matches)}個)")

    # 條件2: 特定爻位 + 五行關係
    for pos in range(1, 7):
        for relation in ['比和', '下生上', '上生下', '下剋上', '上剋下']:
            matches = []
            for yao in data:
                if yao['position'] != pos:
                    continue
                if yao['hex_num'] not in hex_to_info:
                    continue
                info = hex_to_info[yao['hex_num']]
                if get_wuxing_relation(info['lower'], info['upper']) == relation:
                    matches.append(yao)

            if matches and len(matches) >= 3:
                labels = [y['label'] for y in matches]
                ji_rate = sum(1 for l in labels if l == 1) / len(labels)
                xi_rate = sum(1 for l in labels if l == -1) / len(labels)
                if ji_rate >= 0.8:
                    conditions_results.append(f"爻{pos} + {relation} = {ji_rate*100:.0f}%吉 ({len(matches)}個)")
                if xi_rate >= 0.8:
                    conditions_results.append(f"爻{pos} + {relation} = {xi_rate*100:.0f}%凶 ({len(matches)}個)")

    # 條件3: 特定爻位 + 對稱性
    for pos in range(1, 7):
        for is_sym in [True, False]:
            matches = [y for y in data
                      if y['position'] == pos
                      and y['hex_num'] in hex_to_info
                      and hex_to_info[y['hex_num']]['is_symmetric'] == is_sym]
            if matches and len(matches) >= 3:
                labels = [y['label'] for y in matches]
                ji_rate = sum(1 for l in labels if l == 1) / len(labels)
                xi_rate = sum(1 for l in labels if l == -1) / len(labels)
                sym_str = '對稱卦' if is_sym else '非對稱卦'
                if ji_rate >= 0.8:
                    conditions_results.append(f"爻{pos} + {sym_str} = {ji_rate*100:.0f}%吉 ({len(matches)}個)")
                if xi_rate >= 0.8:
                    conditions_results.append(f"爻{pos} + {sym_str} = {xi_rate*100:.0f}%凶 ({len(matches)}個)")

    if conditions_results:
        print("\n發現高準確率規則:")
        for r in conditions_results[:20]:
            print(f"  {r}")
    else:
        print("\n未發現100%準確率規則")

def analyze_zhong_yao(data, struct_data):
    """分析中位爻 (2爻和5爻)"""
    print("\n" + "=" * 70)
    print("中位爻 (得中) 分析")
    print("=" * 70)

    # 2爻是下卦的中位，5爻是上卦的中位
    zhong_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})

    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        hex_to_trigrams[int(hex_num)] = (info['lower_trigram']['name'], info['upper_trigram']['name'])

    for yao in data:
        pos = yao['position']
        hex_num = yao['hex_num']

        if pos == 2:  # 下卦中位
            if hex_num in hex_to_trigrams:
                lower, _ = hex_to_trigrams[hex_num]
                zhong_stats[f'二爻-下卦{lower}']['total'] += 1
                if yao['label'] == 1:
                    zhong_stats[f'二爻-下卦{lower}']['ji'] += 1
                elif yao['label'] == -1:
                    zhong_stats[f'二爻-下卦{lower}']['xiong'] += 1

        if pos == 5:  # 上卦中位
            if hex_num in hex_to_trigrams:
                _, upper = hex_to_trigrams[hex_num]
                zhong_stats[f'五爻-上卦{upper}']['total'] += 1
                if yao['label'] == 1:
                    zhong_stats[f'五爻-上卦{upper}']['ji'] += 1
                elif yao['label'] == -1:
                    zhong_stats[f'五爻-上卦{upper}']['xiong'] += 1

    print("\n二爻 (下卦中位) 按下卦分類:")
    print("  下卦   吉率    凶率")
    for trigram in ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']:
        key = f'二爻-下卦{trigram}'
        s = zhong_stats[key]
        if s['total'] > 0:
            print(f"  {trigram}    {s['ji']/s['total']*100:5.1f}%  {s['xiong']/s['total']*100:5.1f}%")

    print("\n五爻 (上卦中位) 按上卦分類:")
    print("  上卦   吉率    凶率")
    for trigram in ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']:
        key = f'五爻-上卦{trigram}'
        s = zhong_stats[key]
        if s['total'] > 0:
            print(f"  {trigram}    {s['ji']/s['total']*100:5.1f}%  {s['xiong']/s['total']*100:5.1f}%")

def analyze_ji_extremes(data, struct_data):
    """分析極端情況 (全吉或全凶的卦)"""
    print("\n" + "=" * 70)
    print("極端情況分析 (每卦的吉凶分布)")
    print("=" * 70)

    hex_to_name = {}
    for hex_num, info in struct_data.items():
        hex_to_name[int(hex_num)] = info['name']

    hex_labels = defaultdict(list)
    for yao in data:
        hex_labels[yao['hex_num']].append(yao['label'])

    all_ji = []
    all_xiong = []
    mostly_ji = []
    mostly_xiong = []

    for hex_num, labels in hex_labels.items():
        if len(labels) != 6:
            continue
        ji_count = sum(1 for l in labels if l == 1)
        xiong_count = sum(1 for l in labels if l == -1)
        name = hex_to_name.get(hex_num, '?')

        if ji_count == 6:
            all_ji.append(f"{hex_num}.{name}")
        if xiong_count == 6:
            all_xiong.append(f"{hex_num}.{name}")
        if ji_count >= 5:
            mostly_ji.append(f"{hex_num}.{name} ({ji_count}吉)")
        if xiong_count >= 3:
            mostly_xiong.append(f"{hex_num}.{name} ({xiong_count}凶)")

    print(f"\n全吉卦 (6爻皆吉): {all_ji if all_ji else '無'}")
    print(f"全凶卦 (6爻皆凶): {all_xiong if all_xiong else '無'}")
    print(f"\n高吉卦 (≥5爻吉): {mostly_ji if mostly_ji else '無'}")
    print(f"高凶卦 (≥3爻凶): {mostly_xiong[:10] if mostly_xiong else '無'}")

def compare_with_previous(data):
    """比較與之前分析的差異"""
    print("\n" + "=" * 70)
    print("與之前分析的關鍵差異")
    print("=" * 70)

    # 計算統計
    labels = [y['label'] for y in data]
    counter = Counter(labels)
    total = len(labels)

    print("\n當前分析結果:")
    print(f"  總樣本: {total}")
    print(f"  吉: {counter[1]} ({counter[1]/total*100:.1f}%)")
    print(f"  中: {counter[0]} ({counter[0]/total*100:.1f}%)")
    print(f"  凶: {counter[-1]} ({counter[-1]/total*100:.1f}%)")
    print(f"  基線: {counter[0]/total*100:.1f}%")

    print("\n之前的分析結果 (參考FINAL_ANALYSIS_REPORT.md):")
    print(f"  總樣本: 384")
    print(f"  吉: 138 (35.9%)")
    print(f"  中: 145 (37.8%)")
    print(f"  凶: 101 (26.3%)")

    print("\n差異分析:")
    print(f"  - 樣本減少: 384 → {total} (咸卦數據問題)")
    print(f"  - 凶率下降: 26.3% → {counter[-1]/total*100:.1f}% (修正「无不利」誤分類)")
    print(f"  - 中率上升: 37.8% → {counter[0]/total*100:.1f}%")

def main():
    data = load_corrected_data()
    struct_data = load_structure()

    # 五行分析
    analysis_wuxing(data, struct_data)

    # 對稱卦分析
    analysis_symmetry(data, struct_data)

    # 中位爻分析
    analyze_zhong_yao(data, struct_data)

    # 極端情況分析
    analyze_ji_extremes(data, struct_data)

    # 搜尋100%規則
    search_100_percent_rules(data, struct_data)

    # 與之前分析比較
    compare_with_previous(data)

if __name__ == "__main__":
    main()
