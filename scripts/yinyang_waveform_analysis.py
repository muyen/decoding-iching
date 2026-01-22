#!/usr/bin/env python3
"""
陰陽消長波形分析

核心假設：
1. 六爻可視為時間序列（從初爻到上爻）
2. 陰陽的「消長」（上升/下降趨勢）影響吉凶
3. 「陽長陰消」vs「陽消陰長」有不同效應

分析維度：
1. 波形趨勢（上升、下降、穩定）
2. 轉折點位置
3. 能量積累模式
4. 與位置效應的交互
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics


def load_data():
    """載入384爻數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def binary_to_wave(binary):
    """
    將六爻二進制轉換為波形序列

    返回：從初爻到上爻的陽爻值列表 [1/0, 1/0, ...]
    """
    # binary是從上到下（上爻在前），需要反轉
    return [int(c) for c in reversed(binary)]


def analyze_wave_trend(wave):
    """
    分析波形的整體趨勢

    返回：
    - trend: 'rising', 'falling', 'stable', 'volatile'
    - score: 趨勢強度
    """
    # 計算差分序列
    diffs = [wave[i+1] - wave[i] for i in range(len(wave)-1)]

    # 計算趨勢分數：正=上升，負=下降
    trend_score = sum(diffs)

    # 計算波動性
    volatility = sum(abs(d) for d in diffs)

    if volatility == 0:
        return 'constant', 0
    elif abs(trend_score) >= 3:
        return 'strong_rising' if trend_score > 0 else 'strong_falling', trend_score
    elif abs(trend_score) >= 1:
        return 'rising' if trend_score > 0 else 'falling', trend_score
    else:
        return 'volatile', trend_score


def analyze_turning_points(wave):
    """
    分析波形的轉折點

    返回轉折點位置列表（1-indexed爻位）
    """
    turning_points = []

    for i in range(1, len(wave)-1):
        # 局部極值
        if wave[i] > wave[i-1] and wave[i] > wave[i+1]:
            turning_points.append(('peak', i+1))
        elif wave[i] < wave[i-1] and wave[i] < wave[i+1]:
            turning_points.append(('valley', i+1))
        # 陰陽轉換點
        elif wave[i] != wave[i-1] and wave[i] == wave[i+1]:
            turning_points.append(('transition', i+1))

    return turning_points


def analyze_energy_accumulation(wave):
    """
    分析能量積累模式

    陽爻 = 能量
    從初爻累積到上爻，看能量如何分布
    """
    # 累積和
    cumsum = []
    total = 0
    for v in wave:
        total += v
        cumsum.append(total)

    # 能量分布特徵
    lower_energy = sum(wave[:3])  # 下卦能量
    upper_energy = sum(wave[3:])  # 上卦能量

    # 能量集中位置
    weighted_pos = sum(v * (i+1) for i, v in enumerate(wave))
    total_energy = sum(wave)
    center_of_mass = weighted_pos / total_energy if total_energy > 0 else 3.5

    return {
        'cumsum': cumsum,
        'lower_energy': lower_energy,
        'upper_energy': upper_energy,
        'center_of_mass': center_of_mass,
        'total_energy': total_energy
    }


def wave_trend_analysis(data):
    """分析波形趨勢與吉凶的關係"""
    print("\n" + "="*70)
    print("【分析1】陰陽消長趨勢與吉凶")
    print("="*70)

    trend_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        label = item['label']

        wave = binary_to_wave(binary)
        trend, score = analyze_wave_trend(wave)

        if label == 1:
            trend_stats[trend]['吉'] += 1
        elif label == -1:
            trend_stats[trend]['凶'] += 1
        else:
            trend_stats[trend]['中'] += 1

    print("\n波形趨勢分類：")
    print("-" * 60)
    print(f"{'趨勢':^15} {'吉率':^10} {'凶率':^10} {'樣本數':^8} {'解讀'}")
    print("-" * 60)

    interpretations = {
        'strong_rising': '陽氣大漲',
        'rising': '陽氣漸長',
        'stable': '陰陽平穩',
        'falling': '陽氣漸消',
        'strong_falling': '陽氣大消',
        'volatile': '陰陽波動',
        'constant': '全陽或全陰',
    }

    for trend in ['strong_rising', 'rising', 'volatile', 'stable', 'falling', 'strong_falling', 'constant']:
        stats = trend_stats.get(trend, {'吉': 0, '中': 0, '凶': 0})
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            interp = interpretations.get(trend, '')
            print(f"{trend:^15} {ji_rate:5.1f}%     {xiong_rate:5.1f}%     n={total:3}  {interp}")

    return trend_stats


def turning_point_analysis(data):
    """分析轉折點位置與吉凶"""
    print("\n" + "="*70)
    print("【分析2】轉折點位置與吉凶")
    print("="*70)

    # 統計各位置作為轉折點的效應
    tp_at_pos = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})
    tp_count_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        label = item['label']

        wave = binary_to_wave(binary)
        tps = analyze_turning_points(wave)

        # 轉折點數量
        tp_count = len(tps)
        if label == 1:
            tp_count_stats[tp_count]['吉'] += 1
        elif label == -1:
            tp_count_stats[tp_count]['凶'] += 1
        else:
            tp_count_stats[tp_count]['中'] += 1

        # 各位置的轉折點
        for tp_type, pos in tps:
            if label == 1:
                tp_at_pos[pos]['吉'] += 1
            elif label == -1:
                tp_at_pos[pos]['凶'] += 1
            else:
                tp_at_pos[pos]['中'] += 1

    print("\n轉折點數量與吉凶：")
    print("-" * 50)

    for count in range(5):
        stats = tp_count_stats[count]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            bar = '█' * int(ji_rate / 5)
            print(f"  {count}個轉折點: 吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  (n={total:3}) {bar}")

    print("\n轉折點在各位置的效應：")
    print("-" * 50)

    for pos in range(2, 6):  # 只有2-5爻可能是轉折點
        stats = tp_at_pos[pos]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  爻{pos}為轉折點: 吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  (n={total})")

    return tp_at_pos, tp_count_stats


def energy_distribution_analysis(data):
    """分析能量分布與吉凶"""
    print("\n" + "="*70)
    print("【分析3】能量分布模式與吉凶")
    print("="*70)

    # 上下卦能量差
    energy_diff_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})
    # 能量重心
    com_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})
    # 總能量
    total_energy_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        label = item['label']

        wave = binary_to_wave(binary)
        energy = analyze_energy_accumulation(wave)

        # 能量差
        diff = energy['upper_energy'] - energy['lower_energy']
        if diff > 0:
            diff_key = '上強下弱'
        elif diff < 0:
            diff_key = '下強上弱'
        else:
            diff_key = '上下平衡'

        # 能量重心
        com = energy['center_of_mass']
        if com < 2.5:
            com_key = '重心偏下'
        elif com > 4.5:
            com_key = '重心偏上'
        else:
            com_key = '重心居中'

        # 總能量
        total = energy['total_energy']
        if total <= 2:
            total_key = '低能量'
        elif total >= 4:
            total_key = '高能量'
        else:
            total_key = '中能量'

        if label == 1:
            energy_diff_stats[diff_key]['吉'] += 1
            com_stats[com_key]['吉'] += 1
            total_energy_stats[total_key]['吉'] += 1
        elif label == -1:
            energy_diff_stats[diff_key]['凶'] += 1
            com_stats[com_key]['凶'] += 1
            total_energy_stats[total_key]['凶'] += 1
        else:
            energy_diff_stats[diff_key]['中'] += 1
            com_stats[com_key]['中'] += 1
            total_energy_stats[total_key]['中'] += 1

    print("\n【發現A】上下卦能量差：")
    print("-" * 50)
    for key in ['下強上弱', '上下平衡', '上強下弱']:
        stats = energy_diff_stats[key]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  {key}: 吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  (n={total})")

    print("\n【發現B】能量重心位置：")
    print("-" * 50)
    for key in ['重心偏下', '重心居中', '重心偏上']:
        stats = com_stats[key]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  {key}: 吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  (n={total})")

    print("\n【發現C】總能量水平：")
    print("-" * 50)
    for key in ['低能量', '中能量', '高能量']:
        stats = total_energy_stats[key]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  {key}: 吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  (n={total})")

    return energy_diff_stats, com_stats, total_energy_stats


def wave_pattern_analysis(data):
    """分析特定波形模式與吉凶"""
    print("\n" + "="*70)
    print("【分析4】特定波形模式與吉凶")
    print("="*70)

    pattern_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    # 定義典型模式
    patterns = {
        '泰型': lambda w: sum(w[:3]) >= 2 and sum(w[3:]) <= 1,  # 下陽上陰
        '否型': lambda w: sum(w[:3]) <= 1 and sum(w[3:]) >= 2,  # 下陰上陽
        '乾型': lambda w: sum(w) == 6,  # 全陽
        '坤型': lambda w: sum(w) == 0,  # 全陰
        '既濟型': lambda w: w == [1, 0, 1, 0, 1, 0] or w == [0, 1, 0, 1, 0, 1],  # 交替
        '漸進型': lambda w: all(w[i] <= w[i+1] for i in range(5)),  # 漸增
        '漸退型': lambda w: all(w[i] >= w[i+1] for i in range(5)),  # 漸減
        'V型': lambda w: w[2] < w[0] and w[2] < w[5] and w[3] < w[0],  # 中間低
        '倒V型': lambda w: w[2] > w[0] and w[2] > w[5] and w[3] > w[5],  # 中間高
    }

    for item in data:
        binary = item['binary']
        label = item['label']

        wave = binary_to_wave(binary)

        for pattern_name, pattern_func in patterns.items():
            try:
                if pattern_func(wave):
                    if label == 1:
                        pattern_stats[pattern_name]['吉'] += 1
                    elif label == -1:
                        pattern_stats[pattern_name]['凶'] += 1
                    else:
                        pattern_stats[pattern_name]['中'] += 1
            except:
                pass

    print("\n典型波形模式：")
    print("-" * 60)
    print(f"{'模式':^10} {'吉率':^10} {'凶率':^10} {'樣本數':^8} {'特徵'}")
    print("-" * 60)

    descriptions = {
        '泰型': '下強上弱，地天泰',
        '否型': '上強下弱，天地否',
        '乾型': '全陽，純剛',
        '坤型': '全陰，純柔',
        '既濟型': '交替，既濟',
        '漸進型': '陽氣漸長',
        '漸退型': '陽氣漸消',
        'V型': '中間低谷',
        '倒V型': '中間高峰',
    }

    for pattern in ['泰型', '否型', '乾型', '坤型', '漸進型', '漸退型', 'V型', '倒V型', '既濟型']:
        stats = pattern_stats[pattern]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            desc = descriptions.get(pattern, '')
            print(f"{pattern:^10} {ji_rate:5.1f}%     {xiong_rate:5.1f}%     n={total:3}  {desc}")

    return pattern_stats


def position_wave_interaction(data):
    """分析位置與波形的交互效應"""
    print("\n" + "="*70)
    print("【分析5】位置×波形交互效應")
    print("="*70)

    # 在上升趨勢 vs 下降趨勢中，各位置的吉率
    pos_in_trend = defaultdict(lambda: defaultdict(lambda: {'吉': 0, '凶': 0}))

    for item in data:
        binary = item['binary']
        pos = item['position']
        label = item['label']

        wave = binary_to_wave(binary)
        trend, _ = analyze_wave_trend(wave)

        if trend in ['strong_rising', 'rising']:
            trend_key = '上升趨勢'
        elif trend in ['strong_falling', 'falling']:
            trend_key = '下降趨勢'
        else:
            trend_key = '波動/穩定'

        if label == 1:
            pos_in_trend[pos][trend_key]['吉'] += 1
        elif label == -1:
            pos_in_trend[pos][trend_key]['凶'] += 1

    print("\n各位置在不同趨勢中的吉率：")
    print("-" * 60)
    print(f"{'位置':^6}", end='')
    for trend in ['上升趨勢', '下降趨勢', '波動/穩定']:
        print(f"{trend:^15}", end='')
    print()
    print("-" * 60)

    for pos in range(1, 7):
        print(f"爻{pos:^4}", end='')
        for trend in ['上升趨勢', '下降趨勢', '波動/穩定']:
            stats = pos_in_trend[pos][trend]
            total = stats['吉'] + stats['凶']
            if total > 0:
                ji_rate = stats['吉'] / total * 100
                print(f"{ji_rate:5.1f}% (n={total:2})", end='')
            else:
                print(f"{'  -':^15}", end='')
        print()

    print("\n【解讀】")
    print("  - 上升趨勢：陽氣增長環境")
    print("  - 下降趨勢：陽氣衰退環境")
    print("  - 不同位置在不同趨勢中表現不同")

    return pos_in_trend


def synthesize_waveform_findings():
    """總結波形分析發現"""
    print("\n" + "="*70)
    print("陰陽消長波形分析總結")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    陰陽消長波形分析結果                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【波形趨勢效應】                                                    ║
║  ────────────────                                                    ║
║  傳統假設：陽長陰消=吉，陽消陰長=凶                                  ║
║  實際驗證：（待填入數據）                                            ║
║                                                                      ║
║  【能量分布效應】                                                    ║
║  ────────────────                                                    ║
║  上下卦能量差：下強上弱 vs 上強下弱                                  ║
║  能量重心：偏下 vs 偏上 vs 居中                                      ║
║                                                                      ║
║  【轉折點效應】                                                      ║
║  ──────────────                                                      ║
║  轉折點數量與吉凶的關係                                              ║
║  特定位置作為轉折點的意義                                            ║
║                                                                      ║
║  【典型模式效應】                                                    ║
║  ────────────────                                                    ║
║  泰型（下陽上陰）vs 否型（下陰上陽）                                 ║
║  漸進型 vs 漸退型                                                    ║
║  V型 vs 倒V型                                                        ║
║                                                                      ║
║  【核心洞見】                                                        ║
║  ──────────────                                                      ║
║  1. 波形趨勢是判斷吉凶的重要維度                                     ║
║  2. 能量分布比總能量更重要                                           ║
║  3. 位置效應與波形效應有交互作用                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("陰陽消長波形分析")
    print("="*70)
    print("\n將六爻視為時間序列，分析陰陽消長模式與吉凶的關係")

    data = load_data()
    print(f"\n載入 {len(data)} 條爻數據")

    # 分析
    wave_trend_analysis(data)
    turning_point_analysis(data)
    energy_distribution_analysis(data)
    wave_pattern_analysis(data)
    position_wave_interaction(data)

    # 總結
    synthesize_waveform_findings()


if __name__ == '__main__':
    main()
