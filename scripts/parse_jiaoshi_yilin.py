#!/usr/bin/env python3
"""
Parse and analyze 焦氏易林 (Jiaoshi Yilin) - 4096 hexagram transformation verses

Data source: github.com/kr-shadow/KR3 (四庫全書版本)
"""

import re
import json
from pathlib import Path
from collections import defaultdict

# 64 hexagram names mapping
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

# Create lookup set for matching
HEXAGRAM_SET = set(HEXAGRAM_NAMES)

# Fortune/misfortune keywords
JI_KEYWORDS = ['吉', '福', '喜', '利', '安', '寧', '慶', '祥', '榮', '貴', '富', '昌', '亨', '通', '得', '成']
XIONG_KEYWORDS = ['凶', '禍', '災', '患', '危', '憂', '困', '敗', '亡', '死', '傷', '害', '殃', '厄', '失', '病']


def load_text():
    """Load the Jiaoshi Yilin text file"""
    data_path = Path(__file__).parent.parent / 'data' / 'jiaoshi_yilin.txt'
    with open(data_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_yilin(text):
    """Parse the Yilin text into structured data"""
    transformations = []

    # Find all volume/section headers: X之第Y
    current_source = None

    lines = text.split('\n')

    # Pattern for section header: 乾之第一, 坤之第二, etc.
    section_pattern = re.compile(r'^　　(\S+)之第')

    # Pattern for individual transformation: 卦名　詩句
    # The format is: hexagram_name followed by spaces/tab then verse
    trans_pattern = re.compile(r'^(\S+)　+(.+)$')

    current_verse_lines = []
    current_target = None

    for line in lines:
        line = line.rstrip()

        # Check for section header
        section_match = section_pattern.match(line)
        if section_match:
            # Save previous verse if exists
            if current_source and current_target and current_verse_lines:
                verse = ''.join(current_verse_lines)
                transformations.append({
                    'source': current_source,
                    'target': current_target,
                    'verse': verse.strip()
                })

            current_source = section_match.group(1)
            current_target = None
            current_verse_lines = []
            continue

        # Check for transformation entry
        trans_match = trans_pattern.match(line)
        if trans_match:
            potential_target = trans_match.group(1)
            verse_text = trans_match.group(2)

            # Check if it's a valid hexagram name
            if potential_target in HEXAGRAM_SET or potential_target == current_source:
                # Save previous verse if exists
                if current_source and current_target and current_verse_lines:
                    verse = ''.join(current_verse_lines)
                    transformations.append({
                        'source': current_source,
                        'target': current_target,
                        'verse': verse.strip()
                    })

                current_target = potential_target
                current_verse_lines = [verse_text]
            else:
                # Continuation of previous verse
                if current_verse_lines:
                    current_verse_lines.append(line)
        elif line.startswith('　') and current_target:
            # Continuation line (indented)
            current_verse_lines.append(line.strip())

    # Save last verse
    if current_source and current_target and current_verse_lines:
        verse = ''.join(current_verse_lines)
        transformations.append({
            'source': current_source,
            'target': current_target,
            'verse': verse.strip()
        })

    return transformations


def label_fortune(verse):
    """Label the fortune/misfortune of a verse based on keywords"""
    ji_count = sum(1 for kw in JI_KEYWORDS if kw in verse)
    xiong_count = sum(1 for kw in XIONG_KEYWORDS if kw in verse)

    if ji_count > xiong_count:
        return 1  # 吉
    elif xiong_count > ji_count:
        return -1  # 凶
    else:
        return 0  # 中/平


def analyze_transformations(transformations):
    """Analyze patterns in the 4096 transformations"""
    print("\n" + "=" * 70)
    print("焦氏易林 4096變卦分析")
    print("=" * 70)

    print(f"\n總共解析到 {len(transformations)} 個變卦")

    # Label each transformation
    for t in transformations:
        t['label'] = label_fortune(t['verse'])

    # Count by source hexagram
    source_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})
    target_stats = defaultdict(lambda: {'total': 0, 'ji': 0, 'xiong': 0})

    for t in transformations:
        source = t['source']
        target = t['target']
        label = t['label']

        source_stats[source]['total'] += 1
        target_stats[target]['total'] += 1

        if label == 1:
            source_stats[source]['ji'] += 1
            target_stats[target]['ji'] += 1
        elif label == -1:
            source_stats[source]['xiong'] += 1
            target_stats[target]['xiong'] += 1

    # Find best/worst source hexagrams
    print("\n【從哪個卦出發最吉？】")
    print("-" * 50)
    source_ji_rates = []
    for hex_name, stats in source_stats.items():
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            source_ji_rates.append((hex_name, ji_rate, stats['total']))

    source_ji_rates.sort(key=lambda x: -x[1])
    print("最吉的本卦 (出發點):")
    for name, rate, n in source_ji_rates[:5]:
        print(f"  {name}: {rate:.1f}% 吉率 (n={n})")

    print("\n最凶的本卦 (出發點):")
    for name, rate, n in source_ji_rates[-5:]:
        print(f"  {name}: {rate:.1f}% 吉率 (n={n})")

    # Find best/worst target hexagrams
    print("\n【變到哪個卦最吉？】")
    print("-" * 50)
    target_ji_rates = []
    for hex_name, stats in target_stats.items():
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            target_ji_rates.append((hex_name, ji_rate, stats['total']))

    target_ji_rates.sort(key=lambda x: -x[1])
    print("最吉的變卦目標:")
    for name, rate, n in target_ji_rates[:5]:
        print(f"  {name}: {rate:.1f}% 吉率 (n={n})")

    print("\n最凶的變卦目標:")
    for name, rate, n in target_ji_rates[-5:]:
        print(f"  {name}: {rate:.1f}% 吉率 (n={n})")

    # Self-transformation (本卦之本卦)
    print("\n【本卦不變 (X之X) 的吉凶】")
    print("-" * 50)
    self_trans = [t for t in transformations if t['source'] == t['target']]
    if self_trans:
        ji_count = sum(1 for t in self_trans if t['label'] == 1)
        xiong_count = sum(1 for t in self_trans if t['label'] == -1)
        print(f"  總數: {len(self_trans)}")
        print(f"  吉率: {ji_count/len(self_trans)*100:.1f}%")
        print(f"  凶率: {xiong_count/len(self_trans)*100:.1f}%")

    # Compare with our 384 爻 findings
    print("\n【與周易384爻對比】")
    print("-" * 50)
    print("周易研究發現的福地卦: 謙、臨、需")
    print("焦氏易林中這些卦作為目標的吉率:")
    for hex_name in ['謙', '臨', '需']:
        if hex_name in target_stats:
            stats = target_stats[hex_name]
            if stats['total'] > 0:
                print(f"  {hex_name}: {stats['ji']/stats['total']*100:.1f}% 吉率")

    return transformations


def build_transition_matrix(transformations):
    """Build a 64x64 transition matrix of fortune"""
    matrix = {}

    for t in transformations:
        key = (t['source'], t['target'])
        matrix[key] = t['label']

    return matrix


def compare_with_zhouyi():
    """Compare Yilin findings with our 384 爻 research"""
    print("\n" + "=" * 70)
    print("焦氏易林 vs 周易384爻 比較分析")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    焦氏易林核心發現                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  【最吉的出發點】大畜、姤、節、小畜、蠱                               │
│  【最凶的出發點】明夷、益、剥、革、離                                 │
│                                                                     │
│  【最吉的目標】咸(51.6%)、復(43.8%)、賁(42.2%)                       │
│  【最凶的目標】遯(20.3%)、井(23.4%)                                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    與周易384爻研究對比                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  周易福地卦：謙、臨、需                                              │
│  易林中吉率：謙(37.5%)、臨(34.4%)、需(34.4%) ← 中等，非最高          │
│                                                                     │
│  【解釋】                                                           │
│  1. 周易分析的是「爻辭」本身的吉凶                                   │
│  2. 焦氏易林分析的是「變卦過程」的吉凶                               │
│  3. 兩者角度不同：                                                   │
│     - 周易：靜態狀態的吉凶評估                                       │
│     - 易林：動態變化的吉凶預測                                       │
│                                                                     │
│  【有趣發現】                                                        │
│  - 明夷(最凶出發)：從困境出發，變化難吉                              │
│  - 大畜(最吉出發)：蓄積能量後變化易吉                                │
│  - 咸(最吉目標)：感應、交流 → 變化的最佳方向                        │
│  - 復(高吉率目標)：回歸本源 → 變化的第二好方向                      │
│                                                                     │
│  【核心洞見】                                                        │
│  焦氏易林揭示了「變化」本身的規律：                                  │
│  - 從「蓄積」的狀態出發變化最吉（大畜）                              │
│  - 往「感通」的方向變化最吉（咸）                                    │
│  - 從「明傷」的狀態出發變化最凶（明夷）                              │
│                                                                     │
│  這補充了周易的「靜態」分析，提供了「動態」視角                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
    """)


def main():
    print("=" * 70)
    print("焦氏易林解析器")
    print("=" * 70)

    text = load_text()
    print(f"\n載入文本: {len(text)} 字符")

    # Parse
    transformations = parse_yilin(text)

    # Analyze
    transformations = analyze_transformations(transformations)

    # Compare with Zhouyi
    compare_with_zhouyi()

    # Save parsed data
    output_path = Path(__file__).parent.parent / 'data' / 'jiaoshi_yilin_parsed.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transformations, f, ensure_ascii=False, indent=2)

    print(f"\n數據保存至: {output_path}")

    # Build matrix
    matrix = build_transition_matrix(transformations)
    matrix_path = Path(__file__).parent.parent / 'data' / 'yilin_transition_matrix.json'

    # Convert tuple keys to string for JSON
    matrix_json = {f"{k[0]}->{k[1]}": v for k, v in matrix.items()}
    with open(matrix_path, 'w', encoding='utf-8') as f:
        json.dump(matrix_json, f, ensure_ascii=False, indent=2)

    print(f"轉換矩陣保存至: {matrix_path}")


if __name__ == '__main__':
    main()
