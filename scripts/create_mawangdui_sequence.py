#!/usr/bin/env python3
"""Create Mawangdui (馬王堆帛書) hexagram sequence data

The Mawangdui silk manuscript (168 BCE) arranges hexagrams differently from King Wen.
In Mawangdui, hexagrams are grouped by UPPER trigram, with each group of 8 starting
with the pure hexagram (where upper = lower trigram).

This is based on academic reconstructions from Edward Shaughnessy and others.
"""
import json
from pathlib import Path

# Mawangdui sequence: organized by upper trigram
# Each group of 8 shares the same upper trigram
# Within each group, the pure hexagram (same upper/lower) comes first

# Trigram names and their binaries (bottom to top reading)
TRIGRAMS = {
    '乾': '111',  # Heaven
    '艮': '001',  # Mountain
    '坎': '010',  # Water
    '震': '100',  # Thunder
    '坤': '000',  # Earth
    '兌': '110',  # Lake
    '離': '101',  # Fire
    '巽': '011',  # Wind
}

# Mawangdui uses different character variants for some hexagram names
# This is the reconstructed sequence based on scholarship

# The Mawangdui order groups by UPPER trigram
# Order of upper trigrams: 乾, 艮, 坎, 震, 坤, 兌, 離, 巽
# Within each group, order of lower trigrams: same as upper, then others

def create_hexagram_binary(upper_tri, lower_tri):
    """Create 6-bit binary from upper and lower trigrams"""
    return lower_tri + upper_tri  # lower bits first, then upper

# Mawangdui sequence reconstruction
# Based on the pattern: upper trigram constant, lower trigram varies
# The order within each octet starts with the pure hexagram

MAWANGDUI_SEQUENCE = []

# Upper trigram order in Mawangdui
upper_order = ['乾', '艮', '坎', '震', '坤', '兌', '離', '巽']

# Lower trigram order within each group (starts with matching upper)
def get_lower_order(upper):
    """Get the order of lower trigrams for a given upper trigram"""
    # Based on Mawangdui pattern: starts with pure, then follows a specific order
    # This varies slightly but generally follows: matching, then complement pairs
    base_order = ['乾', '坤', '艮', '兌', '坎', '離', '震', '巽']
    # Rotate so the matching trigram comes first
    idx = base_order.index(upper)
    return [upper] + [t for t in base_order if t != upper]

# King Wen hexagram names lookup
KING_WEN_NAMES = {
    '111111': '乾', '000000': '坤',
    '100010': '屯', '010001': '蒙',
    '111010': '需', '010111': '訟',
    '010000': '師', '000010': '比',
    '111011': '小畜', '110111': '履',
    '111000': '泰', '000111': '否',
    '101111': '同人', '111101': '大有',
    '001000': '謙', '000100': '豫',
    '100110': '隨', '011001': '蠱',
    '110000': '臨', '000011': '觀',
    '100101': '噬嗑', '101001': '賁',
    '000001': '剝', '100000': '復',
    '100111': '無妄', '111001': '大畜',
    '100001': '頤', '011110': '大過',
    '010010': '坎', '101101': '離',
    '001110': '咸', '011100': '恆',
    '001111': '遯', '111100': '大壯',
    '000101': '晉', '101000': '明夷',
    '101011': '家人', '110101': '睽',
    '001010': '蹇', '010100': '解',
    '110001': '損', '100011': '益',
    '111110': '夬', '011111': '姤',
    '000110': '萃', '011000': '升',
    '010110': '困', '011010': '井',
    '101110': '革', '011101': '鼎',
    '100100': '震', '001001': '艮',
    '001011': '漸', '110100': '歸妹',
    '101100': '豐', '001101': '旅',
    '011011': '巽', '110110': '兌',
    '010011': '渙', '110010': '節',
    '110011': '中孚', '001100': '小過',
    '101010': '既濟', '010101': '未濟',
}

# Build Mawangdui sequence
mw_position = 1
for upper in upper_order:
    upper_bin = TRIGRAMS[upper]
    lower_sequence = get_lower_order(upper)

    for lower in lower_sequence:
        lower_bin = TRIGRAMS[lower]
        binary = create_hexagram_binary(upper_bin, lower_bin)
        name = KING_WEN_NAMES.get(binary, '?')

        MAWANGDUI_SEQUENCE.append({
            'mawangdui_position': mw_position,
            'name': name,
            'binary': binary,
            'upper_trigram': upper,
            'lower_trigram': lower,
        })
        mw_position += 1

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    output_dir = base_dir / 'data/structure'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save Mawangdui sequence
    mw_file = output_dir / 'mawangdui_sequence.json'

    output_data = {
        'title': '馬王堆帛書易經卦序',
        'english_title': 'Mawangdui Silk Manuscript Hexagram Sequence',
        'date': '168 BCE (burial date)',
        'description': 'The Mawangdui silk manuscript arranges hexagrams by upper trigram, '
                      'different from the King Wen sequence. Each group of 8 hexagrams shares '
                      'the same upper trigram, starting with the pure hexagram.',
        'source': 'Reconstructed from academic sources (Shaughnessy 1997, et al.)',
        'note': 'The exact order within each octet is somewhat uncertain; this follows '
               'the most common scholarly reconstruction.',
        'organization': {
            'principle': 'Grouped by upper trigram',
            'upper_trigram_order': upper_order,
            'octets': 8,
            'hexagrams_per_octet': 8,
        },
        'sequence': MAWANGDUI_SEQUENCE,
    }

    with open(mw_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Saved Mawangdui sequence to {mw_file}")
    print(f"Total hexagrams: {len(MAWANGDUI_SEQUENCE)}")

    # Create comparison file
    comparison = []
    king_wen_lookup = {}
    for kw_pos, (num, name, binary) in enumerate([
        (1, '乾', '111111'), (2, '坤', '000000'),
        (3, '屯', '100010'), (4, '蒙', '010001'),
        (5, '需', '111010'), (6, '訟', '010111'),
        (7, '師', '010000'), (8, '比', '000010'),
        (9, '小畜', '111011'), (10, '履', '110111'),
        (11, '泰', '111000'), (12, '否', '000111'),
        (13, '同人', '101111'), (14, '大有', '111101'),
        (15, '謙', '001000'), (16, '豫', '000100'),
        (17, '隨', '100110'), (18, '蠱', '011001'),
        (19, '臨', '110000'), (20, '觀', '000011'),
        (21, '噬嗑', '100101'), (22, '賁', '101001'),
        (23, '剝', '000001'), (24, '復', '100000'),
        (25, '無妄', '100111'), (26, '大畜', '111001'),
        (27, '頤', '100001'), (28, '大過', '011110'),
        (29, '坎', '010010'), (30, '離', '101101'),
        (31, '咸', '001110'), (32, '恆', '011100'),
        (33, '遯', '001111'), (34, '大壯', '111100'),
        (35, '晉', '000101'), (36, '明夷', '101000'),
        (37, '家人', '101011'), (38, '睽', '110101'),
        (39, '蹇', '001010'), (40, '解', '010100'),
        (41, '損', '110001'), (42, '益', '100011'),
        (43, '夬', '111110'), (44, '姤', '011111'),
        (45, '萃', '000110'), (46, '升', '011000'),
        (47, '困', '010110'), (48, '井', '011010'),
        (49, '革', '101110'), (50, '鼎', '011101'),
        (51, '震', '100100'), (52, '艮', '001001'),
        (53, '漸', '001011'), (54, '歸妹', '110100'),
        (55, '豐', '101100'), (56, '旅', '001101'),
        (57, '巽', '011011'), (58, '兌', '110110'),
        (59, '渙', '010011'), (60, '節', '110010'),
        (61, '中孚', '110011'), (62, '小過', '001100'),
        (63, '既濟', '101010'), (64, '未濟', '010101'),
    ], 1):
        king_wen_lookup[binary] = {'position': num, 'name': name}

    for mw_hex in MAWANGDUI_SEQUENCE:
        kw_data = king_wen_lookup.get(mw_hex['binary'], {})
        comparison.append({
            'name': mw_hex['name'],
            'binary': mw_hex['binary'],
            'mawangdui_position': mw_hex['mawangdui_position'],
            'king_wen_position': kw_data.get('position'),
            'position_difference': abs(mw_hex['mawangdui_position'] - kw_data.get('position', 0)) if kw_data else None,
        })

    comparison_file = output_dir / 'sequence_comparison.json'
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump({
            'title': '卦序比較 (Sequence Comparison)',
            'sequences_compared': ['馬王堆 (Mawangdui)', '文王 (King Wen)'],
            'comparison': comparison,
        }, f, ensure_ascii=False, indent=2)

    print(f"Saved sequence comparison to {comparison_file}")

    # Statistics
    same_position = sum(1 for c in comparison if c['position_difference'] == 0)
    print(f"\nHexagrams in same position in both sequences: {same_position}")

if __name__ == '__main__':
    main()
