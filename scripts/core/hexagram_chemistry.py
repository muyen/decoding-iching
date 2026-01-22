#!/usr/bin/env python3
"""
卦的化學反應模型
Hexagram Chemistry Model

將每個卦視為具有三態（吉/中/凶）的「物質」
當兩卦相遇時產生「化學反應」，決定結果

類比：
- 每個卦 = 一種元素/化合物
- 三態 = 固態/液態/氣態（吉/中/凶）
- 組合 = 化學反應
- 結果 = 反應產物
"""

import json
import math
from collections import defaultdict

# ============================================================
# 載入數據
# ============================================================

def load_data():
    with open('data/analysis/corrected_yaoci_labels.json', 'r', encoding='utf-8') as f:
        return json.load(f)

TRIGRAMS = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']
TRIGRAM_IDX = {t: i for i, t in enumerate(TRIGRAMS)}

BINARY_TO_TRIGRAM = {
    '000': '坤', '001': '震', '010': '坎', '011': '兌',
    '100': '艮', '101': '離', '110': '巽', '111': '乾'
}

LABEL_MAP = {1: '吉', 0: '中', -1: '凶'}

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

# ============================================================
# 建立三元卦的「元素屬性」
# ============================================================

def build_trigram_properties(raw_data):
    """計算每個三元卦的基本屬性（類似元素週期表）"""

    # 統計每個三元卦在不同位置的吉凶分布
    trigram_stats = defaultdict(lambda: {
        'inner': {'吉': 0, '中': 0, '凶': 0, 'total': 0},
        'outer': {'吉': 0, '中': 0, '凶': 0, 'total': 0},
        'all': {'吉': 0, '中': 0, '凶': 0, 'total': 0}
    })

    for entry in raw_data:
        pos = entry['position']
        binary = entry['binary']
        label = LABEL_MAP.get(entry['label'], '中')

        lower = BINARY_TO_TRIGRAM[binary[:3]]
        upper = BINARY_TO_TRIGRAM[binary[3:]]

        if pos <= 3:
            trigram_stats[lower]['inner'][label] += 1
            trigram_stats[lower]['inner']['total'] += 1
            trigram_stats[lower]['all'][label] += 1
            trigram_stats[lower]['all']['total'] += 1
        else:
            trigram_stats[upper]['outer'][label] += 1
            trigram_stats[upper]['outer']['total'] += 1
            trigram_stats[upper]['all'][label] += 1
            trigram_stats[upper]['all']['total'] += 1

    # 計算每個三元卦的「元素屬性」
    properties = {}

    for trigram in TRIGRAMS:
        stats = trigram_stats[trigram]

        # 計算吉/凶傾向（類似電負性）
        all_total = stats['all']['total']
        if all_total > 0:
            ji_tendency = stats['all']['吉'] / all_total
            xiong_tendency = stats['all']['凶'] / all_total
            stability = stats['all']['中'] / all_total  # 穩定性（中的比例）
        else:
            ji_tendency = xiong_tendency = stability = 0

        # 計算內外差異（類似氧化態）
        inner_total = stats['inner']['total']
        outer_total = stats['outer']['total']

        inner_ji = stats['inner']['吉'] / inner_total if inner_total > 0 else 0
        outer_ji = stats['outer']['吉'] / outer_total if outer_total > 0 else 0
        inner_outer_diff = outer_ji - inner_ji  # 正=外卦更吉

        properties[trigram] = {
            'ji_tendency': ji_tendency,      # 吉傾向（0-1）
            'xiong_tendency': xiong_tendency, # 凶傾向（0-1）
            'stability': stability,           # 穩定性（0-1）
            'polarity': inner_outer_diff,    # 極性（內外差異）
            'net_charge': ji_tendency - xiong_tendency,  # 淨電荷（吉-凶）
            'stats': stats
        }

    return properties

# ============================================================
# 建立卦的「分子結構」
# ============================================================

def build_hexagram_molecule(raw_data):
    """將每個卦建模為由兩個三元卦組成的「分子」"""

    # 按卦分組
    hexagram_data = defaultdict(lambda: {'labels': [], 'binary': None})

    for entry in raw_data:
        hex_num = entry['hex_num']
        hexagram_data[hex_num]['labels'].append((entry['position'], LABEL_MAP.get(entry['label'], '中')))
        hexagram_data[hex_num]['binary'] = entry['binary']

    molecules = {}

    for hex_num, data in hexagram_data.items():
        binary = data['binary']
        if not binary:
            continue

        lower = BINARY_TO_TRIGRAM[binary[:3]]
        upper = BINARY_TO_TRIGRAM[binary[3:]]

        # 計算分子狀態
        labels = [l for _, l in sorted(data['labels'])]
        ji_count = labels.count('吉')
        xiong_count = labels.count('凶')
        zhong_count = labels.count('中')

        # 主要狀態（類似物質的相態）
        if ji_count > xiong_count and ji_count > zhong_count:
            primary_state = '吉態'
        elif xiong_count > ji_count and xiong_count > zhong_count:
            primary_state = '凶態'
        else:
            primary_state = '中態'

        # 分子穩定性
        stability = zhong_count / 6

        # 反應活性（極端值越多越活潑）
        reactivity = (ji_count + xiong_count) / 6

        molecules[hex_num] = {
            'name': HEXAGRAM_NAMES.get(hex_num, f'卦{hex_num}'),
            'lower': lower,
            'upper': upper,
            'binary': binary,
            'labels': labels,
            'ji_count': ji_count,
            'xiong_count': xiong_count,
            'zhong_count': zhong_count,
            'net_score': ji_count - xiong_count,
            'primary_state': primary_state,
            'stability': stability,
            'reactivity': reactivity
        }

    return molecules

# ============================================================
# 化學反應規則
# ============================================================

def calculate_reaction(mol1, mol2, trigram_props):
    """計算兩個卦相遇時的「化學反應」"""

    # 獲取三元卦屬性
    lower1_prop = trigram_props[mol1['lower']]
    upper1_prop = trigram_props[mol1['upper']]
    lower2_prop = trigram_props[mol2['lower']]
    upper2_prop = trigram_props[mol2['upper']]

    # 計算反應能量
    # 規則1：相同三元卦相遇 - 穩定但無變化
    same_trigram_bonus = 0
    if mol1['lower'] == mol2['lower']:
        same_trigram_bonus += 0.1
    if mol1['upper'] == mol2['upper']:
        same_trigram_bonus += 0.1

    # 規則2：互補三元卦相遇 - 可能產生強反應
    # 乾坤、坎離、艮兌、震巽 是互補對
    complementary_pairs = [('乾', '坤'), ('坎', '離'), ('艮', '兌'), ('震', '巽')]
    complementary_bonus = 0
    for pair in complementary_pairs:
        if (mol1['lower'], mol2['lower']) in [pair, pair[::-1]]:
            complementary_bonus += 0.2
        if (mol1['upper'], mol2['upper']) in [pair, pair[::-1]]:
            complementary_bonus += 0.2

    # 規則3：反應活性
    avg_reactivity = (mol1['reactivity'] + mol2['reactivity']) / 2

    # 規則4：電荷平衡
    charge_balance = (lower1_prop['net_charge'] + upper1_prop['net_charge'] +
                      lower2_prop['net_charge'] + upper2_prop['net_charge']) / 4

    # 綜合反應結果
    reaction_result = {
        'molecules': (mol1['name'], mol2['name']),
        'same_trigram_bonus': same_trigram_bonus,
        'complementary_bonus': complementary_bonus,
        'avg_reactivity': avg_reactivity,
        'charge_balance': charge_balance,
        'expected_outcome': 'positive' if charge_balance > 0 else 'negative' if charge_balance < 0 else 'neutral'
    }

    return reaction_result

# ============================================================
# 建立「反應表」（類似化學反應表）
# ============================================================

def build_reaction_table(molecules, trigram_props):
    """建立三元卦之間的反應表"""
    print("\n" + "=" * 70)
    print("三元卦反應表（類似化學元素反應表）")
    print("=" * 70)

    # 計算每對三元卦組合的平均效果
    pair_effects = defaultdict(list)

    for hex_num, mol in molecules.items():
        lower, upper = mol['lower'], mol['upper']
        net = mol['net_score']
        pair_effects[(lower, upper)].append(net)

    # 顯示反應表
    print("\n組合反應結果（平均淨分）:")
    print("\n       下卦（內卦）")
    print("       " + "  ".join(f"{t:>4}" for t in TRIGRAMS))
    print("     " + "-" * 50)

    for upper in TRIGRAMS:
        row = f" {upper} |"
        for lower in TRIGRAMS:
            effects = pair_effects.get((lower, upper), [])
            if effects:
                avg = sum(effects) / len(effects)
                if avg >= 2:
                    row += f" +++  "
                elif avg >= 1:
                    row += f" ++   "
                elif avg > 0:
                    row += f" +    "
                elif avg > -1:
                    row += f" -    "
                elif avg > -2:
                    row += f" --   "
                else:
                    row += f" ---  "
            else:
                row += f"  ?   "
        print(f"上{row}")

    print("\n圖例: +++很吉(≥+2), ++吉(+1~+2), +微吉(0~+1), -微凶(-1~0), --凶(-2~-1), ---很凶(<-2)")

    return pair_effects

# ============================================================
# 建立元素週期表
# ============================================================

def print_periodic_table(trigram_props):
    """以元素週期表的形式展示三元卦屬性"""
    print("\n" + "=" * 70)
    print("三元卦元素週期表")
    print("=" * 70)

    print("""
類比：
• 吉傾向 ≈ 電負性（吸引好結果的能力）
• 凶傾向 ≈ 反電負性（吸引壞結果的能力）
• 穩定性 ≈ 惰性（產生中性結果的傾向）
• 極性 ≈ 氧化態（外卦表現 - 內卦表現）
• 淨電荷 ≈ 離子電荷（吉 - 凶）
""")

    print("\n" + "-" * 70)
    print(f"{'三元卦':^8} {'吉傾向':^10} {'凶傾向':^10} {'穩定性':^10} {'極性':^10} {'淨電荷':^10}")
    print("-" * 70)

    for trigram in TRIGRAMS:
        p = trigram_props[trigram]
        print(f"  {trigram:^6}  {p['ji_tendency']:^8.1%}  {p['xiong_tendency']:^8.1%}  "
              f"{p['stability']:^8.1%}  {p['polarity']:+8.1%}  {p['net_charge']:+8.1%}")

    # 分組
    print("\n\n### 三元卦分類（類似元素族）")
    print("-" * 50)

    # 按淨電荷分組
    positive = [(t, p) for t, p in trigram_props.items() if p['net_charge'] > 0.15]
    neutral = [(t, p) for t, p in trigram_props.items() if -0.15 <= p['net_charge'] <= 0.15]
    negative = [(t, p) for t, p in trigram_props.items() if p['net_charge'] < -0.15]

    print(f"\n吉族（淨電荷 > +15%）: {', '.join(t for t, _ in positive)}")
    print(f"中族（淨電荷 ≈ 0）: {', '.join(t for t, _ in neutral)}")
    print(f"凶族（淨電荷 < -15%）: {', '.join(t for t, _ in negative) if negative else '無'}")

    # 按穩定性分組
    stable = [(t, p) for t, p in trigram_props.items() if p['stability'] > 0.5]
    reactive = [(t, p) for t, p in trigram_props.items() if p['stability'] < 0.5]

    print(f"\n穩定族（穩定性 > 50%）: {', '.join(t for t, _ in stable)}")
    print(f"活潑族（穩定性 < 50%）: {', '.join(t for t, _ in reactive)}")

# ============================================================
# 分子狀態圖
# ============================================================

def print_molecular_states(molecules):
    """顯示所有卦的分子狀態"""
    print("\n" + "=" * 70)
    print("64卦分子狀態圖")
    print("=" * 70)

    # 按狀態分類
    ji_state = [m for m in molecules.values() if m['primary_state'] == '吉態']
    zhong_state = [m for m in molecules.values() if m['primary_state'] == '中態']
    xiong_state = [m for m in molecules.values() if m['primary_state'] == '凶態']

    print(f"\n吉態卦 ({len(ji_state)}個):")
    for m in sorted(ji_state, key=lambda x: -x['net_score'])[:10]:
        print(f"  {m['name']}({m['lower']}/{m['upper']}): 淨分={m['net_score']:+d}, 活性={m['reactivity']:.1%}")
    if len(ji_state) > 10:
        print(f"  ... 共{len(ji_state)}個")

    print(f"\n中態卦 ({len(zhong_state)}個):")
    for m in sorted(zhong_state, key=lambda x: -x['stability'])[:10]:
        print(f"  {m['name']}({m['lower']}/{m['upper']}): 穩定性={m['stability']:.1%}")
    if len(zhong_state) > 10:
        print(f"  ... 共{len(zhong_state)}個")

    print(f"\n凶態卦 ({len(xiong_state)}個):")
    for m in sorted(xiong_state, key=lambda x: x['net_score'])[:10]:
        print(f"  {m['name']}({m['lower']}/{m['upper']}): 淨分={m['net_score']:+d}, 活性={m['reactivity']:.1%}")
    if len(xiong_state) > 10:
        print(f"  ... 共{len(xiong_state)}個")

# ============================================================
# 預測化學反應結果
# ============================================================

def predict_interaction(hex1_num, hex2_num, molecules, trigram_props):
    """預測兩個卦相互作用的結果"""
    mol1 = molecules.get(hex1_num)
    mol2 = molecules.get(hex2_num)

    if not mol1 or not mol2:
        return None

    print(f"\n預測: {mol1['name']} + {mol2['name']} 的反應")
    print("-" * 40)

    # 分析反應物
    print(f"\n反應物1: {mol1['name']}")
    print(f"  結構: {mol1['lower']}/{mol1['upper']}")
    print(f"  狀態: {mol1['primary_state']} (淨分={mol1['net_score']:+d})")
    print(f"  活性: {mol1['reactivity']:.1%}")

    print(f"\n反應物2: {mol2['name']}")
    print(f"  結構: {mol2['lower']}/{mol2['upper']}")
    print(f"  狀態: {mol2['primary_state']} (淨分={mol2['net_score']:+d})")
    print(f"  活性: {mol2['reactivity']:.1%}")

    # 計算反應
    reaction = calculate_reaction(mol1, mol2, trigram_props)

    print(f"\n反應分析:")
    print(f"  同元素加成: {reaction['same_trigram_bonus']:+.2f}")
    print(f"  互補反應: {reaction['complementary_bonus']:+.2f}")
    print(f"  平均活性: {reaction['avg_reactivity']:.1%}")
    print(f"  電荷平衡: {reaction['charge_balance']:+.2f}")

    # 預測結果
    combined_score = mol1['net_score'] + mol2['net_score']
    if combined_score > 3:
        prediction = "強吉反應"
    elif combined_score > 0:
        prediction = "弱吉反應"
    elif combined_score > -3:
        prediction = "弱凶反應"
    else:
        prediction = "強凶反應"

    print(f"\n預測結果: {prediction} (組合淨分={combined_score:+d})")

    return reaction

# ============================================================
# 建立親和度矩陣
# ============================================================

def build_affinity_matrix(molecules, trigram_props):
    """建立64x64的卦際親和度矩陣"""
    print("\n" + "=" * 70)
    print("卦際親和度分析")
    print("=" * 70)

    # 計算每對卦的親和度
    affinity_scores = {}

    for i in range(1, 65):
        for j in range(i, 65):
            mol1 = molecules.get(i)
            mol2 = molecules.get(j)

            if not mol1 or not mol2:
                continue

            # 親和度 = 狀態相似性 + 結構相似性
            # 狀態相似性
            state_sim = 0
            if mol1['primary_state'] == mol2['primary_state']:
                state_sim = 1
            elif (mol1['primary_state'] in ['吉態', '中態'] and mol2['primary_state'] in ['吉態', '中態']):
                state_sim = 0.5
            elif (mol1['primary_state'] in ['凶態', '中態'] and mol2['primary_state'] in ['凶態', '中態']):
                state_sim = 0.5

            # 結構相似性
            struct_sim = 0
            if mol1['lower'] == mol2['lower']:
                struct_sim += 0.25
            if mol1['upper'] == mol2['upper']:
                struct_sim += 0.25
            if mol1['lower'] == mol2['upper'] or mol1['upper'] == mol2['lower']:
                struct_sim += 0.1

            # 淨分相似性
            score_diff = abs(mol1['net_score'] - mol2['net_score'])
            score_sim = max(0, 1 - score_diff / 6)

            # 綜合親和度
            affinity = state_sim * 0.4 + struct_sim * 0.3 + score_sim * 0.3

            affinity_scores[(i, j)] = {
                'affinity': affinity,
                'state_sim': state_sim,
                'struct_sim': struct_sim,
                'score_sim': score_sim
            }

    # 找出最高親和度對
    sorted_pairs = sorted(affinity_scores.items(), key=lambda x: -x[1]['affinity'])

    print("\n### 最高親和度的卦對")
    print("-" * 60)

    for (i, j), scores in sorted_pairs[:15]:
        mol1, mol2 = molecules[i], molecules[j]
        print(f"  {mol1['name']} ↔ {mol2['name']}: 親和度={scores['affinity']:.2f}")
        print(f"    狀態相似={scores['state_sim']:.2f}, 結構相似={scores['struct_sim']:.2f}, 淨分相似={scores['score_sim']:.2f}")

    print("\n### 最低親和度的卦對")
    print("-" * 60)

    for (i, j), scores in sorted_pairs[-10:]:
        mol1, mol2 = molecules[i], molecules[j]
        print(f"  {mol1['name']} ↔ {mol2['name']}: 親和度={scores['affinity']:.2f}")

    return affinity_scores

# ============================================================
# 導出數據
# ============================================================

def export_chemistry_data(trigram_props, molecules, affinity_scores):
    """導出化學模型數據"""
    output = {
        'trigram_properties': {t: {k: v for k, v in p.items() if k != 'stats'}
                               for t, p in trigram_props.items()},
        'molecules': {str(k): {key: val for key, val in v.items()}
                      for k, v in molecules.items()},
        'top_affinities': [{'pair': [i, j], **scores}
                           for (i, j), scores in sorted(affinity_scores.items(),
                                                        key=lambda x: -x[1]['affinity'])[:100]]
    }

    with open('data/analysis/hexagram_chemistry.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n化學模型數據已保存到: data/analysis/hexagram_chemistry.json")

# ============================================================
# 主程序
# ============================================================

def main():
    print("卦的化學反應模型")
    print("Hexagram Chemistry Model")
    print("=" * 70)

    # 載入數據
    raw_data = load_data()
    print(f"\n載入 {len(raw_data)} 條爻數據")

    # 建立三元卦屬性
    print("\n建立三元卦元素屬性...")
    trigram_props = build_trigram_properties(raw_data)
    print_periodic_table(trigram_props)

    # 建立卦的分子結構
    print("\n建立64卦分子結構...")
    molecules = build_hexagram_molecule(raw_data)
    print_molecular_states(molecules)

    # 建立反應表
    pair_effects = build_reaction_table(molecules, trigram_props)

    # 建立親和度矩陣
    affinity_scores = build_affinity_matrix(molecules, trigram_props)

    # 示範預測
    print("\n" + "=" * 70)
    print("示範：卦際反應預測")
    print("=" * 70)

    # 乾 + 坤
    predict_interaction(1, 2, molecules, trigram_props)
    # 泰 + 否
    predict_interaction(11, 12, molecules, trigram_props)
    # 坎 + 離
    predict_interaction(29, 30, molecules, trigram_props)

    # 導出數據
    export_chemistry_data(trigram_props, molecules, affinity_scores)

    # 總結
    print("\n" + "=" * 70)
    print("總結：化學模型的啟示")
    print("=" * 70)
    print("""
### 三元卦如同元素

1. **吉族元素**: 震、坤、巽、離、乾、兌
   - 這些三元卦傾向產生吉的結果
   - 類似電正性元素，容易「給出」好能量

2. **穩定元素**: 大部分三元卦穩定性較高（中的比例高）
   - 類似惰性氣體，不易產生極端反應

3. **互補反應**
   - 乾↔坤、坎↔離、艮↔兌、震↔巽 是互補對
   - 組合時可能產生特殊效應

### 卦如同分子

1. **三態分類**
   - 吉態卦：淨分高，傾向好結果
   - 中態卦：穩定，結果中性
   - 凶態卦：淨分低，需要謹慎

2. **反應活性**
   - 高活性卦（極端值多）容易產生變化
   - 低活性卦（中性多）結果穩定

### 實用預測

當兩卦相遇：
1. 看三元卦是否互補 → 可能有化學反應
2. 看狀態是否相似 → 同態更容易融合
3. 看活性高低 → 高活性組合結果更極端
""")

if __name__ == "__main__":
    main()
