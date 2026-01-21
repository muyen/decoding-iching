#!/usr/bin/env python3
"""
易經化學預測器 - I Ching Chemistry Predictor
Based on reverse-engineered patterns from 384 yao analysis

Formula v5.0:
  Score = Inner[下卦] + Outer[上卦] + Position[爻位]
        + Special + 應 + 陰乘陽 + 三位陽爻

Accuracy: 51.8% (vs 33.3% baseline, +18.5% improvement)
"""

import json
import os
from typing import Tuple, Dict, Optional

# Trigram mappings
TRIGRAM_BINARY = {
    '111': '乾', '000': '坤', '001': '震', '110': '巽',
    '010': '坎', '101': '離', '100': '艮', '011': '兌'
}

TRIGRAM_NAMES = {
    '乾': 'Heaven', '坤': 'Earth', '震': 'Thunder', '巽': 'Wind',
    '坎': 'Water', '離': 'Fire', '艮': 'Mountain', '兌': 'Lake'
}

# Inner trigram effect (下卦效應)
INNER_EFFECT = {
    '坤': +2.25,  # Earth - best foundation
    '乾': +1.38,  # Heaven
    '兌': +1.38,  # Lake
    '離': +1.25,  # Fire
    '震': +1.00,  # Thunder
    '坎': +0.88,  # Water
    '巽': +0.62,  # Wind
    '艮': -0.12,  # Mountain - worst foundation
}

# Outer trigram effect (上卦效應)
OUTER_EFFECT = {
    '巽': +1.50,  # Wind - best above
    '離': +1.50,  # Fire
    '乾': +1.38,  # Heaven
    '坤': +1.38,  # Earth
    '震': +0.88,  # Thunder
    '坎': +0.88,  # Water
    '兌': +0.75,  # Lake
    '艮': +0.38,  # Mountain - lowest above
}

# Position effect (爻位效應)
POSITION_EFFECT = {
    5: +0.52,  # 九五之尊 - best
    2: +0.47,  # 六二中正 - second best
    1: +0.23,  # 初爻
    4: +0.17,  # 四爻
    6: +0.03,  # 上爻
    3: -0.50,  # 三多凶 - worst
}


def get_trigrams(binary: str) -> Tuple[str, str]:
    """Extract lower and upper trigrams from 6-bit binary string."""
    if len(binary) != 6:
        raise ValueError(f"Binary must be 6 characters, got {len(binary)}")
    lower = binary[3:]  # positions 1-3
    upper = binary[:3]  # positions 4-6
    return TRIGRAM_BINARY.get(lower, '?'), TRIGRAM_BINARY.get(upper, '?')


def get_yao_yinyang(binary: str, position: int) -> int:
    """Get if yao is yang (1) or yin (0)."""
    return int(binary[6 - position])


def is_ying_proper(binary: str, position: int) -> bool:
    """Check if 應 (corresponding) is proper (one yin, one yang)."""
    corresp_map = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corresp_pos = corresp_map[position]
    my_yy = get_yao_yinyang(binary, position)
    corresp_yy = get_yao_yinyang(binary, corresp_pos)
    return my_yy != corresp_yy


def is_yin_cheng_yang(binary: str, position: int) -> bool:
    """Check if yin yao is below yang yao (陰乘陽)."""
    if position >= 6:
        return False
    my_yy = get_yao_yinyang(binary, position)
    above_yy = get_yao_yinyang(binary, position + 1)
    return my_yy == 0 and above_yy == 1


def calculate_score(binary: str, position: int) -> Optional[float]:
    """Calculate the chemistry score for a yao."""
    lower, upper = get_trigrams(binary)

    # Base score
    score = INNER_EFFECT.get(lower, 0) + OUTER_EFFECT.get(upper, 0)

    # Position effect
    score += POSITION_EFFECT.get(position, 0)

    # Special rules for pure hexagrams
    if lower == upper:
        if lower == '乾':
            return None  # Pure yang - return neutral
        elif lower == '艮':
            score -= 2.0  # Double mountain - worst
        elif lower == '坎':
            score -= 1.0  # Double water - danger

    # Best combinations bonus
    if lower == '坤' and upper in ['震', '巽']:
        score += 1.0

    # 應 effect (NEW in v4)
    if is_ying_proper(binary, position):
        score += 0.25

    # 陰乘陽 effect (NEW in v4)
    if is_yin_cheng_yang(binary, position):
        score += 0.15

    # 三位陽爻 penalty (NEW in v5)
    if position == 3 and get_yao_yinyang(binary, position) == 1:
        score -= 0.30

    return score


def predict(binary: str, position: int) -> Tuple[str, float, str]:
    """
    Predict 吉凶 based on trigram chemistry.

    Returns:
        (prediction, score, explanation)
    """
    score = calculate_score(binary, position)

    if score is None:
        return ('中', 0, '純陽不生 - 乾卦六爻皆中')

    factors = []
    lower, upper = get_trigrams(binary)
    factors.append(f"內{lower} 外{upper}")

    if is_ying_proper(binary, position):
        factors.append("有應")
    if is_yin_cheng_yang(binary, position):
        factors.append("陰乘陽")
    if position == 3 and get_yao_yinyang(binary, position) == 1:
        factors.append("三位陽爻凶")

    if score > 2.8:
        prediction = '吉'
        explanation = f'Score {score:.2f} > 2.8 ({", ".join(factors)})'
    elif score < 1.2:
        prediction = '凶'
        explanation = f'Score {score:.2f} < 1.2 ({", ".join(factors)})'
    else:
        prediction = '中'
        explanation = f'Score {score:.2f} in [1.2, 2.8] ({", ".join(factors)})'

    return (prediction, score, explanation)


def predict_hexagram(binary: str) -> Dict:
    """Predict all 6 yaos of a hexagram."""
    lower, upper = get_trigrams(binary)

    results = {
        'hexagram': f'{lower}+{upper}',
        'lower': {'name': lower, 'english': TRIGRAM_NAMES[lower]},
        'upper': {'name': upper, 'english': TRIGRAM_NAMES[upper]},
        'yaos': {}
    }

    for pos in range(1, 7):
        pred, score, expl = predict(binary, pos)
        results['yaos'][pos] = {
            'prediction': pred,
            'score': score,
            'explanation': expl
        }

    return results


def print_chemistry_table():
    """Print the full 8x8 chemistry reaction table."""
    trigrams = ['乾', '坤', '震', '巽', '坎', '離', '艮', '兌']

    print("=" * 70)
    print("八卦組合化學反應表")
    print("=" * 70)
    print("\n內卦（下）→")
    print("外卦（上）↓   ", end="")
    for t in trigrams:
        print(f"{t:>6}", end="")
    print("\n" + "-" * 70)

    for upper in trigrams:
        print(f"  {upper}        ", end="")
        for lower in trigrams:
            # Use a sample binary for this combination
            lower_bin = [k for k, v in TRIGRAM_BINARY.items() if v == lower][0]
            upper_bin = [k for k, v in TRIGRAM_BINARY.items() if v == upper][0]
            binary = upper_bin + lower_bin
            score = calculate_score(binary, 3)  # Use position 3 as neutral
            if score is None:
                print(f"{'中':>6}", end="")
            else:
                if score > 3:
                    marker = "★★"
                elif score > 2:
                    marker = "★ "
                elif score < 1:
                    marker = "✗✗"
                elif score < 2:
                    marker = "✗ "
                else:
                    marker = "  "
                print(f"{score:>4.1f}{marker}", end="")
        print()


# Example usage and testing
if __name__ == '__main__':
    print("=" * 70)
    print("易經化學預測器 v5.0")
    print("=" * 70)

    # Test cases
    test_cases = [
        ('000001', '謙', 5),  # 坤+震, position 5
        ('010010', '坎', 3),  # 坎+坎, position 3
        ('111111', '乾', 5),  # 乾+乾, position 5
        ('100100', '艮', 1),  # 艮+艮, position 1
    ]

    print("\n測試案例:")
    print("-" * 70)
    for binary, name, pos in test_cases:
        pred, score, expl = predict(binary, pos)
        print(f"{name}卦 {pos}爻: {expl} → {pred}")

    print("\n")
    print_chemistry_table()

    # Validate against actual data
    print("\n" + "=" * 70)
    print("驗證準確率")
    print("=" * 70)

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, '../data/analysis/corrected_yaoci_labels.json')
        with open(data_path, 'r') as f:
            data = json.load(f)

        correct = 0
        total = 0

        for entry in data:
            binary = entry['binary']
            pos = entry['position']
            actual = entry['label']

            pred, score, _ = predict(binary, pos)

            # Map prediction to numeric
            pred_num = {'吉': 1, '中': 0, '凶': -1}[pred]

            if pred_num == actual:
                correct += 1
            total += 1

        print(f"\n準確率: {correct}/{total} = {correct/total*100:.1f}%")
        print(f"隨機基線: 33.3%")
        print(f"提升: +{(correct/total - 0.333)*100:.1f}%")

    except FileNotFoundError:
        print("(數據文件未找到，跳過驗證)")
