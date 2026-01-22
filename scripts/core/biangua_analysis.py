#!/usr/bin/env python3
"""
變卦 (Changing Hexagram) Analysis
Analyzes all 384 possible single-line changes (64 hexagrams × 6 lines)

For each line change:
- Original hexagram (本卦) → Changed hexagram (之卦)
- Compare 吉凶 of the changing line vs the overall trend of 之卦
- Find patterns: when does 凶→吉 or 吉→凶 occur?
"""

import json
import os
from collections import defaultdict

# Hexagram data
TRIGRAM_BINARY = {
    '乾': '111', '兌': '110', '離': '101', '震': '100',
    '巽': '011', '坎': '010', '艮': '001', '坤': '000'
}

BINARY_TRIGRAM = {v: k for k, v in TRIGRAM_BINARY.items()}

HEXAGRAM_NAMES = [
    "", "乾", "坤", "屯", "蒙", "需", "訟", "師", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "謙", "豫",
    "隨", "蠱", "臨", "觀", "噬嗑", "賁", "剝", "復",
    "無妄", "大畜", "頤", "大過", "坎", "離", "咸", "恆",
    "遯", "大壯", "晉", "明夷", "家人", "睽", "蹇", "解",
    "損", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "漸", "歸妹", "豐", "旅",
    "巽", "兌", "渙", "節", "中孚", "小過", "既濟", "未濟"
]

# King Wen sequence binary (from bottom to top, 0=yin, 1=yang)
HEXAGRAM_BINARY = {
    1: '111111', 2: '000000', 3: '010001', 4: '100010', 5: '010111', 6: '111010',
    7: '000010', 8: '010000', 9: '110111', 10: '111011', 11: '000111', 12: '111000',
    13: '111101', 14: '101111', 15: '000100', 16: '001000', 17: '011001', 18: '100110',
    19: '000011', 20: '110000', 21: '101001', 22: '100101', 23: '100000', 24: '000001',
    25: '111001', 26: '100111', 27: '100001', 28: '011110', 29: '010010', 30: '101101',
    31: '011100', 32: '001110', 33: '111100', 34: '001111', 35: '101000', 36: '000101',
    37: '110101', 38: '101011', 39: '010100', 40: '001010', 41: '100011', 42: '110001',
    43: '011111', 44: '111110', 45: '011000', 46: '000110', 47: '011010', 48: '010110',
    49: '011101', 50: '101110', 51: '001001', 52: '100100', 53: '110100', 54: '001011',
    55: '001101', 56: '101100', 57: '110110', 58: '011011', 59: '110010', 60: '010011',
    61: '110011', 62: '001100', 63: '010101', 64: '101010'
}

# Reverse lookup
BINARY_HEXAGRAM = {v: k for k, v in HEXAGRAM_BINARY.items()}

# 吉凶 keywords
JI_KEYWORDS = {'元吉': 2, '大吉': 2, '吉': 1, '終吉': 1.5, '貞吉': 1, '无咎': 0.5, '悔亡': 0.5, '利': 0.3, '亨': 0.3}
XIONG_KEYWORDS = {'大凶': -2, '凶': -1, '厲': -0.5, '吝': -0.3, '悔': -0.3, '咎': -0.5}


def load_yaoci_data():
    """Load yaoci data from the ctext JSON file"""
    yaoci_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ctext', 'zhouyi_64gua.json')

    if not os.path.exists(yaoci_path):
        # Try alternative path
        yaoci_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'yaoci.json')

    try:
        with open(yaoci_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        hexagrams = {}
        for hex_data in data.get('hexagrams', []):
            num = hex_data['metadata']['number']
            content = hex_data.get('content_zh', [])
            hexagrams[num] = {
                'name': hex_data.get('title_zh', HEXAGRAM_NAMES[num]),
                'lines': content[1:7] if len(content) > 6 else content[1:]  # Skip guaci
            }
        return hexagrams
    except Exception as e:
        print(f"Error loading yaoci: {e}")
        return {}


def classify_text(text):
    """Classify yaoci text as 吉(1), 中(0), or 凶(-1)"""
    ji_score = sum(weight for kw, weight in JI_KEYWORDS.items() if kw in text)
    xiong_score = sum(weight for kw, weight in XIONG_KEYWORDS.items() if kw in text)

    total = ji_score + xiong_score
    if total > 0.3:
        return 1  # 吉
    elif total < -0.3:
        return -1  # 凶
    return 0  # 中


def get_hexagram_ji_rate(hex_num, yaoci_data):
    """Calculate the 吉 rate for a hexagram"""
    if hex_num not in yaoci_data:
        return 0.5

    lines = yaoci_data[hex_num].get('lines', [])
    if not lines:
        return 0.5

    ji_count = sum(1 for line in lines if classify_text(line) == 1)
    return ji_count / len(lines)


def flip_line(binary, position):
    """Flip a single line (0-indexed from bottom)"""
    binary_list = list(binary)
    # Position 0 = bottom (rightmost in our string)
    idx = 5 - position  # Convert to string index
    binary_list[idx] = '0' if binary_list[idx] == '1' else '1'
    return ''.join(binary_list)


def analyze_all_changes(yaoci_data):
    """Analyze all 384 possible single-line changes"""
    results = []

    for hex_num in range(1, 65):
        original_binary = HEXAGRAM_BINARY[hex_num]
        original_name = HEXAGRAM_NAMES[hex_num]
        original_ji_rate = get_hexagram_ji_rate(hex_num, yaoci_data)

        lines = yaoci_data.get(hex_num, {}).get('lines', [])

        for line_pos in range(6):
            # Get the yaoci for this line
            yaoci_text = lines[line_pos] if line_pos < len(lines) else ""
            yaoci_class = classify_text(yaoci_text)

            # Calculate the changed hexagram
            changed_binary = flip_line(original_binary, line_pos)
            changed_num = BINARY_HEXAGRAM.get(changed_binary, 0)

            if changed_num == 0:
                continue

            changed_name = HEXAGRAM_NAMES[changed_num]
            changed_ji_rate = get_hexagram_ji_rate(changed_num, yaoci_data)

            # Determine the trend change
            trend_change = changed_ji_rate - original_ji_rate

            results.append({
                'original_num': hex_num,
                'original_name': original_name,
                'original_binary': original_binary,
                'original_ji_rate': round(original_ji_rate, 3),
                'line_position': line_pos + 1,  # 1-indexed for display
                'line_type': '陽' if original_binary[5-line_pos] == '1' else '陰',
                'yaoci_text': yaoci_text[:30] + '...' if len(yaoci_text) > 30 else yaoci_text,
                'yaoci_class': '吉' if yaoci_class == 1 else ('凶' if yaoci_class == -1 else '中'),
                'changed_num': changed_num,
                'changed_name': changed_name,
                'changed_binary': changed_binary,
                'changed_ji_rate': round(changed_ji_rate, 3),
                'trend_change': round(trend_change, 3),
                'trend_direction': '↑' if trend_change > 0.1 else ('↓' if trend_change < -0.1 else '→')
            })

    return results


def analyze_patterns(results):
    """Find patterns in the transformation data"""
    patterns = {
        'xiong_to_ji': [],      # 凶爻 but 之卦 better
        'ji_to_xiong': [],      # 吉爻 but 之卦 worse
        'line_position_trends': defaultdict(list),
        'trigram_changes': defaultdict(list),
        'summary_stats': {}
    }

    for r in results:
        # 凶→吉: current line is 凶 but changing improves the situation
        if r['yaoci_class'] == '凶' and r['trend_change'] > 0.15:
            patterns['xiong_to_ji'].append(r)

        # 吉→凶: current line is 吉 but changing worsens the situation
        if r['yaoci_class'] == '吉' and r['trend_change'] < -0.15:
            patterns['ji_to_xiong'].append(r)

        # Group by line position
        patterns['line_position_trends'][r['line_position']].append(r['trend_change'])

    # Calculate position averages
    position_avg = {}
    for pos, trends in patterns['line_position_trends'].items():
        position_avg[pos] = round(sum(trends) / len(trends), 4) if trends else 0

    patterns['summary_stats'] = {
        'total_changes': len(results),
        'xiong_to_ji_count': len(patterns['xiong_to_ji']),
        'ji_to_xiong_count': len(patterns['ji_to_xiong']),
        'position_avg_trend': position_avg,
        'trend_up_count': sum(1 for r in results if r['trend_direction'] == '↑'),
        'trend_down_count': sum(1 for r in results if r['trend_direction'] == '↓'),
        'trend_neutral_count': sum(1 for r in results if r['trend_direction'] == '→')
    }

    return patterns


def generate_report(results, patterns):
    """Generate markdown report"""
    report = """# 變卦分析報告：384種單爻變化的吉凶規律

*分析日期：2026-01-21*

---

## 摘要

本分析研究了64卦×6爻=384種單爻變化的規律：
- **本卦**：當前狀態
- **動爻**：引發變化的爻
- **之卦**：變化後的結果

---

## 一、總體統計

| 指標 | 數值 |
|------|------|
| 總變化數 | {total} |
| 之卦趨勢向上 (↑) | {up} ({up_pct:.1f}%) |
| 之卦趨勢向下 (↓) | {down} ({down_pct:.1f}%) |
| 之卦趨勢持平 (→) | {neutral} ({neutral_pct:.1f}%) |

---

## 二、爻位與變化趨勢

不同爻位變動後，之卦吉凶的平均變化：

| 爻位 | 平均趨勢變化 | 解讀 |
|------|-------------|------|
""".format(
        total=patterns['summary_stats']['total_changes'],
        up=patterns['summary_stats']['trend_up_count'],
        up_pct=patterns['summary_stats']['trend_up_count']/384*100,
        down=patterns['summary_stats']['trend_down_count'],
        down_pct=patterns['summary_stats']['trend_down_count']/384*100,
        neutral=patterns['summary_stats']['trend_neutral_count'],
        neutral_pct=patterns['summary_stats']['trend_neutral_count']/384*100
    )

    pos_meanings = {
        1: '初爻（起始）',
        2: '二爻（發展）',
        3: '三爻（轉折）',
        4: '四爻（進入）',
        5: '五爻（成熟）',
        6: '上爻（終結）'
    }

    for pos in range(1, 7):
        avg = patterns['summary_stats']['position_avg_trend'].get(pos, 0)
        direction = '↑' if avg > 0.01 else ('↓' if avg < -0.01 else '→')
        report += f"| {pos_meanings[pos]} | {avg:+.4f} {direction} | {'變後趨吉' if avg > 0 else ('變後趨凶' if avg < 0 else '持平')} |\n"

    report += """
---

## 三、重要發現：「凶爻變吉」案例

以下是動爻本身為凶，但變化後之卦反而更好的案例（有出路）：

| 本卦 | 動爻 | 爻辭 | 之卦 | 趨勢變化 |
|------|------|------|------|----------|
"""

    for r in sorted(patterns['xiong_to_ji'], key=lambda x: -x['trend_change'])[:20]:
        report += f"| {r['original_name']} | 第{r['line_position']}爻 | {r['yaoci_text']} | {r['changed_name']} | +{r['trend_change']:.2f} |\n"

    report += """
**解讀**：這些案例說明，即使當前爻辭顯凶，變化後反而有轉機。「窮則變，變則通」。

---

## 四、警示發現：「吉爻變凶」案例

以下是動爻本身為吉，但變化後之卦反而更差的案例（好景不長）：

| 本卦 | 動爻 | 爻辭 | 之卦 | 趨勢變化 |
|------|------|------|------|----------|
"""

    for r in sorted(patterns['ji_to_xiong'], key=lambda x: x['trend_change'])[:20]:
        report += f"| {r['original_name']} | 第{r['line_position']}爻 | {r['yaoci_text']} | {r['changed_name']} | {r['trend_change']:.2f} |\n"

    report += """
**解讀**：這些案例說明，即使當前爻辭顯吉，也需注意變化後的走向。「盛極必衰」。

---

## 五、實用解卦指南

### 5.1 看變卦的時機

1. **占得動爻時**：必須同時看本卦和之卦
2. **動爻為凶時**：查看之卦是否有轉機
3. **動爻為吉時**：確認之卦不會逆轉

### 5.2 本卦與之卦的關係類型

| 關係 | 意義 | 解讀 |
|------|------|------|
| 之卦為本卦的錯卦 | 根本性質轉變 | 大變局 |
| 之卦為本卦的綜卦 | 視角/立場轉變 | 換位思考 |
| 僅差一爻 | 微調性變化 | 漸進發展 |

### 5.3 卜卦時的多角度分析

```
完整解讀 = 本卦（現狀）
         + 動爻（轉折點）
         + 之卦（趨勢）
         + 互卦（內在本質）
         + 對爻/應爻（外援）
```

---

## 六、384變卦速查表

"""

    # Group by original hexagram
    by_hexagram = defaultdict(list)
    for r in results:
        by_hexagram[r['original_num']].append(r)

    report += "### 前16卦示例\n\n"

    for hex_num in range(1, 17):
        hex_results = by_hexagram.get(hex_num, [])
        if not hex_results:
            continue

        report += f"#### {hex_num}. {HEXAGRAM_NAMES[hex_num]}\n\n"
        report += "| 動爻 | 爻性 | 之卦 | 爻辭吉凶 | 趨勢 |\n"
        report += "|------|------|------|----------|------|\n"

        for r in hex_results:
            report += f"| {r['line_position']} | {r['line_type']} | {r['changed_name']} | {r['yaoci_class']} | {r['trend_direction']} |\n"

        report += "\n"

    report += """
---

## 附錄：完整數據

完整的384變卦數據保存在：`data/analysis/biangua_384.json`

---

*分析工具：Python*
*數據來源：周易六十四卦爻辭*
"""

    return report


def main():
    print("Loading yaoci data...")
    yaoci_data = load_yaoci_data()

    if not yaoci_data:
        print("Failed to load yaoci data")
        return

    print(f"Loaded {len(yaoci_data)} hexagrams")

    print("Analyzing all 384 single-line changes...")
    results = analyze_all_changes(yaoci_data)
    print(f"Generated {len(results)} transformations")

    print("Finding patterns...")
    patterns = analyze_patterns(results)

    # Save JSON data
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis')
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, 'biangua_384.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'transformations': results,
            'patterns': {
                'summary_stats': patterns['summary_stats'],
                'xiong_to_ji': patterns['xiong_to_ji'][:30],
                'ji_to_xiong': patterns['ji_to_xiong'][:30]
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON to {json_path}")

    # Generate report
    report = generate_report(results, patterns)

    report_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'BIANGUA_ANALYSIS.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Saved report to {report_path}")

    # Print summary
    print("\n=== 變卦分析摘要 ===")
    print(f"總變化數: {patterns['summary_stats']['total_changes']}")
    print(f"凶爻變吉案例: {patterns['summary_stats']['xiong_to_ji_count']}")
    print(f"吉爻變凶案例: {patterns['summary_stats']['ji_to_xiong_count']}")
    print("\n爻位平均趨勢變化:")
    for pos, avg in sorted(patterns['summary_stats']['position_avg_trend'].items()):
        print(f"  第{pos}爻: {avg:+.4f}")


if __name__ == '__main__':
    main()
