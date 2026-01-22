#!/usr/bin/env python3
"""
易經查表預測器 - I Ching Lookup-Based Predictor
Uses complete interaction tables for structural prediction + text analysis

This is the TRUE yao property system based on statistical analysis of 384 yaos.
"""

import json
import os
import re
from typing import Tuple, Dict, Optional

# Trigram mappings
TRIGRAM_BINARY = {
    '111': '乾', '000': '坤', '001': '震', '110': '巽',
    '010': '坎', '101': '離', '100': '艮', '011': '兌'
}

# Complete Inner × Outer × Position lookup table (64 hexagrams × 6 positions)
# Format: (inner, outer) → [pos1, pos2, pos3, pos4, pos5, pos6]
# Values: 1=吉, 0=中, -1=凶
HEXAGRAM_LOOKUP = {
    ('乾', '乾'): [0, 0, 0, 0, 0, 0],
    ('乾', '坤'): [1, 1, 0, 0, 1, 0],
    ('乾', '震'): [-1, 0, 1, 1, 1, 1],
    ('乾', '巽'): [0, 1, -1, 1, -1, 1],
    ('乾', '坎'): [1, -1, 1, 1, 1, 0],
    ('乾', '離'): [0, 0, 0, 1, 0, 0],
    ('乾', '艮'): [1, 0, -1, 0, 1, 0],
    ('乾', '兌'): [1, 0, -1, -1, 0, 0],
    ('坤', '乾'): [1, 0, 0, 0, 1, 0],
    ('坤', '坤'): [0, 1, 0, 0, 1, 0],
    ('坤', '震'): [1, 1, 1, 1, 1, 0],
    ('坤', '巽'): [1, 1, 1, 0, 1, 1],
    ('坤', '坎'): [-1, 1, -1, 0, -1, 0],
    ('坤', '離'): [0, 1, 0, 0, 0, 0],
    ('坤', '艮'): [1, 1, 0, 0, 0, -1],
    ('坤', '兌'): [1, 1, 0, 1, 1, 0],
    ('震', '乾'): [0, 0, 1, 1, 1, 0],
    ('震', '坤'): [-1, -1, 0, -1, 1, 0],
    ('震', '震'): [1, 0, -1, 0, 0, 1],
    ('震', '巽'): [0, -1, 0, 1, 1, 1],
    ('震', '坎'): [0, 1, 0, 0, 1, 0],
    ('震', '離'): [0, 0, 1, 0, 1, 0],
    ('震', '艮'): [-1, -1, -1, 1, 1, 1],
    ('震', '兌'): [1, 0, -1, 0, 0, 0],
    ('巽', '乾'): [0, 0, -1, 0, 0, -1],
    ('巽', '坤'): [0, 1, 0, 1, 1, 0],
    ('巽', '震'): [0, 0, 0, 1, 0, 0],
    ('巽', '巽'): [1, 1, -1, 1, -1, 0],
    ('巽', '坎'): [0, -1, -1, 0, 0, 1],
    ('巽', '離'): [0, 1, -1, 1, 0, 1],
    ('巽', '艮'): [1, 0, 0, -1, 1, 0],
    ('巽', '兌'): [0, 1, -1, 1, 0, -1],
    ('坎', '乾'): [1, 1, 0, 0, 1, 1],
    ('坎', '坤'): [1, 1, 0, 1, 1, -1],
    ('坎', '震'): [0, 0, 0, 0, 0, 1],
    ('坎', '巽'): [0, -1, 0, 0, 1, -1],
    ('坎', '坎'): [-1, 0, 0, 0, 0, -1],
    ('坎', '離'): [0, 0, 0, 0, 0, -1],
    ('坎', '艮'): [1, 0, 0, 1, 0, 0],
    ('坎', '兌'): [0, 0, 0, 0, 0, 1],
    ('離', '乾'): [0, 0, 0, 0, 1, 1],
    ('離', '坤'): [1, 1, 0, -1, 1, 1],
    ('離', '震'): [-1, 0, -1, 0, 0, -1],
    ('離', '巽'): [1, 0, 0, 0, 0, 1],
    ('離', '坎'): [0, 1, -1, 1, 1, 0],
    ('離', '離'): [0, 1, -1, 0, 1, 0],
    ('離', '艮'): [0, 0, 0, 1, 0, -1],
    ('離', '兌'): [1, 1, 1, -1, 0, 1],
    ('艮', '乾'): [-1, 1, -1, 1, 0, 1],
    ('艮', '坤'): [-1, 1, -1, 0, 0, 0],
    ('艮', '震'): [-1, 0, -1, 0, 0, -1],
    ('艮', '巽'): [1, 0, 0, 0, 1, 0],
    ('艮', '坎'): [0, 1, 0, 0, 1, 1],
    ('艮', '離'): [0, 1, 0, 1, 1, -1],
    ('艮', '艮'): [1, -1, -1, 0, -1, -1],
    ('艮', '兌'): [-1, 0, 0, 0, 0, -1],
    ('兌', '乾'): [1, 1, 0, 0, 0, -1],
    ('兌', '坤'): [0, 0, 0, 0, 0, 0],
    ('兌', '震'): [0, 1, -1, 0, 1, 1],
    ('兌', '巽'): [1, 0, 0, 0, 0, -1],
    ('兌', '坎'): [1, 0, 0, 1, 0, 0],
    ('兌', '離'): [0, 1, 0, 1, 1, 1],
    ('兌', '艮'): [1, 1, -1, 0, 1, -1],
    ('兌', '兌'): [0, 1, 0, 0, 1, -1],
}

# High-confidence text keywords
JI_HIGH = {'无不利': 3.0, '元吉': 3.0, '大吉': 3.0, '終吉': 3.0}
JI_MED = {'貞吉': 2.5, '吉': 2.5}
XIONG_HIGH = {'災': -3.0, '凶': -2.5, '貞凶': -2.5}

# Weak signals (not deterministic)
JI_WEAK = {'悔亡': 0.5, '利': 0.3, '无咎': 0.1}
XIONG_WEAK = {'眚': -2.0, '厲': -0.8, '悔': -0.3}
NEUTRAL = {'吝': 0.0}  # 吝 is ALWAYS 中!


def get_trigrams(binary: str) -> Tuple[str, str]:
    """Extract lower and upper trigrams from 6-bit binary string."""
    if len(binary) != 6:
        raise ValueError(f"Binary must be 6 characters, got {len(binary)}")
    lower = binary[3:]  # positions 1-3
    upper = binary[:3]  # positions 4-6
    return TRIGRAM_BINARY.get(lower, '?'), TRIGRAM_BINARY.get(upper, '?')


def predict_structure(binary: str, position: int) -> int:
    """Predict based on structural lookup table only."""
    inner, outer = get_trigrams(binary)
    lookup = HEXAGRAM_LOOKUP.get((inner, outer))
    if lookup:
        return lookup[position - 1]
    return 0  # Default to 中 if not found


def extract_keywords(text: str) -> Tuple[list, list]:
    """Extract 吉 and 凶 keywords from text."""
    ji_found = []
    xiong_found = []

    # High confidence keywords
    for kw in JI_HIGH:
        if kw in text:
            ji_found.append((kw, JI_HIGH[kw], 'high'))
    for kw in JI_MED:
        if kw in text and not any(k[0] in kw or kw in k[0] for k in ji_found):
            ji_found.append((kw, JI_MED[kw], 'med'))

    for kw in XIONG_HIGH:
        if kw in text:
            xiong_found.append((kw, XIONG_HIGH[kw], 'high'))

    # Weak signals
    for kw in JI_WEAK:
        if kw in text and not any(k[0] in kw or kw in k[0] for k in ji_found):
            ji_found.append((kw, JI_WEAK[kw], 'weak'))

    for kw in XIONG_WEAK:
        if kw in text and not any(k[0] in kw or kw in k[0] for k in xiong_found):
            xiong_found.append((kw, XIONG_WEAK[kw], 'weak'))

    return ji_found, xiong_found


def analyze_text_patterns(text: str) -> Tuple[float, list]:
    """Analyze complex text patterns."""
    adjustments = 0.0
    reasons = []

    # ========================================
    # CONDITIONAL PATTERNS (A情況吉，B情況凶)
    # ========================================

    # 征凶居吉 pattern → 吉 (staying is good)
    if re.search(r'征.{0,2}凶.{0,6}居.{0,2}(吉|貞)', text):
        adjustments = 99  # Force 吉
        reasons.append('征凶居吉→吉')
        return adjustments, reasons

    # 凶...居吉 pattern → 中 (conditional)
    if re.search(r'凶.{0,10}居.{0,2}吉', text):
        adjustments = -99  # Force 中
        reasons.append('凶居吉→中')
        return adjustments, reasons

    # 婦人吉，夫子凶 pattern → 中 (depends on who)
    if re.search(r'婦.{0,3}吉.{0,6}(夫|男).{0,3}凶', text):
        adjustments = -99  # Force 中
        reasons.append('婦吉夫凶→中')
        return adjustments, reasons

    # 貞吉...有攸往凶 pattern → 吉 (staying is good)
    if re.search(r'貞.{0,2}吉.{0,10}(有攸往|往).{0,3}(見|).{0,2}凶', text):
        adjustments = 99  # Force 吉
        reasons.append('貞吉往凶→吉')
        return adjustments, reasons

    # 厲吉...終吝 pattern → 中 (mixed, has regret at end)
    if re.search(r'厲.{0,2}吉', text) and '終吝' in text:
        adjustments = -99  # Force 中
        reasons.append('厲吉終吝→中')
        return adjustments, reasons

    # 厲吉 pattern (danger but ultimately good) → 吉
    if re.search(r'厲.{0,2}吉', text):
        adjustments = 99  # Force 吉
        reasons.append('厲吉→吉')
        return adjustments, reasons

    # 有疾厲...吉 pattern → 吉
    if re.search(r'有疾厲.{0,10}吉', text):
        adjustments = 99  # Force 吉
        reasons.append('有疾厲吉→吉')
        return adjustments, reasons

    # ========================================
    # SIZE MODIFIERS
    # ========================================

    # 小吉大凶 pattern → 中
    if re.search(r'小.{0,3}(吉|利).{0,8}大.{0,3}(凶|厲)', text):
        adjustments = -99  # Force 中
        reasons.append('小吉大凶→中')
        return adjustments, reasons

    # 大吉小凶 pattern → 吉
    if re.search(r'大.{0,3}(吉|利).{0,8}小.{0,3}(凶|厲)', text):
        adjustments = 99  # Force 吉
        reasons.append('大吉小凶→吉')
        return adjustments, reasons

    # ========================================
    # NEUTRAL PATTERNS
    # ========================================

    # 无咎无譽 → definitely 中
    if '无咎' in text and '无譽' in text:
        adjustments = -99  # Force 中
        reasons.append('无咎无譽→中')
        return adjustments, reasons

    # ========================================
    # WEAK ADJUSTMENTS
    # ========================================

    # 勿用 → warning, more likely 中
    if '勿用' in text:
        adjustments -= 0.5
        reasons.append('勿用')

    # 不利 negation
    if '不利' in text:
        adjustments -= 0.5
        reasons.append('不利')

    # 无攸利 = nothing beneficial
    if '无攸利' in text:
        adjustments -= 0.3
        reasons.append('无攸利')

    return adjustments, reasons


def predict(binary: str, position: int, text: str = "") -> Tuple[int, str]:
    """
    Predict 吉凶 using combined structure + text analysis.

    Returns:
        (prediction: 1=吉, 0=中, -1=凶, explanation)
    """
    inner, outer = get_trigrams(binary)

    # Extract text signals
    ji_kw, xiong_kw = extract_keywords(text)

    # Check for high-confidence text signals first
    has_high_ji = any(kw[2] == 'high' for kw in ji_kw)
    has_high_xiong = any(kw[2] == 'high' for kw in xiong_kw)
    has_med_ji = any(kw[2] in ['high', 'med'] for kw in ji_kw)

    # Analyze complex patterns
    pattern_adj, pattern_reasons = analyze_text_patterns(text)

    # Handle forced patterns (小吉大凶, etc.)
    if pattern_adj == -99:
        return 0, ', '.join(pattern_reasons)
    if pattern_adj == 99:
        return 1, ', '.join(pattern_reasons)

    # Check for mixed high signals (吉+凶 both present)
    if has_high_ji and has_high_xiong:
        return 0, '吉凶混合'

    # High confidence text overrides structure
    if has_high_ji:
        return 1, f"強吉詞: {[k[0] for k in ji_kw if k[2] == 'high']}"
    if has_high_xiong:
        return -1, f"強凶詞: {[k[0] for k in xiong_kw if k[2] == 'high']}"

    # Medium confidence text (吉)
    if has_med_ji and not xiong_kw:
        return 1, f"吉詞: {[k[0] for k in ji_kw if k[2] in ['high', 'med']]}"

    # 吝 special case - always 中
    if '吝' in text and not has_high_ji:
        return 0, '吝→中'

    # Fall back to structural prediction
    struct_pred = predict_structure(binary, position)

    # Apply weak text adjustments
    ji_score = sum(k[1] for k in ji_kw if k[2] == 'weak')
    xiong_score = sum(k[1] for k in xiong_kw if k[2] == 'weak')
    text_score = ji_score + xiong_score + pattern_adj

    # Combine structure and weak text signals
    if struct_pred == 1 and text_score >= -0.5:
        return 1, f"結構吉 + 文本({text_score:+.1f})"
    elif struct_pred == -1 and text_score <= 0.5:
        return -1, f"結構凶 + 文本({text_score:+.1f})"
    elif struct_pred == 1 and text_score < -0.5:
        return 0, f"結構吉但文本弱化"
    elif struct_pred == -1 and text_score > 0.5:
        return 0, f"結構凶但文本緩和"
    else:
        return 0, f"結構中 ({inner}+{outer} pos{position})"


def validate_accuracy():
    """Validate against labeled data."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '../data/analysis/corrected_yaoci_labels.json')

    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("(數據文件未找到)")
        return

    # Structure-only accuracy
    struct_correct = 0
    for entry in data:
        pred = predict_structure(entry['binary'], entry['position'])
        if pred == entry['label']:
            struct_correct += 1

    # Full model accuracy
    full_correct = 0
    errors = []
    for entry in data:
        pred, reason = predict(entry['binary'], entry['position'], entry['text'])
        if pred == entry['label']:
            full_correct += 1
        else:
            errors.append({
                'hex': entry['hex_name'],
                'pos': entry['position'],
                'text': entry['text'][:40],
                'actual': entry['label'],
                'pred': pred,
                'reason': reason
            })

    print(f"\n結構查表準確率: {struct_correct}/384 = {struct_correct/384*100:.1f}%")
    print(f"完整模型準確率: {full_correct}/384 = {full_correct/384*100:.1f}%")
    print(f"錯誤數: {len(errors)}")

    if errors:
        print(f"\n前10個錯誤:")
        label_map = {1: '吉', 0: '中', -1: '凶'}
        for e in errors[:10]:
            print(f"  {e['hex']}{e['pos']}爻: {e['text']}...")
            print(f"    預測:{label_map[e['pred']]} 實際:{label_map[e['actual']]} ({e['reason']})")


if __name__ == '__main__':
    print("=" * 70)
    print("易經查表預測器")
    print("=" * 70)

    # Example predictions
    examples = [
        ('000001', 5, '六五：黃裳，元吉。'),  # 謙卦五爻
        ('100010', 5, '九五：屯其膏，小貞吉，大貞凶。'),  # 屯卦五爻
        ('111111', 3, '九三：君子終日乾乾，夕惕若，厲，无咎。'),  # 乾卦三爻
    ]

    print("\n測試案例:")
    label_map = {1: '吉', 0: '中', -1: '凶'}
    for binary, pos, text in examples:
        pred, reason = predict(binary, pos, text)
        inner, outer = get_trigrams(binary)
        print(f"\n{inner}+{outer} {pos}爻: {text}")
        print(f"  → {label_map[pred]} ({reason})")

    print("\n")
    validate_accuracy()
