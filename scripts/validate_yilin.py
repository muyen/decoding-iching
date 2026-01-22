#!/usr/bin/env python3
"""
Validate 焦氏易林 against our structural analysis

Question: Does Yilin's fortune labels align with mathematical structure?
If yes → Yilin may have encoded real patterns
If no → Yilin may be arbitrary/literary
"""

import json
from pathlib import Path
from collections import defaultdict

# Load our 384 爻 data
def load_zhouyi_data():
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load Yilin data
def load_yilin_data():
    data_path = Path(__file__).parent.parent / 'data' / 'jiaoshi_yilin_parsed.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Hexagram number to name mapping
HEXAGRAM_NAMES = [
    "乾", "坤", "屯", "蒙", "需", "訟", "師", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "謙", "豫",
    "隨", "蠱", "臨", "觀", "噬嗑", "賁", "剝", "復",
    "無妄", "大畜", "頤", "大過", "坎", "離", "咸", "恆",
    "遯", "大壯", "晉", "明夷", "家人", "睽", "蹇", "解",
    "損", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "漸", "歸妹", "豐", "旅",
    "巽", "兌", "渙", "節", "中孚", "小過", "既濟", "未濟"
]

def get_hexagram_ji_rate(zhouyi_data):
    """Calculate ji rate for each hexagram from 384 爻 data"""
    hex_stats = defaultdict(lambda: {'ji': 0, 'total': 0})

    for item in zhouyi_data:
        hex_num = item['hex_num']
        label = item['label']
        hex_stats[hex_num]['total'] += 1
        if label == 1:
            hex_stats[hex_num]['ji'] += 1

    result = {}
    for hex_num, stats in hex_stats.items():
        if stats['total'] > 0:
            result[hex_num] = stats['ji'] / stats['total']

    return result


def validate_yilin_against_structure(yilin_data, zhouyi_ji_rates):
    """Check if Yilin's labels correlate with structural patterns"""

    print("=" * 70)
    print("驗證焦氏易林：是否符合數學結構？")
    print("=" * 70)

    # Hypothesis 1: Transformations TO good hexagrams should be more ji
    print("\n【假設1】變到吉卦 → 易林應該說吉")
    print("-" * 50)

    # Get Zhouyi's best and worst hexagrams
    sorted_hex = sorted(zhouyi_ji_rates.items(), key=lambda x: -x[1])
    best_hex_nums = [h[0] for h in sorted_hex[:10]]  # Top 10
    worst_hex_nums = [h[0] for h in sorted_hex[-10:]]  # Bottom 10

    best_hex_names = [HEXAGRAM_NAMES[n-1] for n in best_hex_nums]
    worst_hex_names = [HEXAGRAM_NAMES[n-1] for n in worst_hex_nums]

    print(f"周易吉率最高的卦: {best_hex_names[:5]}")
    print(f"周易吉率最低的卦: {worst_hex_names[:5]}")

    # Check Yilin's labels for transformations to these hexagrams
    to_best = [t for t in yilin_data if t['target'] in best_hex_names]
    to_worst = [t for t in yilin_data if t['target'] in worst_hex_names]

    if to_best:
        to_best_ji = sum(1 for t in to_best if t['label'] == 1) / len(to_best) * 100
        print(f"\n變到「周易吉卦」時，易林說吉的比例: {to_best_ji:.1f}% (n={len(to_best)})")

    if to_worst:
        to_worst_ji = sum(1 for t in to_worst if t['label'] == 1) / len(to_worst) * 100
        print(f"變到「周易凶卦」時，易林說吉的比例: {to_worst_ji:.1f}% (n={len(to_worst)})")

    if to_best and to_worst:
        diff = to_best_ji - to_worst_ji
        if diff > 5:
            print(f"\n✓ 差異 {diff:.1f}% → 易林與周易結構一致")
        elif diff < -5:
            print(f"\n✗ 差異 {diff:.1f}% → 易林與周易結構相反！")
        else:
            print(f"\n? 差異 {diff:.1f}% → 無明顯相關")

    # Hypothesis 2: Hamming distance matters?
    # Transformations with fewer bit flips should be easier (more ji)?
    print("\n\n【假設2】變化越小 → 應該越吉？")
    print("-" * 50)

    # We need binary representations
    HEXAGRAM_BINARY = {}
    for i, name in enumerate(HEXAGRAM_NAMES):
        HEXAGRAM_BINARY[name] = format(i, '06b')

    def hamming_distance(name1, name2):
        if name1 not in HEXAGRAM_BINARY or name2 not in HEXAGRAM_BINARY:
            return None
        b1 = HEXAGRAM_BINARY[name1]
        b2 = HEXAGRAM_BINARY[name2]
        return sum(c1 != c2 for c1, c2 in zip(b1, b2))

    # Group by Hamming distance
    dist_stats = defaultdict(lambda: {'ji': 0, 'total': 0})

    for t in yilin_data:
        dist = hamming_distance(t['source'], t['target'])
        if dist is not None:
            dist_stats[dist]['total'] += 1
            if t['label'] == 1:
                dist_stats[dist]['ji'] += 1

    print("漢明距離 vs 吉率:")
    for dist in sorted(dist_stats.keys()):
        stats = dist_stats[dist]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            bar = '█' * int(ji_rate / 5)
            print(f"  距離={dist}: {ji_rate:5.1f}% 吉率 (n={stats['total']:3d}) {bar}")

    # Hypothesis 3: Self-transformation should be most stable
    print("\n\n【假設3】本卦不變 (X之X) → 應該最穩定？")
    print("-" * 50)

    self_trans = [t for t in yilin_data if t['source'] == t['target']]
    other_trans = [t for t in yilin_data if t['source'] != t['target']]

    if self_trans and other_trans:
        self_ji = sum(1 for t in self_trans if t['label'] == 1) / len(self_trans) * 100
        other_ji = sum(1 for t in other_trans if t['label'] == 1) / len(other_trans) * 100

        print(f"本卦不變 (X之X) 吉率: {self_ji:.1f}% (n={len(self_trans)})")
        print(f"變到其他卦吉率: {other_ji:.1f}% (n={len(other_trans)})")

        if self_ji > other_ji:
            print("\n✓ 本卦不變確實更穩定")
        else:
            print("\n✗ 本卦不變反而更差？")

    # Summary
    print("\n" + "=" * 70)
    print("驗證結論")
    print("=" * 70)
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  焦氏易林的可靠性評估：                                              │
│                                                                     │
│  如果易林與周易結構一致 → 焦延壽可能觀察到了真實規律                │
│  如果易林與周易結構無關 → 易林可能只是文學創作                      │
│  如果易林與周易結構相反 → 需要更多研究                              │
│                                                                     │
│  重要提醒：                                                          │
│  1. 我們用「關鍵詞」標記易林吉凶，可能有誤差                        │
│  2. 易林本身是占卜用途，不一定追求邏輯一致                          │
│  3. 「正確」的定義本身就有爭議                                      │
│                                                                     │
│  我們能確定的是：                                                    │
│  - 可以檢驗「內部一致性」                                           │
│  - 可以與周易結構「交叉驗證」                                       │
│  - 無法證明「預測準確性」（需要實驗數據）                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
    """)


def main():
    zhouyi_data = load_zhouyi_data()
    yilin_data = load_yilin_data()

    print(f"載入周易數據: {len(zhouyi_data)} 條")
    print(f"載入易林數據: {len(yilin_data)} 條")

    zhouyi_ji_rates = get_hexagram_ji_rate(zhouyi_data)

    validate_yilin_against_structure(yilin_data, zhouyi_ji_rates)


if __name__ == '__main__':
    main()
