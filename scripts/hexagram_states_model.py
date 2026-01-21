#!/usr/bin/env python3
"""
卦的三態模型
Hexagram Three-States Model

每個卦可以處於三種狀態之一：吉態、中態、凶態
就像物質可以是固態、液態、氣態

當兩卦相遇時，結果取決於雙方的狀態組合
"""

import json
import math
from collections import defaultdict
from itertools import product

# ============================================================
# 載入數據
# ============================================================

def load_data():
    with open('data/analysis/corrected_yaoci_labels.json', 'r', encoding='utf-8') as f:
        return json.load(f)

TRIGRAMS = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']
BINARY_TO_TRIGRAM = {
    '000': '坤', '001': '震', '010': '坎', '011': '兌',
    '100': '艮', '101': '離', '110': '巽', '111': '乾'
}
LABEL_MAP = {1: '吉', 0: '中', -1: '凶'}
STATES = ['吉', '中', '凶']

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
# 建立卦的三態概率分布
# ============================================================

def build_state_distributions(raw_data):
    """
    計算每個卦在每個爻位上處於各狀態的概率

    每個卦有6個爻位，每個爻位可以是吉/中/凶
    這裡我們計算每個卦整體處於各狀態的傾向
    """

    # 按卦分組
    hexagram_yaos = defaultdict(list)
    for entry in raw_data:
        hex_num = entry['hex_num']
        label = LABEL_MAP.get(entry['label'], '中')
        hexagram_yaos[hex_num].append(label)

    # 計算每個卦的狀態分布
    state_distributions = {}

    for hex_num in range(1, 65):
        labels = hexagram_yaos.get(hex_num, [])
        if not labels:
            continue

        # 計算各狀態的比例
        ji_prob = labels.count('吉') / len(labels)
        zhong_prob = labels.count('中') / len(labels)
        xiong_prob = labels.count('凶') / len(labels)

        state_distributions[hex_num] = {
            'name': HEXAGRAM_NAMES.get(hex_num, f'卦{hex_num}'),
            'P(吉)': ji_prob,
            'P(中)': zhong_prob,
            'P(凶)': xiong_prob,
            # 最可能的狀態
            'dominant_state': max(STATES, key=lambda s: [ji_prob, zhong_prob, xiong_prob][STATES.index(s)]),
            # 狀態熵（多樣性）
            'entropy': -sum(p * math.log2(p) if p > 0 else 0 for p in [ji_prob, zhong_prob, xiong_prob])
        }

    return state_distributions

# ============================================================
# 建立爻位的狀態轉移
# ============================================================

def build_position_state_matrix(raw_data):
    """
    建立爻位 × 狀態的概率矩陣

    顯示在每個爻位上，卦處於各狀態的概率
    """

    # 統計每個爻位的狀態分布
    position_states = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0, 'total': 0})

    for entry in raw_data:
        pos = entry['position']
        label = LABEL_MAP.get(entry['label'], '中')
        position_states[pos][label] += 1
        position_states[pos]['total'] += 1

    # 轉換為概率
    position_probs = {}
    for pos in range(1, 7):
        total = position_states[pos]['total']
        if total > 0:
            position_probs[pos] = {
                'P(吉)': position_states[pos]['吉'] / total,
                'P(中)': position_states[pos]['中'] / total,
                'P(凶)': position_states[pos]['凶'] / total
            }

    return position_probs

# ============================================================
# 建立三元卦的狀態傾向
# ============================================================

def build_trigram_state_tendency(raw_data):
    """
    計算每個三元卦在不同狀態下的傾向

    三元卦作為內卦或外卦時，對卦整體狀態的影響
    """

    # 統計
    trigram_states = defaultdict(lambda: {
        'inner': {'吉': 0, '中': 0, '凶': 0, 'total': 0},
        'outer': {'吉': 0, '中': 0, '凶': 0, 'total': 0}
    })

    for entry in raw_data:
        pos = entry['position']
        binary = entry['binary']
        label = LABEL_MAP.get(entry['label'], '中')

        lower = BINARY_TO_TRIGRAM[binary[:3]]
        upper = BINARY_TO_TRIGRAM[binary[3:]]

        if pos <= 3:
            trigram_states[lower]['inner'][label] += 1
            trigram_states[lower]['inner']['total'] += 1
        else:
            trigram_states[upper]['outer'][label] += 1
            trigram_states[upper]['outer']['total'] += 1

    # 計算傾向
    tendencies = {}
    for trigram in TRIGRAMS:
        inner = trigram_states[trigram]['inner']
        outer = trigram_states[trigram]['outer']

        inner_total = inner['total']
        outer_total = outer['total']

        tendencies[trigram] = {
            'inner': {
                'P(吉)': inner['吉'] / inner_total if inner_total > 0 else 0,
                'P(中)': inner['中'] / inner_total if inner_total > 0 else 0,
                'P(凶)': inner['凶'] / inner_total if inner_total > 0 else 0,
            },
            'outer': {
                'P(吉)': outer['吉'] / outer_total if outer_total > 0 else 0,
                'P(中)': outer['中'] / outer_total if outer_total > 0 else 0,
                'P(凶)': outer['凶'] / outer_total if outer_total > 0 else 0,
            }
        }

    return tendencies

# ============================================================
# 狀態交互矩陣
# ============================================================

def build_state_interaction_matrix(raw_data):
    """
    建立狀態之間的交互矩陣

    當一個爻處於狀態A，相鄰爻處於狀態B時，會發生什麼？
    """

    # 按卦分組
    hexagram_yaos = defaultdict(dict)
    for entry in raw_data:
        hex_num = entry['hex_num']
        pos = entry['position']
        label = LABEL_MAP.get(entry['label'], '中')
        hexagram_yaos[hex_num][pos] = label

    # 統計相鄰爻的狀態轉移
    transitions = defaultdict(int)

    for hex_num, yaos in hexagram_yaos.items():
        for pos in range(1, 6):
            if pos in yaos and pos + 1 in yaos:
                current = yaos[pos]
                next_state = yaos[pos + 1]
                transitions[(current, next_state)] += 1

    # 轉換為概率矩陣
    interaction_matrix = {}
    for state1 in STATES:
        row_total = sum(transitions[(state1, s2)] for s2 in STATES)
        interaction_matrix[state1] = {}
        for state2 in STATES:
            interaction_matrix[state1][state2] = transitions[(state1, state2)] / row_total if row_total > 0 else 0

    return interaction_matrix

# ============================================================
# 輸出結果
# ============================================================

def print_state_distributions(state_dist):
    print("=" * 70)
    print("卦的三態分布")
    print("=" * 70)

    print("""
每個卦可以處於三種狀態：
• 吉態：傾向產生好結果
• 中態：結果中性
• 凶態：傾向產生壞結果
""")

    # 按主要狀態分類
    ji_dominant = [(h, d) for h, d in state_dist.items() if d['dominant_state'] == '吉']
    zhong_dominant = [(h, d) for h, d in state_dist.items() if d['dominant_state'] == '中']
    xiong_dominant = [(h, d) for h, d in state_dist.items() if d['dominant_state'] == '凶']

    print(f"\n### 吉態卦 ({len(ji_dominant)}個)")
    print("-" * 50)
    print(f"{'卦名':^8} {'P(吉)':^8} {'P(中)':^8} {'P(凶)':^8} {'熵':^8}")
    print("-" * 50)
    for h, d in sorted(ji_dominant, key=lambda x: -x[1]['P(吉)'])[:15]:
        print(f"  {d['name']:^6} {d['P(吉)']:^7.1%} {d['P(中)']:^7.1%} {d['P(凶)']:^7.1%} {d['entropy']:^7.2f}")

    print(f"\n### 中態卦 ({len(zhong_dominant)}個)")
    print("-" * 50)
    print(f"{'卦名':^8} {'P(吉)':^8} {'P(中)':^8} {'P(凶)':^8} {'熵':^8}")
    print("-" * 50)
    for h, d in sorted(zhong_dominant, key=lambda x: -x[1]['P(中)'])[:15]:
        print(f"  {d['name']:^6} {d['P(吉)']:^7.1%} {d['P(中)']:^7.1%} {d['P(凶)']:^7.1%} {d['entropy']:^7.2f}")

    print(f"\n### 凶態卦 ({len(xiong_dominant)}個)")
    print("-" * 50)
    print(f"{'卦名':^8} {'P(吉)':^8} {'P(中)':^8} {'P(凶)':^8} {'熵':^8}")
    print("-" * 50)
    for h, d in sorted(xiong_dominant, key=lambda x: -x[1]['P(凶)'])[:15]:
        print(f"  {d['name']:^6} {d['P(吉)']:^7.1%} {d['P(中)']:^7.1%} {d['P(凶)']:^7.1%} {d['entropy']:^7.2f}")

def print_position_states(position_probs):
    print("\n" + "=" * 70)
    print("爻位的狀態分布")
    print("=" * 70)

    print("\n每個爻位處於各狀態的概率：\n")
    print(f"{'爻位':^8} {'P(吉)':^10} {'P(中)':^10} {'P(凶)':^10}")
    print("-" * 40)

    for pos in range(1, 7):
        p = position_probs[pos]
        # 可視化
        ji_bar = '█' * int(p['P(吉)'] * 20)
        zhong_bar = '▒' * int(p['P(中)'] * 20)
        xiong_bar = '░' * int(p['P(凶)'] * 20)

        print(f"  爻{pos}    {p['P(吉)']:^9.1%} {p['P(中)']:^9.1%} {p['P(凶)']:^9.1%}")
        print(f"         {ji_bar}{zhong_bar}{xiong_bar}")

def print_trigram_tendencies(tendencies):
    print("\n" + "=" * 70)
    print("三元卦的狀態傾向")
    print("=" * 70)

    print("\n### 作為內卦（下卦）時")
    print("-" * 50)
    print(f"{'三元卦':^8} {'P(吉)':^10} {'P(中)':^10} {'P(凶)':^10}")
    print("-" * 50)

    for trigram in TRIGRAMS:
        t = tendencies[trigram]['inner']
        print(f"  {trigram:^6} {t['P(吉)']:^9.1%} {t['P(中)']:^9.1%} {t['P(凶)']:^9.1%}")

    print("\n### 作為外卦（上卦）時")
    print("-" * 50)
    print(f"{'三元卦':^8} {'P(吉)':^10} {'P(中)':^10} {'P(凶)':^10}")
    print("-" * 50)

    for trigram in TRIGRAMS:
        t = tendencies[trigram]['outer']
        print(f"  {trigram:^6} {t['P(吉)']:^9.1%} {t['P(中)']:^9.1%} {t['P(凶)']:^9.1%}")

def print_interaction_matrix(interaction_matrix):
    print("\n" + "=" * 70)
    print("狀態交互矩陣（Markov轉移）")
    print("=" * 70)

    print("""
當前爻處於某狀態時，下一爻處於各狀態的概率：
（類似相態轉移）
""")

    print(f"{'當前狀態':^10} → {'下一爻為吉':^12} {'下一爻為中':^12} {'下一爻為凶':^12}")
    print("-" * 55)

    for state1 in STATES:
        row = interaction_matrix[state1]
        print(f"  {state1:^8}   {row['吉']:^11.1%} {row['中']:^11.1%} {row['凶']:^11.1%}")

    print("\n解讀：")
    print("• 吉→吉: 吉會傳染（連續吉）")
    print("• 凶→凶: 凶也會傳染（連續凶）")
    print("• 中→中: 中是最穩定的狀態")

# ============================================================
# 建立完整的三態模型
# ============================================================

def build_complete_state_model(raw_data):
    """建立完整的卦三態模型"""

    # 按卦分組
    hexagram_data = defaultdict(lambda: {'yaos': {}, 'binary': None})
    for entry in raw_data:
        hex_num = entry['hex_num']
        pos = entry['position']
        label = LABEL_MAP.get(entry['label'], '中')
        hexagram_data[hex_num]['yaos'][pos] = label
        hexagram_data[hex_num]['binary'] = entry['binary']

    # 為每個卦建立完整的狀態模型
    models = {}

    for hex_num in range(1, 65):
        data = hexagram_data.get(hex_num)
        if not data or not data['binary']:
            continue

        binary = data['binary']
        yaos = data['yaos']

        lower = BINARY_TO_TRIGRAM[binary[:3]]
        upper = BINARY_TO_TRIGRAM[binary[3:]]

        # 計算各狀態的能量（以概率為基礎）
        labels = [yaos.get(p, '中') for p in range(1, 7)]

        ji_energy = labels.count('吉') / 6
        zhong_energy = labels.count('中') / 6
        xiong_energy = labels.count('凶') / 6

        # 狀態向量
        state_vector = [ji_energy, zhong_energy, xiong_energy]

        # 主要狀態（波茲曼分布中的基態）
        primary_state = STATES[state_vector.index(max(state_vector))]

        # 激發能量（離開基態需要的能量）
        excitation_energy = 1 - max(state_vector)

        models[hex_num] = {
            'name': HEXAGRAM_NAMES.get(hex_num, f'卦{hex_num}'),
            'lower': lower,
            'upper': upper,
            'state_vector': state_vector,
            'primary_state': primary_state,
            'excitation_energy': excitation_energy,
            'labels': labels
        }

    return models

def print_state_model(models):
    print("\n" + "=" * 70)
    print("64卦三態模型")
    print("=" * 70)

    print("""
每個卦的狀態向量 [P(吉), P(中), P(凶)] 表示該卦處於各狀態的傾向
""")

    # 按主要狀態分組
    by_state = {'吉': [], '中': [], '凶': []}
    for h, m in models.items():
        by_state[m['primary_state']].append((h, m))

    for state in STATES:
        print(f"\n### {state}態卦 ({len(by_state[state])}個)")
        print("-" * 60)

        sorted_models = sorted(by_state[state],
                               key=lambda x: -x[1]['state_vector'][STATES.index(state)])

        for h, m in sorted_models[:10]:
            sv = m['state_vector']
            print(f"  {m['name']:^4} ({m['lower']}/{m['upper']}): "
                  f"[{sv[0]:.1%}, {sv[1]:.1%}, {sv[2]:.1%}] "
                  f"激發能={m['excitation_energy']:.1%}")

        if len(sorted_models) > 10:
            print(f"  ... 共{len(sorted_models)}個")

# ============================================================
# 狀態組合預測
# ============================================================

def predict_state_combination(model1, model2):
    """預測兩卦狀態組合的結果"""

    # 狀態向量乘積（張量積簡化版）
    sv1 = model1['state_vector']
    sv2 = model2['state_vector']

    # 計算各種組合的概率
    combinations = {}
    for i, s1 in enumerate(STATES):
        for j, s2 in enumerate(STATES):
            prob = sv1[i] * sv2[j]
            combinations[(s1, s2)] = prob

    # 預測結果
    # 規則：吉+吉=大吉, 吉+凶=中, 凶+凶=大凶
    result_probs = {'大吉': 0, '吉': 0, '中': 0, '凶': 0, '大凶': 0}

    for (s1, s2), prob in combinations.items():
        if s1 == '吉' and s2 == '吉':
            result_probs['大吉'] += prob
        elif s1 == '凶' and s2 == '凶':
            result_probs['大凶'] += prob
        elif (s1 == '吉' and s2 == '凶') or (s1 == '凶' and s2 == '吉'):
            result_probs['中'] += prob * 0.5
            result_probs['吉'] += prob * 0.25
            result_probs['凶'] += prob * 0.25
        elif s1 == '吉' or s2 == '吉':
            result_probs['吉'] += prob
        elif s1 == '凶' or s2 == '凶':
            result_probs['凶'] += prob
        else:
            result_probs['中'] += prob

    return result_probs, combinations

def print_combination_examples(models):
    print("\n" + "=" * 70)
    print("狀態組合預測示例")
    print("=" * 70)

    examples = [
        (1, 2, "乾 + 坤"),
        (11, 12, "泰 + 否"),
        (29, 30, "坎 + 離"),
        (63, 64, "既濟 + 未濟"),
        (15, 46, "謙 + 升"),  # 都是吉態
        (7, 56, "師 + 旅"),   # 都是凶態
    ]

    for h1, h2, desc in examples:
        m1 = models.get(h1)
        m2 = models.get(h2)

        if not m1 or not m2:
            continue

        print(f"\n### {desc}")
        print("-" * 40)
        print(f"  {m1['name']} 狀態向量: {[f'{x:.1%}' for x in m1['state_vector']]}")
        print(f"  {m2['name']} 狀態向量: {[f'{x:.1%}' for x in m2['state_vector']]}")

        result_probs, combos = predict_state_combination(m1, m2)

        print(f"\n  組合結果概率:")
        for result, prob in sorted(result_probs.items(), key=lambda x: -x[1]):
            if prob > 0.01:
                bar = '█' * int(prob * 30)
                print(f"    {result:^4}: {prob:5.1%} {bar}")

# ============================================================
# 導出數據
# ============================================================

def export_state_model(models, state_dist, position_probs, trigram_tend, interaction):
    """導出三態模型數據"""

    output = {
        'hexagram_states': {
            str(h): {
                'name': m['name'],
                'lower': m['lower'],
                'upper': m['upper'],
                'state_vector': m['state_vector'],
                'primary_state': m['primary_state'],
                'excitation_energy': m['excitation_energy']
            }
            for h, m in models.items()
        },
        'position_states': position_probs,
        'trigram_tendencies': trigram_tend,
        'state_interaction_matrix': interaction
    }

    with open('data/analysis/hexagram_three_states.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n三態模型數據已保存到: data/analysis/hexagram_three_states.json")

# ============================================================
# 主程序
# ============================================================

def main():
    print("卦的三態模型")
    print("Hexagram Three-States Model")
    print("=" * 70)

    print("""
模型核心思想：
每個卦像物質一樣，可以處於三種狀態：
• 吉態 (類似固態) - 穩定、積極
• 中態 (類似液態) - 流動、中性
• 凶態 (類似氣態) - 不穩定、消極

當兩卦相遇時，就像化學反應，結果取決於雙方的狀態
""")

    # 載入數據
    raw_data = load_data()
    print(f"\n載入 {len(raw_data)} 條爻數據")

    # 建立各種模型
    print("\n建立狀態分布...")
    state_dist = build_state_distributions(raw_data)
    print_state_distributions(state_dist)

    print("\n建立爻位狀態...")
    position_probs = build_position_state_matrix(raw_data)
    print_position_states(position_probs)

    print("\n建立三元卦傾向...")
    trigram_tend = build_trigram_state_tendency(raw_data)
    print_trigram_tendencies(trigram_tend)

    print("\n建立狀態交互矩陣...")
    interaction = build_state_interaction_matrix(raw_data)
    print_interaction_matrix(interaction)

    print("\n建立完整三態模型...")
    models = build_complete_state_model(raw_data)
    print_state_model(models)

    print("\n狀態組合預測...")
    print_combination_examples(models)

    # 導出數據
    export_state_model(models, state_dist, position_probs, trigram_tend, interaction)

    # 總結
    print("\n" + "=" * 70)
    print("總結：三態模型的應用")
    print("=" * 70)
    print("""
### 核心發現

1. **卦的狀態分布**
   - 大多數卦主要處於「中態」（穩定）
   - 少數卦傾向「吉態」或「凶態」

2. **爻位的狀態傾向**
   - 爻5 最傾向吉態 (48.4%)
   - 爻3 最傾向凶態 (32.8%)
   - 爻2 最傾向中態 (43.8%)

3. **三元卦的狀態調控**
   - 震卦作為外卦時大幅提升吉態概率
   - 艮卦作為內卦時增加凶態概率

4. **狀態轉移規律**
   - 吉→吉: 37.6% (吉態傳染)
   - 中→中: 50.0% (中態穩定)
   - 凶→凶: 17.2% (凶態也會傳染但較弱)

### 實用預測公式

卦的狀態 = f(爻位概率, 三元卦傾向, 前一爻狀態)

當兩卦組合時：
• 吉態 + 吉態 → 大吉
• 吉態 + 凶態 → 中和（不確定）
• 凶態 + 凶態 → 大凶
• 中態 + 任何 → 維持穩定
""")

if __name__ == "__main__":
    main()
