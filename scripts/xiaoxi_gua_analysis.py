#!/usr/bin/env python3
"""
消息卦 (Sovereign Hexagrams) Analysis
Analyzes the 12 sovereign hexagrams that represent the waxing and waning of yin/yang
through the annual cycle.

The 12 消息卦:
復 (24) → 臨 (19) → 泰 (11) → 大壯 (34) → 夬 (43) → 乾 (1) [陽長]
姤 (44) → 遯 (33) → 否 (12) → 觀 (20) → 剝 (23) → 坤 (2) [陰長]
"""

import json
import os
from collections import defaultdict

# The 12 Sovereign Hexagrams with their King Wen numbers and binary
XIAOXI_GUA = {
    # Yang waxing (陽長) - from 復 to 乾
    '復': {'kw': 24, 'binary': '100000', 'yang_count': 1, 'month': 11, 'phase': 'yang_waxing'},
    '臨': {'kw': 19, 'binary': '110000', 'yang_count': 2, 'month': 12, 'phase': 'yang_waxing'},
    '泰': {'kw': 11, 'binary': '111000', 'yang_count': 3, 'month': 1, 'phase': 'yang_waxing'},
    '大壯': {'kw': 34, 'binary': '111100', 'yang_count': 4, 'month': 2, 'phase': 'yang_waxing'},
    '夬': {'kw': 43, 'binary': '111110', 'yang_count': 5, 'month': 3, 'phase': 'yang_waxing'},
    '乾': {'kw': 1, 'binary': '111111', 'yang_count': 6, 'month': 4, 'phase': 'yang_waxing'},

    # Yin waxing (陰長) - from 姤 to 坤
    '姤': {'kw': 44, 'binary': '011111', 'yang_count': 5, 'month': 5, 'phase': 'yin_waxing'},
    '遯': {'kw': 33, 'binary': '001111', 'yang_count': 4, 'month': 6, 'phase': 'yin_waxing'},
    '否': {'kw': 12, 'binary': '000111', 'yang_count': 3, 'month': 7, 'phase': 'yin_waxing'},
    '觀': {'kw': 20, 'binary': '000011', 'yang_count': 2, 'month': 8, 'phase': 'yin_waxing'},
    '剝': {'kw': 23, 'binary': '000001', 'yang_count': 1, 'month': 9, 'phase': 'yin_waxing'},
    '坤': {'kw': 2, 'binary': '000000', 'yang_count': 0, 'month': 10, 'phase': 'yin_waxing'},
}

# Trigram mappings
TRIGRAM_BINARY = {
    '乾': '111', '兌': '110', '離': '101', '震': '100',
    '巽': '011', '坎': '010', '艮': '001', '坤': '000'
}

JI_KEYWORDS = {
    '元吉': 2, '大吉': 2, '吉': 1, '無咎': 0.5, '利': 0.5,
    '亨': 0.5, '貞吉': 1, '終吉': 1, '有喜': 1, '有慶': 1
}

XIONG_KEYWORDS = {
    '凶': -1, '大凶': -2, '厲': -0.5, '吝': -0.3, '悔': -0.3,
    '咎': -0.3, '災': -1, '死': -1.5, '亡': -0.5, '困': -0.5
}

def load_hexagram_data():
    yaoci_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ctext', 'zhouyi_64gua.json')
    with open(yaoci_path, 'r', encoding='utf-8') as f:
        yaoci_data = json.load(f)

    struct_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'structure', 'hexagrams_structure.json')
    with open(struct_path, 'r', encoding='utf-8') as f:
        struct_data = json.load(f)

    hexagrams = []
    for hex_data in yaoci_data['hexagrams']:
        number = hex_data['metadata']['number']
        name = hex_data['title_zh']
        content = hex_data['content_zh']
        struct = struct_data.get(str(number), {})

        lines = []
        for i in range(1, min(7, len(content))):
            lines.append({'text': content[i]})

        hexagrams.append({
            'number': number,
            'name': name,
            'lines': lines,
            'trigrams': {
                'upper': struct.get('upper_trigram', {}).get('name', ''),
                'lower': struct.get('lower_trigram', {}).get('name', '')
            },
            'binary': struct.get('binary', '')
        })

    return hexagrams

def classify_yao(text):
    ji_score = sum(weight for kw, weight in JI_KEYWORDS.items() if kw in text)
    xiong_score = sum(weight for kw, weight in XIONG_KEYWORDS.items() if kw in text)

    total = ji_score + xiong_score
    if total > 0.3:
        return 1
    elif total < -0.3:
        return -1
    return 0

def get_binary(gua):
    upper = gua.get('trigrams', {}).get('upper', '')
    lower = gua.get('trigrams', {}).get('lower', '')
    return TRIGRAM_BINARY.get(upper, '000') + TRIGRAM_BINARY.get(lower, '000')

def analyze_xiaoxi_gua(hexagrams):
    """Analyze the 12 sovereign hexagrams"""
    results = {
        'xiaoxi': {},  # Individual sovereign hexagrams
        'non_xiaoxi': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},  # Non-sovereign
        'yang_waxing': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},  # 陽長 phase
        'yin_waxing': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},   # 陰長 phase
        'by_yang_count': defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0}),
    }

    # Initialize individual xiaoxi gua
    for name in XIAOXI_GUA:
        results['xiaoxi'][name] = {
            'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0,
            'by_position': [{'ji': 0, 'xiong': 0, 'zhong': 0} for _ in range(6)],
            **XIAOXI_GUA[name]
        }

    # Analyze each hexagram
    for gua in hexagrams:
        name = gua.get('name', '')
        lines = gua.get('lines', [])

        is_xiaoxi = name in XIAOXI_GUA

        for i, line in enumerate(lines):
            text = line.get('text', '')
            if not text:
                continue

            outcome = classify_yao(text)
            outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else 'zhong')

            if is_xiaoxi:
                results['xiaoxi'][name]['total'] += 1
                results['xiaoxi'][name][outcome_key] += 1
                results['xiaoxi'][name]['by_position'][i][outcome_key] += 1

                # Phase
                phase = XIAOXI_GUA[name]['phase']
                results[phase]['total'] += 1
                results[phase][outcome_key] += 1

                # By yang count
                yang_count = XIAOXI_GUA[name]['yang_count']
                results['by_yang_count'][yang_count]['total'] += 1
                results['by_yang_count'][yang_count][outcome_key] += 1
            else:
                results['non_xiaoxi']['total'] += 1
                results['non_xiaoxi'][outcome_key] += 1

    # Convert defaultdict
    results['by_yang_count'] = dict(results['by_yang_count'])

    return results

def analyze_changing_line_position(hexagrams):
    """
    Analyze if the position of the changing line (進退爻) in sovereign hexagrams
    has special significance.

    In sovereign hexagrams, there's always one line that represents the change:
    - Yang waxing: The bottom yang line is the "active" one
    - Yin waxing: The bottom yin line is the "active" one
    """
    results = {
        'changing_line': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
        'non_changing_line': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
    }

    for gua in hexagrams:
        name = gua.get('name', '')
        if name not in XIAOXI_GUA:
            continue

        lines = gua.get('lines', [])
        binary = XIAOXI_GUA[name]['binary']
        phase = XIAOXI_GUA[name]['phase']
        yang_count = XIAOXI_GUA[name]['yang_count']

        # Find the changing line position
        # Yang waxing: the topmost yang line is the changing one
        # Yin waxing: the topmost yin line is the changing one
        if phase == 'yang_waxing' and yang_count > 0:
            # Find position of topmost yang (reading from bottom)
            changing_pos = yang_count - 1  # 0-indexed from bottom
        elif phase == 'yin_waxing' and yang_count < 6:
            # Find position of topmost yin
            yin_count = 6 - yang_count
            changing_pos = yang_count  # First yin from bottom (0-indexed)
        else:
            changing_pos = -1

        for i, line in enumerate(lines):
            text = line.get('text', '')
            if not text:
                continue

            outcome = classify_yao(text)
            outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else 'zhong')

            if i == changing_pos:
                results['changing_line']['total'] += 1
                results['changing_line'][outcome_key] += 1
            else:
                results['non_changing_line']['total'] += 1
                results['non_changing_line'][outcome_key] += 1

    return results

def main():
    print("=" * 60)
    print("消息卦 (Sovereign Hexagrams) Analysis")
    print("=" * 60)

    hexagrams = load_hexagram_data()

    # Display the 12 sovereign hexagrams
    print("\nThe 12 Sovereign Hexagrams (消息卦):")
    print("-" * 50)
    print("\n陽長 (Yang Waxing) Phase:")
    yang_gua = [(n, d) for n, d in XIAOXI_GUA.items() if d['phase'] == 'yang_waxing']
    yang_gua.sort(key=lambda x: x[1]['month'])
    for name, data in yang_gua:
        print(f"  {name} (KW {data['kw']:2d}): {data['binary']} - Month {data['month']:2d}")

    print("\n陰長 (Yin Waxing) Phase:")
    yin_gua = [(n, d) for n, d in XIAOXI_GUA.items() if d['phase'] == 'yin_waxing']
    yin_gua.sort(key=lambda x: x[1]['month'])
    for name, data in yin_gua:
        print(f"  {name} (KW {data['kw']:2d}): {data['binary']} - Month {data['month']:2d}")

    # Analyze
    print("\n" + "=" * 60)
    print("Analysis Results")
    print("=" * 60)

    results = analyze_xiaoxi_gua(hexagrams)

    # Compare sovereign vs non-sovereign
    print("\n1. Sovereign vs Non-Sovereign Hexagrams:")
    print("-" * 50)

    xiaoxi_total = sum(d['total'] for d in results['xiaoxi'].values())
    xiaoxi_ji = sum(d['ji'] for d in results['xiaoxi'].values())
    xiaoxi_xiong = sum(d['xiong'] for d in results['xiaoxi'].values())

    print(f"\n  消息卦 (12 hexagrams, {xiaoxi_total} yaos):")
    print(f"    吉率: {xiaoxi_ji/xiaoxi_total:.1%}")
    print(f"    凶率: {xiaoxi_xiong/xiaoxi_total:.1%}")

    non_total = results['non_xiaoxi']['total']
    non_ji = results['non_xiaoxi']['ji']
    non_xiong = results['non_xiaoxi']['xiong']

    print(f"\n  非消息卦 (52 hexagrams, {non_total} yaos):")
    print(f"    吉率: {non_ji/non_total:.1%}")
    print(f"    凶率: {non_xiong/non_total:.1%}")

    # Compare phases
    print("\n2. Yang Waxing vs Yin Waxing Phases:")
    print("-" * 50)

    yang = results['yang_waxing']
    yin = results['yin_waxing']

    print(f"\n  陽長 (Yang waxing, 36 yaos):")
    print(f"    吉率: {yang['ji']/yang['total']:.1%}")
    print(f"    凶率: {yang['xiong']/yang['total']:.1%}")

    print(f"\n  陰長 (Yin waxing, 36 yaos):")
    print(f"    吉率: {yin['ji']/yin['total']:.1%}")
    print(f"    凶率: {yin['xiong']/yin['total']:.1%}")

    # By yang count
    print("\n3. By Yang Count (陽爻數量):")
    print("-" * 50)

    for yang_count in sorted(results['by_yang_count'].keys()):
        data = results['by_yang_count'][yang_count]
        if data['total'] > 0:
            print(f"\n  {yang_count} yang lines:")
            print(f"    吉率: {data['ji']/data['total']:.1%}")
            print(f"    凶率: {data['xiong']/data['total']:.1%}")

    # Individual sovereign hexagrams
    print("\n4. Individual Sovereign Hexagrams:")
    print("-" * 50)

    for name in ['復', '臨', '泰', '大壯', '夬', '乾', '姤', '遯', '否', '觀', '剝', '坤']:
        data = results['xiaoxi'][name]
        if data['total'] > 0:
            ji_rate = data['ji'] / data['total']
            xiong_rate = data['xiong'] / data['total']
            print(f"\n  {name} ({data['binary']}):")
            print(f"    吉率: {ji_rate:.1%}, 凶率: {xiong_rate:.1%}")

    # Changing line analysis
    print("\n5. Changing Line (進退爻) Analysis:")
    print("-" * 50)

    changing_results = analyze_changing_line_position(hexagrams)

    cl = changing_results['changing_line']
    ncl = changing_results['non_changing_line']

    if cl['total'] > 0:
        print(f"\n  Changing line (active yao):")
        print(f"    吉率: {cl['ji']/cl['total']:.1%}")
        print(f"    凶率: {cl['xiong']/cl['total']:.1%}")

    if ncl['total'] > 0:
        print(f"\n  Non-changing lines:")
        print(f"    吉率: {ncl['ji']/ncl['total']:.1%}")
        print(f"    凶率: {ncl['xiong']/ncl['total']:.1%}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    print("\n消息卦 represent the annual cycle of yin-yang waxing and waning.")
    print("\nKey Findings:")

    # Check for significant differences
    if xiaoxi_total > 0 and non_total > 0:
        diff = abs(xiaoxi_ji/xiaoxi_total - non_ji/non_total)
        if diff > 0.05:
            print(f"• Sovereign hexagrams have {'higher' if xiaoxi_ji/xiaoxi_total > non_ji/non_total else 'lower'} 吉率 than average")
        else:
            print("• Sovereign hexagrams have similar 吉率 to non-sovereign hexagrams")

    if yang['total'] > 0 and yin['total'] > 0:
        diff = abs(yang['ji']/yang['total'] - yin['ji']/yin['total'])
        if diff > 0.1:
            print(f"• {'Yang waxing' if yang['ji']/yang['total'] > yin['ji']/yin['total'] else 'Yin waxing'} phase has higher 吉率")
        else:
            print("• Both phases (yang/yin waxing) have similar 吉率")

    # Save results
    results_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis', 'xiaoxi_gua_analysis.json')
    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    main()
