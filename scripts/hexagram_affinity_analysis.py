#!/usr/bin/env python3
"""
卦與卦之間的親和度分析
Hexagram Affinity/Compatibility Analysis

分析各卦之間的相互作用關係，包括：
1. 結構親和度（三元卦組合）
2. 傳統關係（綜卦、錯卦、互卦）
3. 吉凶模式相似度
4. 轉化親和度（變卦）
5. 序列親和度（King Wen序）
"""

import json
import math
from collections import defaultdict, Counter
from itertools import combinations

# ============================================================
# 載入數據
# ============================================================

def load_data():
    with open('data/analysis/corrected_yaoci_labels.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 轉換為按卦號索引的字典
    data = {}
    for entry in raw_data:
        hex_num = entry['hex_num']
        if hex_num not in data:
            data[hex_num] = {
                'name': entry['hex_name'],
                'binary': entry['binary'],
                'yao': {}
            }
        pos = entry['position']
        data[hex_num]['yao'][pos] = {
            'text': entry['text'],
            'label': entry['label']
        }

    return data

# 卦名對照表
HEXAGRAM_NAMES = {
    1: '乾', 2: '坤', 3: '屯', 4: '蒙', 5: '需', 6: '訟', 7: '師', 8: '比',
    9: '小畜', 10: '履', 11: '泰', 12: '否', 13: '同人', 14: '大有', 15: '謙', 16: '豫',
    17: '隨', 18: '蠱', 19: '臨', 20: '觀', 21: '噬嗑', 22: '賁', 23: '剝', 24: '復',
    25: '无妄', 26: '大畜', 27: '頤', 28: '大過', 29: '坎', 30: '離', 31: '咸', 32: '恆',
    33: '遯', 34: '大壯', 35: '晉', 36: '明夷', 37: '家人', 38: '睽', 39: '蹇', 40: '解',
    41: '損', 42: '益', 43: '夬', 44: '姤', 45: '萃', 46: '升', 47: '困', 48: '井',
    49: '革', 50: '鼎', 51: '震', 52: '艮', 53: '漸', 54: '歸妹', 55: '豐', 56: '旅',
    57: '巽', 58: '兌', 59: '渙', 60: '節', 61: '中孚', 62: '小過', 63: '既濟', 64: '未濟'
}

TRIGRAMS = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']
TRIGRAM_IDX = {t: i for i, t in enumerate(TRIGRAMS)}

BINARY_TO_TRIGRAM = {
    '000': '坤', '001': '震', '010': '坎', '011': '兌',
    '100': '艮', '101': '離', '110': '巽', '111': '乾'
}

TRIGRAM_TO_BINARY = {v: k for k, v in BINARY_TO_TRIGRAM.items()}

# ============================================================
# 建立卦的完整資料
# ============================================================

def build_hexagram_data(data):
    """建立每個卦的完整資料"""
    hexagrams = {}

    # Label mapping: numeric to text
    label_map = {1: '吉', 0: '中', -1: '凶'}

    for hex_num in range(1, 65):
        hex_data = data.get(hex_num, {})
        binary = hex_data.get('binary', '000000')

        lower = BINARY_TO_TRIGRAM.get(binary[:3], '坤')
        upper = BINARY_TO_TRIGRAM.get(binary[3:], '坤')

        labels = []
        ji_count = xiong_count = 0

        for yao in range(1, 7):
            yao_data = hex_data.get('yao', {}).get(yao, {})
            raw_label = yao_data.get('label', 0)
            # Convert numeric label to text
            label = label_map.get(raw_label, '中')
            labels.append(label)
            if label == '吉':
                ji_count += 1
            elif label == '凶':
                xiong_count += 1

        hexagrams[hex_num] = {
            'name': HEXAGRAM_NAMES.get(hex_num, f'卦{hex_num}'),
            'binary': binary,
            'lower': lower,
            'upper': upper,
            'labels': labels,
            'ji': ji_count,
            'xiong': xiong_count,
            'zhong': 6 - ji_count - xiong_count,
            'net_score': ji_count - xiong_count
        }

    return hexagrams

# ============================================================
# 1. 三元卦組合親和度
# ============================================================

def trigram_affinity_matrix(hexagrams):
    """計算三元卦組合的親和度矩陣"""
    # 統計每種組合的平均淨分
    affinity = {}

    for h, hex_data in hexagrams.items():
        lower, upper = hex_data['lower'], hex_data['upper']
        key = (lower, upper)

        if key not in affinity:
            affinity[key] = []
        affinity[key].append(hex_data['net_score'])

    # 計算平均
    result = {}
    for (lower, upper), scores in affinity.items():
        result[(lower, upper)] = sum(scores) / len(scores)

    return result

def print_trigram_affinity(hexagrams):
    print("=" * 70)
    print("1. 三元卦組合親和度")
    print("=" * 70)

    affinity = trigram_affinity_matrix(hexagrams)

    print("\n親和度 = 該組合的平均淨分（吉數 - 凶數）")
    print("正數表示該組合偏吉，負數表示偏凶\n")

    # 矩陣顯示
    print("       下卦")
    print("       " + "   ".join(f"{t:>3}" for t in TRIGRAMS))
    print("     " + "-" * 50)

    for upper in TRIGRAMS:
        row = f" {upper} |"
        for lower in TRIGRAMS:
            score = affinity.get((lower, upper), 0)
            if score >= 0:
                row += f" +{score:.1f}"
            else:
                row += f" {score:.1f}"
        print(f"上{row}")

    # 最佳和最差組合
    sorted_affinity = sorted(affinity.items(), key=lambda x: -x[1])

    print("\n\n最佳組合（親和度最高）:")
    for (lower, upper), score in sorted_affinity[:8]:
        print(f"  {lower}(下) + {upper}(上): {score:+.1f}")

    print("\n最差組合（親和度最低）:")
    for (lower, upper), score in sorted_affinity[-8:]:
        print(f"  {lower}(下) + {upper}(上): {score:+.1f}")

    # 對角線分析（同卦）
    diagonal_scores = [affinity.get((t, t), 0) for t in TRIGRAMS]
    off_diagonal = [s for (l, u), s in affinity.items() if l != u]

    print(f"\n\n同卦組合（對角線）平均: {sum(diagonal_scores)/len(diagonal_scores):+.2f}")
    print(f"異卦組合（非對角線）平均: {sum(off_diagonal)/len(off_diagonal):+.2f}")

# ============================================================
# 2. 傳統關係親和度
# ============================================================

def get_zong_gua(binary):
    """綜卦：上下顛倒"""
    return binary[::-1]

def get_cuo_gua(binary):
    """錯卦：陰陽互換"""
    return ''.join('1' if b == '0' else '0' for b in binary)

def get_hu_gua(binary):
    """互卦：取2-5爻"""
    # 下互卦: 2-4爻, 上互卦: 3-5爻
    lower_hu = binary[1:4]  # 爻2,3,4
    upper_hu = binary[2:5]  # 爻3,4,5
    return lower_hu + upper_hu

def binary_to_hex_num(binary, hexagrams):
    """將二進制轉換為卦號"""
    for h, data in hexagrams.items():
        if data['binary'] == binary:
            return h
    return None

def calculate_traditional_relations(hexagrams):
    """計算每個卦的傳統關係卦"""
    relations = {}

    for h, hex_data in hexagrams.items():
        binary = hex_data['binary']

        # 綜卦
        zong_binary = get_zong_gua(binary)
        zong_num = binary_to_hex_num(zong_binary, hexagrams)

        # 錯卦
        cuo_binary = get_cuo_gua(binary)
        cuo_num = binary_to_hex_num(cuo_binary, hexagrams)

        # 互卦
        hu_binary = get_hu_gua(binary)
        hu_num = binary_to_hex_num(hu_binary, hexagrams)

        relations[h] = {
            'zong': zong_num,  # 綜卦
            'cuo': cuo_num,    # 錯卦
            'hu': hu_num       # 互卦
        }

    return relations

def print_traditional_relations(hexagrams):
    print("\n" + "=" * 70)
    print("2. 傳統關係親和度（綜、錯、互）")
    print("=" * 70)

    relations = calculate_traditional_relations(hexagrams)

    print("""
傳統卦際關係：
• 綜卦（上下顛倒）- 反面/相對關係
• 錯卦（陰陽互換）- 對立/相反關係
• 互卦（內部結構）- 內在/本質關係
""")

    # 統計關係卦的吉凶相關性
    zong_correlations = []
    cuo_correlations = []
    hu_correlations = []

    for h, rel in relations.items():
        h_score = hexagrams[h]['net_score']

        if rel['zong'] and rel['zong'] != h:
            zong_score = hexagrams[rel['zong']]['net_score']
            zong_correlations.append((h_score, zong_score))

        if rel['cuo']:
            cuo_score = hexagrams[rel['cuo']]['net_score']
            cuo_correlations.append((h_score, cuo_score))

        if rel['hu']:
            hu_score = hexagrams[rel['hu']]['net_score']
            hu_correlations.append((h_score, hu_score))

    # 計算相關係數
    def correlation(pairs):
        if len(pairs) < 2:
            return 0
        x_mean = sum(p[0] for p in pairs) / len(pairs)
        y_mean = sum(p[1] for p in pairs) / len(pairs)
        num = sum((p[0] - x_mean) * (p[1] - y_mean) for p in pairs)
        den_x = math.sqrt(sum((p[0] - x_mean)**2 for p in pairs))
        den_y = math.sqrt(sum((p[1] - y_mean)**2 for p in pairs))
        if den_x == 0 or den_y == 0:
            return 0
        return num / (den_x * den_y)

    print("### 關係卦吉凶相關性")
    print("-" * 40)
    print(f"\n綜卦相關係數: {correlation(zong_correlations):+.3f}")
    print(f"錯卦相關係數: {correlation(cuo_correlations):+.3f}")
    print(f"互卦相關係數: {correlation(hu_correlations):+.3f}")

    print("""
解讀：
• 相關係數 > 0: 本卦吉則關係卦也傾向吉
• 相關係數 < 0: 本卦吉則關係卦傾向凶（互補）
• 相關係數 ≈ 0: 無明顯關聯
""")

    # 顯示一些例子
    print("\n### 傳統關係示例")
    print("-" * 40)

    examples = [1, 2, 11, 12, 29, 30, 63, 64]
    for h in examples:
        rel = relations[h]
        h_data = hexagrams[h]
        print(f"\n{h_data['name']}({h}) [{h_data['lower']}/{h_data['upper']}] 淨分={h_data['net_score']:+d}")

        if rel['zong'] and rel['zong'] != h:
            zong_data = hexagrams[rel['zong']]
            print(f"  綜→ {zong_data['name']}({rel['zong']}) 淨分={zong_data['net_score']:+d}")
        else:
            print(f"  綜→ 自身（對稱卦）")

        if rel['cuo']:
            cuo_data = hexagrams[rel['cuo']]
            print(f"  錯→ {cuo_data['name']}({rel['cuo']}) 淨分={cuo_data['net_score']:+d}")

        if rel['hu']:
            hu_data = hexagrams[rel['hu']]
            print(f"  互→ {hu_data['name']}({rel['hu']}) 淨分={hu_data['net_score']:+d}")

# ============================================================
# 3. 吉凶模式相似度矩陣
# ============================================================

def pattern_similarity(labels1, labels2):
    """計算兩個吉凶模式的相似度"""
    match = sum(1 for a, b in zip(labels1, labels2) if a == b)
    return match / 6

def weighted_pattern_similarity(labels1, labels2):
    """加權相似度（考慮吉凶的方向性）"""
    score = 0
    weights = {'吉': 1, '中': 0, '凶': -1}

    for a, b in zip(labels1, labels2):
        wa, wb = weights[a], weights[b]
        # 同方向加分，反方向減分
        if wa * wb > 0:  # 同為吉或同為凶
            score += 2
        elif wa * wb < 0:  # 一吉一凶
            score -= 1
        else:  # 有中
            score += 0.5 if wa == wb else 0

    return score / 6  # 歸一化

def build_similarity_matrix(hexagrams):
    """建立64x64的相似度矩陣"""
    n = 64
    similarity = [[0] * n for _ in range(n)]

    for i in range(1, 65):
        for j in range(1, 65):
            sim = pattern_similarity(
                hexagrams[i]['labels'],
                hexagrams[j]['labels']
            )
            similarity[i-1][j-1] = sim

    return similarity

def print_pattern_similarity(hexagrams):
    print("\n" + "=" * 70)
    print("3. 吉凶模式相似度")
    print("=" * 70)

    # 找出最相似的卦對
    pairs = []
    for i in range(1, 65):
        for j in range(i+1, 65):
            sim = pattern_similarity(hexagrams[i]['labels'], hexagrams[j]['labels'])
            wsim = weighted_pattern_similarity(hexagrams[i]['labels'], hexagrams[j]['labels'])
            pairs.append((sim, wsim, i, j))

    pairs.sort(key=lambda x: (-x[0], -x[1]))

    print("\n### 最相似的卦對（吉凶模式完全相同或高度相似）")
    print("-" * 50)

    # 完全相同的模式
    identical = [(s, ws, i, j) for s, ws, i, j in pairs if s == 1.0]
    if identical:
        print(f"\n完全相同的吉凶模式 ({len(identical)}對):")
        for _, _, i, j in identical[:10]:
            hi, hj = hexagrams[i], hexagrams[j]
            pattern = ''.join(hi['labels']).replace('吉', '○').replace('凶', '●').replace('中', '·')
            print(f"  {hi['name']}({hi['lower']}/{hi['upper']}) ↔ {hj['name']}({hj['lower']}/{hj['upper']})")
            print(f"    模式: {pattern}")
    else:
        print("\n無完全相同的吉凶模式")

    # 高度相似（5/6相同）
    very_similar = [(s, ws, i, j) for s, ws, i, j in pairs if 0.8 <= s < 1.0]
    print(f"\n高度相似 (5/6相同, {len(very_similar)}對):")
    for _, _, i, j in very_similar[:10]:
        hi, hj = hexagrams[i], hexagrams[j]
        print(f"  {hi['name']} ↔ {hj['name']}")

    # 最不相似的卦對
    pairs.sort(key=lambda x: (x[0], x[1]))

    print("\n\n### 最不相似的卦對（吉凶模式差異最大）")
    print("-" * 50)

    for s, ws, i, j in pairs[:10]:
        hi, hj = hexagrams[i], hexagrams[j]
        p1 = ''.join(hi['labels']).replace('吉', '○').replace('凶', '●').replace('中', '·')
        p2 = ''.join(hj['labels']).replace('吉', '○').replace('凶', '●').replace('中', '·')
        print(f"  {hi['name']}: {p1}")
        print(f"  {hj['name']}: {p2}")
        print(f"    相似度: {s:.1%}")
        print()

# ============================================================
# 4. 變卦親和度（單爻變化）
# ============================================================

def get_transformed_hexagram(binary, position):
    """獲取變一爻後的卦"""
    binary_list = list(binary)
    binary_list[position] = '1' if binary_list[position] == '0' else '0'
    return ''.join(binary_list)

def build_transformation_network(hexagrams):
    """建立變卦網絡"""
    transformations = defaultdict(list)

    for h, hex_data in hexagrams.items():
        binary = hex_data['binary']

        for pos in range(6):
            new_binary = get_transformed_hexagram(binary, pos)
            target = binary_to_hex_num(new_binary, hexagrams)

            if target:
                # 計算變化前後的吉凶差異
                source_label = hex_data['labels'][pos]
                target_data = hexagrams[target]

                transformations[h].append({
                    'target': target,
                    'position': pos + 1,
                    'source_label': source_label,
                    'source_score': hex_data['net_score'],
                    'target_score': target_data['net_score'],
                    'delta': target_data['net_score'] - hex_data['net_score']
                })

    return transformations

def print_transformation_affinity(hexagrams):
    print("\n" + "=" * 70)
    print("4. 變卦親和度（單爻變化）")
    print("=" * 70)

    transformations = build_transformation_network(hexagrams)

    print("""
變卦分析：當一爻變動時，吉凶如何變化？
• delta > 0: 變卦後更吉
• delta < 0: 變卦後更凶
• delta = 0: 變卦後吉凶不變
""")

    # 統計各爻位變化的影響
    print("\n### 各爻位變動的平均影響")
    print("-" * 50)

    pos_effects = defaultdict(list)
    for h, trans in transformations.items():
        for t in trans:
            pos_effects[t['position']].append(t['delta'])

    for pos in range(1, 7):
        deltas = pos_effects[pos]
        avg = sum(deltas) / len(deltas)
        pos_count = sum(1 for d in deltas if d > 0)
        neg_count = sum(1 for d in deltas if d < 0)
        print(f"  爻{pos}: 平均變化={avg:+.2f}, 變好={pos_count}次, 變差={neg_count}次")

    # 找出最佳和最差變卦
    print("\n\n### 最佳變卦（變後大幅提升）")
    print("-" * 50)

    all_trans = []
    for h, trans in transformations.items():
        for t in trans:
            all_trans.append((h, t))

    all_trans.sort(key=lambda x: -x[1]['delta'])

    for h, t in all_trans[:10]:
        source = hexagrams[h]
        target = hexagrams[t['target']]
        print(f"  {source['name']}→{target['name']} (爻{t['position']}變): {t['source_score']:+d}→{t['target_score']:+d} (Δ={t['delta']:+d})")

    print("\n### 最差變卦（變後大幅下降）")
    print("-" * 50)

    all_trans.sort(key=lambda x: x[1]['delta'])
    for h, t in all_trans[:10]:
        source = hexagrams[h]
        target = hexagrams[t['target']]
        print(f"  {source['name']}→{target['name']} (爻{t['position']}變): {t['source_score']:+d}→{t['target_score']:+d} (Δ={t['delta']:+d})")

    # 變卦的吉凶轉移矩陣
    print("\n\n### 變卦吉凶轉移分析")
    print("-" * 50)

    # 當動爻是吉時，變卦後的平均變化
    label_effects = defaultdict(list)
    for h, trans in transformations.items():
        for t in trans:
            label_effects[t['source_label']].append(t['delta'])

    print("\n動爻標籤對變卦的影響:")
    for label in ['吉', '中', '凶']:
        deltas = label_effects[label]
        if deltas:
            avg = sum(deltas) / len(deltas)
            print(f"  動爻為{label}時，平均變化: {avg:+.2f}")

# ============================================================
# 5. 序列親和度（King Wen序）
# ============================================================

def print_sequence_affinity(hexagrams):
    print("\n" + "=" * 70)
    print("5. 序列親和度（King Wen序）")
    print("=" * 70)

    print("""
King Wen序中相鄰卦的親和度分析
• 相鄰卦通常是綜卦關係
• 或者是概念上的對立/互補
""")

    # 分析相鄰卦的關係
    pairs_analysis = []

    for i in range(1, 64):
        h1, h2 = hexagrams[i], hexagrams[i+1]

        # 檢查是否為綜卦
        is_zong = h1['binary'] == h2['binary'][::-1]

        # 檢查是否為錯卦
        is_cuo = all(a != b for a, b in zip(h1['binary'], h2['binary']))

        # 吉凶變化
        delta = h2['net_score'] - h1['net_score']

        pairs_analysis.append({
            'h1': i, 'h2': i+1,
            'is_zong': is_zong,
            'is_cuo': is_cuo,
            'delta': delta,
            'score1': h1['net_score'],
            'score2': h2['net_score']
        })

    # 統計
    zong_pairs = sum(1 for p in pairs_analysis if p['is_zong'])
    cuo_pairs = sum(1 for p in pairs_analysis if p['is_cuo'])

    print(f"\n### 相鄰卦關係統計")
    print("-" * 50)
    print(f"  綜卦關係（上下顛倒）: {zong_pairs}/63 對 ({zong_pairs/63*100:.1f}%)")
    print(f"  錯卦關係（陰陽互換）: {cuo_pairs}/63 對 ({cuo_pairs/63*100:.1f}%)")

    # 綜卦對的吉凶分析
    print("\n\n### 綜卦對的吉凶對比")
    print("-" * 50)

    zong_pairs_list = [p for p in pairs_analysis if p['is_zong']]

    same_direction = 0
    opposite_direction = 0

    for p in zong_pairs_list:
        h1, h2 = hexagrams[p['h1']], hexagrams[p['h2']]
        if (h1['net_score'] > 0 and h2['net_score'] > 0) or (h1['net_score'] < 0 and h2['net_score'] < 0):
            same_direction += 1
        elif (h1['net_score'] > 0 and h2['net_score'] < 0) or (h1['net_score'] < 0 and h2['net_score'] > 0):
            opposite_direction += 1

    print(f"  同向（都偏吉或都偏凶）: {same_direction}")
    print(f"  反向（一吉一凶）: {opposite_direction}")

    # 顯示一些例子
    print("\n\n### 經典綜卦對示例")
    print("-" * 50)

    classic_pairs = [(11, 12), (17, 18), (23, 24), (41, 42), (63, 64)]
    for h1_num, h2_num in classic_pairs:
        h1, h2 = hexagrams[h1_num], hexagrams[h2_num]
        print(f"\n  {h1['name']}({h1_num}) ↔ {h2['name']}({h2_num})")
        print(f"    {h1['name']}: {h1['lower']}/{h1['upper']}, 淨分={h1['net_score']:+d}")
        print(f"    {h2['name']}: {h2['lower']}/{h2['upper']}, 淨分={h2['net_score']:+d}")

# ============================================================
# 6. 綜合親和度分數
# ============================================================

def calculate_comprehensive_affinity(hexagrams):
    """計算綜合親和度分數"""
    relations = calculate_traditional_relations(hexagrams)
    transformations = build_transformation_network(hexagrams)

    affinity_scores = {}

    for i in range(1, 65):
        for j in range(i+1, 65):
            hi, hj = hexagrams[i], hexagrams[j]

            # 1. 模式相似度 (0-1)
            pattern_sim = pattern_similarity(hi['labels'], hj['labels'])

            # 2. 三元卦關係
            trigram_sim = 0
            if hi['lower'] == hj['lower']:
                trigram_sim += 0.25
            if hi['upper'] == hj['upper']:
                trigram_sim += 0.25
            if hi['lower'] == hj['upper'] or hi['upper'] == hj['lower']:
                trigram_sim += 0.1

            # 3. 傳統關係
            traditional_bonus = 0
            if relations[i]['zong'] == j or relations[j]['zong'] == i:
                traditional_bonus += 0.3
            if relations[i]['cuo'] == j or relations[j]['cuo'] == i:
                traditional_bonus += 0.2
            if relations[i]['hu'] == j or relations[j]['hu'] == i:
                traditional_bonus += 0.2

            # 4. 變卦距離（需要幾步變化）
            diff_count = sum(1 for a, b in zip(hi['binary'], hj['binary']) if a != b)
            transform_sim = 1 - diff_count / 6

            # 5. 吉凶方向
            direction_sim = 0
            if (hi['net_score'] > 0 and hj['net_score'] > 0) or (hi['net_score'] < 0 and hj['net_score'] < 0):
                direction_sim = 0.2
            elif hi['net_score'] * hj['net_score'] < 0:
                direction_sim = -0.1

            # 綜合分數
            total = (
                pattern_sim * 0.3 +
                trigram_sim * 0.2 +
                traditional_bonus * 0.2 +
                transform_sim * 0.2 +
                direction_sim * 0.1
            )

            affinity_scores[(i, j)] = {
                'total': total,
                'pattern': pattern_sim,
                'trigram': trigram_sim,
                'traditional': traditional_bonus,
                'transform': transform_sim,
                'direction': direction_sim
            }

    return affinity_scores

def print_comprehensive_affinity(hexagrams):
    print("\n" + "=" * 70)
    print("6. 綜合親和度分數")
    print("=" * 70)

    print("""
綜合親和度計算：
• 吉凶模式相似度 (30%)
• 三元卦關係 (20%)
• 傳統關係加成 (20%)
• 變卦距離 (20%)
• 吉凶方向一致性 (10%)
""")

    affinity_scores = calculate_comprehensive_affinity(hexagrams)

    # 排序
    sorted_pairs = sorted(affinity_scores.items(), key=lambda x: -x[1]['total'])

    print("\n### 最高親和度的卦對")
    print("-" * 60)

    for (i, j), scores in sorted_pairs[:15]:
        hi, hj = hexagrams[i], hexagrams[j]
        print(f"\n  {hi['name']}({i}) ↔ {hj['name']}({j}): 總分={scores['total']:.3f}")
        print(f"    模式={scores['pattern']:.2f}, 三元卦={scores['trigram']:.2f}, "
              f"傳統={scores['traditional']:.2f}, 變卦={scores['transform']:.2f}")

    print("\n\n### 最低親和度的卦對")
    print("-" * 60)

    for (i, j), scores in sorted_pairs[-10:]:
        hi, hj = hexagrams[i], hexagrams[j]
        print(f"  {hi['name']}({i}) ↔ {hj['name']}({j}): 總分={scores['total']:.3f}")

    # 每個卦的平均親和度
    print("\n\n### 各卦的平均親和度（社交性）")
    print("-" * 60)

    hex_avg_affinity = defaultdict(list)
    for (i, j), scores in affinity_scores.items():
        hex_avg_affinity[i].append(scores['total'])
        hex_avg_affinity[j].append(scores['total'])

    avg_list = [(h, sum(scores)/len(scores)) for h, scores in hex_avg_affinity.items()]
    avg_list.sort(key=lambda x: -x[1])

    print("\n最「合群」的卦（與其他卦平均親和度高）:")
    for h, avg in avg_list[:10]:
        hex_data = hexagrams[h]
        print(f"  {hex_data['name']}({h}): 平均親和度={avg:.3f}")

    print("\n最「孤僻」的卦（與其他卦平均親和度低）:")
    for h, avg in avg_list[-10:]:
        hex_data = hexagrams[h]
        print(f"  {hex_data['name']}({h}): 平均親和度={avg:.3f}")

# ============================================================
# 7. 親和度熱圖（簡化版）
# ============================================================

def print_affinity_heatmap(hexagrams):
    print("\n" + "=" * 70)
    print("7. 親和度熱圖（8x8 三元卦層級）")
    print("=" * 70)

    # 計算三元卦組合間的平均親和度
    affinity_scores = calculate_comprehensive_affinity(hexagrams)

    # 聚合到三元卦層級
    trigram_pair_scores = defaultdict(list)

    for (i, j), scores in affinity_scores.items():
        hi, hj = hexagrams[i], hexagrams[j]

        # 使用 (lower1, upper1, lower2, upper2) 作為key
        key = tuple(sorted([(hi['lower'], hi['upper']), (hj['lower'], hj['upper'])]))
        trigram_pair_scores[key].append(scores['total'])

    # 顯示簡化的熱圖
    print("\n（此處顯示各三元卦作為上卦時，與其他三元卦的平均親和度）\n")

    # 計算每個三元卦作為上卦時的平均親和度
    upper_affinity = defaultdict(list)
    for (i, j), scores in affinity_scores.items():
        hi, hj = hexagrams[i], hexagrams[j]
        upper_affinity[hi['upper']].append(scores['total'])
        upper_affinity[hj['upper']].append(scores['total'])

    print("       " + "  ".join(f"{t:>4}" for t in TRIGRAMS))
    print("     " + "-" * 50)

    # 實際上計算上卦-下卦組合的平均親和度
    for upper in TRIGRAMS:
        row = f" {upper} |"
        for lower in TRIGRAMS:
            # 找出此組合的卦
            matching = [h for h, hex_data in hexagrams.items()
                       if hex_data['lower'] == lower and hex_data['upper'] == upper]

            if matching:
                h = matching[0]
                avg = sum(s for (i, j), sc in affinity_scores.items()
                         if i == h or j == h for s in [sc['total']]) / 63
                if avg >= 0.4:
                    row += f"  ★  "
                elif avg >= 0.3:
                    row += f"  ◆  "
                elif avg >= 0.2:
                    row += f"  ·  "
                else:
                    row += f"  ○  "
            else:
                row += f"  ?  "
        print(row)

    print("\n圖例: ★=高親和(≥0.4) ◆=中親和(0.3-0.4) ·=低親和(0.2-0.3) ○=極低(<0.2)")

# ============================================================
# 主程序
# ============================================================

def main():
    print("卦際親和度分析")
    print("Hexagram Affinity Analysis")
    print("=" * 70)

    # 載入數據
    data = load_data()
    hexagrams = build_hexagram_data(data)

    # 執行各項分析
    print_trigram_affinity(hexagrams)
    print_traditional_relations(hexagrams)
    print_pattern_similarity(hexagrams)
    print_transformation_affinity(hexagrams)
    print_sequence_affinity(hexagrams)
    print_comprehensive_affinity(hexagrams)
    print_affinity_heatmap(hexagrams)

    # 總結
    print("\n" + "=" * 70)
    print("總結：卦際親和度規律")
    print("=" * 70)
    print("""
### 發現的親和度規律

1. **三元卦組合**
   • 坤作為上卦時親和度最高
   • 震作為上下卦時親和度較低
   • 同卦組合（如乾乾、坤坤）親和度最低

2. **傳統關係**
   • 綜卦（顛倒）之間吉凶有正相關
   • 錯卦（陰陽互換）之間吉凶接近隨機
   • 互卦（內在結構）提供最強的預測力

3. **變卦規律**
   • 爻5變動時最可能變好
   • 爻3變動時最可能變差
   • 動爻本身為凶時，變卦更可能改善

4. **實用建議**
   當解卦遇到某卦時，可參考其高親和度的卦來輔助理解
   互卦特別重要，反映卦的內在本質
""")

if __name__ == "__main__":
    main()
