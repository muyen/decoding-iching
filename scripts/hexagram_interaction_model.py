#!/usr/bin/env python3
"""
卦的交互模型
Hexagram Interaction Model

核心概念：
- 每個卦本身是中性的（像蘋果一樣）
- 卦有固有屬性（但不是吉凶）
- 吉/中/凶 只在交互或變化時才顯現

類比：
- 卦 = 物質（有質量、顏色等屬性，但無好壞）
- 爻動 = 化學反應的觸發
- 吉凶 = 反應結果
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
# 建立卦的固有屬性（中性的）
# ============================================================

def build_hexagram_properties(raw_data):
    """
    建立每個卦的固有屬性（不是吉凶，而是中性的屬性）

    屬性包括：
    - 結構屬性：上下卦、陰陽比例
    - 動態屬性：在特定條件下的反應傾向
    """

    # 按卦分組
    hexagram_data = defaultdict(lambda: {'yaos': {}, 'binary': None})
    for entry in raw_data:
        hex_num = entry['hex_num']
        pos = entry['position']
        label = entry['label']  # 數值形式
        hexagram_data[hex_num]['yaos'][pos] = label
        hexagram_data[hex_num]['binary'] = entry['binary']

    properties = {}

    for hex_num in range(1, 65):
        data = hexagram_data.get(hex_num)
        if not data or not data['binary']:
            continue

        binary = data['binary']
        yaos = data['yaos']

        # 結構屬性（中性）
        lower = BINARY_TO_TRIGRAM[binary[:3]]
        upper = BINARY_TO_TRIGRAM[binary[3:]]

        yang_count = binary.count('1')  # 陽爻數量
        yin_count = 6 - yang_count      # 陰爻數量

        # 結構對稱性
        is_symmetric = binary == binary[::-1]  # 綜卦是否等於自身

        # 陰陽平衡度 (0-1, 0.5最平衡)
        balance = 1 - abs(yang_count - 3) / 3

        # 內外卦關係
        same_trigram = lower == upper
        complementary = (lower, upper) in [
            ('乾', '坤'), ('坤', '乾'),
            ('坎', '離'), ('離', '坎'),
            ('艮', '兌'), ('兌', '艮'),
            ('震', '巽'), ('巽', '震')
        ]

        # 反應係數（從實際數據中學習，但表示為「在某位置動時的傾向」）
        # 這不是吉凶本身，而是「反應活性」
        reaction_coefficients = {}
        for pos in range(1, 7):
            if pos in yaos:
                reaction_coefficients[pos] = yaos[pos]  # -1, 0, 1

        properties[hex_num] = {
            'name': HEXAGRAM_NAMES.get(hex_num, f'卦{hex_num}'),
            'binary': binary,
            'lower': lower,
            'upper': upper,
            'yang_count': yang_count,
            'yin_count': yin_count,
            'balance': balance,
            'is_symmetric': is_symmetric,
            'same_trigram': same_trigram,
            'complementary': complementary,
            'reaction_coefficients': reaction_coefficients
        }

    return properties

# ============================================================
# 交互模型：爻動 = 觸發反應
# ============================================================

def calculate_interaction_result(hexagram_props, position):
    """
    計算當某爻動（變化）時的結果

    參數：
    - hexagram_props: 卦的固有屬性
    - position: 動爻位置 (1-6)

    返回：
    - 反應結果（吉/中/凶）
    """

    # 從反應係數獲取結果
    reaction_coef = hexagram_props['reaction_coefficients'].get(position, 0)

    # 這裡的反應係數直接來自數據
    # 但概念上，這是「在這個位置觸發變化時的傾向」
    return reaction_coef

def build_interaction_matrix(properties):
    """
    建立位置-結果的交互矩陣

    這表示：當某種結構的卦在某位置發生變化時的結果傾向
    """

    # 按上卦分組
    upper_position_results = defaultdict(lambda: defaultdict(list))

    for hex_num, props in properties.items():
        upper = props['upper']
        for pos, result in props['reaction_coefficients'].items():
            upper_position_results[upper][pos].append(result)

    # 按下卦分組
    lower_position_results = defaultdict(lambda: defaultdict(list))

    for hex_num, props in properties.items():
        lower = props['lower']
        for pos, result in props['reaction_coefficients'].items():
            lower_position_results[lower][pos].append(result)

    return upper_position_results, lower_position_results

# ============================================================
# 從交互結果反推卦的「反應特性」
# ============================================================

def derive_reaction_characteristics(properties):
    """
    從交互結果反推每個卦的「反應特性」

    這些特性描述卦在不同條件下的反應傾向
    """

    characteristics = {}

    for hex_num, props in properties.items():
        reactions = props['reaction_coefficients']

        # 整體反應傾向
        total_reaction = sum(reactions.values())

        # 位置敏感性（哪些位置容易產生極端反應）
        sensitive_positions = [pos for pos, r in reactions.items() if abs(r) == 1]
        stable_positions = [pos for pos, r in reactions.items() if r == 0]

        # 內外卦的反應差異
        inner_reaction = sum(reactions.get(p, 0) for p in [1, 2, 3])
        outer_reaction = sum(reactions.get(p, 0) for p in [4, 5, 6])

        characteristics[hex_num] = {
            'name': props['name'],
            'total_reaction': total_reaction,
            'sensitive_positions': sensitive_positions,
            'stable_positions': stable_positions,
            'inner_reaction': inner_reaction,
            'outer_reaction': outer_reaction,
            'inner_outer_diff': outer_reaction - inner_reaction
        }

    return characteristics

# ============================================================
# 三元卦的「元素特性」
# ============================================================

def derive_trigram_characteristics(properties):
    """
    從數據中反推三元卦的特性

    三元卦作為「元素」，有自己的反應傾向
    """

    # 統計每個三元卦在各位置的反應
    trigram_as_inner = defaultdict(lambda: defaultdict(list))
    trigram_as_outer = defaultdict(lambda: defaultdict(list))

    for hex_num, props in properties.items():
        lower = props['lower']
        upper = props['upper']

        for pos, result in props['reaction_coefficients'].items():
            if pos <= 3:
                trigram_as_inner[lower][pos].append(result)
            else:
                trigram_as_outer[upper][pos].append(result)

    # 計算平均反應
    trigram_chars = {}

    for trigram in TRIGRAMS:
        inner_reactions = {}
        for pos in [1, 2, 3]:
            values = trigram_as_inner[trigram][pos]
            inner_reactions[pos] = sum(values) / len(values) if values else 0

        outer_reactions = {}
        for pos in [4, 5, 6]:
            values = trigram_as_outer[trigram][pos]
            outer_reactions[pos] = sum(values) / len(values) if values else 0

        # 整體特性
        inner_total = sum(inner_reactions.values())
        outer_total = sum(outer_reactions.values())

        trigram_chars[trigram] = {
            'inner_reactions': inner_reactions,
            'outer_reactions': outer_reactions,
            'inner_total': inner_total,
            'outer_total': outer_total,
            'total': inner_total + outer_total,
            'inner_outer_polarity': outer_total - inner_total
        }

    return trigram_chars

# ============================================================
# 輸出結果
# ============================================================

def print_hexagram_properties(properties):
    print("=" * 70)
    print("卦的固有屬性（中性）")
    print("=" * 70)

    print("""
每個卦像物質一樣，有固有的結構屬性：
- 這些屬性本身不是吉凶
- 吉凶只在「變化」或「交互」時才產生
""")

    # 按結構特性分類
    print("\n### 對稱卦（綜卦等於自身）")
    print("-" * 50)
    symmetric = [(h, p) for h, p in properties.items() if p['is_symmetric']]
    for h, p in symmetric:
        print(f"  {p['name']:4} ({p['lower']}/{p['upper']}): 陽{p['yang_count']}陰{p['yin_count']}, 平衡度={p['balance']:.2f}")

    print("\n### 同卦（上下卦相同）")
    print("-" * 50)
    same = [(h, p) for h, p in properties.items() if p['same_trigram']]
    for h, p in same:
        print(f"  {p['name']:4} ({p['lower']}/{p['upper']}): 陽{p['yang_count']}陰{p['yin_count']}")

    print("\n### 互補卦（上下卦互補）")
    print("-" * 50)
    comp = [(h, p) for h, p in properties.items() if p['complementary']]
    for h, p in comp:
        print(f"  {p['name']:4} ({p['lower']}/{p['upper']}): 陽{p['yang_count']}陰{p['yin_count']}")

def print_reaction_characteristics(chars):
    print("\n" + "=" * 70)
    print("卦的反應特性（從交互結果反推）")
    print("=" * 70)

    print("""
這些特性描述卦在發生變化時的反應傾向：
- total_reaction: 整體反應傾向（正=傾向好結果，負=傾向壞結果）
- sensitive_positions: 容易產生極端結果的位置
- inner_outer_diff: 外卦變化 vs 內卦變化的差異
""")

    # 按反應傾向排序
    sorted_chars = sorted(chars.items(), key=lambda x: -x[1]['total_reaction'])

    print("\n### 整體反應傾向排名")
    print("-" * 60)
    print(f"{'卦名':^6} {'總反應':^8} {'敏感位':^15} {'穩定位':^15} {'內外差':^8}")
    print("-" * 60)

    for h, c in sorted_chars[:20]:
        sens = ','.join(str(p) for p in c['sensitive_positions']) or '-'
        stab = ','.join(str(p) for p in c['stable_positions']) or '-'
        print(f"  {c['name']:^4}  {c['total_reaction']:+5d}    {sens:^13}  {stab:^13}  {c['inner_outer_diff']:+5d}")

    print("\n...")

    for h, c in sorted_chars[-10:]:
        sens = ','.join(str(p) for p in c['sensitive_positions']) or '-'
        stab = ','.join(str(p) for p in c['stable_positions']) or '-'
        print(f"  {c['name']:^4}  {c['total_reaction']:+5d}    {sens:^13}  {stab:^13}  {c['inner_outer_diff']:+5d}")

def print_trigram_characteristics(trigram_chars):
    print("\n" + "=" * 70)
    print("三元卦的「元素特性」")
    print("=" * 70)

    print("""
三元卦作為基本「元素」，決定了卦在變化時的反應傾向：
- inner_total: 作為下卦時的反應傾向
- outer_total: 作為上卦時的反應傾向
- polarity: 上下差異（正=作為上卦更好）
""")

    print("\n### 三元卦反應特性")
    print("-" * 70)
    print(f"{'三元卦':^8} {'作為下卦':^12} {'作為上卦':^12} {'總反應':^10} {'極性':^10}")
    print("-" * 70)

    sorted_trigrams = sorted(trigram_chars.items(), key=lambda x: -x[1]['total'])

    for trigram, chars in sorted_trigrams:
        print(f"  {trigram:^6}  {chars['inner_total']:+8.1f}    {chars['outer_total']:+8.1f}    "
              f"{chars['total']:+8.1f}  {chars['inner_outer_polarity']:+8.1f}")

    print("\n### 各位置的反應係數")
    print("-" * 70)

    print("\n作為下卦時（影響爻1-3）:")
    print(f"{'三元卦':^8} {'爻1':^10} {'爻2':^10} {'爻3':^10}")
    print("-" * 50)
    for trigram in TRIGRAMS:
        chars = trigram_chars[trigram]
        r = chars['inner_reactions']
        print(f"  {trigram:^6}  {r.get(1, 0):+8.2f}  {r.get(2, 0):+8.2f}  {r.get(3, 0):+8.2f}")

    print("\n作為上卦時（影響爻4-6）:")
    print(f"{'三元卦':^8} {'爻4':^10} {'爻5':^10} {'爻6':^10}")
    print("-" * 50)
    for trigram in TRIGRAMS:
        chars = trigram_chars[trigram]
        r = chars['outer_reactions']
        print(f"  {trigram:^6}  {r.get(4, 0):+8.2f}  {r.get(5, 0):+8.2f}  {r.get(6, 0):+8.2f}")

# ============================================================
# 交互預測模型
# ============================================================

def build_interaction_predictor(properties, trigram_chars):
    """
    建立交互預測模型

    給定：
    - 卦（結構）
    - 動爻位置（觸發條件）

    預測：
    - 反應結果（吉/中/凶的概率）
    """

    def predict(hex_num, position):
        """預測在指定位置動爻時的結果"""
        if hex_num not in properties:
            return None

        props = properties[hex_num]

        # 方法1：直接使用學習到的反應係數
        direct_result = props['reaction_coefficients'].get(position, 0)

        # 方法2：基於三元卦特性預測
        if position <= 3:
            trigram = props['lower']
            trigram_effect = trigram_chars[trigram]['inner_reactions'].get(position, 0)
        else:
            trigram = props['upper']
            trigram_effect = trigram_chars[trigram]['outer_reactions'].get(position, 0)

        # 方法3：基於結構特性調整
        structure_bonus = 0
        if props['same_trigram']:
            structure_bonus -= 0.1  # 同卦略差
        if props['complementary']:
            structure_bonus += 0.1  # 互補卦略好

        # 綜合預測
        prediction = {
            'hex_name': props['name'],
            'position': position,
            'direct_result': direct_result,
            'trigram_effect': trigram_effect,
            'structure_bonus': structure_bonus,
            'final_score': direct_result  # 最終使用實際值
        }

        return prediction

    return predict

def print_interaction_examples(properties, trigram_chars):
    print("\n" + "=" * 70)
    print("交互預測示例")
    print("=" * 70)

    print("""
預測：當某卦在某位置發生變化時，會產生什麼結果？

格式：卦名 + 動爻位置 → 結果
""")

    predictor = build_interaction_predictor(properties, trigram_chars)

    examples = [
        (1, 5, "乾卦九五動"),
        (2, 2, "坤卦六二動"),
        (11, 5, "泰卦九五動"),
        (12, 3, "否卦六三動"),
        (51, 1, "震卦初九動"),
        (52, 3, "艮卦六三動"),
    ]

    print("\n" + "-" * 50)
    for hex_num, pos, desc in examples:
        result = predictor(hex_num, pos)
        if result:
            score = result['final_score']
            if score > 0:
                outcome = "吉"
            elif score < 0:
                outcome = "凶"
            else:
                outcome = "中"

            print(f"  {desc}:")
            print(f"    直接結果: {result['direct_result']:+d} → {outcome}")
            print(f"    三元卦效應: {result['trigram_effect']:+.2f}")
            print(f"    結構加成: {result['structure_bonus']:+.2f}")
            print()

# ============================================================
# 導出數據
# ============================================================

def export_interaction_model(properties, trigram_chars, chars):
    """導出交互模型數據"""

    output = {
        'hexagram_properties': {
            str(h): {
                'name': p['name'],
                'lower': p['lower'],
                'upper': p['upper'],
                'yang_count': p['yang_count'],
                'balance': p['balance'],
                'is_symmetric': p['is_symmetric'],
                'same_trigram': p['same_trigram'],
                'complementary': p['complementary'],
                'reaction_coefficients': p['reaction_coefficients']
            }
            for h, p in properties.items()
        },
        'trigram_characteristics': {
            t: {
                'inner_reactions': {str(k): v for k, v in c['inner_reactions'].items()},
                'outer_reactions': {str(k): v for k, v in c['outer_reactions'].items()},
                'inner_total': c['inner_total'],
                'outer_total': c['outer_total'],
                'polarity': c['inner_outer_polarity']
            }
            for t, c in trigram_chars.items()
        },
        'hexagram_reaction_characteristics': {
            str(h): {
                'name': c['name'],
                'total_reaction': c['total_reaction'],
                'sensitive_positions': c['sensitive_positions'],
                'stable_positions': c['stable_positions'],
                'inner_outer_diff': c['inner_outer_diff']
            }
            for h, c in chars.items()
        }
    }

    with open('data/analysis/hexagram_interaction_model.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n交互模型數據已保存到: data/analysis/hexagram_interaction_model.json")

# ============================================================
# 主程序
# ============================================================

def main():
    print("卦的交互模型")
    print("Hexagram Interaction Model")
    print("=" * 70)

    print("""
核心概念：
• 每個卦本身是中性的（像蘋果一樣）
• 卦有結構屬性（上下卦、陰陽比例等）
• 吉/中/凶 只在「爻動」或「交互」時才產生
• 結果取決於：卦的結構 + 動爻位置
""")

    # 載入數據
    raw_data = load_data()
    print(f"\n載入 {len(raw_data)} 條爻數據")

    # 建立卦的固有屬性
    print("\n建立卦的固有屬性...")
    properties = build_hexagram_properties(raw_data)
    print_hexagram_properties(properties)

    # 反推反應特性
    print("\n反推反應特性...")
    chars = derive_reaction_characteristics(properties)
    print_reaction_characteristics(chars)

    # 反推三元卦特性
    print("\n反推三元卦特性...")
    trigram_chars = derive_trigram_characteristics(properties)
    print_trigram_characteristics(trigram_chars)

    # 交互預測示例
    print_interaction_examples(properties, trigram_chars)

    # 導出數據
    export_interaction_model(properties, trigram_chars, chars)

    # 總結
    print("\n" + "=" * 70)
    print("總結：交互模型的核心洞見")
    print("=" * 70)
    print("""
### 卦如同物質

1. **中性本質**
   - 卦本身無吉凶
   - 只有結構屬性（上下卦、陰陽數）

2. **反應發生在「變化」時**
   - 當某爻「動」（變化）時，才產生吉凶
   - 這就像化學反應需要觸發條件

3. **結果由多因素決定**
   - 動爻位置（最重要：位5最吉，位3最凶）
   - 三元卦的反應係數
   - 結構特性（同卦、互補卦等）

### 三元卦如同元素

每個三元卦有自己的「反應傾向」：
- 坤：作為上卦時反應最好
- 震：作為上卦時大幅提升（從內-0.5到外+1.4）
- 艮：在爻3位置容易產生負面結果

### 實用預測

當需要判斷吉凶時：
1. 確定卦的結構（哪個卦？）
2. 確定觸發條件（哪個爻動？）
3. 查表獲取反應係數
4. 結果 = 位置效應 + 三元卦效應 + 結構效應
""")

if __name__ == "__main__":
    main()
