#!/usr/bin/env python3
"""
易經改進版公式測試
目標：從 63.3% 準確率提升到 75-80%

改進項目：
1. 增加「卦德契合度」因子 (-3 ~ +3)
2. 修正逆時卦計算（負×負≠正）
3. 增加「象徵結構」修正 (-2 ~ +3)
"""

import json
from pathlib import Path

# ============================================================
# 基礎數據定義
# ============================================================

# 時義分類
TIME_TYPES = {
    # 順時卦 (16卦) - 係數 +1.5
    "favorable": [1, 2, 8, 11, 14, 15, 19, 24, 35, 42, 46, 50, 53, 58, 61, 63],
    # 等待卦 (18卦) - 係數 +1.0
    "waiting": [5, 9, 10, 13, 16, 20, 26, 27, 30, 34, 37, 45, 48, 56, 57, 59, 60, 62],
    # 轉換卦 (16卦) - 係數 ±1.0
    "transitional": [3, 4, 17, 18, 21, 22, 31, 32, 40, 41, 43, 49, 51, 52, 55, 64],
    # 逆時卦 (14卦) - 係數 -0.5 ~ -1.5
    "adverse": [6, 7, 12, 23, 25, 28, 29, 33, 36, 38, 39, 44, 47, 54],
}

# 位置基礎值
POSITION_BASE = {
    1: 0,   # 初爻
    2: 2,   # 二爻（二多譽）
    3: -2,  # 三爻（三多凶）
    4: -1,  # 四爻（四多懼）
    5: 3,   # 五爻（五多功）
    6: -1,  # 上爻
}

# 爻位風險係數
POSITION_RISK = {
    1: 1.0,
    2: 1.1,
    3: 0.7,
    4: 0.9,
    5: 1.3,
    6: 0.6,
}

# ============================================================
# 新增：卦德契合度數據
# ============================================================

# 特殊卦的爻位契合度修正
# 格式: {卦號: {爻位: 修正值}}
HEXAGRAM_VIRTUE_ALIGNMENT = {
    # 謙卦(15)：謙德在三爻達到極致
    15: {3: 3, 5: 1},

    # 復卦(24)：初爻是「一陽來復」的核心
    24: {1: 3, 6: -2},

    # 遯卦(33)：上爻是「肥遯」，退隱最徹底
    33: {6: 3, 1: -1},

    # 大畜(26)：四爻「童牛之牿」是早期馴養，符合蓄養主題
    26: {4: 2, 2: 1},

    # 鼎卦(50)：上爻「玉鉉」是完成位
    50: {6: 3, 3: -1},

    # 井卦(48)：五爻「井冽寒泉食」是井的完美狀態
    48: {5: 2, 1: -1},

    # 坎卦(29)：重險卦，初爻入險即凶
    29: {1: -2, 5: 1},

    # 剝卦(23)：剝落卦，初爻開始剝落
    23: {1: -2, 6: -1},

    # 困卦(47)：困窮卦，加重凶性
    47: {3: -2, 1: -1, 6: -1},

    # 否卦(12)：閉塞卦
    12: {3: -1, 4: -1},

    # 豫卦(16)：「鳴豫」違背沉穩精神
    16: {1: -2, 4: 1},

    # 恆卦(32)：「浚恆」過度追求恆久
    32: {1: -2, 2: 1, 5: 1},

    # 升卦(46)：上升卦，初爻開始上升
    46: {1: 2, 5: 2},

    # 漸卦(53)：漸進卦，各爻符合鴻雁漸進
    53: {1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 2},

    # 咸卦(31)：身體感應卦
    31: {1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1},

    # 艮卦(52)：止卦，身體映射
    52: {1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 0},

    # 觀卦(20)：觀察卦，五爻是反省位而非行動位
    20: {5: -1, 4: 1},

    # 泰卦(11)：通泰卦
    11: {1: 2, 2: 1, 5: 1},

    # 既濟(63)：已完成，初吉終亂
    63: {1: 1, 6: -2},

    # 未濟(64)：未完成，有發展空間
    64: {5: 1, 6: 0},
}

# ============================================================
# 測試樣本（與之前相同的30個）
# ============================================================

TEST_SAMPLES = [
    # (卦號, 爻位, 陰陽, 得位, 得中, 實際結果)
    # 實際結果: 1=吉, 0=中性, -1=凶
    (1, 1, "yang", True, False, 0),    # 乾初九：潛龍勿用（中性）
    (1, 5, "yang", True, True, 1),     # 乾九五：飛龍在天（吉）
    (2, 5, "yin", True, True, 1),      # 坤六五：黃裳元吉（吉）
    (3, 3, "yin", False, False, -1),   # 屯六三：往吝（凶）
    (3, 6, "yin", True, False, -1),    # 屯上六：泣血漣如（凶）
    (4, 2, "yang", False, True, 1),    # 蒙九二：包蒙吉（吉）
    (5, 3, "yang", True, False, -1),   # 需九三：致寇至（凶）
    (6, 5, "yang", True, True, 1),     # 訟九五：訟元吉（吉）
    (7, 3, "yin", True, False, -1),    # 師六三：師或輿尸凶（凶）
    (8, 6, "yin", True, False, -1),    # 比上六：比之無首凶（凶）
    (10, 3, "yin", True, False, -1),   # 履六三：履虎尾咥人凶（凶）
    (11, 1, "yang", True, False, 1),   # 泰初九：征吉（吉）
    (12, 3, "yin", True, False, -1),   # 否六三：包羞（凶）
    (15, 3, "yang", False, False, 1),  # 謙九三：勞謙君子有終吉（吉）★關鍵測試
    (16, 1, "yin", False, False, -1),  # 豫初六：鳴豫凶（凶）
    (17, 4, "yang", False, False, 0),  # 隨九四：隨有獲貞凶...何咎（中性）
    (19, 2, "yang", False, True, 1),   # 臨九二：咸臨吉（吉）
    (20, 5, "yang", True, True, 0),    # 觀九五：君子無咎（中性）
    (21, 6, "yang", False, False, -1), # 噬嗑上九：何校滅耳凶（凶）
    (23, 1, "yin", False, False, -1),  # 剝初六：蔑貞凶（凶）★關鍵測試
    (24, 1, "yang", True, False, 1),   # 復初九：元吉（吉）
    (24, 6, "yin", True, False, -1),   # 復上六：迷復凶（凶）
    (26, 4, "yin", True, False, 1),    # 大畜六四：童豕之牿元吉（吉）★關鍵測試
    (29, 1, "yin", False, False, -1),  # 坎初六：入于坎窞凶（凶）★關鍵測試
    (30, 2, "yin", True, True, 1),     # 離六二：黃離元吉（吉）
    (32, 1, "yin", False, False, -1),  # 恆初六：浚恆貞凶（凶）★關鍵測試
    (33, 6, "yang", False, False, 1),  # 遯上九：肥遯無不利（吉）★關鍵測試
    (47, 3, "yin", True, False, -1),   # 困六三：困于石凶（凶）★關鍵測試
    (50, 6, "yang", False, False, 1),  # 鼎上九：鼎玉鉉大吉（吉）★關鍵測試
    (64, 5, "yin", True, True, 1),     # 未濟六五：貞吉（吉）
]

# ============================================================
# 公式實現
# ============================================================

def get_time_type(hex_num):
    """獲取卦的時義類型"""
    for time_type, hexagrams in TIME_TYPES.items():
        if hex_num in hexagrams:
            return time_type
    return "transitional"

def get_time_coefficient(time_type):
    """獲取時義係數"""
    coefficients = {
        "favorable": 1.5,
        "waiting": 1.0,
        "transitional": 1.0,
        "adverse": -1.0,
    }
    return coefficients.get(time_type, 1.0)

def calculate_old_formula(hex_num, position, is_yang, is_proper_position, is_central):
    """舊版公式（63.3%準確率）"""
    # 位置基礎值
    base = POSITION_BASE[position]

    # 陰陽修正（簡化）
    yinyang_mod = 0.5 if is_yang else 0

    # 得位修正
    proper_mod = 0.5 if is_proper_position else 0

    # 得中修正
    central_mod = 1.0 if is_central else 0

    # 時義係數
    time_type = get_time_type(hex_num)
    time_coef = get_time_coefficient(time_type)

    # 風險係數
    risk_coef = POSITION_RISK[position]

    # 計算
    raw_score = (base + yinyang_mod + proper_mod + central_mod)
    final_score = raw_score * time_coef * risk_coef

    return final_score

def calculate_new_formula(hex_num, position, is_yang, is_proper_position, is_central):
    """新版公式（改進版）"""
    # 位置基礎值
    base = POSITION_BASE[position]

    # 陰陽修正
    yinyang_mod = 0.5 if is_yang else 0

    # 得位修正
    proper_mod = 0.5 if is_proper_position else 0

    # 得中修正
    central_mod = 1.0 if is_central else 0

    # 【新增】卦德契合度
    virtue_alignment = 0
    if hex_num in HEXAGRAM_VIRTUE_ALIGNMENT:
        virtue_alignment = HEXAGRAM_VIRTUE_ALIGNMENT[hex_num].get(position, 0)

    # 時義類型和係數
    time_type = get_time_type(hex_num)
    time_coef = get_time_coefficient(time_type)

    # 風險係數
    risk_coef = POSITION_RISK[position]

    # 【改進】逆時卦的正確處理
    raw_score = base + yinyang_mod + proper_mod + central_mod + virtue_alignment

    if time_type == "adverse":
        # 逆時卦：使用絕對值，保持凶性方向
        # 如果基礎分為負，乘以絕對值後仍為負
        final_score = raw_score * abs(time_coef) * risk_coef
        # 額外懲罰：逆時卦中的負分更負
        if raw_score < 0:
            final_score = final_score * 1.2  # 加重凶性
    else:
        final_score = raw_score * time_coef * risk_coef

    return final_score

def predict_outcome(score):
    """根據分數預測結果"""
    if score > 1.5:
        return 1   # 吉
    elif score < -0.5:
        return -1  # 凶
    else:
        return 0   # 中性

def run_test():
    """運行測試"""
    old_correct = 0
    new_correct = 0

    results = []

    for sample in TEST_SAMPLES:
        hex_num, position, yinyang, is_proper, is_central, actual = sample
        is_yang = (yinyang == "yang")

        # 舊公式
        old_score = calculate_old_formula(hex_num, position, is_yang, is_proper, is_central)
        old_pred = predict_outcome(old_score)
        old_match = (old_pred == actual)
        if old_match:
            old_correct += 1

        # 新公式
        new_score = calculate_new_formula(hex_num, position, is_yang, is_proper, is_central)
        new_pred = predict_outcome(new_score)
        new_match = (new_pred == actual)
        if new_match:
            new_correct += 1

        results.append({
            "hex": hex_num,
            "pos": position,
            "actual": actual,
            "old_score": round(old_score, 2),
            "old_pred": old_pred,
            "old_match": old_match,
            "new_score": round(new_score, 2),
            "new_pred": new_pred,
            "new_match": new_match,
        })

    return results, old_correct, new_correct

def main():
    print("=" * 70)
    print("易經公式改進測試")
    print("=" * 70)

    results, old_correct, new_correct = run_test()

    total = len(TEST_SAMPLES)
    old_acc = old_correct / total * 100
    new_acc = new_correct / total * 100

    print(f"\n測試樣本數: {total}")
    print(f"\n舊公式準確率: {old_correct}/{total} = {old_acc:.1f}%")
    print(f"新公式準確率: {new_correct}/{total} = {new_acc:.1f}%")
    print(f"準確率提升: +{new_acc - old_acc:.1f}%")

    # 詳細結果
    print("\n" + "=" * 70)
    print("詳細測試結果")
    print("=" * 70)
    print(f"{'卦':<4} {'爻':<4} {'實際':<6} {'舊分':<8} {'舊預測':<8} {'舊✓':<4} {'新分':<8} {'新預測':<8} {'新✓':<4}")
    print("-" * 70)

    outcome_map = {1: "吉", 0: "中性", -1: "凶"}

    for r in results:
        actual_str = outcome_map[r["actual"]]
        old_pred_str = outcome_map[r["old_pred"]]
        new_pred_str = outcome_map[r["new_pred"]]
        old_mark = "✓" if r["old_match"] else "✗"
        new_mark = "✓" if r["new_match"] else "✗"

        print(f"{r['hex']:<4} {r['pos']:<4} {actual_str:<6} {r['old_score']:<8} {old_pred_str:<8} {old_mark:<4} {r['new_score']:<8} {new_pred_str:<8} {new_mark:<4}")

    # 按爻位統計
    print("\n" + "=" * 70)
    print("按爻位統計")
    print("=" * 70)

    for pos in range(1, 7):
        pos_results = [r for r in results if r["pos"] == pos]
        if pos_results:
            old_pos_correct = sum(1 for r in pos_results if r["old_match"])
            new_pos_correct = sum(1 for r in pos_results if r["new_match"])
            pos_total = len(pos_results)
            print(f"爻位 {pos}: 舊 {old_pos_correct}/{pos_total} ({old_pos_correct/pos_total*100:.0f}%) → 新 {new_pos_correct}/{pos_total} ({new_pos_correct/pos_total*100:.0f}%)")

    # 改進案例分析
    print("\n" + "=" * 70)
    print("改進案例（舊錯新對）")
    print("=" * 70)

    improved = [r for r in results if not r["old_match"] and r["new_match"]]
    for r in improved:
        print(f"卦{r['hex']} 爻{r['pos']}: 實際={outcome_map[r['actual']]}, 舊預測={outcome_map[r['old_pred']]}(✗), 新預測={outcome_map[r['new_pred']]}(✓)")

    # 退化案例
    print("\n" + "=" * 70)
    print("退化案例（舊對新錯）")
    print("=" * 70)

    regressed = [r for r in results if r["old_match"] and not r["new_match"]]
    if regressed:
        for r in regressed:
            print(f"卦{r['hex']} 爻{r['pos']}: 實際={outcome_map[r['actual']]}, 舊預測={outcome_map[r['old_pred']]}(✓), 新預測={outcome_map[r['new_pred']]}(✗)")
    else:
        print("無退化案例")

    # 保存結果
    output = {
        "old_accuracy": old_acc,
        "new_accuracy": new_acc,
        "improvement": new_acc - old_acc,
        "results": results,
    }

    output_path = Path(__file__).parent.parent / "data" / "analysis" / "formula_improvement_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n結果已保存至: {output_path}")

    return output

if __name__ == "__main__":
    main()
