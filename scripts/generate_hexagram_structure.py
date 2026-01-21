#!/usr/bin/env python3
"""Generate structured hexagram data with binary representations and relationships"""
import json
from pathlib import Path

# Trigram data (八卦)
TRIGRAMS = {
    '111': {'name': '乾', 'pinyin': 'qian', 'nature': '天', 'attribute': '健', 'family': '父', 'direction': '西北', 'element': '金'},
    '000': {'name': '坤', 'pinyin': 'kun', 'nature': '地', 'attribute': '順', 'family': '母', 'direction': '西南', 'element': '土'},
    '100': {'name': '震', 'pinyin': 'zhen', 'nature': '雷', 'attribute': '動', 'family': '長男', 'direction': '東', 'element': '木'},
    '011': {'name': '巽', 'pinyin': 'xun', 'nature': '風', 'attribute': '入', 'family': '長女', 'direction': '東南', 'element': '木'},
    '010': {'name': '坎', 'pinyin': 'kan', 'nature': '水', 'attribute': '陷', 'family': '中男', 'direction': '北', 'element': '水'},
    '101': {'name': '離', 'pinyin': 'li', 'nature': '火', 'attribute': '麗', 'family': '中女', 'direction': '南', 'element': '火'},
    '001': {'name': '艮', 'pinyin': 'gen', 'nature': '山', 'attribute': '止', 'family': '少男', 'direction': '東北', 'element': '土'},
    '110': {'name': '兌', 'pinyin': 'dui', 'nature': '澤', 'attribute': '說', 'family': '少女', 'direction': '西', 'element': '金'},
}

# King Wen sequence (文王序卦) - traditional order
# Format: (hexagram_number, chinese_name, binary_representation)
# Binary: bottom line first (line 1) to top (line 6)
KING_WEN_SEQUENCE = [
    (1, '乾', '111111'),   (2, '坤', '000000'),
    (3, '屯', '100010'),   (4, '蒙', '010001'),
    (5, '需', '111010'),   (6, '訟', '010111'),
    (7, '師', '010000'),   (8, '比', '000010'),
    (9, '小畜', '111011'), (10, '履', '110111'),
    (11, '泰', '111000'),  (12, '否', '000111'),
    (13, '同人', '101111'), (14, '大有', '111101'),
    (15, '謙', '001000'),  (16, '豫', '000100'),
    (17, '隨', '100110'),  (18, '蠱', '011001'),
    (19, '臨', '110000'),  (20, '觀', '000011'),
    (21, '噬嗑', '100101'), (22, '賁', '101001'),
    (23, '剝', '000001'),  (24, '復', '100000'),
    (25, '無妄', '100111'), (26, '大畜', '111001'),
    (27, '頤', '100001'),  (28, '大過', '011110'),
    (29, '坎', '010010'),  (30, '離', '101101'),
    (31, '咸', '001110'),  (32, '恆', '011100'),
    (33, '遯', '001111'),  (34, '大壯', '111100'),
    (35, '晉', '000101'),  (36, '明夷', '101000'),
    (37, '家人', '101011'), (38, '睽', '110101'),
    (39, '蹇', '001010'),  (40, '解', '010100'),
    (41, '損', '110001'),  (42, '益', '100011'),
    (43, '夬', '111110'),  (44, '姤', '011111'),
    (45, '萃', '000110'),  (46, '升', '011000'),
    (47, '困', '010110'),  (48, '井', '011010'),
    (49, '革', '101110'),  (50, '鼎', '011101'),
    (51, '震', '100100'),  (52, '艮', '001001'),
    (53, '漸', '001011'),  (54, '歸妹', '110100'),
    (55, '豐', '101100'),  (56, '旅', '001101'),
    (57, '巽', '011011'),  (58, '兌', '110110'),
    (59, '渙', '010011'),  (60, '節', '110010'),
    (61, '中孚', '110011'), (62, '小過', '001100'),
    (63, '既濟', '101010'), (64, '未濟', '010101'),
]

def binary_to_decimal(binary_str):
    """Convert binary string to decimal (treating bottom line as LSB)"""
    return int(binary_str, 2)

def get_trigram(binary_str, position):
    """Get upper (4-6) or lower (1-3) trigram from hexagram binary"""
    if position == 'upper':
        return binary_str[3:6]  # lines 4,5,6
    else:
        return binary_str[0:3]  # lines 1,2,3

def get_nuclear_trigram(binary_str, position):
    """Get nuclear trigrams (互卦): lines 2-3-4 (lower) and 3-4-5 (upper)"""
    if position == 'upper':
        return binary_str[2:5]  # lines 3,4,5
    else:
        return binary_str[1:4]  # lines 2,3,4

def get_inverse(binary_str):
    """Get 180° rotation (翻轉)"""
    return binary_str[::-1]

def get_complement(binary_str):
    """Get all lines flipped (錯卦)"""
    return ''.join('1' if c == '0' else '0' for c in binary_str)

def count_yang_lines(binary_str):
    """Count yang (1) lines"""
    return binary_str.count('1')

def get_fuxi_position(binary_str):
    """Fu Xi position is simply the decimal value + 1 (1-indexed)"""
    # Note: In Fu Xi arrangement, the binary is read differently
    # Fu Xi reads from top to bottom, so we reverse
    reversed_binary = binary_str[::-1]
    return int(reversed_binary, 2)

def find_hexagram_by_binary(binary_str, sequence):
    """Find King Wen number for a given binary"""
    for num, name, binary in sequence:
        if binary == binary_str:
            return num
    return None

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    output_dir = base_dir / 'data/structure'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build hexagram data
    hexagrams = {}

    for kw_num, name, binary in KING_WEN_SEQUENCE:
        lower_tri = get_trigram(binary, 'lower')
        upper_tri = get_trigram(binary, 'upper')
        nuclear_lower = get_nuclear_trigram(binary, 'lower')
        nuclear_upper = get_nuclear_trigram(binary, 'upper')

        inverse_binary = get_inverse(binary)
        complement_binary = get_complement(binary)

        inverse_kw = find_hexagram_by_binary(inverse_binary, KING_WEN_SEQUENCE)
        complement_kw = find_hexagram_by_binary(complement_binary, KING_WEN_SEQUENCE)

        hexagrams[kw_num] = {
            'king_wen_number': kw_num,
            'name': name,
            'binary': binary,
            'decimal': binary_to_decimal(binary),
            'fuxi_position': get_fuxi_position(binary),

            # Trigrams
            'lower_trigram': {
                'binary': lower_tri,
                **TRIGRAMS.get(lower_tri, {})
            },
            'upper_trigram': {
                'binary': upper_tri,
                **TRIGRAMS.get(upper_tri, {})
            },

            # Nuclear trigrams (互卦)
            'nuclear_lower_trigram': {
                'binary': nuclear_lower,
                **TRIGRAMS.get(nuclear_lower, {})
            },
            'nuclear_upper_trigram': {
                'binary': nuclear_upper,
                **TRIGRAMS.get(nuclear_upper, {})
            },

            # Relationships
            'inverse_hexagram': inverse_kw,  # 180° rotation
            'complement_hexagram': complement_kw,  # all lines flipped
            'is_symmetric': binary == inverse_binary,

            # Properties
            'yang_count': count_yang_lines(binary),
            'yin_count': 6 - count_yang_lines(binary),
            'canon': 'upper' if kw_num <= 30 else 'lower',
            'pair': (kw_num + 1) // 2,

            # Individual lines (for later population)
            'lines': [
                {'position': i+1, 'type': 'yang' if binary[i] == '1' else 'yin'}
                for i in range(6)
            ]
        }

    # Save hexagram structure
    hexagram_file = output_dir / 'hexagrams_structure.json'
    with open(hexagram_file, 'w', encoding='utf-8') as f:
        json.dump(hexagrams, f, ensure_ascii=False, indent=2)
    print(f"Saved hexagram structure to {hexagram_file}")

    # Save trigram data
    trigram_file = output_dir / 'trigrams.json'
    with open(trigram_file, 'w', encoding='utf-8') as f:
        json.dump(TRIGRAMS, f, ensure_ascii=False, indent=2)
    print(f"Saved trigram data to {trigram_file}")

    # Generate transformation graph (single line changes)
    transformations = []
    for kw_num, name, binary in KING_WEN_SEQUENCE:
        for i in range(6):
            # Flip one line
            new_binary = list(binary)
            new_binary[i] = '1' if new_binary[i] == '0' else '0'
            new_binary = ''.join(new_binary)

            target_kw = find_hexagram_by_binary(new_binary, KING_WEN_SEQUENCE)
            if target_kw:
                transformations.append({
                    'from_hexagram': kw_num,
                    'to_hexagram': target_kw,
                    'changed_line': i + 1,
                    'from_binary': binary,
                    'to_binary': new_binary
                })

    transform_file = output_dir / 'transformations.json'
    with open(transform_file, 'w', encoding='utf-8') as f:
        json.dump(transformations, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(transformations)} transformations to {transform_file}")

    # Generate sequence comparison (Fu Xi vs King Wen)
    sequences = {
        'king_wen': [(h['king_wen_number'], h['name'], h['binary']) for h in hexagrams.values()],
        'fuxi': sorted(
            [(h['fuxi_position'], h['name'], h['binary'], h['king_wen_number'])
             for h in hexagrams.values()],
            key=lambda x: x[0]
        )
    }

    sequence_file = output_dir / 'sequences.json'
    with open(sequence_file, 'w', encoding='utf-8') as f:
        json.dump(sequences, f, ensure_ascii=False, indent=2)
    print(f"Saved sequence comparison to {sequence_file}")

    # Statistics
    print("\n=== Statistics ===")
    symmetric = sum(1 for h in hexagrams.values() if h['is_symmetric'])
    print(f"Symmetric hexagrams (翻轉不變): {symmetric}")
    print(f"Total transformations: {len(transformations)}")

    # Yang count distribution
    yang_dist = {}
    for h in hexagrams.values():
        yc = h['yang_count']
        yang_dist[yc] = yang_dist.get(yc, 0) + 1
    print(f"Yang line distribution: {yang_dist}")

if __name__ == '__main__':
    main()
