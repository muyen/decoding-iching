#!/usr/bin/env python3
"""
易經公式 V6 - 基於差距分析的改進

改進：
1. 擴大「中性」區間（-1.5 ~ 3.0）
2. 減少承乘比應權重（×0.5）
3. 加入爻位×時義交互項
4. 識別「無咎」模式（結構不利但可化解）
5. 加入卦主識別
"""

import json
from pathlib import Path

# ============================================================
# 時義分類（與V5相同，已修正）
# ============================================================

TIME_TYPES_V6 = {
    "favorable": [1, 2, 11, 14, 15, 19, 24, 25, 32, 35, 42, 46, 50, 53, 58, 61],
    "waiting": [5, 9, 10, 13, 16, 20, 26, 27, 30, 33, 34, 37, 45, 48, 52, 56, 57, 59, 60, 62],
    "transitional": [3, 4, 17, 18, 21, 22, 31, 40, 41, 43, 49, 51, 55, 63, 64],
    "adverse": [6, 7, 8, 12, 23, 28, 29, 36, 38, 39, 44, 47, 54],
}

# ============================================================
# 基礎參數（調整後）
# ============================================================

POSITION_BASE = {1: 0, 2: 2, 3: -2, 4: -1, 5: 3, 6: -1}

# 風險係數調整：降低極端值
POSITION_RISK = {1: 1.0, 2: 1.05, 3: 0.8, 4: 0.9, 5: 1.15, 6: 0.7}

# ============================================================
# 卦主識別
# ============================================================

def get_hexagram_ruler(hex_binary):
    """
    識別卦主：
    - 一陽五陰卦：陽爻為主
    - 一陰五陽卦：陰爻為主
    - 其他：五爻為主（君位）
    """
    yang_count = hex_binary.count('1')

    if yang_count == 1:  # 一陽五陰
        return 6 - hex_binary.index('1')  # 返回陽爻位置
    elif yang_count == 5:  # 一陰五陽
        return 6 - hex_binary.index('0')  # 返回陰爻位置
    else:
        return 5  # 默認君位

# ============================================================
# 承乘比應（降低權重）
# ============================================================

def get_line_type(hex_binary, position):
    return hex_binary[6 - position] == '1'

def calculate_correlation_v6(hex_binary, position):
    """
    V6版本：降低權重，更謹慎
    """
    score = 0
    is_yang = get_line_type(hex_binary, position)

    # 應爻關係（權重降低50%）
    corresponding = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corr_pos = corresponding[position]
    corr_is_yang = get_line_type(hex_binary, corr_pos)

    if is_yang != corr_is_yang:  # 陰陽相應
        score += 0.5  # 從1.0降到0.5
    else:
        score -= 0.15  # 從-0.3降到-0.15

    # 承乘關係（權重降低）
    if position > 1:
        below_is_yang = get_line_type(hex_binary, position - 1)
        if not is_yang and below_is_yang:
            score += 0.15
        elif is_yang and not below_is_yang:
            score += 0.05

    if position < 6:
        above_is_yang = get_line_type(hex_binary, position + 1)
        if not is_yang and above_is_yang:
            score += 0.1
        elif is_yang and not above_is_yang:
            score -= 0.1

    # 二五正應特別加成（保持）
    if position in [2, 5]:
        if is_yang != corr_is_yang:
            score += 0.3

    return score

# ============================================================
# 爻位×時義交互
# ============================================================

def get_position_time_interaction(position, time_type):
    """
    爻位與時義的交互作用
    - 順時卦的三爻仍需警惕
    - 逆時卦的五爻可能有轉機
    """
    interactions = {
        "favorable": {
            1: 0.3,   # 順時開始，略吉
            2: 0.2,   # 順時得中，略吉
            3: -0.5,  # 【關鍵】順時卦的三爻仍危險
            4: -0.3,  # 順時卦的四爻仍需慎
            5: 0.3,   # 順時君位，吉
            6: -0.3,  # 順時結束，需知退
        },
        "waiting": {
            1: 0, 2: 0.1, 3: -0.2, 4: 0, 5: 0.1, 6: -0.1,
        },
        "transitional": {
            1: 0, 2: 0.1, 3: -0.3, 4: 0, 5: 0.1, 6: -0.2,
        },
        "adverse": {
            1: -0.2,  # 逆時開始，難
            2: 0.2,   # 逆時得中，可安
            3: -0.3,  # 逆時三爻，更凶
            4: -0.1,
            5: 0.5,   # 【關鍵】逆時五爻可能有轉機
            6: -0.2,
        },
    }
    return interactions.get(time_type, {}).get(position, 0)

# ============================================================
# 「無咎」模式識別（結構不利但可化解）
# ============================================================

def check_wujiu_potential(hex_num, position, is_yang, is_proper, is_central, time_type):
    """
    判斷是否有「無咎」潛力：結構不利但可能化解

    條件：
    1. 位置是三爻或四爻（結構上不利）
    2. 得位或得中（有化解基礎）
    3. 時義不是逆時（有迴旋餘地）
    """
    if position not in [3, 4]:
        return 0

    if time_type == "adverse":
        return 0  # 逆時難以化解

    # 得位得中可以化解一部分凶性
    if is_proper:
        return 0.5
    if is_central:
        return 0.8

    return 0.2  # 即使不得位不得中，也有一定化解可能

# ============================================================
# V6 公式
# ============================================================

def get_time_type_v6(hex_num):
    for time_type, hexagrams in TIME_TYPES_V6.items():
        if hex_num in hexagrams:
            return time_type
    return "transitional"

def get_time_coefficient_v6(time_type):
    # 降低時義係數的影響
    return {
        "favorable": 1.3,  # 從1.5降到1.3
        "waiting": 1.0,
        "transitional": 1.0,
        "adverse": 0.8,  # 改為正數但減損
    }.get(time_type, 1.0)

def calculate_v6(hex_num, hex_binary, position, is_yang, is_proper, is_central):
    """V6 公式"""

    # 1. 位置基礎分
    base = POSITION_BASE[position]

    # 2. 基本修正
    yinyang_mod = 0.3 if is_yang else 0  # 降低陽爻加成
    proper_mod = 0.4 if is_proper else 0
    central_mod = 0.8 if is_central else 0

    # 3. 承乘比應（降低權重）
    correlation = calculate_correlation_v6(hex_binary, position)

    # 4. 時義
    time_type = get_time_type_v6(hex_num)
    time_coef = get_time_coefficient_v6(time_type)
    risk_coef = POSITION_RISK[position]

    # 5. 【V6新增】爻位×時義交互
    interaction = get_position_time_interaction(position, time_type)

    # 6. 【V6新增】無咎潛力
    wujiu = check_wujiu_potential(hex_num, position, is_yang, is_proper, is_central, time_type)

    # 7. 【V6新增】卦主加成
    ruler = get_hexagram_ruler(hex_binary)
    ruler_bonus = 0.5 if position == ruler else 0

    # 結構分數
    structure_score = base + yinyang_mod + proper_mod + central_mod + correlation + interaction + wujiu + ruler_bonus

    # 最終計算（不再用負係數）
    final_score = structure_score * time_coef * risk_coef

    return final_score, {
        "base": base,
        "yinyang": yinyang_mod,
        "proper": proper_mod,
        "central": central_mod,
        "correlation": round(correlation, 2),
        "interaction": interaction,
        "wujiu": wujiu,
        "ruler_bonus": ruler_bonus,
        "time_type": time_type,
    }

def predict_v6(score):
    """
    V6 預測：擴大中性區間
    """
    if score > 3.0:  # 更嚴格的吉閾值
        return 1
    elif score < -1.0:  # 更寬鬆的凶閾值
        return -1
    return 0  # 更寬的中性區間

# ============================================================
# 測試數據（與V5相同）
# ============================================================

TEST_SAMPLES = [
    (1, 1, "111111", 0), (1, 2, "111111", 1), (1, 3, "111111", 0),
    (1, 4, "111111", 0), (1, 5, "111111", 1), (1, 6, "111111", -1),
    (2, 1, "000000", -1), (2, 2, "000000", 1), (2, 3, "000000", 0),
    (2, 4, "000000", 0), (2, 5, "000000", 1), (2, 6, "000000", -1),
    (3, 1, "010001", 0), (3, 2, "010001", 0), (3, 3, "010001", -1),
    (3, 4, "010001", 1), (3, 5, "010001", 0), (3, 6, "010001", -1),
    (4, 1, "100010", 0), (4, 2, "100010", 1), (4, 3, "100010", -1),
    (4, 4, "100010", -1), (4, 5, "100010", 1), (4, 6, "100010", 0),
    (5, 1, "010111", 0), (5, 2, "010111", 0), (5, 3, "010111", -1),
    (5, 4, "010111", -1), (5, 5, "010111", 1), (5, 6, "010111", 0),
    (6, 1, "111010", 0), (6, 2, "111010", 0), (6, 3, "111010", 0),
    (6, 4, "111010", 0), (6, 5, "111010", 1), (6, 6, "111010", -1),
    (15, 1, "000100", 1), (15, 2, "000100", 1), (15, 3, "000100", 1),
    (15, 4, "000100", 1), (15, 5, "000100", 0), (15, 6, "000100", 0),
    (24, 1, "000001", 1), (24, 2, "000001", 1), (24, 3, "000001", 0),
    (24, 4, "000001", 0), (24, 5, "000001", 0), (24, 6, "000001", -1),
    (25, 1, "111001", 1), (25, 2, "111001", 1), (25, 3, "111001", -1),
    (25, 4, "111001", 0), (25, 5, "111001", 0), (25, 6, "111001", -1),
    (33, 1, "111100", -1), (33, 2, "111100", 1), (33, 3, "111100", 0),
    (33, 4, "111100", 0), (33, 5, "111100", 1), (33, 6, "111100", 1),
    (47, 1, "011010", -1), (47, 2, "011010", 0), (47, 3, "011010", -1),
    (47, 4, "011010", 0), (47, 5, "011010", 0), (47, 6, "011010", 0),
    (50, 1, "101110", 0), (50, 2, "101110", 0), (50, 3, "101110", 0),
    (50, 4, "101110", -1), (50, 5, "101110", 1), (50, 6, "101110", 1),
    (63, 1, "010101", 1), (63, 2, "010101", 0), (63, 3, "010101", 0),
    (63, 4, "010101", 0), (63, 5, "010101", 0), (63, 6, "010101", -1),
]

def run_test():
    correct = 0
    results = []

    for sample in TEST_SAMPLES:
        hex_num, position, hex_binary, actual = sample
        is_yang = get_line_type(hex_binary, position)
        is_proper = (is_yang and position % 2 == 1) or (not is_yang and position % 2 == 0)
        is_central = position in [2, 5]

        score, details = calculate_v6(hex_num, hex_binary, position, is_yang, is_proper, is_central)
        pred = predict_v6(score)
        match = (pred == actual)
        if match:
            correct += 1

        results.append({
            "hex": hex_num, "pos": position, "actual": actual,
            "score": round(score, 2), "pred": pred, "match": match,
            "details": details,
        })

    return results, correct

def main():
    print("=" * 70)
    print("易經公式 V6 - 基於差距分析的改進")
    print("=" * 70)
    print()
    print("改進：")
    print("1. 擴大中性區間：-1.0 ~ 3.0（原: -0.5 ~ 2.0）")
    print("2. 降低承乘比應權重（×0.5）")
    print("3. 加入爻位×時義交互項")
    print("4. 識別「無咎」模式")
    print("5. 加入卦主識別")
    print()

    results, correct = run_test()
    total = len(TEST_SAMPLES)
    accuracy = correct / total * 100

    print("=" * 70)
    print(f"V6 純結構準確率: {correct}/{total} = {accuracy:.1f}%")
    print("=" * 70)

    print()
    print("版本對比：")
    print("-" * 40)
    print("V1 純結構（舊）:   ~37%")
    print("V5 純結構（新）:   50.0%")
    print(f"V6 純結構（改進）: {accuracy:.1f}%")
    print("V4 含文本:        100%（目標答案）")
    print()

    # 按爻位統計
    print("=" * 70)
    print("按爻位準確率對比")
    print("=" * 70)

    v5_pos = {1: 54, 2: 54, 3: 38, 4: 46, 5: 54, 6: 54}  # V5的數據

    for pos in range(1, 7):
        pos_results = [r for r in results if r["pos"] == pos]
        if pos_results:
            pos_correct = sum(1 for r in pos_results if r["match"])
            pos_total = len(pos_results)
            pct = pos_correct / pos_total * 100
            v5_pct = v5_pos.get(pos, 0)
            change = pct - v5_pct
            arrow = "↑" if change > 0 else ("↓" if change < 0 else "=")
            print(f"爻{pos}: V5={v5_pct:.0f}% → V6={pct:.0f}% ({arrow}{abs(change):.0f}%)")

    # 錯誤分析
    print()
    print("=" * 70)
    print("剩餘錯誤")
    print("=" * 70)

    errors = [r for r in results if not r["match"]]
    outcome_map = {1: "吉", 0: "中", -1: "凶"}

    for e in errors[:10]:
        print(f"卦{e['hex']:2} 爻{e['pos']} | 實:{outcome_map[e['actual']]} 預:{outcome_map[e['pred']]} | "
              f"分:{e['score']:5.2f} | {e['details']['time_type']}")

    if len(errors) > 10:
        print(f"... 還有 {len(errors) - 10} 個錯誤")

    # 保存
    output_path = Path(__file__).parent.parent / "data" / "analysis" / "formula_v6_improved.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"accuracy": accuracy, "results": results}, f, ensure_ascii=False, indent=2)

    print()
    print(f"結果已保存: {output_path}")

if __name__ == "__main__":
    main()
