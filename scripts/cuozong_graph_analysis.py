#!/usr/bin/env python3
"""
錯綜卦與圖論分析

分析錯卦(complement)和綜卦(inverse)關係與我們的圖論發現(吸引子/排斥子)的結合
"""

import json
import os

# Get project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

def load_data():
    """Load hexagram structure and yaoci data"""
    with open(os.path.join(project_root, 'data/structure/hexagrams_structure.json'), 'r') as f:
        structure = json.load(f)

    with open(os.path.join(project_root, 'data/analysis/corrected_yaoci_labels.json'), 'r') as f:
        yaoci = json.load(f)

    return structure, yaoci

def calculate_hexagram_fortune(yaoci_data, hex_num):
    """Calculate fortune rate for a hexagram"""
    ji_count = 0
    total = 0
    for yao in yaoci_data:
        if yao['hex_num'] == hex_num:
            total += 1
            # Label: 1 = 吉, 0 = 中, -1 = 凶
            if yao['label'] == 1:
                ji_count += 1
    return ji_count / total if total > 0 else 0

def analyze_cuozong_relationships(structure, yaoci):
    """Analyze 錯綜 relationships with fortune rates"""

    results = {
        'summary': {},
        'pairs': [],
        'patterns': {}
    }

    # Calculate fortune rate for each hexagram
    hex_fortune = {}
    for hex_num in range(1, 65):
        hex_fortune[hex_num] = calculate_hexagram_fortune(yaoci, hex_num)

    # Analyze each hexagram
    for key, hex_data in structure.items():
        hex_num = int(key)
        name = hex_data['name']
        inverse_num = hex_data['inverse_hexagram']
        complement_num = hex_data['complement_hexagram']
        is_symmetric = hex_data.get('is_symmetric', False)

        own_fortune = hex_fortune[hex_num]
        inverse_fortune = hex_fortune[inverse_num] if inverse_num else None
        complement_fortune = hex_fortune[complement_num] if complement_num else None

        # Only process each pair once (use smaller number as key)
        if hex_num <= inverse_num:
            pair_info = {
                'hex1': hex_num,
                'hex1_name': name,
                'hex1_fortune': own_fortune,
                'inverse_num': inverse_num,
                'inverse_name': structure[str(inverse_num)]['name'] if inverse_num else None,
                'inverse_fortune': inverse_fortune,
                'complement_num': complement_num,
                'complement_name': structure[str(complement_num)]['name'] if complement_num else None,
                'complement_fortune': complement_fortune,
                'is_symmetric': is_symmetric,
                'inverse_diff': abs(own_fortune - inverse_fortune) if inverse_fortune is not None else None,
                'complement_diff': abs(own_fortune - complement_fortune) if complement_fortune is not None else None
            }
            results['pairs'].append(pair_info)

    # Analyze patterns
    # 1. Do 綜卦 pairs have similar fortune?
    inverse_diffs = [p['inverse_diff'] for p in results['pairs'] if p['inverse_diff'] is not None]
    avg_inverse_diff = sum(inverse_diffs) / len(inverse_diffs) if inverse_diffs else 0

    # 2. Do 錯卦 pairs have opposite fortune?
    complement_diffs = [p['complement_diff'] for p in results['pairs'] if p['complement_diff'] is not None]
    avg_complement_diff = sum(complement_diffs) / len(complement_diffs) if complement_diffs else 0

    # 3. Find pairs with most similar fortune (綜卦)
    similar_pairs = sorted([p for p in results['pairs'] if p['inverse_diff'] is not None],
                          key=lambda x: x['inverse_diff'])[:10]

    # 4. Find pairs with most different fortune (綜卦)
    different_pairs = sorted([p for p in results['pairs'] if p['inverse_diff'] is not None],
                            key=lambda x: x['inverse_diff'], reverse=True)[:10]

    results['summary'] = {
        'avg_inverse_diff': avg_inverse_diff,
        'avg_complement_diff': avg_complement_diff,
        'most_similar_inverse': similar_pairs[:5],
        'most_different_inverse': different_pairs[:5]
    }

    return results

def analyze_attractor_repeller_cuozong(structure, yaoci):
    """Analyze how 錯綜 relationships connect with attractor/repeller classification"""

    # Our previously identified attractors and repellers
    attractors = ['謙', '臨', '需']  # Stay hexagrams
    repellers = ['觀', '恆', '旅']    # Leave hexagrams
    traps = ['乾', '坎', '既濟']      # Easy in, hard out

    hex_name_to_num = {structure[k]['name']: int(k) for k in structure}

    findings = []

    for name in attractors + repellers + traps:
        hex_num = hex_name_to_num.get(name)
        if hex_num is None:
            continue

        hex_data = structure[str(hex_num)]
        inverse_num = hex_data['inverse_hexagram']
        complement_num = hex_data['complement_hexagram']

        inverse_name = structure[str(inverse_num)]['name'] if inverse_num else None
        complement_name = structure[str(complement_num)]['name'] if complement_num else None

        category = 'attractor' if name in attractors else ('repeller' if name in repellers else 'trap')

        # Check if inverse/complement is in opposite category
        inverse_cat = None
        if inverse_name in attractors:
            inverse_cat = 'attractor'
        elif inverse_name in repellers:
            inverse_cat = 'repeller'
        elif inverse_name in traps:
            inverse_cat = 'trap'

        complement_cat = None
        if complement_name in attractors:
            complement_cat = 'attractor'
        elif complement_name in repellers:
            complement_cat = 'repeller'
        elif complement_name in traps:
            complement_cat = 'trap'

        findings.append({
            'name': name,
            'category': category,
            'inverse': inverse_name,
            'inverse_category': inverse_cat,
            'complement': complement_name,
            'complement_category': complement_cat
        })

    return findings

def analyze_nuclear_hexagram_effect(structure, yaoci):
    """Analyze how 互卦 relates to graph theory findings"""

    # Calculate fortune for each hexagram
    hex_fortune = {}
    for hex_num in range(1, 65):
        hex_fortune[hex_num] = calculate_hexagram_fortune(yaoci, hex_num)

    # Analyze correlation between hexagram and nuclear hexagram fortune
    correlations = []

    for key, hex_data in structure.items():
        hex_num = int(key)
        name = hex_data['name']
        own_fortune = hex_fortune[hex_num]

        # Get nuclear (互) hexagram
        nuclear_lower = hex_data['nuclear_lower_trigram']['binary']
        nuclear_upper = hex_data['nuclear_upper_trigram']['binary']
        nuclear_binary = nuclear_lower + nuclear_upper

        # Find nuclear hexagram by binary
        nuclear_num = None
        for k, v in structure.items():
            if v['binary'] == nuclear_binary:
                nuclear_num = int(k)
                break

        if nuclear_num:
            nuclear_fortune = hex_fortune[nuclear_num]
            correlations.append({
                'hex_num': hex_num,
                'hex_name': name,
                'hex_fortune': own_fortune,
                'nuclear_num': nuclear_num,
                'nuclear_name': structure[str(nuclear_num)]['name'],
                'nuclear_fortune': nuclear_fortune,
                'diff': abs(own_fortune - nuclear_fortune)
            })

    # Calculate average difference
    avg_diff = sum(c['diff'] for c in correlations) / len(correlations) if correlations else 0

    # Find hexagrams whose fortune differs greatly from nuclear
    large_diff = sorted(correlations, key=lambda x: x['diff'], reverse=True)[:10]
    small_diff = sorted(correlations, key=lambda x: x['diff'])[:10]

    return {
        'avg_nuclear_diff': avg_diff,
        'large_diff_from_nuclear': large_diff[:5],
        'small_diff_from_nuclear': small_diff[:5],
        'all_correlations': correlations
    }

def main():
    print("="*60)
    print("錯綜卦與圖論分析")
    print("="*60)

    structure, yaoci = load_data()

    # Analysis 1: 錯綜 fortune relationships
    print("\n## 1. 錯綜卦吉凶相關性分析")
    print("-"*40)

    cuozong_results = analyze_cuozong_relationships(structure, yaoci)

    print(f"\n綜卦(上下顛倒)吉率平均差異: {cuozong_results['summary']['avg_inverse_diff']:.1%}")
    print(f"錯卦(陰陽全反)吉率平均差異: {cuozong_results['summary']['avg_complement_diff']:.1%}")

    print("\n### 綜卦吉率最相似的5對：")
    for p in cuozong_results['summary']['most_similar_inverse']:
        print(f"  {p['hex1_name']}({p['hex1_fortune']:.0%}) ↔ {p['inverse_name']}({p['inverse_fortune']:.0%}) 差異:{p['inverse_diff']:.0%}")

    print("\n### 綜卦吉率差異最大的5對：")
    for p in cuozong_results['summary']['most_different_inverse']:
        print(f"  {p['hex1_name']}({p['hex1_fortune']:.0%}) ↔ {p['inverse_name']}({p['inverse_fortune']:.0%}) 差異:{p['inverse_diff']:.0%}")

    # Analysis 2: Attractor/Repeller and 錯綜 relationships
    print("\n## 2. 吸引子/排斥子的錯綜關係")
    print("-"*40)

    attractor_findings = analyze_attractor_repeller_cuozong(structure, yaoci)

    for f in attractor_findings:
        print(f"\n{f['name']} ({f['category']}):")
        print(f"  綜卦: {f['inverse']} ({f['inverse_category'] or '一般'})")
        print(f"  錯卦: {f['complement']} ({f['complement_category'] or '一般'})")

    # Analysis 3: Nuclear hexagram analysis
    print("\n## 3. 互卦影響力分析")
    print("-"*40)

    nuclear_results = analyze_nuclear_hexagram_effect(structure, yaoci)

    print(f"\n互卦吉率與本卦平均差異: {nuclear_results['avg_nuclear_diff']:.1%}")

    print("\n### 與互卦差異最大的5卦（互卦影響力低）：")
    for c in nuclear_results['large_diff_from_nuclear']:
        print(f"  {c['hex_name']}({c['hex_fortune']:.0%}) 互卦:{c['nuclear_name']}({c['nuclear_fortune']:.0%}) 差異:{c['diff']:.0%}")

    print("\n### 與互卦最相似的5卦（互卦影響力高）：")
    for c in nuclear_results['small_diff_from_nuclear']:
        print(f"  {c['hex_name']}({c['hex_fortune']:.0%}) 互卦:{c['nuclear_name']}({c['nuclear_fortune']:.0%}) 差異:{c['diff']:.0%}")

    # Summary insights
    print("\n" + "="*60)
    print("## 關鍵發現")
    print("="*60)

    print("""
1. 綜卦（上下顛倒）關係：
   - 綜卦是同一事物的不同視角
   - 吉率相似 = 本質相同，只是立場不同
   - 吉率差異大 = 視角轉換帶來不同命運

2. 錯卦（陰陽全反）關係：
   - 錯卦是完全相反的狀態
   - 理論上應該吉凶相反
   - 但實際差異可能因結構複雜而不完全對稱

3. 互卦（內部結構）關係：
   - 互卦代表事物的內在本質
   - 與本卦吉率相似 = 表裡如一
   - 與本卦吉率差異大 = 表裡不一，需要注意
""")

    return cuozong_results, nuclear_results

if __name__ == '__main__':
    main()
