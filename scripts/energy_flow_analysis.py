#!/usr/bin/env python3
"""
能量流動分析

用戶洞見：「it is flow of yin yang - flow of energy - so the flow determine
and interact and cause the result」

核心假設：吉凶由陰陽能量的流動決定
- 能量順暢流動 = 吉
- 能量阻塞停滯 = 凶
- 能量方向決定結果
"""

import json
from pathlib import Path
from collections import defaultdict
import math

def load_data():
    """載入384爻數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_yao_sequence(binary):
    """從binary獲取六爻序列（從初爻到上爻）"""
    # binary是從上到下，我們需要從下到上
    return [int(b) for b in reversed(binary)]


def analyze_yinyang_flow(data):
    """
    分析1：陰陽消長流動

    假設：六爻中陽氣的「流動趨勢」決定吉凶
    - 陽氣上升（下陰上陽）= 吉
    - 陽氣下降（下陽上陰）= 凶
    """
    print("\n" + "="*70)
    print("分析1：陰陽消長流動")
    print("="*70)

    flow_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        yao_seq = get_yao_sequence(binary)
        label = item['label']

        # 計算下卦和上卦的陽爻數
        lower_yang = sum(yao_seq[:3])  # 初、二、三
        upper_yang = sum(yao_seq[3:])  # 四、五、上

        # 判斷流動趨勢
        if upper_yang > lower_yang:
            flow = "陽氣上升"
        elif upper_yang < lower_yang:
            flow = "陽氣下降"
        else:
            flow = "陰陽平衡"

        if label == 1:
            flow_stats[flow]['吉'] += 1
        elif label == -1:
            flow_stats[flow]['凶'] += 1
        else:
            flow_stats[flow]['中'] += 1

    print("\n【發現】陽氣流動方向與吉凶：")
    print("-" * 60)
    print(f"{'流動趨勢':^12} {'吉率':^10} {'凶率':^10} {'樣本數':^8}")
    print("-" * 60)

    for flow, stats in sorted(flow_stats.items(),
                              key=lambda x: -x[1]['吉']/max(sum(x[1].values()),1)):
        total = sum(stats.values())
        ji_rate = stats['吉'] / total * 100
        xiong_rate = stats['凶'] / total * 100
        print(f"{flow:^12} {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total}")


def analyze_momentum(data):
    """
    分析2：能量動量

    假設：爻位中的陽爻「位置」決定能量強度
    高位陽爻 = 能量高
    低位陽爻 = 能量低
    """
    print("\n" + "="*70)
    print("分析2：能量動量分析")
    print("="*70)

    # 計算每個卦的「能量動量」
    momentum_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        yao_seq = get_yao_sequence(binary)

        # 計算動量：陽爻位置的加權和
        # 位置越高，權重越大
        momentum = sum((i+1) * yao_seq[i] for i in range(6))
        # 歸一化到0-21範圍
        max_momentum = 1+2+3+4+5+6  # = 21
        momentum_ratio = momentum / max_momentum

        # 分組
        if momentum_ratio > 0.6:
            group = "高動量(陽在高位)"
        elif momentum_ratio < 0.4:
            group = "低動量(陽在低位)"
        else:
            group = "中動量"

        label = item['label']
        if label == 1:
            momentum_stats[group]['吉'] += 1
        elif label == -1:
            momentum_stats[group]['凶'] += 1
        else:
            momentum_stats[group]['中'] += 1

    print("\n【發現】能量動量與吉凶：")
    print("-" * 60)

    for group in ["高動量(陽在高位)", "中動量", "低動量(陽在低位)"]:
        stats = momentum_stats[group]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  {group}: 吉率={ji_rate:.1f}% 凶率={xiong_rate:.1f}% (n={total})")


def analyze_flow_blockage(data):
    """
    分析3：能量阻塞

    假設：連續的陰爻形成「阻塞」，阻礙能量流動
    連續陰爻越多 = 阻塞越嚴重 = 越凶
    """
    print("\n" + "="*70)
    print("分析3：能量阻塞分析")
    print("="*70)

    def count_max_consecutive_yin(yao_seq):
        """計算最長連續陰爻數"""
        max_count = 0
        current = 0
        for y in yao_seq:
            if y == 0:  # 陰爻
                current += 1
                max_count = max(max_count, current)
            else:
                current = 0
        return max_count

    blockage_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        yao_seq = get_yao_sequence(binary)
        max_yin = count_max_consecutive_yin(yao_seq)

        label = item['label']
        if label == 1:
            blockage_stats[max_yin]['吉'] += 1
        elif label == -1:
            blockage_stats[max_yin]['凶'] += 1
        else:
            blockage_stats[max_yin]['中'] += 1

    print("\n【發現】連續陰爻（阻塞）與吉凶：")
    print("-" * 60)
    print(f"{'最長連續陰爻':^15} {'吉率':^10} {'凶率':^10} {'樣本數':^8}")
    print("-" * 60)

    for blockage in sorted(blockage_stats.keys()):
        stats = blockage_stats[blockage]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            blockage_desc = f"{blockage}個連續陰爻"
            print(f"{blockage_desc:^15} {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total}")


def analyze_yinyang_transition(data):
    """
    分析4：陰陽轉換點

    假設：陰陽轉換的「位置」影響吉凶
    - 在關鍵位置（三、四爻）轉換 = 轉折
    - 轉換點決定能量流向
    """
    print("\n" + "="*70)
    print("分析4：陰陽轉換點分析")
    print("="*70)

    def find_transitions(yao_seq):
        """找出所有陰陽轉換點"""
        transitions = []
        for i in range(5):
            if yao_seq[i] != yao_seq[i+1]:
                transitions.append(i+1)  # 轉換發生在第i+1和i+2爻之間
        return transitions

    transition_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        yao_seq = get_yao_sequence(binary)
        transitions = find_transitions(yao_seq)

        # 關注在「三四爻之間」的轉換（上下卦交界）
        has_boundary_transition = 3 in transitions

        key = "有邊界轉換" if has_boundary_transition else "無邊界轉換"

        label = item['label']
        if label == 1:
            transition_stats[key]['吉'] += 1
        elif label == -1:
            transition_stats[key]['凶'] += 1
        else:
            transition_stats[key]['中'] += 1

    print("\n【發現】上下卦交界處的陰陽轉換：")
    print("-" * 60)

    for key, stats in transition_stats.items():
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"  {key}: 吉率={ji_rate:.1f}% 凶率={xiong_rate:.1f}% (n={total})")


def analyze_energy_gradient(data):
    """
    分析5：能量梯度

    假設：六爻中的陰陽分布形成「梯度」
    - 平滑梯度 = 能量順暢 = 吉
    - 陡峭梯度 = 能量激烈 = 凶
    """
    print("\n" + "="*70)
    print("分析5：能量梯度分析")
    print("="*70)

    def calculate_gradient(yao_seq):
        """計算能量變化的劇烈程度"""
        changes = 0
        for i in range(5):
            if yao_seq[i] != yao_seq[i+1]:
                changes += 1
        return changes

    gradient_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        binary = item['binary']
        yao_seq = get_yao_sequence(binary)
        gradient = calculate_gradient(yao_seq)

        label = item['label']
        if label == 1:
            gradient_stats[gradient]['吉'] += 1
        elif label == -1:
            gradient_stats[gradient]['凶'] += 1
        else:
            gradient_stats[gradient]['中'] += 1

    print("\n【發現】能量變化次數與吉凶：")
    print("-" * 60)
    print(f"{'陰陽轉換次數':^15} {'吉率':^10} {'凶率':^10} {'樣本數':^8}")
    print("-" * 60)

    for gradient in sorted(gradient_stats.keys()):
        stats = gradient_stats[gradient]
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"     {gradient}次         {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total}")


def analyze_trigram_interaction_energy(data):
    """
    分析6：卦德能量交互

    假設：上下卦的「能量屬性」決定交互結果
    """
    print("\n" + "="*70)
    print("分析6：卦德能量交互")
    print("="*70)

    HEXAGRAM_TRIGRAMS = {
        1: ('乾', '乾'), 2: ('坤', '坤'), 3: ('震', '坎'), 4: ('坎', '艮'),
        5: ('乾', '坎'), 6: ('坎', '乾'), 7: ('坎', '坤'), 8: ('坤', '坎'),
        9: ('乾', '巽'), 10: ('兌', '乾'), 11: ('乾', '坤'), 12: ('坤', '乾'),
        13: ('離', '乾'), 14: ('乾', '離'), 15: ('艮', '坤'), 16: ('坤', '震'),
        17: ('兌', '震'), 18: ('巽', '艮'), 19: ('兌', '坤'), 20: ('坤', '巽'),
        21: ('震', '離'), 22: ('離', '艮'), 23: ('艮', '坤'), 24: ('坤', '震'),
        25: ('震', '乾'), 26: ('乾', '艮'), 27: ('震', '艮'), 28: ('兌', '巽'),
        29: ('坎', '坎'), 30: ('離', '離'), 31: ('兌', '艮'), 32: ('巽', '震'),
        33: ('艮', '乾'), 34: ('乾', '震'), 35: ('坤', '離'), 36: ('離', '坤'),
        37: ('離', '巽'), 38: ('兌', '離'), 39: ('艮', '坎'), 40: ('坎', '震'),
        41: ('兌', '艮'), 42: ('巽', '震'), 43: ('兌', '乾'), 44: ('乾', '巽'),
        45: ('兌', '坤'), 46: ('坤', '巽'), 47: ('兌', '坎'), 48: ('坎', '巽'),
        49: ('兌', '離'), 50: ('離', '巽'), 51: ('震', '震'), 52: ('艮', '艮'),
        53: ('艮', '巽'), 54: ('兌', '震'), 55: ('震', '離'), 56: ('離', '艮'),
        57: ('巽', '巽'), 58: ('兌', '兌'), 59: ('坎', '巽'), 60: ('兌', '坎'),
        61: ('兌', '巽'), 62: ('震', '艮'), 63: ('坎', '離'), 64: ('離', '坎'),
    }

    # 八卦能量屬性
    # 說卦傳：乾健、坤順、震動、巽入、坎陷、離麗、艮止、兌說
    trigram_energy = {
        '乾': {'type': '剛', 'direction': '上', 'yang_count': 3},
        '坤': {'type': '柔', 'direction': '下', 'yang_count': 0},
        '震': {'type': '動', 'direction': '上', 'yang_count': 1},
        '巽': {'type': '入', 'direction': '下', 'yang_count': 2},
        '坎': {'type': '陷', 'direction': '流', 'yang_count': 1},
        '離': {'type': '麗', 'direction': '外', 'yang_count': 2},
        '艮': {'type': '止', 'direction': '止', 'yang_count': 1},
        '兌': {'type': '說', 'direction': '外', 'yang_count': 2},
    }

    # 分析能量交互
    interaction_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        hex_num = item['hex_num']
        if hex_num not in HEXAGRAM_TRIGRAMS:
            continue

        lower, upper = HEXAGRAM_TRIGRAMS[hex_num]
        lower_e = trigram_energy.get(lower, {})
        upper_e = trigram_energy.get(upper, {})

        if not lower_e or not upper_e:
            continue

        # 判斷能量交互類型
        lower_dir = lower_e['direction']
        upper_dir = upper_e['direction']

        if lower_dir == '上' and upper_dir == '下':
            interaction = "相迎（下上上下）"
        elif lower_dir == '上' and upper_dir == '上':
            interaction = "同升（都往上）"
        elif lower_dir == '下' and upper_dir == '下':
            interaction = "同降（都往下）"
        elif lower_dir == '止' or upper_dir == '止':
            interaction = "有阻（有止）"
        elif lower_dir == '陷' or upper_dir == '陷':
            interaction = "有險（有陷）"
        else:
            interaction = "其他"

        label = item['label']
        if label == 1:
            interaction_stats[interaction]['吉'] += 1
        elif label == -1:
            interaction_stats[interaction]['凶'] += 1
        else:
            interaction_stats[interaction]['中'] += 1

    print("\n【發現】卦德能量方向與吉凶：")
    print("-" * 60)
    print(f"{'能量交互':^15} {'吉率':^10} {'凶率':^10} {'樣本數':^8}")
    print("-" * 60)

    for interaction, stats in sorted(interaction_stats.items(),
                                     key=lambda x: -x[1]['吉']/max(sum(x[1].values()),1)):
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            print(f"{interaction:^15} {ji_rate:6.1f}%    {xiong_rate:6.1f}%    n={total}")


def synthesize_energy_theory():
    """
    綜合能量流動理論
    """
    print("\n" + "="*70)
    print("能量流動理論總結")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                      能量流動決定吉凶                                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【核心原理】                                                        ║
║  ────────────                                                        ║
║  易經描述的是「能量的狀態和流動」                                    ║
║                                                                      ║
║  陰（─ ─）= 能量收斂、靜止、接受                                    ║
║  陽（───）= 能量發散、運動、給予                                    ║
║                                                                      ║
║  吉 = 能量順暢流動，符合自然規律                                     ║
║  凶 = 能量阻塞停滯，違背自然規律                                     ║
║                                                                      ║
║  【具體規律】                                                        ║
║  ────────────                                                        ║
║                                                                      ║
║  1. 方向規律：                                                       ║
║     陽氣自然向上，陰氣自然向下                                       ║
║     下陽上陰 = 陰陽交感 = 泰卦 = 吉                                  ║
║     下陰上陽 = 陰陽不交 = 否卦 = 凶                                  ║
║                                                                      ║
║  2. 阻塞規律：                                                       ║
║     連續陰爻 = 能量阻塞區                                            ║
║     阻塞越多 = 能量越難流動 = 越凶                                   ║
║                                                                      ║
║  3. 位置規律：                                                       ║
║     三爻 = 上下卦交界 = 能量轉換區 = 最不穩定                        ║
║     五爻 = 能量最高點 = 最有力                                       ║
║                                                                      ║
║  4. 梯度規律：                                                       ║
║     陰陽轉換次數 = 能量變化劇烈程度                                  ║
║     過於劇烈 = 不穩定 = 較凶                                         ║
║     過於平緩 = 停滯 = 較凶                                           ║
║     適中變化 = 健康流動 = 較吉                                       ║
║                                                                      ║
║  【與傳統理論的對應】                                                ║
║  ──────────────────                                                  ║
║                                                                      ║
║  - 「三多凶」= 能量轉換區最不穩定                                    ║
║  - 「得中」  = 能量分布平衡                                          ║
║  - 「時義」  = 能量流動的時機對不對                                  ║
║  - 「承乘」  = 相鄰爻之間的能量傳遞                                  ║
║  - 「應」    = 對應位置的能量共振                                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("能量流動分析")
    print("="*70)
    print("\n核心假設：吉凶由陰陽能量的流動決定\n")

    data = load_data()

    analyze_yinyang_flow(data)
    analyze_momentum(data)
    analyze_flow_blockage(data)
    analyze_yinyang_transition(data)
    analyze_energy_gradient(data)
    analyze_trigram_interaction_energy(data)
    synthesize_energy_theory()


if __name__ == '__main__':
    main()
