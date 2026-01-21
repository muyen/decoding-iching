#!/usr/bin/env python3
"""
承乘比應 Analysis - Traditional Yao Relationship Patterns
Analyzes the four types of yao relationships described in I Ching tradition:
- 承 (chéng): Supporting from below (yin supports yang)
- 乘 (chéng): Riding from above (yang rides yin)
- 比 (bǐ): Adjacent relationship
- 應 (yìng): Corresponding positions (1-4, 2-5, 3-6)
"""

import json
import os
from collections import defaultdict

# Trigram mappings
TRIGRAM_BINARY = {
    '乾': '111', '兌': '110', '離': '101', '震': '100',
    '巽': '011', '坎': '010', '艮': '001', '坤': '000'
}

# Keyword weights for 吉凶 classification
JI_KEYWORDS = {
    '元吉': 2, '大吉': 2, '吉': 1, '無咎': 0.5, '利': 0.5,
    '亨': 0.5, '貞吉': 1, '終吉': 1, '有喜': 1, '有慶': 1
}

XIONG_KEYWORDS = {
    '凶': -1, '大凶': -2, '厲': -0.5, '吝': -0.3, '悔': -0.3,
    '咎': -0.3, '災': -1, '死': -1.5, '亡': -0.5, '困': -0.5
}

def load_hexagram_data():
    """Load hexagram data from JSON files"""
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
    """Get binary representation of hexagram"""
    upper = gua.get('trigrams', {}).get('upper', '')
    lower = gua.get('trigrams', {}).get('lower', '')
    return TRIGRAM_BINARY.get(upper, '000') + TRIGRAM_BINARY.get(lower, '000')

def classify_yao(text):
    """Classify yao as 吉(1), 中(0), or 凶(-1)"""
    ji_score = sum(weight for kw, weight in JI_KEYWORDS.items() if kw in text)
    xiong_score = sum(weight for kw, weight in XIONG_KEYWORDS.items() if kw in text)

    total = ji_score + xiong_score
    if total > 0.3:
        return 1
    elif total < -0.3:
        return -1
    return 0

def analyze_cheng_relationships(hexagrams):
    """
    分析承乘關係
    承 (Supporting): 陰爻承陽爻 (yin below yang - harmonious)
    乘 (Riding): 陽爻乘陰爻 (yang above yin - less harmonious)
    """
    results = {
        'yin_supports_yang': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
        'yang_rides_yin': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
        'same_polarity': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
    }

    for gua in hexagrams:
        binary = get_binary(gua)
        lines = gua.get('lines', [])

        for i in range(1, 6):  # Positions 2-6 (can have relationship with below)
            if i >= len(lines):
                continue

            text = lines[i].get('text', '')
            outcome = classify_yao(text)

            # Current yao and yao below (note: binary is top-to-bottom)
            current = int(binary[5-i])
            below = int(binary[5-i+1])

            outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else 'zhong')

            if current == 1 and below == 0:  # Yang above yin
                results['yang_rides_yin']['total'] += 1
                results['yang_rides_yin'][outcome_key] += 1
            elif current == 0 and below == 1:  # Yin above yang (承)
                results['yin_supports_yang']['total'] += 1
                results['yin_supports_yang'][outcome_key] += 1
            else:  # Same polarity
                results['same_polarity']['total'] += 1
                results['same_polarity'][outcome_key] += 1

    return results

def analyze_ying_relationships(hexagrams):
    """
    分析應關係 (Corresponding positions)
    Position pairs: 1-4, 2-5, 3-6
    正應: One yin, one yang (harmonious)
    不應: Same polarity (disharmonious)
    """
    results = {
        'zheng_ying': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},  # Correct correspondence
        'bu_ying': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},      # No correspondence
    }

    pairs = [(0, 3), (1, 4), (2, 5)]  # 1-4, 2-5, 3-6 (0-indexed)

    for gua in hexagrams:
        binary = get_binary(gua)
        lines = gua.get('lines', [])

        for lower_pos, upper_pos in pairs:
            # Analyze both positions in the pair
            for pos in [lower_pos, upper_pos]:
                if pos >= len(lines):
                    continue

                text = lines[pos].get('text', '')
                outcome = classify_yao(text)
                outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else 'zhong')

                # Check if corresponding positions have different polarities
                lower_yao = int(binary[5-lower_pos])
                upper_yao = int(binary[5-upper_pos])

                if lower_yao != upper_yao:  # 正應
                    results['zheng_ying']['total'] += 1
                    results['zheng_ying'][outcome_key] += 1
                else:  # 不應
                    results['bu_ying']['total'] += 1
                    results['bu_ying'][outcome_key] += 1

    return results

def analyze_bi_relationships(hexagrams):
    """
    分析比關係 (Adjacent relationships)
    比鄰: Adjacent yaos with different polarities
    """
    results = {
        'adjacent_different': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
        'adjacent_same': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},
    }

    for gua in hexagrams:
        binary = get_binary(gua)
        lines = gua.get('lines', [])

        for i in range(6):
            if i >= len(lines):
                continue

            text = lines[i].get('text', '')
            outcome = classify_yao(text)
            outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else 'zhong')

            current = int(binary[5-i])

            # Check adjacent yaos
            neighbors = []
            if i > 0:
                neighbors.append(int(binary[5-i+1]))  # Below
            if i < 5:
                neighbors.append(int(binary[5-i-1]))  # Above

            has_different = any(n != current for n in neighbors)

            if has_different:
                results['adjacent_different']['total'] += 1
                results['adjacent_different'][outcome_key] += 1
            else:
                results['adjacent_same']['total'] += 1
                results['adjacent_same'][outcome_key] += 1

    return results

def analyze_zhong_zheng(hexagrams):
    """
    分析中正 (Center-Correctness)
    中: Positions 2, 5 (center of trigrams)
    正: Position matches polarity (odd=yang, even=yin)
    """
    results = {
        'zhong_zheng': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},  # Both center and correct
        'zhong_only': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},   # Center but not correct
        'zheng_only': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},   # Correct but not center
        'neither': {'total': 0, 'ji': 0, 'xiong': 0, 'zhong': 0},      # Neither
    }

    for gua in hexagrams:
        binary = get_binary(gua)
        lines = gua.get('lines', [])

        for i in range(6):
            if i >= len(lines):
                continue

            text = lines[i].get('text', '')
            outcome = classify_yao(text)
            outcome_key = 'ji' if outcome == 1 else ('xiong' if outcome == -1 else 'zhong')

            position = i + 1  # 1-6
            yao_value = int(binary[5-i])

            is_zhong = position in [2, 5]  # Center positions
            is_zheng = (position % 2 == 1 and yao_value == 1) or \
                       (position % 2 == 0 and yao_value == 0)  # Odd=yang, Even=yin

            if is_zhong and is_zheng:
                results['zhong_zheng']['total'] += 1
                results['zhong_zheng'][outcome_key] += 1
            elif is_zhong:
                results['zhong_only']['total'] += 1
                results['zhong_only'][outcome_key] += 1
            elif is_zheng:
                results['zheng_only']['total'] += 1
                results['zheng_only'][outcome_key] += 1
            else:
                results['neither']['total'] += 1
                results['neither'][outcome_key] += 1

    return results

def chi_square_test(observed, expected):
    """Simple chi-square calculation"""
    chi_sq = 0
    for o, e in zip(observed, expected):
        if e > 0:
            chi_sq += (o - e) ** 2 / e
    return chi_sq

def print_analysis(name, results):
    """Print analysis results with statistics"""
    print(f"\n{name}")
    print("-" * 50)

    # Calculate overall baseline
    all_ji = sum(r['ji'] for r in results.values())
    all_xiong = sum(r['xiong'] for r in results.values())
    all_zhong = sum(r['zhong'] for r in results.values())
    all_total = sum(r['total'] for r in results.values())

    if all_total == 0:
        print("  No data available")
        return

    baseline_ji = all_ji / all_total
    baseline_xiong = all_xiong / all_total

    for key, data in results.items():
        total = data['total']
        if total == 0:
            continue

        ji_rate = data['ji'] / total
        xiong_rate = data['xiong'] / total

        print(f"\n  {key}:")
        print(f"    Total: {total}")
        print(f"    吉率: {ji_rate:.1%} (baseline: {baseline_ji:.1%})")
        print(f"    凶率: {xiong_rate:.1%} (baseline: {baseline_xiong:.1%})")

        # Chi-square test vs baseline
        expected = [total * baseline_ji, total * baseline_xiong, total * (1 - baseline_ji - baseline_xiong)]
        observed = [data['ji'], data['xiong'], data['zhong']]
        chi_sq = chi_square_test(observed, expected)
        print(f"    χ² vs baseline: {chi_sq:.2f}")

def main():
    print("=" * 60)
    print("承乘比應 Analysis - Traditional Yao Relationship Patterns")
    print("=" * 60)

    hexagrams = load_hexagram_data()
    print(f"\nAnalyzing {len(hexagrams)} hexagrams...\n")

    # 1. 承乘 Analysis
    cheng_results = analyze_cheng_relationships(hexagrams)
    print_analysis("1. 承乘關係 (Supporting/Riding Relationships)", cheng_results)

    # 2. 應 Analysis
    ying_results = analyze_ying_relationships(hexagrams)
    print_analysis("2. 應關係 (Corresponding Positions: 1-4, 2-5, 3-6)", ying_results)

    # 3. 比 Analysis
    bi_results = analyze_bi_relationships(hexagrams)
    print_analysis("3. 比關係 (Adjacent Relationships)", bi_results)

    # 4. 中正 Analysis
    zhong_zheng_results = analyze_zhong_zheng(hexagrams)
    print_analysis("4. 中正 (Center-Correctness Analysis)", zhong_zheng_results)

    # Summary
    print("\n" + "=" * 60)
    print("Summary: Key Findings")
    print("=" * 60)

    findings = []

    # Check 中正
    zz = zhong_zheng_results['zhong_zheng']
    if zz['total'] > 0:
        zz_ji = zz['ji'] / zz['total']
        if zz_ji > 0.45:
            findings.append(f"• 中正 (center + correct polarity) has high 吉率: {zz_ji:.1%}")

    # Check 正應
    zy = ying_results['zheng_ying']
    if zy['total'] > 0:
        zy_ji = zy['ji'] / zy['total']
        if zy_ji > 0.40:
            findings.append(f"• 正應 (correct correspondence) has 吉率: {zy_ji:.1%}")

    # Check 承
    ys = cheng_results['yin_supports_yang']
    if ys['total'] > 0:
        ys_ji = ys['ji'] / ys['total']
        if ys_ji > 0.40:
            findings.append(f"• 陰承陽 (yin supports yang) has 吉率: {ys_ji:.1%}")

    if findings:
        for f in findings:
            print(f)
    else:
        print("• No strongly significant patterns found")
        print("• Yao relationships have moderate but not dominant effect on 吉凶")

    # Save results
    results_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis', 'yao_relationships.json')
    os.makedirs(os.path.dirname(results_path), exist_ok=True)

    all_results = {
        '承乘': cheng_results,
        '應': ying_results,
        '比': bi_results,
        '中正': zhong_zheng_results
    }

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    main()
