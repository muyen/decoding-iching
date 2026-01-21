#!/usr/bin/env python3
"""
正確提取爻辭 - 處理兩種數據格式

問題：
- 卦1-51：content[0]=卦辭, content[1-6]=爻辭
- 卦52-64：content包含彖傳和象傳，結構不同

解決：通過識別爻辭的開頭標記來提取
"""

import json
import os
import re
from collections import defaultdict, Counter

def load_yaoci():
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'ctext', 'zhouyi_64gua.json')
    with open(path, 'r') as f:
        return json.load(f)

def load_structure():
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'structure', 'hexagrams_structure.json')
    with open(path, 'r') as f:
        return json.load(f)

# 爻辭開頭標記 (支持：、:、，作為分隔符)
YAO_PATTERNS = {
    1: [r'^初九[：:，]', r'^初六[：:，]'],
    2: [r'^九二[：:，]', r'^六二[：:，]'],
    3: [r'^九三[：:，]', r'^六三[：:，]'],
    4: [r'^九四[：:，]', r'^六四[：:，]'],
    5: [r'^九五[：:，]', r'^六五[：:，]'],
    6: [r'^上九[：:，]', r'^上六[：:，]'],
}

def extract_yaoci_for_hexagram(content, hex_num):
    """
    從content列表中提取6個爻辭

    Returns:
        dict: {1: '初爻文本', 2: '二爻文本', ...}
    """
    yaoci = {}

    for entry in content:
        for pos, patterns in YAO_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, entry):
                    yaoci[pos] = entry
                    break

    return yaoci

def validate_extraction(yaoci_data, struct_data):
    """驗證提取是否正確"""
    print("=" * 70)
    print("爻辭提取驗證")
    print("=" * 70)

    all_yaoci = []
    missing = []

    for hex_item in yaoci_data['hexagrams']:
        num = hex_item['metadata']['number']
        name = hex_item['title_zh']
        content = hex_item['content_zh']

        struct = struct_data.get(str(num), {})
        binary = struct.get('binary', '000000')

        yaoci = extract_yaoci_for_hexagram(content, num)

        # 檢查是否有6個爻
        if len(yaoci) != 6:
            missing.append({
                'hex': num,
                'name': name,
                'found': list(yaoci.keys()),
                'missing': [p for p in range(1, 7) if p not in yaoci]
            })

        for pos in range(1, 7):
            text = yaoci.get(pos, '')
            all_yaoci.append({
                'hex_num': num,
                'hex_name': name,
                'position': pos,
                'binary': binary,
                'text': text,
                'is_valid': bool(text)
            })

    # 報告結果
    valid_count = sum(1 for y in all_yaoci if y['is_valid'])
    print(f"\n有效爻辭: {valid_count}/384 ({valid_count/384*100:.1f}%)")

    if missing:
        print(f"\n缺失的卦 ({len(missing)}個):")
        for m in missing:
            print(f"  {m['hex']:2d}.{m['name']}: 缺少爻位 {m['missing']}")
    else:
        print("\n✓ 所有64卦都有完整的6爻爻辭")

    return all_yaoci

# ============================================================
# 改進的吉凶分類
# ============================================================

# 正面關鍵詞（按長度排序，長的優先）
JI_KEYWORDS = [
    ('无不利', 0.8),  # 特別處理：沒有不利 = 有利
    ('無不利', 0.8),
    ('元吉', 2.0),
    ('大吉', 2.0),
    ('終吉', 1.5),
    ('貞吉', 1.5),
    ('有喜', 1.0),
    ('有慶', 1.0),
    ('无咎', 0.3),
    ('無咎', 0.3),
    ('悔亡', 0.3),
    ('吉', 1.0),
    ('利', 0.3),
    ('亨', 0.3),
]

# 負面關鍵詞
XIONG_KEYWORDS = [
    ('大凶', -2.0),
    ('終凶', -1.5),
    ('貞凶', -1.5),
    ('往凶', -1.0),
    ('凶', -1.0),
    ('不利', -0.5),
    ('厲', -0.5),
    ('吝', -0.3),
    ('悔', -0.3),
    ('咎', -0.3),
    ('災', -1.0),
    ('眚', -0.5),
]

def classify_yaoci(text):
    """
    從爻辭文本判斷吉凶

    特別處理：
    1. 「无不利」應該是正面的（沒有不利）
    2. 「不利」在「无不利」之後不應重複計算
    3. 「咎」在「无咎」之後不應重複計算
    """
    if not text:
        return (0, 0, 0, [], [])

    ji_score = 0.0
    xiong_score = 0.0
    ji_found = []
    xiong_found = []

    # 追蹤已匹配的位置
    matched_positions = set()

    # 先處理吉關鍵詞（長的優先）
    for kw, weight in JI_KEYWORDS:
        idx = 0
        while True:
            pos = text.find(kw, idx)
            if pos == -1:
                break

            positions = set(range(pos, pos + len(kw)))
            if not positions & matched_positions:
                # 特殊處理：「利」要排除「不利」的情況
                if kw == '利' and pos > 0 and text[pos-1] == '不':
                    idx = pos + 1
                    continue

                ji_score += weight
                ji_found.append(kw)
                matched_positions |= positions

            idx = pos + 1

    # 處理凶關鍵詞
    for kw, weight in XIONG_KEYWORDS:
        idx = 0
        while True:
            pos = text.find(kw, idx)
            if pos == -1:
                break

            positions = set(range(pos, pos + len(kw)))
            if not positions & matched_positions:
                # 特殊處理：「咎」要排除「无咎」
                if kw == '咎' and pos > 0 and text[pos-1] in ['无', '無']:
                    idx = pos + 1
                    continue

                # 特殊處理：「悔」要排除「悔亡」
                if kw == '悔' and pos < len(text)-1 and text[pos+1] == '亡':
                    idx = pos + 1
                    continue

                # 特殊處理：「不利」要排除「无不利」
                if kw == '不利' and pos > 0 and text[pos-1] == '无':
                    idx = pos + 1
                    continue

                xiong_score += weight
                xiong_found.append(kw)
                matched_positions |= positions

            idx = pos + 1

    total = ji_score + xiong_score

    if total > 0.3:
        label = 1
    elif total < -0.3:
        label = -1
    else:
        label = 0

    return (label, ji_score, xiong_score, ji_found, xiong_found)

def analyze_with_corrected_data(yaoci_data, struct_data):
    """使用正確提取的數據進行分析"""
    print("\n" + "=" * 70)
    print("使用正確數據的分析結果")
    print("=" * 70)

    all_yaos = []
    pos_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'zhong': 0, 'xiong': 0})

    for hex_item in yaoci_data['hexagrams']:
        num = hex_item['metadata']['number']
        name = hex_item['title_zh']
        content = hex_item['content_zh']

        struct = struct_data.get(str(num), {})
        binary = struct.get('binary', '000000')

        yaoci = extract_yaoci_for_hexagram(content, num)

        for pos in range(1, 7):
            text = yaoci.get(pos, '')
            if not text:
                continue

            label, ji, xiong, ji_kw, xiong_kw = classify_yaoci(text)

            all_yaos.append({
                'hex_num': num,
                'hex_name': name,
                'position': pos,
                'binary': binary,
                'text': text,
                'label': label,
                'ji_score': ji,
                'xiong_score': xiong,
                'ji_keywords': ji_kw,
                'xiong_keywords': xiong_kw
            })

            pos_stats[pos]['total'] += 1
            if label == 1:
                pos_stats[pos]['ji'] += 1
            elif label == 0:
                pos_stats[pos]['zhong'] += 1
            else:
                pos_stats[pos]['xiong'] += 1

    # 總分布
    labels = [y['label'] for y in all_yaos]
    counter = Counter(labels)

    print(f"\n總樣本: {len(all_yaos)}")
    print(f"\n標籤分布:")
    print(f"  吉 (1):  {counter[1]:3d} ({counter[1]/len(labels)*100:.1f}%)")
    print(f"  中 (0):  {counter[0]:3d} ({counter[0]/len(labels)*100:.1f}%)")
    print(f"  凶 (-1): {counter[-1]:3d} ({counter[-1]/len(labels)*100:.1f}%)")

    baseline = max(counter.values()) / len(labels)
    print(f"\n基線 (多數類別): {baseline:.1%}")

    # 爻位分析
    print("\n" + "-" * 50)
    print("爻位分析 (1D)")
    print("-" * 50)
    print("爻位   總數   吉率    中率    凶率")
    print("-" * 45)
    for pos in range(1, 7):
        s = pos_stats[pos]
        if s['total'] == 0:
            continue
        ji_rate = s['ji'] / s['total'] * 100
        zhong_rate = s['zhong'] / s['total'] * 100
        xiong_rate = s['xiong'] / s['total'] * 100
        print(f"  {pos}    {s['total']:3d}   {ji_rate:5.1f}%  {zhong_rate:5.1f}%  {xiong_rate:5.1f}%")

    return all_yaos

def verify_wubuli_cases(yaoci_data):
    """驗證「无不利」的處理"""
    print("\n" + "=" * 70)
    print("「无不利」案例驗證")
    print("=" * 70)

    for hex_item in yaoci_data['hexagrams']:
        num = hex_item['metadata']['number']
        name = hex_item['title_zh']
        content = hex_item['content_zh']

        yaoci = extract_yaoci_for_hexagram(content, num)

        for pos, text in yaoci.items():
            if '无不利' in text or '無不利' in text:
                label, ji, xiong, ji_kw, xiong_kw = classify_yaoci(text)
                label_str = {1: '吉', 0: '中', -1: '凶'}[label]
                print(f"{num:2d}.{name} 爻{pos}: {label_str} (吉{ji:.1f}, 凶{xiong:.1f}) | {ji_kw} | {xiong_kw}")
                print(f"   → {text[:50]}...")

def main():
    yaoci_data = load_yaoci()
    struct_data = load_structure()

    # 1. 驗證提取
    all_yaoci = validate_extraction(yaoci_data, struct_data)

    # 2. 使用正確數據分析
    all_yaos = analyze_with_corrected_data(yaoci_data, struct_data)

    # 3. 驗證「无不利」處理
    verify_wubuli_cases(yaoci_data)

    # 4. 保存正確的數據
    save_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis', 'corrected_yaoci_labels.json')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(all_yaos, f, ensure_ascii=False, indent=2)

    print(f"\n\n數據已保存至: {save_path}")

if __name__ == "__main__":
    main()
