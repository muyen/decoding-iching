#!/usr/bin/env python3
"""
使用修正後的爻辭標籤進行 2D 和 3D 分析

基於 corrected_yaoci_labels.json 的數據
"""

import json
import os
from collections import defaultdict, Counter
import numpy as np

def load_corrected_data():
    """載入修正後的爻辭標籤"""
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'analysis', 'corrected_yaoci_labels.json')
    with open(path, 'r') as f:
        return json.load(f)

def load_structure():
    """載入結構數據"""
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'structure', 'hexagrams_structure.json')
    with open(path, 'r') as f:
        return json.load(f)

# 八卦名稱
TRIGRAM_NAMES = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']  # 按binary 000-111排序
TRIGRAM_BINARY_TO_NAME = {
    '000': '坤', '001': '艮', '010': '坎', '011': '巽',
    '100': '震', '101': '離', '110': '兌', '111': '乾'
}

def get_trigrams_from_binary(binary):
    """從六爻二進制獲取上下卦"""
    lower = binary[:3]  # 初二三爻
    upper = binary[3:]  # 四五上爻
    return TRIGRAM_BINARY_TO_NAME.get(lower, '?'), TRIGRAM_BINARY_TO_NAME.get(upper, '?')

def analysis_1d(data):
    """1D分析：爻位效應"""
    print("=" * 70)
    print("1D 分析：爻位效應 (Position Effect)")
    print("=" * 70)

    pos_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'zhong': 0, 'xiong': 0})

    for yao in data:
        pos = yao['position']
        pos_stats[pos]['total'] += 1
        if yao['label'] == 1:
            pos_stats[pos]['ji'] += 1
        elif yao['label'] == 0:
            pos_stats[pos]['zhong'] += 1
        else:
            pos_stats[pos]['xiong'] += 1

    print("\n爻位   總數   吉率    中率    凶率    淨吉率")
    print("-" * 55)
    for pos in range(1, 7):
        s = pos_stats[pos]
        if s['total'] == 0:
            continue
        ji_rate = s['ji'] / s['total'] * 100
        zhong_rate = s['zhong'] / s['total'] * 100
        xiong_rate = s['xiong'] / s['total'] * 100
        net_ji = ji_rate - xiong_rate
        print(f"  {pos}    {s['total']:3d}   {ji_rate:5.1f}%  {zhong_rate:5.1f}%  {xiong_rate:5.1f}%   {net_ji:+5.1f}%")

    print("\n傳統易學驗證:")
    print(f"  - 五爻(九五之尊): 吉率 {pos_stats[5]['ji']/pos_stats[5]['total']*100:.1f}%, 凶率 {pos_stats[5]['xiong']/pos_stats[5]['total']*100:.1f}%")
    print(f"  - 二爻(二多譽): 吉率 {pos_stats[2]['ji']/pos_stats[2]['total']*100:.1f}%, 凶率 {pos_stats[2]['xiong']/pos_stats[2]['total']*100:.1f}%")
    print(f"  - 三爻(三多凶): 吉率 {pos_stats[3]['ji']/pos_stats[3]['total']*100:.1f}%, 凶率 {pos_stats[3]['xiong']/pos_stats[3]['total']*100:.1f}%")
    print(f"  - 上爻(亢龍有悔): 吉率 {pos_stats[6]['ji']/pos_stats[6]['total']*100:.1f}%, 凶率 {pos_stats[6]['xiong']/pos_stats[6]['total']*100:.1f}%")

    return pos_stats

def analysis_2d(data, struct_data):
    """2D分析：8x8網格（上卦×下卦）"""
    print("\n" + "=" * 70)
    print("2D 分析：8x8 網格 (Upper × Lower Trigram)")
    print("=" * 70)

    # 建立卦號到卦結構的映射
    hex_to_trigrams = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_trigrams[int(hex_num)] = (lower, upper)

    # 統計每個上下卦組合
    grid_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'zhong': 0, 'xiong': 0})

    for yao in data:
        hex_num = yao['hex_num']
        if hex_num not in hex_to_trigrams:
            continue
        lower, upper = hex_to_trigrams[hex_num]
        key = (lower, upper)

        grid_stats[key]['total'] += 1
        if yao['label'] == 1:
            grid_stats[key]['ji'] += 1
        elif yao['label'] == 0:
            grid_stats[key]['zhong'] += 1
        else:
            grid_stats[key]['xiong'] += 1

    # 打印8x8網格
    print("\n吉率網格 (下卦→, 上卦↓):")
    print("     ", end="")
    for lower in TRIGRAM_NAMES:
        print(f"  {lower}  ", end="")
    print()
    print("     " + "-" * 48)

    for upper in TRIGRAM_NAMES:
        print(f" {upper} |", end="")
        for lower in TRIGRAM_NAMES:
            key = (lower, upper)
            if grid_stats[key]['total'] > 0:
                ji_rate = grid_stats[key]['ji'] / grid_stats[key]['total'] * 100
                print(f" {ji_rate:4.0f}%", end="")
            else:
                print("   - ", end="")
        print()

    # 凶率網格
    print("\n凶率網格 (下卦→, 上卦↓):")
    print("     ", end="")
    for lower in TRIGRAM_NAMES:
        print(f"  {lower}  ", end="")
    print()
    print("     " + "-" * 48)

    for upper in TRIGRAM_NAMES:
        print(f" {upper} |", end="")
        for lower in TRIGRAM_NAMES:
            key = (lower, upper)
            if grid_stats[key]['total'] > 0:
                xiong_rate = grid_stats[key]['xiong'] / grid_stats[key]['total'] * 100
                print(f" {xiong_rate:4.0f}%", end="")
            else:
                print("   - ", end="")
        print()

    # 找出最吉和最凶的組合
    best_combos = []
    worst_combos = []
    for key, stats in grid_stats.items():
        if stats['total'] >= 6:  # 至少有6個爻
            ji_rate = stats['ji'] / stats['total']
            xiong_rate = stats['xiong'] / stats['total']
            best_combos.append((key, ji_rate, stats['total']))
            worst_combos.append((key, xiong_rate, stats['total']))

    best_combos.sort(key=lambda x: -x[1])
    worst_combos.sort(key=lambda x: -x[1])

    print("\n最吉組合 (Top 5):")
    for (lower, upper), rate, total in best_combos[:5]:
        print(f"  {upper}/{lower}: 吉率 {rate*100:.1f}% ({total}爻)")

    print("\n最凶組合 (Top 5):")
    for (lower, upper), rate, total in worst_combos[:5]:
        print(f"  {upper}/{lower}: 凶率 {rate*100:.1f}% ({total}爻)")

    # 上卦和下卦單獨統計
    print("\n" + "-" * 50)
    print("上卦統計:")
    upper_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})
    for key, stats in grid_stats.items():
        lower, upper = key
        upper_stats[upper]['total'] += stats['total']
        upper_stats[upper]['ji'] += stats['ji']
        upper_stats[upper]['xiong'] += stats['xiong']

    print("  卦名   總數   吉率    凶率")
    for name in TRIGRAM_NAMES:
        s = upper_stats[name]
        if s['total'] > 0:
            print(f"  {name}    {s['total']:3d}   {s['ji']/s['total']*100:5.1f}%  {s['xiong']/s['total']*100:5.1f}%")

    print("\n下卦統計:")
    lower_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})
    for key, stats in grid_stats.items():
        lower, upper = key
        lower_stats[lower]['total'] += stats['total']
        lower_stats[lower]['ji'] += stats['ji']
        lower_stats[lower]['xiong'] += stats['xiong']

    print("  卦名   總數   吉率    凶率")
    for name in TRIGRAM_NAMES:
        s = lower_stats[name]
        if s['total'] > 0:
            print(f"  {name}    {s['total']:3d}   {s['ji']/s['total']*100:5.1f}%  {s['xiong']/s['total']*100:5.1f}%")

    return grid_stats

def analysis_3d(data, struct_data):
    """3D分析：卦性質×層次"""
    print("\n" + "=" * 70)
    print("3D 分析：卦性質 × 層次 (Trigram Nature × Layer)")
    print("=" * 70)

    # 八卦屬性映射
    TRIGRAM_NATURE = {
        '乾': '剛', '坤': '柔', '震': '動', '巽': '入',
        '坎': '險', '離': '麗', '艮': '止', '兌': '悅'
    }

    # 簡化為三類性質
    NATURE_CATEGORY = {
        '乾': '剛健', '震': '剛健',  # 剛、動
        '坤': '柔順', '巽': '柔順',  # 柔、入
        '坎': '險阻', '艮': '險阻',  # 險、止
        '離': '光明', '兌': '光明',  # 麗、悅
    }

    # 建立卦號到卦結構的映射
    hex_to_info = {}
    for hex_num, info in struct_data.items():
        lower = info['lower_trigram']['name']
        upper = info['upper_trigram']['name']
        hex_to_info[int(hex_num)] = {
            'lower': lower,
            'upper': upper,
            'lower_cat': NATURE_CATEGORY.get(lower, lower),
            'upper_cat': NATURE_CATEGORY.get(upper, upper)
        }

    # 3D: 下卦性質 × 上卦性質 × 爻位層次
    # 層次: 下層(1-2), 中層(3-4), 上層(5-6)
    def get_layer(pos):
        if pos <= 2:
            return '下層'
        elif pos <= 4:
            return '中層'
        else:
            return '上層'

    cube_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'zhong': 0, 'xiong': 0})

    for yao in data:
        hex_num = yao['hex_num']
        if hex_num not in hex_to_info:
            continue
        info = hex_to_info[hex_num]
        layer = get_layer(yao['position'])
        key = (info['lower_cat'], info['upper_cat'], layer)

        cube_stats[key]['total'] += 1
        if yao['label'] == 1:
            cube_stats[key]['ji'] += 1
        elif yao['label'] == 0:
            cube_stats[key]['zhong'] += 1
        else:
            cube_stats[key]['xiong'] += 1

    categories = ['剛健', '柔順', '險阻', '光明']
    layers = ['下層', '中層', '上層']

    # 打印3D結果
    print("\n3D 統計 (下卦性質 × 上卦性質 × 層次):")
    print("\n格式: 吉率/凶率 (樣本數)")

    for layer in layers:
        print(f"\n【{layer}】(爻位 {['1-2', '3-4', '5-6'][layers.index(layer)]})")
        print("       ", end="")
        for upper_cat in categories:
            print(f" {upper_cat[:2]} ", end="")
        print("  ← 上卦性質")
        print("       " + "-" * 28)

        for lower_cat in categories:
            print(f" {lower_cat[:2]} |", end="")
            for upper_cat in categories:
                key = (lower_cat, upper_cat, layer)
                s = cube_stats[key]
                if s['total'] > 0:
                    ji_r = s['ji'] / s['total'] * 100
                    xi_r = s['xiong'] / s['total'] * 100
                    print(f" {ji_r:2.0f}/{xi_r:2.0f}", end="")
                else:
                    print("   - ", end="")
            print()
        print("↑ 下卦性質")

    # 統計層次效應
    print("\n" + "-" * 50)
    print("層次效應總結:")
    layer_totals = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})
    for key, stats in cube_stats.items():
        layer = key[2]
        layer_totals[layer]['total'] += stats['total']
        layer_totals[layer]['ji'] += stats['ji']
        layer_totals[layer]['xiong'] += stats['xiong']

    for layer in layers:
        s = layer_totals[layer]
        if s['total'] > 0:
            print(f"  {layer}: 吉率 {s['ji']/s['total']*100:5.1f}%, 凶率 {s['xiong']/s['total']*100:5.1f}% ({s['total']}爻)")

    # 統計性質組合效應
    print("\n性質組合效應 (不分層次):")
    combo_totals = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})
    for key, stats in cube_stats.items():
        lower_cat, upper_cat, _ = key
        combo_key = (lower_cat, upper_cat)
        combo_totals[combo_key]['total'] += stats['total']
        combo_totals[combo_key]['ji'] += stats['ji']
        combo_totals[combo_key]['xiong'] += stats['xiong']

    print("       ", end="")
    for upper_cat in categories:
        print(f"  {upper_cat[:2]}  ", end="")
    print("  ← 上卦")
    print("       " + "-" * 32)

    for lower_cat in categories:
        print(f" {lower_cat[:2]} |", end="")
        for upper_cat in categories:
            key = (lower_cat, upper_cat)
            s = combo_totals[key]
            if s['total'] > 0:
                ji_r = s['ji'] / s['total'] * 100
                print(f" {ji_r:4.0f}%", end="")
            else:
                print("   - ", end="")
        print()
    print("↑ 下卦")

    return cube_stats

def analysis_yinyang(data, struct_data):
    """陰陽分析：爻的陰陽屬性與位置配合"""
    print("\n" + "=" * 70)
    print("陰陽分析：當位與不當位")
    print("=" * 70)

    # 建立卦號到爻類型的映射
    hex_to_lines = {}
    for hex_num, info in struct_data.items():
        hex_to_lines[int(hex_num)] = info['lines']

    # 當位規則：陽爻在奇數位(1,3,5)，陰爻在偶數位(2,4,6)
    dangwei_stats = {'當位': {'total': 0, 'ji': 0, 'xiong': 0},
                     '不當位': {'total': 0, 'ji': 0, 'xiong': 0}}

    for yao in data:
        hex_num = yao['hex_num']
        if hex_num not in hex_to_lines:
            continue

        lines = hex_to_lines[hex_num]
        pos = yao['position']
        line_type = lines[pos-1]['type']  # 'yang' or 'yin'

        # 判斷當位
        is_odd = pos % 2 == 1
        is_yang = line_type == 'yang'
        is_dangwei = (is_odd and is_yang) or (not is_odd and not is_yang)

        key = '當位' if is_dangwei else '不當位'
        dangwei_stats[key]['total'] += 1
        if yao['label'] == 1:
            dangwei_stats[key]['ji'] += 1
        elif yao['label'] == -1:
            dangwei_stats[key]['xiong'] += 1

    print("\n當位與不當位統計:")
    for key, s in dangwei_stats.items():
        if s['total'] > 0:
            print(f"  {key}: 吉率 {s['ji']/s['total']*100:5.1f}%, 凶率 {s['xiong']/s['total']*100:5.1f}% ({s['total']}爻)")

    # 詳細分析每個位置的陰陽
    print("\n爻位×陰陽詳細:")
    pos_yinyang = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})

    for yao in data:
        hex_num = yao['hex_num']
        if hex_num not in hex_to_lines:
            continue

        lines = hex_to_lines[hex_num]
        pos = yao['position']
        line_type = lines[pos-1]['type']

        key = (pos, line_type)
        pos_yinyang[key]['total'] += 1
        if yao['label'] == 1:
            pos_yinyang[key]['ji'] += 1
        elif yao['label'] == -1:
            pos_yinyang[key]['xiong'] += 1

    print("  爻位  陽爻吉率  陰爻吉率  陽爻凶率  陰爻凶率")
    print("  " + "-" * 50)
    for pos in range(1, 7):
        yang_s = pos_yinyang[(pos, 'yang')]
        yin_s = pos_yinyang[(pos, 'yin')]

        yang_ji = yang_s['ji']/yang_s['total']*100 if yang_s['total'] > 0 else 0
        yin_ji = yin_s['ji']/yin_s['total']*100 if yin_s['total'] > 0 else 0
        yang_xi = yang_s['xiong']/yang_s['total']*100 if yang_s['total'] > 0 else 0
        yin_xi = yin_s['xiong']/yin_s['total']*100 if yin_s['total'] > 0 else 0

        print(f"   {pos}    {yang_ji:5.1f}%    {yin_ji:5.1f}%    {yang_xi:5.1f}%    {yin_xi:5.1f}%")

    return dangwei_stats

def summary_statistics(data):
    """總結統計"""
    print("\n" + "=" * 70)
    print("總結統計")
    print("=" * 70)

    labels = [y['label'] for y in data]
    counter = Counter(labels)

    print(f"\n總樣本數: {len(data)}")
    print(f"\n標籤分布:")
    print(f"  吉 (1):  {counter[1]:3d} ({counter[1]/len(labels)*100:.1f}%)")
    print(f"  中 (0):  {counter[0]:3d} ({counter[0]/len(labels)*100:.1f}%)")
    print(f"  凶 (-1): {counter[-1]:3d} ({counter[-1]/len(labels)*100:.1f}%)")

    baseline = max(counter.values()) / len(labels)
    print(f"\n基線準確率 (多數類): {baseline:.1%}")

    # 檢查缺失的卦
    hex_nums = set(y['hex_num'] for y in data)
    missing = [i for i in range(1, 65) if i not in hex_nums]
    if missing:
        print(f"\n警告: 缺失的卦: {missing}")

    # 每卦的爻數統計
    hex_yao_count = Counter(y['hex_num'] for y in data)
    incomplete = [(num, count) for num, count in hex_yao_count.items() if count != 6]
    if incomplete:
        print(f"\n爻數不完整的卦:")
        for num, count in sorted(incomplete):
            print(f"  卦{num}: {count}爻")

def main():
    print("=" * 70)
    print("修正後的爻辭標籤 - 完整 1D/2D/3D 分析")
    print("=" * 70)

    data = load_corrected_data()
    struct_data = load_structure()

    # 總結統計
    summary_statistics(data)

    # 1D 分析
    analysis_1d(data)

    # 2D 分析
    analysis_2d(data, struct_data)

    # 3D 分析
    analysis_3d(data, struct_data)

    # 陰陽分析
    analysis_yinyang(data, struct_data)

if __name__ == "__main__":
    main()
