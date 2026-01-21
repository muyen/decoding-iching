#!/usr/bin/env python3
"""
深入檢查標籤問題

1. 檢查「不利」vs「利」的匹配
2. 檢查每個爻位的具體爻辭
3. 手動驗證一些關鍵案例
"""

import json
import os
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

# ============================================================
# 更精確的關鍵詞匹配
# ============================================================

# 負面短語（先檢查，避免被正面詞誤匹配）
NEGATIVE_PHRASES = [
    '不利',
    '无攸利',
    '無攸利',
    '勿用',
    '不可',
]

# 正面關鍵詞
JI_KEYWORDS = {
    '元吉': 2.0,
    '大吉': 2.0,
    '終吉': 1.5,
    '貞吉': 1.5,
    '有喜': 1.0,
    '有慶': 1.0,
    '吉': 1.0,
    '利': 0.5,   # 提高權重
    '亨': 0.5,   # 提高權重
    '无咎': 0.3,
    '無咎': 0.3,
    '悔亡': 0.3,
}

# 負面關鍵詞
XIONG_KEYWORDS = {
    '大凶': -2.0,
    '終凶': -1.5,
    '貞凶': -1.5,
    '往凶': -1.0,
    '凶': -1.0,
    '不利': -0.5,  # 明確加入
    '厲': -0.5,
    '吝': -0.3,
    '悔': -0.3,
    '咎': -0.3,
    '災': -1.0,
    '眚': -0.5,
}

def improved_classify(text):
    """改進的分類方法"""
    if not text:
        return (0, 0, 0, [], [])

    ji_score = 0.0
    xiong_score = 0.0
    ji_found = []
    xiong_found = []

    # 創建一個已處理位置的集合
    processed = set()

    # 按長度排序關鍵詞（長的優先）
    all_ji = sorted(JI_KEYWORDS.items(), key=lambda x: -len(x[0]))
    all_xiong = sorted(XIONG_KEYWORDS.items(), key=lambda x: -len(x[0]))

    # 先處理吉關鍵詞
    for kw, weight in all_ji:
        idx = 0
        while True:
            pos = text.find(kw, idx)
            if pos == -1:
                break
            # 檢查是否被處理過
            if not any(p in processed for p in range(pos, pos + len(kw))):
                # 特殊處理：「利」字要檢查是否在「不利」或「无不利」中
                if kw == '利':
                    # 檢查前面是否有「不」
                    if pos > 0 and text[pos-1] == '不':
                        idx = pos + 1
                        continue
                    # 檢查前面是否有「无不」
                    if pos > 1 and text[pos-2:pos] == '无不':
                        idx = pos + 1
                        continue

                ji_score += weight
                ji_found.append(kw)
                for p in range(pos, pos + len(kw)):
                    processed.add(p)
            idx = pos + 1

    # 處理凶關鍵詞
    for kw, weight in all_xiong:
        idx = 0
        while True:
            pos = text.find(kw, idx)
            if pos == -1:
                break
            # 檢查是否被處理過
            if not any(p in processed for p in range(pos, pos + len(kw))):
                # 特殊處理：「咎」要檢查是否在「无咎/無咎」中
                if kw == '咎':
                    if pos > 0 and text[pos-1] in ['无', '無']:
                        idx = pos + 1
                        continue
                # 特殊處理：「悔」要檢查是否在「悔亡」中
                if kw == '悔':
                    if pos < len(text) - 1 and text[pos+1] == '亡':
                        idx = pos + 1
                        continue

                xiong_score += weight
                xiong_found.append(kw)
                for p in range(pos, pos + len(kw)):
                    processed.add(p)
            idx = pos + 1

    total = ji_score + xiong_score

    # 判斷閾值
    if total > 0.3:
        label = 1
    elif total < -0.3:
        label = -1
    else:
        label = 0

    return (label, ji_score, xiong_score, ji_found, xiong_found)

def analyze_position_1(yaoci_data, struct_data):
    """專門分析初爻為什麼吉率這麼高"""
    print("\n" + "=" * 60)
    print("初爻詳細分析")
    print("=" * 60)

    pos1_yaos = []

    for hex_item in yaoci_data['hexagrams']:
        num = hex_item['metadata']['number']
        name = hex_item['title_zh']
        content = hex_item['content_zh']

        if len(content) > 1:
            text = content[1]  # 初爻
            label, ji, xiong, ji_kw, xiong_kw = improved_classify(text)
            pos1_yaos.append({
                'num': num,
                'name': name,
                'text': text,
                'label': label,
                'ji': ji,
                'xiong': xiong,
                'ji_kw': ji_kw,
                'xiong_kw': xiong_kw
            })

    # 統計
    ji_count = sum(1 for y in pos1_yaos if y['label'] == 1)
    zhong_count = sum(1 for y in pos1_yaos if y['label'] == 0)
    xiong_count = sum(1 for y in pos1_yaos if y['label'] == -1)

    print(f"\n初爻統計: 吉={ji_count} ({ji_count/64*100:.1f}%), 中={zhong_count} ({zhong_count/64*100:.1f}%), 凶={xiong_count} ({xiong_count/64*100:.1f}%)")

    # 打印所有初爻
    print("\n所有初爻爻辭:")
    for y in pos1_yaos:
        label_str = {1: '吉', 0: '中', -1: '凶'}[y['label']]
        kw_str = f"[{','.join(y['ji_kw'])}]" if y['ji_kw'] else ""
        xkw_str = f"[{','.join(y['xiong_kw'])}]" if y['xiong_kw'] else ""
        print(f"{y['num']:2d}.{y['name']} → {label_str} | {y['text'][:35]}... | 吉{kw_str} 凶{xkw_str}")

def check_specific_cases(yaoci_data):
    """檢查特定案例"""
    print("\n" + "=" * 60)
    print("特定案例檢查")
    print("=" * 60)

    # 檢查「不利」相關
    print("\n【包含「不利」的爻辭】")
    for hex_item in yaoci_data['hexagrams']:
        for i, text in enumerate(hex_item['content_zh']):
            if '不利' in text:
                label, ji, xiong, ji_kw, xiong_kw = improved_classify(text)
                pos = i if i > 0 else '卦辭'
                label_str = {1: '吉', 0: '中', -1: '凶'}[label]
                print(f"  {hex_item['title_zh']}{pos}: {text[:40]}... → {label_str} (吉{ji}, 凶{xiong})")

    # 檢查「无不利」
    print("\n【包含「无不利」的爻辭】")
    for hex_item in yaoci_data['hexagrams']:
        for i, text in enumerate(hex_item['content_zh']):
            if '无不利' in text or '無不利' in text:
                label, ji, xiong, ji_kw, xiong_kw = improved_classify(text)
                pos = i if i > 0 else '卦辭'
                label_str = {1: '吉', 0: '中', -1: '凶'}[label]
                print(f"  {hex_item['title_zh']}{pos}: {text[:40]}... → {label_str} (吉{ji}, 凶{xiong})")

def compare_old_vs_new(yaoci_data, struct_data):
    """比較舊方法和新方法的差異"""
    print("\n" + "=" * 60)
    print("新舊方法比較")
    print("=" * 60)

    # 舊方法
    OLD_JI_KW = {'元吉': 2, '大吉': 2, '吉': 1, '無咎': 0.5, '无咎': 0.5, '利': 0.5, '亨': 0.5, '貞吉': 1, '終吉': 1, '有喜': 1, '有慶': 1, '悔亡': 0.3}
    OLD_XIONG_KW = {'凶': -1, '大凶': -2, '厲': -0.5, '吝': -0.3, '悔': -0.3, '咎': -0.3, '災': -1, '死': -1.5, '亡': -0.5, '困': -0.5}

    def old_classify(text):
        if not text: return 0
        ji = sum(w for k, w in OLD_JI_KW.items() if k in text)
        xiong = sum(w for k, w in OLD_XIONG_KW.items() if k in text)
        total = ji + xiong
        if total > 0.3: return 1
        elif total < -0.3: return -1
        return 0

    differences = []

    for hex_item in yaoci_data['hexagrams']:
        num = hex_item['metadata']['number']
        name = hex_item['title_zh']
        content = hex_item['content_zh']

        for pos in range(1, 7):
            if pos < len(content):
                text = content[pos]
                old_label = old_classify(text)
                new_label, _, _, _, _ = improved_classify(text)

                if old_label != new_label:
                    differences.append({
                        'hex': name,
                        'pos': pos,
                        'text': text,
                        'old': old_label,
                        'new': new_label
                    })

    print(f"\n標籤差異數量: {len(differences)}")
    print("\n差異詳情:")
    for d in differences[:20]:
        old_str = {1: '吉', 0: '中', -1: '凶'}[d['old']]
        new_str = {1: '吉', 0: '中', -1: '凶'}[d['new']]
        print(f"  {d['hex']}{d['pos']}: {old_str} → {new_str} | {d['text'][:40]}...")

def full_analysis_improved(yaoci_data, struct_data):
    """用改進的方法重新分析"""
    print("\n" + "=" * 60)
    print("改進方法的完整分析")
    print("=" * 60)

    pos_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'zhong': 0, 'xiong': 0})
    all_labels = []

    for hex_item in yaoci_data['hexagrams']:
        content = hex_item['content_zh']

        for pos in range(1, 7):
            if pos < len(content):
                text = content[pos]
                label, _, _, _, _ = improved_classify(text)

                pos_stats[pos]['total'] += 1
                all_labels.append(label)

                if label == 1:
                    pos_stats[pos]['ji'] += 1
                elif label == 0:
                    pos_stats[pos]['zhong'] += 1
                else:
                    pos_stats[pos]['xiong'] += 1

    # 總分布
    label_counter = Counter(all_labels)
    print(f"\n總分布:")
    print(f"  吉: {label_counter[1]} ({label_counter[1]/len(all_labels)*100:.1f}%)")
    print(f"  中: {label_counter[0]} ({label_counter[0]/len(all_labels)*100:.1f}%)")
    print(f"  凶: {label_counter[-1]} ({label_counter[-1]/len(all_labels)*100:.1f}%)")
    print(f"  基線 (全猜中): {label_counter[0]/len(all_labels)*100:.1f}%")

    # 爻位分布
    print("\n爻位分析:")
    print("爻位   總數   吉率    中率    凶率")
    print("-" * 45)
    for pos in range(1, 7):
        s = pos_stats[pos]
        ji_rate = s['ji'] / s['total'] * 100
        zhong_rate = s['zhong'] / s['total'] * 100
        xiong_rate = s['xiong'] / s['total'] * 100
        print(f"  {pos}    {s['total']:3d}   {ji_rate:5.1f}%  {zhong_rate:5.1f}%  {xiong_rate:5.1f}%")

def main():
    yaoci_data = load_yaoci()
    struct_data = load_structure()

    check_specific_cases(yaoci_data)
    compare_old_vs_new(yaoci_data, struct_data)
    full_analysis_improved(yaoci_data, struct_data)
    analyze_position_1(yaoci_data, struct_data)

if __name__ == "__main__":
    main()
