#!/usr/bin/env python3
"""
互卦, 錯卦, 綜卦 Analysis
Analyzes three types of hexagram transformations:

1. 互卦 (Interlocking Hexagram):
   - Takes lines 2,3,4 as lower trigram
   - Takes lines 3,4,5 as upper trigram
   - Creates a new hexagram from the middle lines

2. 錯卦 (Opposite/Inverse Hexagram):
   - Inverts all lines (yang↔yin)
   - Each hexagram has exactly one 錯卦

3. 綜卦 (Overturned/Reverse Hexagram):
   - Turns hexagram upside down (180° rotation)
   - 8 hexagrams are self-symmetric (綜卦 = itself)
"""

import json
import os
from collections import defaultdict

TRIGRAM_BINARY = {
    '乾': '111', '兌': '110', '離': '101', '震': '100',
    '巽': '011', '坎': '010', '艮': '001', '坤': '000'
}

BINARY_TRIGRAM = {v: k for k, v in TRIGRAM_BINARY.items()}

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

def get_binary(gua):
    upper = gua.get('trigrams', {}).get('upper', '')
    lower = gua.get('trigrams', {}).get('lower', '')
    return TRIGRAM_BINARY.get(upper, '000') + TRIGRAM_BINARY.get(lower, '000')

def classify_yao(text):
    ji_score = sum(weight for kw, weight in JI_KEYWORDS.items() if kw in text)
    xiong_score = sum(weight for kw, weight in XIONG_KEYWORDS.items() if kw in text)

    total = ji_score + xiong_score
    if total > 0.3:
        return 1
    elif total < -0.3:
        return -1
    return 0

def get_hexagram_outcome(gua):
    """Get overall 吉凶 for hexagram (majority of its yaos)"""
    lines = gua.get('lines', [])
    outcomes = [classify_yao(line.get('text', '')) for line in lines]

    ji = sum(1 for o in outcomes if o == 1)
    xiong = sum(1 for o in outcomes if o == -1)
    total = len(outcomes)

    return {
        'total': total,
        'ji': ji,
        'xiong': xiong,
        'zhong': total - ji - xiong,
        'ji_rate': ji / total if total > 0 else 0,
        'xiong_rate': xiong / total if total > 0 else 0
    }

def calculate_hugua(binary):
    """
    Calculate 互卦 (interlocking hexagram)
    Lower trigram: lines 2,3,4 (indices 1,2,3 from bottom)
    Upper trigram: lines 3,4,5 (indices 2,3,4 from bottom)
    Binary is stored top-to-bottom, so we need to reverse
    """
    # binary[0] = top (line 6), binary[5] = bottom (line 1)
    # Lines 2,3,4 → indices 4,3,2 in binary → positions 4,3,2
    # Lines 3,4,5 → indices 3,2,1 in binary → positions 3,2,1

    lower = binary[4] + binary[3] + binary[2]  # Lines 2,3,4
    upper = binary[3] + binary[2] + binary[1]  # Lines 3,4,5

    return upper + lower

def calculate_cuogua(binary):
    """
    Calculate 錯卦 (opposite hexagram)
    Invert all lines: 0↔1
    """
    return ''.join('1' if b == '0' else '0' for b in binary)

def calculate_zonggua(binary):
    """
    Calculate 綜卦 (overturned hexagram)
    Reverse the order (180° rotation)
    """
    return binary[::-1]

def build_hexagram_lookup(hexagrams):
    """Build lookup from binary to hexagram"""
    lookup = {}
    for gua in hexagrams:
        binary = get_binary(gua)
        lookup[binary] = gua
    return lookup

def analyze_transformations(hexagrams):
    """Analyze 互卦, 錯卦, 綜卦 relationships"""
    lookup = build_hexagram_lookup(hexagrams)

    results = {
        '互卦': {
            'correlations': [],
            'analysis': {'same_ji': 0, 'diff_ji': 0, 'total': 0}
        },
        '錯卦': {
            'pairs': [],
            'analysis': {'same_ji': 0, 'diff_ji': 0, 'total': 0}
        },
        '綜卦': {
            'pairs': [],
            'self_symmetric': [],
            'analysis': {'same_ji': 0, 'diff_ji': 0, 'total': 0}
        }
    }

    processed_cuo = set()
    processed_zong = set()

    for gua in hexagrams:
        binary = get_binary(gua)
        name = gua.get('name', '')
        outcome = get_hexagram_outcome(gua)

        # 互卦 analysis
        hugua_binary = calculate_hugua(binary)
        if hugua_binary in lookup:
            hugua = lookup[hugua_binary]
            hugua_outcome = get_hexagram_outcome(hugua)

            results['互卦']['correlations'].append({
                'original': name,
                'original_binary': binary,
                'original_ji_rate': outcome['ji_rate'],
                '互卦': hugua.get('name', ''),
                '互卦_binary': hugua_binary,
                '互卦_ji_rate': hugua_outcome['ji_rate']
            })

            # Check correlation
            results['互卦']['analysis']['total'] += 1
            if (outcome['ji_rate'] > 0.4) == (hugua_outcome['ji_rate'] > 0.4):
                results['互卦']['analysis']['same_ji'] += 1
            else:
                results['互卦']['analysis']['diff_ji'] += 1

        # 錯卦 analysis
        cuogua_binary = calculate_cuogua(binary)
        pair_key = tuple(sorted([binary, cuogua_binary]))

        if pair_key not in processed_cuo and cuogua_binary in lookup:
            processed_cuo.add(pair_key)
            cuogua = lookup[cuogua_binary]
            cuogua_outcome = get_hexagram_outcome(cuogua)

            results['錯卦']['pairs'].append({
                'gua1': name,
                'gua1_binary': binary,
                'gua1_ji_rate': outcome['ji_rate'],
                'gua2': cuogua.get('name', ''),
                'gua2_binary': cuogua_binary,
                'gua2_ji_rate': cuogua_outcome['ji_rate'],
                'is_self': binary == cuogua_binary
            })

            results['錯卦']['analysis']['total'] += 1
            if (outcome['ji_rate'] > 0.4) == (cuogua_outcome['ji_rate'] > 0.4):
                results['錯卦']['analysis']['same_ji'] += 1
            else:
                results['錯卦']['analysis']['diff_ji'] += 1

        # 綜卦 analysis
        zonggua_binary = calculate_zonggua(binary)
        pair_key = tuple(sorted([binary, zonggua_binary]))

        if pair_key not in processed_zong and zonggua_binary in lookup:
            processed_zong.add(pair_key)

            is_self_symmetric = binary == zonggua_binary

            if is_self_symmetric:
                results['綜卦']['self_symmetric'].append({
                    'name': name,
                    'binary': binary,
                    'ji_rate': outcome['ji_rate']
                })
            else:
                zonggua = lookup[zonggua_binary]
                zonggua_outcome = get_hexagram_outcome(zonggua)

                results['綜卦']['pairs'].append({
                    'gua1': name,
                    'gua1_binary': binary,
                    'gua1_ji_rate': outcome['ji_rate'],
                    'gua2': zonggua.get('name', ''),
                    'gua2_binary': zonggua_binary,
                    'gua2_ji_rate': zonggua_outcome['ji_rate']
                })

                results['綜卦']['analysis']['total'] += 1
                if (outcome['ji_rate'] > 0.4) == (zonggua_outcome['ji_rate'] > 0.4):
                    results['綜卦']['analysis']['same_ji'] += 1
                else:
                    results['綜卦']['analysis']['diff_ji'] += 1

    return results

def analyze_hugua_trigrams(hexagrams):
    """Analyze which trigrams appear in 互卦 and their effect on 吉凶"""
    lookup = build_hexagram_lookup(hexagrams)

    results = {
        'hugua_upper_trigram': defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0}),
        'hugua_lower_trigram': defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0}),
        'hugua_contains_kan': {'total': 0, 'ji': 0, 'xiong': 0},
        'hugua_contains_gen': {'total': 0, 'ji': 0, 'xiong': 0},
    }

    for gua in hexagrams:
        binary = get_binary(gua)
        hugua_binary = calculate_hugua(binary)

        upper = hugua_binary[:3]
        lower = hugua_binary[3:]

        upper_trigram = BINARY_TRIGRAM.get(upper, '?')
        lower_trigram = BINARY_TRIGRAM.get(lower, '?')

        # Analyze each yao of original hexagram
        lines = gua.get('lines', [])
        for line in lines:
            text = line.get('text', '')
            outcome = classify_yao(text)
            outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else None)

            if outcome_key:
                results['hugua_upper_trigram'][upper_trigram]['total'] += 1
                results['hugua_upper_trigram'][upper_trigram][outcome_key] += 1

                results['hugua_lower_trigram'][lower_trigram]['total'] += 1
                results['hugua_lower_trigram'][lower_trigram][outcome_key] += 1

                if upper_trigram == '坎' or lower_trigram == '坎':
                    results['hugua_contains_kan']['total'] += 1
                    results['hugua_contains_kan'][outcome_key] += 1

                if upper_trigram == '艮' or lower_trigram == '艮':
                    results['hugua_contains_gen']['total'] += 1
                    results['hugua_contains_gen'][outcome_key] += 1

    # Convert defaultdict
    results['hugua_upper_trigram'] = dict(results['hugua_upper_trigram'])
    results['hugua_lower_trigram'] = dict(results['hugua_lower_trigram'])

    return results

def main():
    print("=" * 60)
    print("互卦, 錯卦, 綜卦 Analysis")
    print("=" * 60)

    hexagrams = load_hexagram_data()
    results = analyze_transformations(hexagrams)

    # 1. 互卦 Analysis
    print("\n1. 互卦 (Interlocking Hexagram) Analysis")
    print("-" * 50)
    print("\n互卦 is formed by taking lines 2-3-4 as lower trigram")
    print("and lines 3-4-5 as upper trigram.")

    hugua = results['互卦']
    print(f"\nTotal pairs analyzed: {len(hugua['correlations'])}")

    if hugua['analysis']['total'] > 0:
        same_rate = hugua['analysis']['same_ji'] / hugua['analysis']['total']
        print(f"Original-互卦 outcome correlation: {same_rate:.1%}")
        print(f"  (If original is mostly 吉, is 互卦 also mostly 吉?)")

    # Show some examples
    print("\nSample 互卦 relationships:")
    for item in hugua['correlations'][:5]:
        print(f"  {item['original']} → {item['互卦']}: {item['original_ji_rate']:.1%} → {item['互卦_ji_rate']:.1%}")

    # 2. 錯卦 Analysis
    print("\n2. 錯卦 (Opposite Hexagram) Analysis")
    print("-" * 50)
    print("\n錯卦 inverts all lines (yang↔yin).")

    cuogua = results['錯卦']
    print(f"\nTotal pairs: {len(cuogua['pairs'])}")

    if cuogua['analysis']['total'] > 0:
        same_rate = cuogua['analysis']['same_ji'] / cuogua['analysis']['total']
        print(f"Original-錯卦 outcome correlation: {same_rate:.1%}")

    print("\nSample 錯卦 pairs:")
    for pair in cuogua['pairs'][:5]:
        print(f"  {pair['gua1']} ↔ {pair['gua2']}: {pair['gua1_ji_rate']:.1%} vs {pair['gua2_ji_rate']:.1%}")

    # 3. 綜卦 Analysis
    print("\n3. 綜卦 (Overturned Hexagram) Analysis")
    print("-" * 50)
    print("\n綜卦 is the 180° rotation of the hexagram.")

    zonggua = results['綜卦']
    print(f"\nRotation pairs: {len(zonggua['pairs'])}")
    print(f"Self-symmetric hexagrams: {len(zonggua['self_symmetric'])}")

    print("\nSelf-symmetric hexagrams (綜卦 = itself):")
    for item in zonggua['self_symmetric']:
        print(f"  {item['name']} ({item['binary']}): 吉率 {item['ji_rate']:.1%}")

    if zonggua['analysis']['total'] > 0:
        same_rate = zonggua['analysis']['same_ji'] / zonggua['analysis']['total']
        print(f"\nOriginal-綜卦 outcome correlation: {same_rate:.1%}")

    print("\nSample 綜卦 pairs:")
    for pair in zonggua['pairs'][:5]:
        print(f"  {pair['gua1']} ↔ {pair['gua2']}: {pair['gua1_ji_rate']:.1%} vs {pair['gua2_ji_rate']:.1%}")

    # 4. 互卦 Trigram Analysis (as suggested by 易經大師)
    print("\n4. 互卦 Trigram Effect on 吉凶")
    print("-" * 50)

    trigram_results = analyze_hugua_trigrams(hexagrams)

    print("\n互卦 Upper Trigram Statistics:")
    for trigram, data in sorted(trigram_results['hugua_upper_trigram'].items(),
                                 key=lambda x: x[1]['ji']/(x[1]['total']+0.1), reverse=True):
        if data['total'] > 0:
            ji_rate = data['ji'] / data['total']
            xiong_rate = data['xiong'] / data['total']
            print(f"  {trigram}: 吉率 {ji_rate:.1%}, 凶率 {xiong_rate:.1%} (n={data['total']})")

    print("\n互卦 contains 坎 (danger) trigram:")
    kan = trigram_results['hugua_contains_kan']
    if kan['total'] > 0:
        print(f"  吉率: {kan['ji']/kan['total']:.1%}, 凶率: {kan['xiong']/kan['total']:.1%}")

    print("\n互卦 contains 艮 (stopping) trigram:")
    gen = trigram_results['hugua_contains_gen']
    if gen['total'] > 0:
        print(f"  吉率: {gen['ji']/gen['total']:.1%}, 凶率: {gen['xiong']/gen['total']:.1%}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    print("\nKey Findings:")

    # Check correlations
    if hugua['analysis']['total'] > 0:
        same_rate = hugua['analysis']['same_ji'] / hugua['analysis']['total']
        if same_rate > 0.6:
            print(f"• 互卦 shows moderate correlation with original hexagram 吉凶 ({same_rate:.1%})")
        else:
            print(f"• 互卦 shows weak correlation with original hexagram 吉凶 ({same_rate:.1%})")

    if cuogua['analysis']['total'] > 0:
        same_rate = cuogua['analysis']['same_ji'] / cuogua['analysis']['total']
        if same_rate < 0.4:
            print(f"• 錯卦 pairs tend to have OPPOSITE outcomes ({same_rate:.1%} similarity)")
        elif same_rate > 0.6:
            print(f"• 錯卦 pairs tend to have SIMILAR outcomes ({same_rate:.1%} similarity)")

    if zonggua['analysis']['total'] > 0:
        same_rate = zonggua['analysis']['same_ji'] / zonggua['analysis']['total']
        print(f"• 綜卦 pairs have {same_rate:.1%} similarity in 吉凶 outcomes")

    print(f"• 8 self-symmetric hexagrams found (same when rotated 180°)")

    # Save results
    results_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis', 'transformation_analysis.json')
    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    main()
