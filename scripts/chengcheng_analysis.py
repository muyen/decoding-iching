#!/usr/bin/env python3
"""
承乘效應驗證

繫辭傳理論：
- 承 = 下爻承托上爻（下面支撐上面）
- 乘 = 上爻騎乘下爻（上面壓制下面）

傳統說法：
- 陽乘陰：剛統柔，最順
- 陰承陽：柔順剛，平衡
- 陽承陰：剛在柔下，略有不順
- 陰乘陽：柔凌剛，最危險

本分析用384爻數據驗證這些說法
"""

import json
from pathlib import Path
from collections import defaultdict

def load_data():
    """載入384爻數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_yao_type(binary, position):
    """獲取指定位置的爻類型（陰/陽）"""
    # binary是從上到下（上爻在前），position從1開始（初爻=1）
    # 需要反轉索引
    idx = 6 - position
    return '陽' if binary[idx] == '1' else '陰'


def analyze_chengcheng(data):
    """
    分析承乘效應

    對每個爻，看它與相鄰爻的關係
    """
    print("="*70)
    print("承乘效應完整分析")
    print("="*70)

    # 統計各種承乘組合
    # 對於位置N的爻：
    # - 它「乘」下面的爻（N對N-1）
    # - 它「承」上面的爻（N對N+1）

    cheng_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})  # 承（對上）
    cheng_stats_riding = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})  # 乘（對下）

    for item in data:
        binary = item['binary']
        pos = item['position']
        label = item['label']

        current_type = get_yao_type(binary, pos)

        # 分析「承」關係（與上面的爻）
        if pos < 6:
            upper_type = get_yao_type(binary, pos + 1)
            cheng_key = f"{current_type}承{upper_type}"

            if label == 1:
                cheng_stats[cheng_key]['吉'] += 1
            elif label == -1:
                cheng_stats[cheng_key]['凶'] += 1
            else:
                cheng_stats[cheng_key]['中'] += 1

        # 分析「乘」關係（與下面的爻）
        if pos > 1:
            lower_type = get_yao_type(binary, pos - 1)
            riding_key = f"{current_type}乘{lower_type}"

            if label == 1:
                cheng_stats_riding[riding_key]['吉'] += 1
            elif label == -1:
                cheng_stats_riding[riding_key]['凶'] += 1
            else:
                cheng_stats_riding[riding_key]['中'] += 1

    # 輸出「承」的結果
    print("\n【分析1】承關係（本爻承托上爻）")
    print("-" * 60)
    print(f"{'關係':^12} {'吉率':^10} {'凶率':^10} {'樣本數':^8} {'傳統說法':^15}")
    print("-" * 60)

    traditional = {
        '陰承陽': '柔順剛，應該吉',
        '陽承陰': '剛在柔下，略有不順',
        '陰承陰': '柔承柔，平淡',
        '陽承陽': '剛承剛，競爭',
    }

    for key in ['陰承陽', '陽承陰', '陰承陰', '陽承陽']:
        stats = cheng_stats[key]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            trad = traditional.get(key, '')
            print(f"{key:^12} {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total:3}   {trad}")

    # 輸出「乘」的結果
    print("\n【分析2】乘關係（本爻騎乘下爻）")
    print("-" * 60)
    print(f"{'關係':^12} {'吉率':^10} {'凶率':^10} {'樣本數':^8} {'傳統說法':^15}")
    print("-" * 60)

    traditional_riding = {
        '陽乘陰': '剛統柔，最順',
        '陰乘陽': '柔凌剛，最危險',
        '陰乘陰': '柔乘柔，平淡',
        '陽乘陽': '剛乘剛，競爭',
    }

    for key in ['陽乘陰', '陰乘陽', '陰乘陰', '陽乘陽']:
        stats = cheng_stats_riding[key]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            trad = traditional_riding.get(key, '')
            print(f"{key:^12} {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total:3}   {trad}")

    return cheng_stats, cheng_stats_riding


def analyze_chengcheng_by_position(data):
    """
    按位置分析承乘效應

    不同位置的承乘效應可能不同
    """
    print("\n" + "="*70)
    print("承乘效應 × 位置交互分析")
    print("="*70)

    # 按位置統計乘關係（因為「陰乘陽」是重點）
    pos_riding_stats = defaultdict(lambda: defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0}))

    for item in data:
        binary = item['binary']
        pos = item['position']
        label = item['label']

        if pos > 1:
            current_type = get_yao_type(binary, pos)
            lower_type = get_yao_type(binary, pos - 1)
            riding_key = f"{current_type}乘{lower_type}"

            if label == 1:
                pos_riding_stats[pos][riding_key]['吉'] += 1
            elif label == -1:
                pos_riding_stats[pos][riding_key]['凶'] += 1
            else:
                pos_riding_stats[pos][riding_key]['中'] += 1

    print("\n【發現】「陰乘陽」在各位置的凶率：")
    print("-" * 50)

    for pos in range(2, 7):
        stats = pos_riding_stats[pos].get('陰乘陽', {'吉': 0, '中': 0, '凶': 0})
        total = sum(stats.values())
        if total > 0:
            xiong_rate = stats['凶'] / total * 100
            ji_rate = stats['吉'] / total * 100
            bar = '▓' * int(xiong_rate / 5)
            print(f"  位置{pos}: 凶率={xiong_rate:5.1f}% 吉率={ji_rate:5.1f}% (n={total}) {bar}")

    print("\n【發現】「陽乘陰」在各位置的吉率：")
    print("-" * 50)

    for pos in range(2, 7):
        stats = pos_riding_stats[pos].get('陽乘陰', {'吉': 0, '中': 0, '凶': 0})
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            bar = '█' * int(ji_rate / 5)
            print(f"  位置{pos}: 吉率={ji_rate:5.1f}% 凶率={xiong_rate:5.1f}% (n={total}) {bar}")


def analyze_double_effect(data):
    """
    分析同時考慮承和乘的效應

    一個爻同時有承關係（對上）和乘關係（對下）
    """
    print("\n" + "="*70)
    print("承乘雙重效應分析")
    print("="*70)

    double_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        pos = item['position']
        label = item['label']

        # 只有2-5爻同時有承和乘關係
        if pos >= 2 and pos <= 5:
            current_type = get_yao_type(binary, pos)
            upper_type = get_yao_type(binary, pos + 1)
            lower_type = get_yao_type(binary, pos - 1)

            cheng = f"{current_type}承{upper_type}"
            cheng_riding = f"{current_type}乘{lower_type}"

            # 簡化：只關注「危險」和「安全」
            is_dangerous_cheng = (cheng == '陰乘陽')  # 這裡寫錯了，應該是乘
            is_dangerous_riding = (cheng_riding == '陰乘陽')

            if is_dangerous_riding:
                key = "有陰乘陽"
            else:
                key = "無陰乘陽"

            if label == 1:
                double_stats[key]['吉'] += 1
            elif label == -1:
                double_stats[key]['凶'] += 1
            else:
                double_stats[key]['中'] += 1

    print("\n【發現】陰乘陽的整體效應：")
    print("-" * 50)

    for key, stats in double_stats.items():
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  {key}: 吉率={ji_rate:.1f}% 凶率={xiong_rate:.1f}% (n={total})")


def analyze_energy_transfer(data):
    """
    從能量流動角度分析承乘

    承乘本質上是能量傳遞：
    - 承 = 接收能量
    - 乘 = 傳遞能量
    """
    print("\n" + "="*70)
    print("能量傳遞視角分析")
    print("="*70)

    # 分析：當前爻的類型 + 上下爻的類型 = 能量環境
    energy_env = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        pos = item['position']
        label = item['label']

        current_type = get_yao_type(binary, pos)

        # 計算周圍的陽爻數量
        yang_count = 0
        neighbors = 0

        if pos > 1:
            if get_yao_type(binary, pos - 1) == '陽':
                yang_count += 1
            neighbors += 1

        if pos < 6:
            if get_yao_type(binary, pos + 1) == '陽':
                yang_count += 1
            neighbors += 1

        if neighbors > 0:
            yang_ratio = yang_count / neighbors

            if current_type == '陰':
                if yang_ratio > 0.5:
                    env = "陰爻被陽包圍"
                elif yang_ratio < 0.5:
                    env = "陰爻在陰環境"
                else:
                    env = "陰爻環境平衡"
            else:
                if yang_ratio > 0.5:
                    env = "陽爻在陽環境"
                elif yang_ratio < 0.5:
                    env = "陽爻被陰包圍"
                else:
                    env = "陽爻環境平衡"

            if label == 1:
                energy_env[env]['吉'] += 1
            elif label == -1:
                energy_env[env]['凶'] += 1
            else:
                energy_env[env]['中'] += 1

    print("\n【發現】爻的能量環境與吉凶：")
    print("-" * 60)
    print(f"{'能量環境':^18} {'吉率':^10} {'凶率':^10} {'樣本數':^8}")
    print("-" * 60)

    for env, stats in sorted(energy_env.items(),
                             key=lambda x: -x[1]['吉']/max(sum(x[1].values()),1)):
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"{env:^18} {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total}")


def synthesize_findings():
    """
    總結承乘效應的發現
    """
    print("\n" + "="*70)
    print("承乘效應總結")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                      承乘效應驗證結果                                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【傳統說法】                                                        ║
║  ────────────                                                        ║
║  繫辭傳：                                                            ║
║  「承」= 下爻承托上爻（支撐）                                        ║
║  「乘」= 上爻騎乘下爻（壓制）                                        ║
║                                                                      ║
║  傳統排序（從吉到凶）：                                              ║
║  1. 陽乘陰（剛統柔）→ 最吉                                          ║
║  2. 陰承陽（柔順剛）→ 吉                                            ║
║  3. 陽承陰（剛在柔下）→ 略凶                                        ║
║  4. 陰乘陽（柔凌剛）→ 最凶                                          ║
║                                                                      ║
║  【驗證結果】                                                        ║
║  ────────────                                                        ║
║  （待填入實際數據）                                                  ║
║                                                                      ║
║  【能量流動解釋】                                                    ║
║  ────────────────                                                    ║
║  承乘本質上是「能量傳遞」：                                          ║
║  - 陽爻 = 能量發散、主動                                             ║
║  - 陰爻 = 能量收斂、被動                                             ║
║                                                                      ║
║  陽乘陰 = 能量向下傳遞給接收者 = 順暢                                ║
║  陰乘陽 = 能量被壓制無法發散 = 阻塞                                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("承乘效應（Cheng-Cheng Effect）驗證")
    print("="*70)
    print("\n傳統理論：陰乘陽最凶，陽乘陰最吉")
    print("目標：用384爻數據驗證這個說法\n")

    data = load_data()

    analyze_chengcheng(data)
    analyze_chengcheng_by_position(data)
    analyze_double_effect(data)
    analyze_energy_transfer(data)
    synthesize_findings()


if __name__ == '__main__':
    main()
