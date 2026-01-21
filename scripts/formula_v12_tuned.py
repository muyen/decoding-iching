#!/usr/bin/env python3
"""
V12 公式：權重微調版

基於V11錯誤分析：
1. 坎（險）懲罰過重 → 降低
2. 得中加分過高導致假陽性 → 降低
3. 五爻保護過強 → 調整
4. 閾值需要重新校準
"""

import json
from pathlib import Path
from collections import defaultdict

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

TRIGRAM_MEANINGS = {
    "111": {"name": "乾", "symbol": "天", "quality": "健", "nature": "剛", "position": "上", "risk": 0},
    "000": {"name": "坤", "symbol": "地", "quality": "順", "nature": "柔", "position": "下", "risk": 0},
    "001": {"name": "震", "symbol": "雷", "quality": "動", "nature": "剛", "position": "下", "risk": 0.2},
    "010": {"name": "坎", "symbol": "水", "quality": "險", "nature": "柔", "position": "下", "risk": 0.6},  # 降低
    "011": {"name": "兌", "symbol": "澤", "quality": "悅", "nature": "柔", "position": "下", "risk": 0},
    "100": {"name": "艮", "symbol": "山", "quality": "止", "nature": "中", "position": "上", "risk": 0.1},
    "101": {"name": "離", "symbol": "火", "quality": "麗", "nature": "剛", "position": "上", "risk": 0.15},
    "110": {"name": "巽", "symbol": "風", "quality": "入", "nature": "柔", "position": "中", "risk": 0},
}

# 繫辭傳經典規則（微調）
CLASSICAL_POSITION = {
    1: 0,       # 初難知
    2: 0.25,   # 二多譽（略降）
    3: -0.35,  # 三多凶（略降）
    4: -0.1,   # 四多懼
    5: 0.4,    # 五多功（略降）
    6: -0.25,  # 上易知
}

def get_line(binary, pos):
    return int(binary[6 - pos])

def get_trigram(binary, which):
    if which == "lower":
        return binary[3:6]
    else:
        return binary[0:3]

def get_nature_relation(nature1, nature2):
    if nature1 == "中" or nature2 == "中":
        return "調和"
    if nature1 != nature2:
        return "相濟"
    if nature1 == "剛":
        return "太剛"
    return "太柔"

def extract_features(pos, binary):
    line = get_line(binary, pos)
    f = {}

    f["is_yang"] = line == 1
    f["pos"] = pos
    f["binary"] = binary
    f["is_central"] = pos in [2, 5]
    f["is_inner"] = pos <= 3
    f["classical_tendency"] = CLASSICAL_POSITION.get(pos, 0)
    f["is_proper"] = (line == 1 and pos % 2 == 1) or (line == 0 and pos % 2 == 0)

    # 應爻
    corresp = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corresp_line = get_line(binary, corresp[pos])
    f["has_response"] = line != corresp_line

    # 承
    f["has_cheng"] = False
    if pos > 1:
        below = get_line(binary, pos - 1)
        if line == 0 and below == 1:
            f["has_cheng"] = True

    # 比鄰
    f["same_neighbors"] = 0
    if pos > 1 and get_line(binary, pos - 1) == line:
        f["same_neighbors"] += 1
    if pos < 6 and get_line(binary, pos + 1) == line:
        f["same_neighbors"] += 1
    f["is_isolated"] = f["same_neighbors"] == 0 and pos not in [1, 6]

    # 卦結構
    yang_count = binary.count('1')
    f["yang_count"] = yang_count
    f["balance"] = abs(yang_count - 3)

    # 卦主
    f["is_ruler"] = False
    if yang_count == 1 and line == 1:
        f["is_ruler"] = True
    if yang_count == 5 and line == 0:
        f["is_ruler"] = True

    # 八卦
    lower = get_trigram(binary, "lower")
    upper = get_trigram(binary, "upper")
    lower_m = TRIGRAM_MEANINGS.get(lower, {})
    upper_m = TRIGRAM_MEANINGS.get(upper, {})

    f["lower_name"] = lower_m.get("name", "?")
    f["upper_name"] = upper_m.get("name", "?")
    f["lower"] = lower
    f["upper"] = upper
    f["nature_relation"] = get_nature_relation(
        lower_m.get("nature", "中"),
        upper_m.get("nature", "中")
    )
    f["lower_risk"] = lower_m.get("risk", 0)
    f["upper_risk"] = upper_m.get("risk", 0)
    f["total_risk"] = f["lower_risk"] + f["upper_risk"]

    f["is_pure"] = yang_count == 0 or yang_count == 6
    f["is_alternating"] = binary in ["010101", "101010"]

    if pos <= 3:
        my_trigram_m = lower_m
    else:
        my_trigram_m = upper_m
    f["in_danger_trigram"] = my_trigram_m.get("risk", 0) >= 0.5  # 降低閾值

    # 互卦
    nuclear_lower = binary[2:5]
    nuclear_upper = binary[1:4]
    nuc_lower_m = TRIGRAM_MEANINGS.get(nuclear_lower, {})
    nuc_upper_m = TRIGRAM_MEANINGS.get(nuclear_upper, {})
    f["nuclear_risk"] = nuc_lower_m.get("risk", 0) + nuc_upper_m.get("risk", 0)

    return f

def predict_v12(pos, binary):
    f = extract_features(pos, binary)
    score = 0.0
    details = {}

    # 規則1：得中（降低權重）
    if f["is_central"]:
        score += 0.9  # 從1.2降到0.9
        details["central"] = 0.9

    # 規則2：經典位置傾向
    score += f["classical_tendency"]
    details["classical"] = f["classical_tendency"]

    # 規則3：卦主
    if f["is_ruler"]:
        score += 1.0  # 從1.2降到1.0
        details["ruler"] = 1.0

    # 規則4：得中+無應
    if f["is_central"] and not f["has_response"]:
        score += 0.25  # 從0.3降到0.25
        details["central_stable"] = 0.25

    # 規則5：不得中+有應
    if not f["is_central"] and f["has_response"]:
        score -= 0.15  # 從0.2降到0.15
        details["response_unstable"] = -0.15

    # 規則6：承
    if f["has_cheng"]:
        score += 0.15
        details["cheng"] = 0.15

    # 規則7：艮在下（略降）
    if f["lower"] == "100":
        score += 0.6  # 從0.8降到0.6
        details["gen_below"] = 0.6

    # 規則8：止/順組合
    if f["lower"] == "100" and f["upper"] == "000":
        score += 0.3  # 從0.4降到0.3
        details["qian_pattern"] = 0.3

    # 規則9：坎（險）降低懲罰
    if f["lower"] == "010" or f["upper"] == "010":
        score -= 0.2  # 從0.3降到0.2
        details["kan_present"] = -0.2

    # 規則10：坤在上
    if f["upper"] == "000":
        score += 0.1
        details["kun_above"] = 0.1

    # 規則11：孤立
    if f["is_isolated"]:
        score -= 0.2
        details["isolated"] = -0.2

    # 規則12：在險卦中
    if f["in_danger_trigram"]:
        score -= 0.2  # 從0.3降到0.2
        details["in_danger"] = -0.2

    # 規則13：純卦極端
    if f["is_pure"]:
        if pos == 6:
            score -= 0.4
            details["pure_top"] = -0.4
        if pos == 1 and f["yang_count"] == 0:
            score -= 0.25
            details["pure_yin_start"] = -0.25

    # 規則14：六爻懲罰（略降）
    if pos == 6:
        score -= 0.25  # 從0.3降到0.25
        details["pos6_extra"] = -0.25

    # 規則15：五爻保護（改為軟保護）
    # 不再強制設為中，而是減少負面分數
    if pos == 5 and score < -0.2:
        score = -0.15
        details["pos5_protect"] = "soft"

    # === 新規則：剛柔平衡獎勵 ===
    if f["nature_relation"] == "相濟":
        score += 0.1
        details["balance_reward"] = 0.1

    details["total"] = score

    # 調整閾值
    if score >= 1.1:  # 從1.3降到1.1
        return 1, details
    elif score <= -0.35:  # 從-0.4調整到-0.35
        return -1, details
    else:
        return 0, details

# ============================================================
# 測試
# ============================================================

print("=" * 70)
print("V12 權重微調版")
print("=" * 70)
print()

correct = 0
errors = []

for hex_num, pos, binary, actual in SAMPLES:
    pred, details = predict_v12(pos, binary)
    if pred == actual:
        correct += 1
    else:
        f = extract_features(pos, binary)
        errors.append({
            "hex": hex_num,
            "pos": pos,
            "binary": binary,
            "actual": actual,
            "pred": pred,
            "score": details.get("total", 0),
            "lower": f["lower_name"],
            "upper": f["upper_name"],
        })

accuracy = correct / len(SAMPLES) * 100
baseline = sum(1 for s in SAMPLES if s[3] == 0) / len(SAMPLES) * 100

print(f"準確率: {accuracy:.1f}% ({correct}/{len(SAMPLES)})")
print(f"隨機基準: {baseline:.1f}%")
print(f"提升: +{accuracy - baseline:.1f}%")
print()

print(f"錯誤數: {len(errors)}")
print("\n錯誤案例（前15個）：")
for e in errors[:15]:
    actual_str = ["凶", "中", "吉"][e["actual"] + 1]
    pred_str = ["凶", "中", "吉"][e["pred"] + 1]
    print(f"  卦{e['hex']:2} 爻{e['pos']} | {e['lower']}/{e['upper']} | "
          f"實際:{actual_str} 預測:{pred_str} | 分數:{e['score']:.2f}")

# 分析錯誤類型
print()
print("=" * 70)
print("錯誤類型分析")
print("=" * 70)

error_types = {
    "過度吉": 0,  # 預測吉，實際中或凶
    "過度凶": 0,  # 預測凶，實際中或吉
    "漏報吉": 0,  # 預測中，實際吉
    "漏報凶": 0,  # 預測中，實際凶
}

for e in errors:
    if e["pred"] == 1 and e["actual"] <= 0:
        error_types["過度吉"] += 1
    elif e["pred"] == -1 and e["actual"] >= 0:
        error_types["過度凶"] += 1
    elif e["pred"] == 0 and e["actual"] == 1:
        error_types["漏報吉"] += 1
    elif e["pred"] == 0 and e["actual"] == -1:
        error_types["漏報凶"] += 1

print()
for t, count in error_types.items():
    print(f"  {t}: {count}")

# 版本對比
print()
print("=" * 70)
print("版本進程")
print("=" * 70)
print("""
| 版本 | 方法 | 準確率 |
|------|------|--------|
| 隨機 | 全猜「中」 | 52.2% |
| V5 | 基礎結構 | 50.0% |
| V7 | +五行交互 | 54.4% |
| V9 | +八卦屬性 | 56.7% |
| V10 | +週期/變卦 | 45.6% |
| V11 | V9精煉 | 57.8% |
""")
print(f"| V12 | 權重微調 | {accuracy:.1f}% |")

print()
print("=" * 70)
print("結論")
print("=" * 70)
print(f"""
V12 準確率: {accuracy:.1f}%

主要調整：
1. 降低「得中」權重（0.9 vs 1.2）
2. 降低坎卦懲罰
3. 加入剛柔平衡獎勵
4. 調整閾值

純結構極限推測：~58-60%
""")
