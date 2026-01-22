#!/usr/bin/env python3
"""
條件句數據庫建立與分析

目標：從384爻辭中提取所有「X則Y」模式
例如：征凶、居吉、利涉大川、不利...等

這些條件句揭示了古人總結的「行動指南」：
- 什麼情況下該動（征）
- 什麼情況下該靜（居）
- 什麼情況下有利（利）
- 什麼情況下危險（凶、厲）
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class ConditionPattern:
    """條件句模式"""
    condition: str      # 條件（行動）
    result: str         # 結果（吉凶）
    full_text: str      # 完整爻辭
    hex_num: int        # 卦號
    hex_name: str       # 卦名
    position: int       # 爻位
    label: int          # 整體標籤（1=吉, 0=中, -1=凶）


def load_data():
    """載入384爻數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_condition_patterns(data) -> List[ConditionPattern]:
    """
    從爻辭中提取條件句模式

    主要模式：
    1. 行動+結果：征凶、居吉、往吉、來凶
    2. 條件+結果：利X、不利X
    3. 狀態+評價：无咎、有孚、貞吉
    4. 時間+結果：終吉、初吉
    """
    patterns = []

    # 定義結果關鍵詞
    positive_results = ['吉', '利', '亨', '无咎', '有孚', '得', '喜']
    negative_results = ['凶', '咎', '悔', '吝', '厲', '眚', '兇']

    # 定義行動關鍵詞
    actions = ['征', '往', '來', '行', '居', '貞', '涉', '見', '用', '取', '進', '退', '守', '安']

    for item in data:
        text = item['text']
        hex_num = item['hex_num']
        hex_name = item['hex_name']
        position = item['position']
        label = item['label']

        # 模式1：行動+結果（如「征凶」「往吉」）
        for action in actions:
            for result in positive_results + negative_results:
                pattern = f"{action}{result}"
                if pattern in text:
                    patterns.append(ConditionPattern(
                        condition=action,
                        result=result,
                        full_text=text,
                        hex_num=hex_num,
                        hex_name=hex_name,
                        position=position,
                        label=label
                    ))

        # 模式2：「利X」模式
        li_matches = re.findall(r'利[^，。、\s]{1,4}', text)
        for match in li_matches:
            result_type = '利'
            patterns.append(ConditionPattern(
                condition=match,
                result=result_type,
                full_text=text,
                hex_num=hex_num,
                hex_name=hex_name,
                position=position,
                label=label
            ))

        # 模式3：「不利X」模式
        buli_matches = re.findall(r'不利[^，。、\s]{1,4}', text)
        for match in buli_matches:
            patterns.append(ConditionPattern(
                condition=match,
                result='不利',
                full_text=text,
                hex_num=hex_num,
                hex_name=hex_name,
                position=position,
                label=label
            ))

        # 模式4：「X則Y」顯式條件句
        ze_matches = re.findall(r'([^，。、\s]{1,4})則([^，。、\s]{1,4})', text)
        for cond, res in ze_matches:
            patterns.append(ConditionPattern(
                condition=cond,
                result=res,
                full_text=text,
                hex_num=hex_num,
                hex_name=hex_name,
                position=position,
                label=label
            ))

        # 模式5：貞X結構
        zhen_matches = re.findall(r'貞[吉凶咎厲悔吝亨]', text)
        for match in zhen_matches:
            patterns.append(ConditionPattern(
                condition='貞',
                result=match[1],
                full_text=text,
                hex_num=hex_num,
                hex_name=hex_name,
                position=position,
                label=label
            ))

        # 模式6：終/初+結果
        time_matches = re.findall(r'(終|初)[吉凶咎厲悔吝]', text)
        for match in time_matches:
            patterns.append(ConditionPattern(
                condition=match,
                result=text[text.find(match)+len(match)-1] if match in text else '',
                full_text=text,
                hex_num=hex_num,
                hex_name=hex_name,
                position=position,
                label=label
            ))

    return patterns


def analyze_action_result_pairs(patterns: List[ConditionPattern]):
    """分析「行動-結果」配對的統計"""
    print("\n" + "="*70)
    print("【分析1】行動-結果配對統計")
    print("="*70)

    # 統計行動+結果組合
    action_result_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0, 'examples': []})

    actions = ['征', '往', '來', '行', '居', '貞']
    results = ['吉', '凶', '咎', '悔', '吝', '厲', '亨', '无咎']

    for p in patterns:
        if p.condition in actions and p.result in results:
            key = f"{p.condition}{p.result}"
            if p.label == 1:
                action_result_stats[key]['吉'] += 1
            elif p.label == -1:
                action_result_stats[key]['凶'] += 1
            else:
                action_result_stats[key]['中'] += 1

            if len(action_result_stats[key]['examples']) < 3:
                action_result_stats[key]['examples'].append(f"{p.hex_name}卦{p.position}爻")

    print("\n主要「行動+結果」組合：")
    print("-" * 60)
    print(f"{'組合':^10} {'出現次數':^10} {'爻整體吉率':^12} {'解讀':^20}")
    print("-" * 60)

    # 排序：按出現次數
    sorted_pairs = sorted(action_result_stats.items(),
                         key=lambda x: sum(x[1][k] for k in ['吉','中','凶']),
                         reverse=True)

    interpretations = {
        '征凶': '出征會凶，應守不應攻',
        '征吉': '出征吉利，可以行動',
        '往吉': '前往有利',
        '往凶': '前往有害',
        '居吉': '安居則吉，宜靜不宜動',
        '居凶': '安居也凶，處境困難',
        '貞吉': '守正則吉',
        '貞凶': '即使守正也凶，局勢不利',
        '來吉': '返回/迎來有利',
        '來凶': '返回/迎來有害',
        '行吉': '行動吉利',
    }

    for pair, stats in sorted_pairs[:15]:
        total = sum(stats[k] for k in ['吉', '中', '凶'])
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            interp = interpretations.get(pair, '')
            examples = ', '.join(stats['examples'][:2])
            print(f"{pair:^10} {total:^10} {ji_rate:5.1f}%      {interp}")

    return action_result_stats


def analyze_li_patterns(patterns: List[ConditionPattern]):
    """分析「利X」模式"""
    print("\n" + "="*70)
    print("【分析2】「利X」行動建議分析")
    print("="*70)

    li_patterns = [p for p in patterns if p.condition.startswith('利') and len(p.condition) > 1]

    # 統計不同的「利X」模式
    li_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0, 'positions': []})

    for p in li_patterns:
        key = p.condition
        if p.label == 1:
            li_stats[key]['吉'] += 1
        elif p.label == -1:
            li_stats[key]['凶'] += 1
        else:
            li_stats[key]['中'] += 1
        li_stats[key]['positions'].append(p.position)

    print("\n「利X」模式統計（出現>=2次）：")
    print("-" * 70)
    print(f"{'模式':^15} {'次數':^6} {'吉率':^8} {'主要出現位置':^15} {'解讀'}")
    print("-" * 70)

    interpretations = {
        '利涉大川': '適合冒險、跨越障礙',
        '利見大人': '適合見貴人、尋求幫助',
        '利貞': '適合守正',
        '利有攸往': '適合有所前往',
        '利建侯': '適合建立根據地',
        '利用祭祀': '適合祭祀、精神活動',
        '利武人之貞': '適合軍事行動',
        '利艱貞': '適合在困難中堅守',
        '利西南': '適合向西南方向',
        '利東北': '適合向東北方向',
    }

    sorted_li = sorted(li_stats.items(), key=lambda x: sum(x[1][k] for k in ['吉','中','凶']), reverse=True)

    for pattern, stats in sorted_li:
        total = sum(stats[k] for k in ['吉', '中', '凶'])
        if total >= 2:
            ji_rate = stats['吉'] / total * 100
            pos_counter = Counter(stats['positions'])
            main_pos = ', '.join([f"爻{p}" for p, _ in pos_counter.most_common(3)])
            interp = interpretations.get(pattern, '')
            print(f"{pattern:^15} {total:^6} {ji_rate:5.1f}%   {main_pos:^15} {interp}")

    return li_stats


def analyze_buli_patterns(patterns: List[ConditionPattern]):
    """分析「不利X」模式"""
    print("\n" + "="*70)
    print("【分析3】「不利X」警告模式分析")
    print("="*70)

    buli_patterns = [p for p in patterns if '不利' in p.condition]

    buli_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for p in buli_patterns:
        key = p.condition
        if p.label == 1:
            buli_stats[key]['吉'] += 1
        elif p.label == -1:
            buli_stats[key]['凶'] += 1
        else:
            buli_stats[key]['中'] += 1

    print("\n「不利X」警告模式：")
    print("-" * 60)

    for pattern, stats in sorted(buli_stats.items(), key=lambda x: sum(x[1].values()), reverse=True):
        total = sum(stats.values())
        ji_rate = stats['吉'] / total * 100 if total > 0 else 0
        xiong_rate = stats['凶'] / total * 100 if total > 0 else 0
        print(f"  {pattern}: 出現{total}次, 吉率={ji_rate:.1f}%, 凶率={xiong_rate:.1f}%")

    # 有趣發現：「不利」的爻整體吉率如何？
    total_buli = len(buli_patterns)
    ji_count = sum(1 for p in buli_patterns if p.label == 1)
    xiong_count = sum(1 for p in buli_patterns if p.label == -1)

    print(f"\n【發現】標註「不利」的爻整體：")
    print(f"  吉率={ji_count/total_buli*100:.1f}% ({ji_count}/{total_buli})")
    print(f"  凶率={xiong_count/total_buli*100:.1f}% ({xiong_count}/{total_buli})")
    print(f"  說明：「不利」是警告，但不代表整體結果必然是凶")

    return buli_stats


def analyze_wujiu_pattern(data):
    """深入分析「无咎」模式"""
    print("\n" + "="*70)
    print("【分析4】「无咎」（无過失）深度分析")
    print("="*70)

    wujiu_yaos = [item for item in data if '无咎' in item['text']]

    print(f"\n「无咎」出現次數：{len(wujiu_yaos)} 次")

    # 按位置統計
    pos_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})
    for item in wujiu_yaos:
        pos = item['position']
        label = item['label']
        if label == 1:
            pos_stats[pos]['吉'] += 1
        elif label == -1:
            pos_stats[pos]['凶'] += 1
        else:
            pos_stats[pos]['中'] += 1

    print("\n「无咎」在各位置的分布和吉凶：")
    print("-" * 50)

    for pos in range(1, 7):
        stats = pos_stats[pos]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            bar = '█' * int(total / 2)
            print(f"  爻{pos}: {total:2}次  吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  {bar}")

    # 分析「无咎」的語義模式
    print("\n「无咎」的語義模式：")
    print("-" * 50)

    # 提取「无咎」前面的內容
    context_patterns = defaultdict(int)
    for item in wujiu_yaos:
        text = item['text']
        # 找到无咎前面的內容
        idx = text.find('无咎')
        if idx > 0:
            before = text[max(0, idx-10):idx]
            # 簡化：取最後2-4個字
            if len(before) >= 2:
                short_before = before[-4:] if len(before) >= 4 else before[-2:]
                context_patterns[short_before] += 1

    print("「无咎」前常見上下文：")
    for pattern, count in sorted(context_patterns.items(), key=lambda x: -x[1])[:10]:
        print(f"  「{pattern}...无咎」: {count}次")

    # 關鍵發現
    total = len(wujiu_yaos)
    ji_count = sum(1 for y in wujiu_yaos if y['label'] == 1)
    xiong_count = sum(1 for y in wujiu_yaos if y['label'] == -1)
    zhong_count = total - ji_count - xiong_count

    print(f"\n【關鍵發現】「无咎」的真正含義：")
    print(f"  整體吉率：{ji_count/total*100:.1f}%")
    print(f"  整體凶率：{xiong_count/total*100:.1f}%")
    print(f"  整體中率：{zhong_count/total*100:.1f}%")
    print(f"\n  「无咎」≠ 吉，而是「沒有過失」")
    print(f"  這是一種「及格」而非「優秀」的評價")


def analyze_position_action_interaction(patterns: List[ConditionPattern]):
    """分析「位置×行動」的交互效應"""
    print("\n" + "="*70)
    print("【分析5】位置×行動交互效應")
    print("="*70)

    # 統計每個位置的不同行動建議
    pos_action = defaultdict(lambda: defaultdict(int))
    pos_action_ji = defaultdict(lambda: defaultdict(int))

    key_actions = ['征', '往', '來', '居', '貞']

    for p in patterns:
        if p.condition in key_actions:
            pos_action[p.position][p.condition] += 1
            if p.label == 1:
                pos_action_ji[p.position][p.condition] += 1

    print("\n各位置的行動建議頻率：")
    print("-" * 60)
    print(f"{'位置':^6}", end='')
    for action in key_actions:
        print(f"{action:^10}", end='')
    print()
    print("-" * 60)

    for pos in range(1, 7):
        print(f"爻{pos:^4}", end='')
        for action in key_actions:
            count = pos_action[pos][action]
            if count > 0:
                ji_count = pos_action_ji[pos][action]
                ji_rate = ji_count / count * 100
                print(f"{count:3}({ji_rate:4.0f}%)", end='')
            else:
                print(f"{'  -':^10}", end='')
        print()

    print("\n【解讀】")
    print("  - 某位置出現某行動多 = 該位置適合該行動")
    print("  - 吉率高 = 該位置做該行動效果好")


def build_action_guide(patterns: List[ConditionPattern], data):
    """建立行動指南數據庫"""
    print("\n" + "="*70)
    print("【輸出】易經行動指南數據庫")
    print("="*70)

    guide = {
        'action_result_pairs': {},
        'li_recommendations': {},
        'buli_warnings': {},
        'position_advice': {},
        'summary': {}
    }

    # 1. 行動-結果配對
    action_results = defaultdict(lambda: {'count': 0, 'ji_rate': 0, 'examples': []})
    for p in patterns:
        if len(p.condition) == 1 and p.condition in '征往來居貞行':
            key = f"{p.condition}{p.result}"
            action_results[key]['count'] += 1
            action_results[key]['examples'].append({
                'hex': p.hex_name,
                'pos': p.position,
                'text': p.full_text[:30]
            })

    guide['action_result_pairs'] = dict(action_results)

    # 2. 「利X」建議
    li_recs = defaultdict(lambda: {'count': 0, 'examples': []})
    for p in patterns:
        if p.condition.startswith('利') and len(p.condition) > 1:
            li_recs[p.condition]['count'] += 1
            if len(li_recs[p.condition]['examples']) < 5:
                li_recs[p.condition]['examples'].append({
                    'hex': p.hex_name,
                    'pos': p.position
                })

    guide['li_recommendations'] = dict(li_recs)

    # 3. 位置建議
    for pos in range(1, 7):
        pos_patterns = [p for p in patterns if p.position == pos]
        if pos_patterns:
            action_counts = Counter(p.condition for p in pos_patterns if len(p.condition) <= 2)
            guide['position_advice'][pos] = {
                'common_actions': action_counts.most_common(5),
                'total_patterns': len(pos_patterns)
            }

    # 4. 總結
    guide['summary'] = {
        'total_patterns': len(patterns),
        'total_yaos': len(data),
        'pattern_coverage': f"{len(patterns)/len(data)*100:.1f}%"
    }

    # 保存到JSON
    output_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'condition_patterns.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(guide, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n行動指南已保存至：{output_path}")
    print(f"共提取 {len(patterns)} 個條件句模式")

    return guide


def print_key_findings():
    """輸出關鍵發現"""
    print("\n" + "="*70)
    print("條件句分析關鍵發現")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    易經條件句系統總結                                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【核心模式】                                                        ║
║  ────────────                                                        ║
║  1. 行動+結果：征凶/征吉、往凶/往吉、居凶/居吉                      ║
║  2. 條件句：利X（推薦）、不利X（警告）                              ║
║  3. 評價詞：无咎、有孚、貞吉/貞凶                                   ║
║                                                                      ║
║  【行動指南翻譯】                                                    ║
║  ────────────────                                                    ║
║  • 「征」= 主動出擊、進攻、遠行                                     ║
║  • 「往」= 前往、主動接近                                           ║
║  • 「來」= 返回、等待對方接近                                       ║
║  • 「居」= 安守、不動、維持現狀                                     ║
║  • 「貞」= 堅守正道、固守原則                                       ║
║                                                                      ║
║  【「利X」系統】                                                     ║
║  ──────────────                                                      ║
║  • 利涉大川 = 適合冒險、跨越困難                                    ║
║  • 利見大人 = 適合尋求幫助、拜訪貴人                                ║
║  • 利貞 = 適合堅守                                                  ║
║  • 利有攸往 = 適合有所行動                                          ║
║                                                                      ║
║  【「无咎」真義】                                                    ║
║  ────────────────                                                    ║
║  • 「无咎」≠ 吉                                                     ║
║  • 「无咎」= 沒有過失、不會出錯                                     ║
║  • 這是「及格」而非「優秀」的評價                                   ║
║  • 常出現在危險位置（如三爻），意為「雖險但能避禍」                 ║
║                                                                      ║
║  【位置×行動交互】                                                   ║
║  ──────────────────                                                  ║
║  • 初爻：多「勿用」「潛」- 不宜行動                                 ║
║  • 二爻：多「利見」- 適合尋求支持                                   ║
║  • 三爻：多「厲」「无咎」- 危險但可過                               ║
║  • 四爻：多「或」「无咎」- 謹慎選擇                                 ║
║  • 五爻：多「吉」「利」- 最適合行動                                 ║
║  • 上爻：多「悔」「窮」- 物極必反                                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("易經條件句數據庫建立與分析")
    print("="*70)
    print("\n從384爻辭中提取「X則Y」行動指南模式")

    data = load_data()
    print(f"\n載入 {len(data)} 條爻辭")

    # 提取條件句
    patterns = extract_condition_patterns(data)
    print(f"提取到 {len(patterns)} 個條件句模式")

    # 分析
    analyze_action_result_pairs(patterns)
    analyze_li_patterns(patterns)
    analyze_buli_patterns(patterns)
    analyze_wujiu_pattern(data)
    analyze_position_action_interaction(patterns)

    # 建立數據庫
    guide = build_action_guide(patterns, data)

    # 輸出關鍵發現
    print_key_findings()


if __name__ == '__main__':
    main()
