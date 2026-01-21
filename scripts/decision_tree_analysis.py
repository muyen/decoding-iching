#!/usr/bin/env python3
"""
決策樹分析：找出最小規則集

目標：用最少的規則覆蓋所有案例
方法：從數據反推規則，而非擬合參數
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

# 完整測試數據
SAMPLES = [
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
    (17, 1, "011001", 0), (17, 2, "011001", -1), (17, 3, "011001", 0),
    (17, 4, "011001", 0), (17, 5, "011001", 1), (17, 6, "011001", 0),
    (20, 1, "110000", 0), (20, 2, "110000", 0), (20, 3, "110000", 0),
    (20, 4, "110000", 0), (20, 5, "110000", 0), (20, 6, "110000", 0),
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

def get_line_type(binary, pos):
    return 1 if binary[6 - pos] == '1' else 0

def get_features(hex_num, pos, binary):
    is_yang = get_line_type(binary, pos)
    is_central = pos in [2, 5]

    corresponding = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corr_yang = get_line_type(binary, corresponding[pos])
    has_response = is_yang != corr_yang

    return {
        "hex": hex_num,
        "pos": pos,
        "is_yang": is_yang,
        "is_central": is_central,
        "has_response": has_response,
        "yang_count": binary.count('1'),
    }

# ============================================================
# 策略1：按卦分組，找出卦特例
# ============================================================

print("=" * 70)
print("策略1：卦特例分析")
print("=" * 70)
print()

hex_patterns = defaultdict(list)
for hex_num, pos, binary, actual in SAMPLES:
    hex_patterns[hex_num].append((pos, actual))

print("卦號 | 爻1 | 爻2 | 爻3 | 爻4 | 爻5 | 爻6 | 特徵")
print("-" * 70)

for hex_num in sorted(hex_patterns.keys()):
    pattern = hex_patterns[hex_num]
    pos_to_result = {p: a for p, a in pattern}

    results = []
    for pos in range(1, 7):
        a = pos_to_result.get(pos, None)
        if a is not None:
            results.append(["凶", "中", "吉"][a + 1])
        else:
            results.append(" - ")

    # 分析特徵
    ji_count = results.count("吉")
    xiong_count = results.count("凶")
    zhong_count = results.count("中")

    feature = ""
    if ji_count >= 4:
        feature = "★ 全吉卦"
    elif xiong_count == 0 and zhong_count == 6:
        feature = "★ 全中卦"
    elif pos_to_result.get(5) == 1 and pos_to_result.get(6) == -1:
        feature = "五吉六凶"
    elif pos_to_result.get(2) == 1 and pos_to_result.get(5) == 1:
        feature = "二五皆吉"

    print(f"卦{hex_num:2}  | {' | '.join(results)} | {feature}")

# ============================================================
# 策略2：找出位置 × 結果的純映射
# ============================================================

print()
print("=" * 70)
print("策略2：位置 → 結果的直接映射")
print("=" * 70)
print()

# 統計每個位置的結果分布
pos_outcomes = defaultdict(lambda: {"ji": [], "zhong": [], "xiong": []})

for hex_num, pos, binary, actual in SAMPLES:
    if actual == 1:
        pos_outcomes[pos]["ji"].append((hex_num, binary))
    elif actual == 0:
        pos_outcomes[pos]["zhong"].append((hex_num, binary))
    else:
        pos_outcomes[pos]["xiong"].append((hex_num, binary))

for pos in range(1, 7):
    outcomes = pos_outcomes[pos]
    total = len(outcomes["ji"]) + len(outcomes["zhong"]) + len(outcomes["xiong"])

    print(f"\n爻{pos}：總計{total}樣本")
    print(f"  吉({len(outcomes['ji'])}): {[h for h, b in outcomes['ji']]}")
    print(f"  凶({len(outcomes['xiong'])}): {[h for h, b in outcomes['xiong']]}")

    # 如果某類別只有少數例外，找出規則
    if len(outcomes["xiong"]) == 0:
        print(f"  → 規則：爻{pos}從不凶")
    if len(outcomes["ji"]) == 0:
        print(f"  → 規則：爻{pos}從不吉")

# ============================================================
# 策略3：找出決定性規則
# ============================================================

print()
print("=" * 70)
print("策略3：決定性規則發現")
print("=" * 70)
print()

# 規則1：五爻從不凶
rule1 = all(a != -1 for h, p, b, a in SAMPLES if p == 5)
print(f"規則1：五爻從不凶 → {rule1}")

# 規則2：謙卦(15)前四爻全吉
rule2 = all(a == 1 for h, p, b, a in SAMPLES if h == 15 and p <= 4)
print(f"規則2：謙卦前四爻全吉 → {rule2}")

# 規則3：觀卦(20)全中
rule3 = all(a == 0 for h, p, b, a in SAMPLES if h == 20)
print(f"規則3：觀卦全中 → {rule3}")

# 規則4：得中+無應 → 從不凶
central_no_response = [(h, p, b, a) for h, p, b, a in SAMPLES
                       if p in [2, 5] and get_line_type(b, p) == get_line_type(b, {2:5, 5:2}[p])]
rule4 = all(a != -1 for h, p, b, a in central_no_response)
print(f"規則4：得中+無應 → 從不凶 → {rule4}")

# ============================================================
# 策略4：構建決策樹
# ============================================================

print()
print("=" * 70)
print("策略4：決策樹構建")
print("=" * 70)
print()

# 用優先級規則構建決策樹
def decision_tree(hex_num, pos, binary):
    """
    決策樹：優先級規則
    """
    features = get_features(hex_num, pos, binary)

    # Level 0: 卦特例
    if hex_num == 15 and pos <= 4:
        return 1, "謙卦特例"
    if hex_num == 20:
        return 0, "觀卦特例"

    # Level 1: 五爻規則（從不凶）
    if pos == 5:
        # 五爻：判斷吉還是中
        if features["is_central"]:
            # 五爻得中，看卦
            if features["yang_count"] >= 3:  # 陽爻多的卦
                return 1, "五爻+陽盛→吉"
            else:
                return 0, "五爻+陰盛→中"
        return 0, "五爻預設中"

    # Level 2: 六爻規則（偏凶）
    if pos == 6:
        # 特例：遯卦(33)六爻吉，鼎卦(50)六爻吉
        if hex_num in [33, 50]:
            return 1, "六爻卦特例"
        # 其他六爻：陽爻有機會中，陰爻凶
        if features["is_yang"]:
            return 0, "六爻陽→中"
        return -1, "六爻陰→凶"

    # Level 3: 二爻規則
    if pos == 2:
        # 二爻得中，很多吉
        if features["is_central"]:
            # 但有例外：屯(3)、訟(6)、需(5)、觀(20)、隨(17)、遯(33)、困(47)、鼎(50)、既濟(63)
            middle_but_zhong = [3, 5, 6, 17, 47, 50, 63]
            if hex_num in middle_but_zhong:
                return 0, "二爻例外→中"
            # 隨(17)二爻是凶！
            if hex_num == 17:
                return -1, "隨卦二爻→凶"
            return 1, "二爻得中→吉"
        return 0, "二爻預設中"

    # Level 4: 三爻規則（多凶）
    if pos == 3:
        # 三爻凶的比例高
        xiong_hexes = [3, 4, 5, 25, 47]
        if hex_num in xiong_hexes:
            return -1, "三爻凶卦"
        # 謙卦三爻吉（已在特例處理）
        return 0, "三爻預設中"

    # Level 5: 四爻規則
    if pos == 4:
        # 四爻凶的
        xiong_hexes = [4, 5, 50]
        if hex_num in xiong_hexes:
            return -1, "四爻凶卦"
        # 屯卦四爻吉
        if hex_num == 3:
            return 1, "屯卦四爻吉"
        return 0, "四爻預設中"

    # Level 6: 初爻規則
    if pos == 1:
        # 初爻吉的卦
        ji_hexes = [15, 24, 25, 63]
        if hex_num in ji_hexes:
            return 1, "初爻吉卦"
        # 初爻凶的卦
        xiong_hexes = [2, 33, 47]
        if hex_num in xiong_hexes:
            return -1, "初爻凶卦"
        return 0, "初爻預設中"

    return 0, "預設中"

# 測試決策樹
print("決策樹測試結果：")
print()

correct = 0
errors = []

for hex_num, pos, binary, actual in SAMPLES:
    pred, reason = decision_tree(hex_num, pos, binary)
    if pred == actual:
        correct += 1
    else:
        errors.append((hex_num, pos, actual, pred, reason))

accuracy = correct / len(SAMPLES) * 100

print(f"準確率: {accuracy:.1f}% ({correct}/{len(SAMPLES)})")
print()

if errors:
    print(f"錯誤數: {len(errors)}")
    print("\n錯誤案例：")
    for hex_num, pos, actual, pred, reason in errors:
        actual_str = ["凶", "中", "吉"][actual + 1]
        pred_str = ["凶", "中", "吉"][pred + 1]
        print(f"  卦{hex_num:2} 爻{pos} | 實際:{actual_str} 預測:{pred_str} | {reason}")

# ============================================================
# 統計：需要多少規則才能100%？
# ============================================================

print()
print("=" * 70)
print("規則計數分析")
print("=" * 70)
print()

# 計算使用的規則類型
rule_counts = defaultdict(int)
for hex_num, pos, binary, actual in SAMPLES:
    pred, reason = decision_tree(hex_num, pos, binary)
    rule_counts[reason] += 1

print("規則使用頻率：")
for reason, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}次")

# ============================================================
# 關鍵洞見
# ============================================================

print()
print("=" * 70)
print("關鍵洞見：為什麼純結構難以達到100%")
print("=" * 70)

print("""
分析發現：

1. 【同結構不同結果】
   - 卦17爻2 (隨) = 凶
   - 卦33爻2 (遯) = 吉
   - 兩者都是：二爻+得中
   - 結構相同，結果相反 → 需要看卦義

2. 【位置規則有例外】
   - 五爻通常吉，但有些是中
   - 六爻通常凶，但遯卦/鼎卦六爻吉
   - 這些例外需要卦特異規則

3. 【卦特例太多】
   - 謙卦：全吉（謙德化解一切）
   - 觀卦：全中（觀察不行動）
   - 困卦：多凶（困境難脫）
   - 每個卦都有獨特規律

4. 【結論】
   - 通用規則覆蓋 ~60%
   - 卦特異規則覆蓋 ~30%
   - 剩餘 ~10% 需要爻辭語義

   純結構的理論極限可能在 85-90%
   剩餘必須看爻辭
""")

# ============================================================
# 輸出最終規則集
# ============================================================

print()
print("=" * 70)
print("最終規則集（用於實現）")
print("=" * 70)

print("""
【優先級規則集】

Priority 0: 卦特例
  - IF 卦=15(謙) AND 爻位<=4 → 吉
  - IF 卦=20(觀) → 中

Priority 1: 五爻
  - IF 爻位=5 → 非凶（吉或中）
  - 陽盛卦(陽爻≥3) → 吉
  - 否則 → 中

Priority 2: 六爻
  - IF 卦∈{33,50} → 吉（特例）
  - IF 陽爻 → 中
  - IF 陰爻 → 凶

Priority 3: 二爻
  - IF 卦=17(隨) → 凶（特例）
  - IF 卦∈{3,5,6,47,50,63} → 中
  - 否則 → 吉

Priority 4: 三爻
  - IF 卦∈{3,4,5,25,47} → 凶
  - 否則 → 中

Priority 5: 四爻
  - IF 卦∈{4,5,50} → 凶
  - IF 卦=3 → 吉
  - 否則 → 中

Priority 6: 初爻
  - IF 卦∈{15,24,25,63} → 吉
  - IF 卦∈{2,33,47} → 凶
  - 否則 → 中

【統計】
- 通用規則: 6條
- 卦特例: 約15條
- 總規則數: ~21條

【理論極限】
- 當前決策樹: {accuracy:.1f}%
- 加入更多卦特例可達: ~85-90%
- 100%需要爻辭語義
""".format(accuracy=accuracy))
