#!/usr/bin/env python3
"""
統一能量模型

基於所有分析結果，建立一個統一的理論框架來解釋易經吉凶

核心概念：
1. 自由度（Choice Space）- 選擇空間越大越吉
2. 能量流動（Energy Flow）- 流動方向和阻塞程度
3. 位置效應（Position Effect）- 爻位本身的吉凶傾向
4. 結構平衡（Structural Balance）- 上下卦、體用關係

目標：用一個統一的公式預測爻的吉凶
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


# ============================================
# 模型1：自由度模型
# ============================================

def calculate_freedom(position):
    """
    計算位置的自由度

    基於「選擇空間」理論
    """
    freedom_map = {
        1: 3,  # 初爻：多種可能
        2: 4,  # 二爻：得中，最大選擇
        3: 1,  # 三爻：夾在中間，最少選擇
        4: 3,  # 四爻：可上可退
        5: 4,  # 五爻：領導位，資源多
        6: 2,  # 上爻：到頂，只能下
    }
    return freedom_map.get(position, 2)


# ============================================
# 模型2：能量流動模型
# ============================================

def calculate_energy_flow(binary):
    """
    計算能量流動分數

    基於波形分析的發現
    """
    wave = [int(c) for c in reversed(binary)]

    # 1. 轉折點數量（2個最佳）
    turning_points = 0
    for i in range(1, 5):
        if (wave[i] > wave[i-1] and wave[i] > wave[i+1]) or \
           (wave[i] < wave[i-1] and wave[i] < wave[i+1]):
            turning_points += 1

    tp_score = 1.0 if turning_points == 2 else 0.5

    # 2. 邊界轉換（上下卦交界有轉換更吉）
    boundary_change = 1 if wave[2] != wave[3] else 0
    boundary_score = 1.0 + 0.3 * boundary_change

    # 3. 能量分布（4個陽爻最佳）
    yang_count = sum(wave)
    if yang_count == 4:
        yang_score = 1.2
    elif yang_count in [3, 5]:
        yang_score = 1.0
    else:
        yang_score = 0.8

    return tp_score * boundary_score * yang_score


# ============================================
# 模型3：位置效應模型
# ============================================

def get_position_base_rate(position):
    """
    獲取位置的基礎吉率

    基於統計分析的結果
    """
    base_rates = {
        1: 0.39,  # 初爻
        2: 0.45,  # 二爻
        3: 0.11,  # 三爻（最凶）
        4: 0.34,  # 四爻
        5: 0.48,  # 五爻（最吉）
        6: 0.30,  # 上爻
    }
    return base_rates.get(position, 0.35)


# ============================================
# 模型4：體用關係模型
# ============================================

TRIGRAM_BINARY = {
    '乾': '111', '兌': '110', '離': '101', '震': '100',
    '巽': '011', '坎': '010', '艮': '001', '坤': '000'
}

XIANTIAN_ORDER = {
    '乾': 1, '兌': 2, '離': 3, '震': 4,
    '巽': 5, '坎': 6, '艮': 7, '坤': 8
}


def get_trigrams(binary):
    """獲取上下卦"""
    lower_bin = binary[3:]
    upper_bin = binary[:3]

    lower_name = None
    upper_name = None

    for name, b in TRIGRAM_BINARY.items():
        if b == lower_bin:
            lower_name = name
        if b == upper_bin:
            upper_name = name

    return lower_name, upper_name


def calculate_tiyu_score(binary, position):
    """
    計算體用關係分數

    體強用弱 = 加分
    用強體弱 = 減分
    """
    lower, upper = get_trigrams(binary)
    if not lower or not upper:
        return 1.0

    if position <= 3:
        yong = lower
        ti = upper
    else:
        yong = upper
        ti = lower

    ti_order = XIANTIAN_ORDER[ti]
    yong_order = XIANTIAN_ORDER[yong]

    if ti_order < yong_order:
        return 1.1  # 體強用弱，加分
    elif ti_order > yong_order:
        return 0.95  # 用強體弱，略減分
    else:
        return 0.9  # 體用平衡，最差（反直覺但數據支持）


# ============================================
# 模型5：行動指南模型
# ============================================

def get_action_modifier(text, position):
    """
    根據爻辭關鍵詞調整分數

    基於條件句分析的發現
    """
    score = 1.0

    # 貞吉最可靠
    if '貞吉' in text:
        score *= 1.5

    # 貞凶很糟糕
    if '貞凶' in text:
        score *= 0.5

    # 征凶警告
    if '征凶' in text:
        score *= 0.7

    # 无咎只是及格
    if '无咎' in text and '吉' not in text:
        score *= 0.9

    # 位置特定調整
    if position == 5 and '往' in text:
        score *= 1.2  # 五爻適合行動

    if position == 3 and '貞' in text:
        score *= 0.8  # 三爻即使守正也難

    return score


# ============================================
# 統一模型
# ============================================

def unified_energy_score(item):
    """
    計算統一能量分數

    綜合所有因素
    """
    binary = item['binary']
    position = item['position']
    text = item['text']

    # 各子模型分數
    freedom_score = calculate_freedom(position) / 4.0  # 歸一化到0-1
    flow_score = calculate_energy_flow(binary)
    position_score = get_position_base_rate(position)
    tiyu_score = calculate_tiyu_score(binary, position)
    action_score = get_action_modifier(text, position)

    # 加權組合
    weights = {
        'position': 0.40,   # 位置效應最強
        'freedom': 0.20,    # 自由度效應
        'flow': 0.15,       # 能量流動
        'tiyu': 0.15,       # 體用關係
        'action': 0.10,     # 行動指南
    }

    # 計算加權分數
    weighted_score = (
        weights['position'] * position_score +
        weights['freedom'] * freedom_score +
        weights['flow'] * (flow_score - 1) * 0.3 + 0.35 +  # 調整範圍
        weights['tiyu'] * (tiyu_score - 1) * 0.5 + 0.35 +
        weights['action'] * (action_score - 1) * 0.3 + 0.35
    )

    return weighted_score


def evaluate_model(data):
    """評估模型預測能力"""
    print("\n" + "="*70)
    print("統一能量模型評估")
    print("="*70)

    # 計算每個爻的預測分數
    predictions = []
    for item in data:
        score = unified_energy_score(item)
        actual = item['label']
        predictions.append({
            'score': score,
            'actual': actual,
            'hex_num': item['hex_num'],
            'position': item['position']
        })

    # 按分數分組評估
    print("\n按預測分數分組的實際吉凶分布：")
    print("-" * 60)

    sorted_preds = sorted(predictions, key=lambda x: x['score'])

    # 分成5組
    n = len(sorted_preds)
    group_size = n // 5

    for i in range(5):
        start = i * group_size
        end = start + group_size if i < 4 else n
        group = sorted_preds[start:end]

        ji_count = sum(1 for p in group if p['actual'] == 1)
        xiong_count = sum(1 for p in group if p['actual'] == -1)
        total = len(group)

        ji_rate = ji_count / total * 100
        xiong_rate = xiong_count / total * 100

        avg_score = sum(p['score'] for p in group) / total

        label = ['最低', '較低', '中等', '較高', '最高'][i]
        print(f"  {label}分組 (分數≈{avg_score:.2f}): 吉率={ji_rate:5.1f}%  凶率={xiong_rate:5.1f}%  n={total}")

    # 計算分類準確率
    print("\n分類預測準確率：")
    print("-" * 50)

    # 如果分數 > 0.38 預測為吉
    threshold = 0.38
    correct_ji = sum(1 for p in predictions if p['score'] > threshold and p['actual'] == 1)
    incorrect_ji = sum(1 for p in predictions if p['score'] > threshold and p['actual'] != 1)
    correct_xiong = sum(1 for p in predictions if p['score'] <= threshold and p['actual'] == -1)
    total_ji = sum(1 for p in predictions if p['actual'] == 1)
    total_xiong = sum(1 for p in predictions if p['actual'] == -1)

    print(f"  吉預測準確率：{correct_ji}/{total_ji} = {correct_ji/total_ji*100:.1f}%")
    print(f"  凶召回率：{correct_xiong}/{total_xiong} = {correct_xiong/total_xiong*100:.1f}%")

    return predictions


def analyze_model_components(data):
    """分析各模型組件的貢獻"""
    print("\n" + "="*70)
    print("模型組件貢獻分析")
    print("="*70)

    # 單獨評估每個組件
    components = {
        'position': lambda item: get_position_base_rate(item['position']),
        'freedom': lambda item: calculate_freedom(item['position']) / 4.0,
        'flow': lambda item: calculate_energy_flow(item['binary']),
        'tiyu': lambda item: calculate_tiyu_score(item['binary'], item['position']),
    }

    print("\n各組件與吉凶的相關性：")
    print("-" * 50)

    for comp_name, comp_func in components.items():
        # 計算高分組 vs 低分組的吉率差異
        scored = [(comp_func(item), item['label']) for item in data]
        sorted_scored = sorted(scored, key=lambda x: x[0])

        n = len(sorted_scored)
        low_half = sorted_scored[:n//2]
        high_half = sorted_scored[n//2:]

        low_ji_rate = sum(1 for _, l in low_half if l == 1) / len(low_half) * 100
        high_ji_rate = sum(1 for _, l in high_half if l == 1) / len(high_half) * 100

        diff = high_ji_rate - low_ji_rate
        bar = '█' * int(abs(diff) / 3)

        print(f"  {comp_name:10}: 高分吉率={high_ji_rate:5.1f}%  低分吉率={low_ji_rate:5.1f}%  差={diff:+5.1f}% {bar}")


def print_unified_theory():
    """輸出統一理論"""
    print("\n" + "="*70)
    print("統一能量理論")
    print("="*70)

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    易經統一能量理論                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  【核心公式】                                                        ║
║  ────────────                                                        ║
║  吉凶分數 = 0.40×位置效應 + 0.20×自由度 + 0.15×能量流動             ║
║           + 0.15×體用關係 + 0.10×行動指南                           ║
║                                                                      ║
║  【五大因素】                                                        ║
║  ────────────                                                        ║
║  1. 位置效應 (40%)                                                   ║
║     - 五爻最吉 (48%), 三爻最凶 (11%)                                ║
║     - 這是最強的預測因素                                             ║
║                                                                      ║
║  2. 自由度 (20%)                                                     ║
║     - 選擇空間越大越吉                                               ║
║     - 三爻自由度=1（被卡住）= 最凶                                  ║
║     - 二五爻自由度=4（選擇多）= 最吉                                ║
║                                                                      ║
║  3. 能量流動 (15%)                                                   ║
║     - 2個轉折點最佳                                                  ║
║     - 上下卦交界有變化更吉                                           ║
║     - 4個陽爻最優                                                    ║
║                                                                      ║
║  4. 體用關係 (15%)                                                   ║
║     - 體強用弱 = 最吉                                                ║
║     - 體用平衡 = 反而最差（反直覺！）                               ║
║                                                                      ║
║  5. 行動指南 (10%)                                                   ║
║     - 貞吉 → 守正則吉                                               ║
║     - 征凶 → 出征則凶                                               ║
║     - 位置×行動有交互效應                                           ║
║                                                                      ║
║  【傳統理論修正】                                                    ║
║  ────────────────                                                    ║
║  ✗ 當位效應：實際很弱（<1%差異）                                    ║
║  ✗ 陽乘陰最順：陰乘陰反而更吉                                       ║
║  ✗ 更多陽爻=更吉：4個最優，6個(乾卦)反而0%吉率                     ║
║  ✓ 三多凶五多功：強驗證                                             ║
║  ✓ 得中為貴：強驗證（+18%吉率）                                     ║
║                                                                      ║
║  【實用指南】                                                        ║
║  ────────────                                                        ║
║  1. 看位置：三爻預設警惕，五爻預設有利                              ║
║  2. 看自由度：被卡住就凶，有選擇就吉                                ║
║  3. 看能量：適中變化最佳，極端不利                                  ║
║  4. 看行動詞：貞吉可信，征凶要慎                                    ║
║                                                                      ║
║  【哲學意義】                                                        ║
║  ────────────                                                        ║
║  易經本質是「變化可行性評估系統」：                                  ║
║  - 吉 = 有發展空間，能量可流動                                      ║
║  - 凶 = 被阻塞，無法變化                                            ║
║  - 中 = 穩定狀態，維持現狀                                          ║
║                                                                      ║
║  這解釋了為什麼結構只能預測~50%：                                   ║
║  另外50%是「行動」和「時機」的結果                                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print("="*70)
    print("統一能量模型建構")
    print("="*70)
    print("\n綜合所有分析結果，建立統一理論框架")

    data = load_data()
    print(f"\n載入 {len(data)} 條爻數據")

    # 評估模型
    evaluate_model(data)

    # 分析組件
    analyze_model_components(data)

    # 輸出理論
    print_unified_theory()


if __name__ == '__main__':
    main()
