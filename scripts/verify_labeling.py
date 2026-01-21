#!/usr/bin/env python3
"""
驗證吉凶標籤的準確性

從爻辭文本中提取吉凶判斷，並檢查：
1. 關鍵詞衝突（如「無咎」包含「咎」）
2. 標籤分布
3. 邊界情況
"""

import json
import os
import re
from collections import defaultdict, Counter

def load_yaoci():
    """載入爻辭數據"""
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'ctext', 'zhouyi_64gua.json')
    with open(path, 'r') as f:
        return json.load(f)

def load_structure():
    """載入結構數據"""
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'structure', 'hexagrams_structure.json')
    with open(path, 'r') as f:
        return json.load(f)

# ============================================================
# 吉凶關鍵詞 - 需要按優先順序處理
# ============================================================

# 優先匹配的組合詞（先匹配長的）
JI_PHRASES = [
    ('元吉', 2.0),
    ('大吉', 2.0),
    ('終吉', 1.5),
    ('貞吉', 1.5),
    ('有喜', 1.0),
    ('有慶', 1.0),
    ('无咎', 0.5),  # 無咎 = 沒有災禍，偏中性
    ('無咎', 0.5),
    ('悔亡', 0.5),  # 後悔消失
    ('吉', 1.0),
    ('利', 0.3),
    ('亨', 0.3),
]

XIONG_PHRASES = [
    ('大凶', -2.0),
    ('終凶', -1.5),
    ('貞凶', -1.5),
    ('往凶', -1.0),
    ('凶', -1.0),
    ('厲', -0.5),
    ('吝', -0.3),
    ('悔', -0.3),
    ('咎', -0.3),  # 注意：要在無咎之後檢查
    ('災', -1.0),
    ('眚', -0.5),
]

def classify_yaoci(text):
    """
    從爻辭文本判斷吉凶

    Returns:
        (label, ji_score, xiong_score, keywords_found)
        label: 1=吉, 0=中, -1=凶
    """
    if not text:
        return (0, 0, 0, [])

    # 用於追蹤已匹配的位置，避免重複計算
    matched_positions = set()
    keywords_found = []

    ji_score = 0.0
    xiong_score = 0.0

    # 先處理吉的關鍵詞（優先匹配長詞）
    for phrase, weight in JI_PHRASES:
        start = 0
        while True:
            pos = text.find(phrase, start)
            if pos == -1:
                break
            # 檢查是否已被匹配
            positions = set(range(pos, pos + len(phrase)))
            if not positions & matched_positions:
                ji_score += weight
                keywords_found.append((phrase, 'ji', weight))
                matched_positions |= positions
            start = pos + 1

    # 處理凶的關鍵詞
    for phrase, weight in XIONG_PHRASES:
        start = 0
        while True:
            pos = text.find(phrase, start)
            if pos == -1:
                break
            # 檢查是否已被匹配
            positions = set(range(pos, pos + len(phrase)))
            if not positions & matched_positions:
                xiong_score += weight
                keywords_found.append((phrase, 'xiong', weight))
                matched_positions |= positions
            start = pos + 1

    total = ji_score + xiong_score

    # 判斷閾值
    if total > 0.3:
        label = 1
    elif total < -0.3:
        label = -1
    else:
        label = 0

    return (label, ji_score, xiong_score, keywords_found)

def analyze_all_yaos():
    """分析所有384爻"""
    yaoci_data = load_yaoci()
    struct_data = load_structure()

    all_yaos = []

    for hex_item in yaoci_data['hexagrams']:
        num = hex_item['metadata']['number']
        name = hex_item['title_zh']
        content = hex_item['content_zh']

        # 獲取二進制
        struct = struct_data.get(str(num), {})
        binary = struct.get('binary', '000000')

        for pos in range(1, 7):
            # content[0] 是卦辭，content[1-6] 是爻辭
            text = content[pos] if pos < len(content) else ''

            label, ji_score, xiong_score, keywords = classify_yaoci(text)

            all_yaos.append({
                'hex_num': num,
                'hex_name': name,
                'position': pos,
                'binary': binary,
                'text': text,
                'label': label,
                'ji_score': ji_score,
                'xiong_score': xiong_score,
                'keywords': keywords
            })

    return all_yaos

def print_distribution(yaos):
    """打印標籤分布"""
    labels = [y['label'] for y in yaos]
    counter = Counter(labels)

    print("\n" + "=" * 60)
    print("標籤分布")
    print("=" * 60)
    print(f"總數: {len(labels)}")
    print(f"吉 (1):  {counter[1]:3d} ({counter[1]/len(labels)*100:.1f}%)")
    print(f"中 (0):  {counter[0]:3d} ({counter[0]/len(labels)*100:.1f}%)")
    print(f"凶 (-1): {counter[-1]:3d} ({counter[-1]/len(labels)*100:.1f}%)")

    # 基線
    most_common = counter.most_common(1)[0]
    baseline = most_common[1] / len(labels)
    print(f"\n基線 (全猜'{['凶','中','吉'][most_common[0]+1]}'): {baseline:.1%}")

def print_keyword_stats(yaos):
    """打印關鍵詞統計"""
    keyword_counts = defaultdict(int)

    for yao in yaos:
        for kw, kw_type, weight in yao['keywords']:
            keyword_counts[(kw, kw_type)] += 1

    print("\n" + "=" * 60)
    print("關鍵詞出現頻率")
    print("=" * 60)

    print("\n【吉類】")
    for (kw, kw_type), count in sorted(keyword_counts.items(), key=lambda x: -x[1]):
        if kw_type == 'ji':
            print(f"  {kw}: {count}")

    print("\n【凶類】")
    for (kw, kw_type), count in sorted(keyword_counts.items(), key=lambda x: -x[1]):
        if kw_type == 'xiong':
            print(f"  {kw}: {count}")

def print_position_analysis(yaos):
    """打印爻位分析"""
    print("\n" + "=" * 60)
    print("爻位分析 (1D)")
    print("=" * 60)

    pos_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'zhong': 0, 'xiong': 0})

    for yao in yaos:
        pos = yao['position']
        pos_stats[pos]['total'] += 1
        if yao['label'] == 1:
            pos_stats[pos]['ji'] += 1
        elif yao['label'] == 0:
            pos_stats[pos]['zhong'] += 1
        else:
            pos_stats[pos]['xiong'] += 1

    print("\n爻位   總數   吉率    中率    凶率")
    print("-" * 45)
    for pos in range(1, 7):
        s = pos_stats[pos]
        ji_rate = s['ji'] / s['total'] * 100
        zhong_rate = s['zhong'] / s['total'] * 100
        xiong_rate = s['xiong'] / s['total'] * 100
        print(f"  {pos}    {s['total']:3d}   {ji_rate:5.1f}%  {zhong_rate:5.1f}%  {xiong_rate:5.1f}%")

def print_samples(yaos, n=10):
    """打印樣本爻辭和標籤"""
    print("\n" + "=" * 60)
    print(f"樣本爻辭（前{n}個）")
    print("=" * 60)

    for yao in yaos[:n]:
        label_str = {1: '吉', 0: '中', -1: '凶'}[yao['label']]
        kw_str = ', '.join([f"{k}({t})" for k, t, w in yao['keywords']])
        print(f"\n[{yao['hex_name']} 第{yao['position']}爻] → {label_str}")
        print(f"  爻辭: {yao['text'][:50]}...")
        print(f"  關鍵詞: {kw_str if kw_str else '無'}")
        print(f"  吉分: {yao['ji_score']}, 凶分: {yao['xiong_score']}")

def print_edge_cases(yaos):
    """打印邊界情況"""
    print("\n" + "=" * 60)
    print("邊界情況 (分數接近0的爻)")
    print("=" * 60)

    edge_cases = [y for y in yaos if -0.5 < (y['ji_score'] + y['xiong_score']) < 0.5]

    print(f"\n邊界情況數量: {len(edge_cases)}")

    for yao in edge_cases[:15]:
        total = yao['ji_score'] + yao['xiong_score']
        label_str = {1: '吉', 0: '中', -1: '凶'}[yao['label']]
        kw_str = ', '.join([k for k, t, w in yao['keywords']])
        print(f"  [{yao['hex_name']}{yao['position']}] 總分={total:.1f} → {label_str} | {kw_str if kw_str else '無'}")

def check_wujiu_conflicts(yaos):
    """檢查「無咎」和「咎」的衝突"""
    print("\n" + "=" * 60)
    print("「無咎/咎」衝突檢查")
    print("=" * 60)

    conflicts = []
    for yao in yaos:
        has_wujiu = any(k in ['无咎', '無咎'] for k, t, w in yao['keywords'])
        has_jiu = any(k == '咎' for k, t, w in yao['keywords'])

        if has_wujiu and has_jiu:
            conflicts.append(yao)

    if conflicts:
        print(f"\n發現 {len(conflicts)} 個衝突:")
        for yao in conflicts[:5]:
            print(f"  [{yao['hex_name']}{yao['position']}] {yao['keywords']}")
    else:
        print("\n✓ 無衝突（無咎正確處理）")

def main():
    print("=" * 60)
    print("爻辭吉凶標籤驗證分析")
    print("=" * 60)

    yaos = analyze_all_yaos()

    print_distribution(yaos)
    print_keyword_stats(yaos)
    print_position_analysis(yaos)
    check_wujiu_conflicts(yaos)
    print_edge_cases(yaos)
    print_samples(yaos, 10)

    # 保存數據
    save_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis', 'verified_labels.json')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 轉換為可序列化格式
    save_data = []
    for yao in yaos:
        save_data.append({
            'hex_num': yao['hex_num'],
            'hex_name': yao['hex_name'],
            'position': yao['position'],
            'binary': yao['binary'],
            'text': yao['text'],
            'label': yao['label'],
            'ji_score': yao['ji_score'],
            'xiong_score': yao['xiong_score'],
            'keywords': [(k, t, w) for k, t, w in yao['keywords']]
        })

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"\n\n數據已保存至: {save_path}")

if __name__ == "__main__":
    main()
