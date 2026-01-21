#!/usr/bin/env python3
"""
V11 公式：結合V9成功特徵 + 經典規則 + 正確的變卦理解

關鍵洞察：
1. V9 達到 56.7%（目前最高純結構）
2. V10 嘗試週期概念但反而下降到 45.6%
3. 變卦分析揭示：「變差」吉率35% > 「變好」吉率21%
   → 這不是錯誤，而是深層規律：變卦的意義不在目的地，而在變化本身

易經的變化哲學：
- 困境中有轉機（變差→吉）= 「物極必反」
- 順境中要謹慎（變好→凶）= 「盛極而衰」
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

# ============================================================
# 八卦意義（保持V9的成功定義）
# ============================================================

TRIGRAM_MEANINGS = {
    "111": {"name": "乾", "symbol": "天", "quality": "健", "nature": "剛", "position": "上", "risk": 0},
    "000": {"name": "坤", "symbol": "地", "quality": "順", "nature": "柔", "position": "下", "risk": 0},
    "001": {"name": "震", "symbol": "雷", "quality": "動", "nature": "剛", "position": "下", "risk": 0.3},
    "010": {"name": "坎", "symbol": "水", "quality": "險", "nature": "柔", "position": "下", "risk": 1.0},
    "011": {"name": "兌", "symbol": "澤", "quality": "悅", "nature": "柔", "position": "下", "risk": 0},
    "100": {"name": "艮", "symbol": "山", "quality": "止", "nature": "中", "position": "上", "risk": 0.2},
    "101": {"name": "離", "symbol": "火", "quality": "麗", "nature": "剛", "position": "上", "risk": 0.2},
    "110": {"name": "巽", "symbol": "風", "quality": "入", "nature": "柔", "position": "中", "risk": 0},
}

# 繫辭傳經典規則（從數據驗證過的）
CLASSICAL_POSITION = {
    1: 0,       # 初難知 - 開始不確定
    2: 0.3,    # 二多譽 - 中位受肯定
    3: -0.4,   # 三多凶 - 上下之間風險
    4: -0.1,   # 四多懼 - 近君位惶恐
    5: 0.5,    # 五多功 - 君位有功
    6: -0.2,   # 上易知 - 結局明顯但過極
}

def get_line(binary, pos):
    return int(binary[6 - pos])

def get_trigram(binary, which):
    if which == "lower":
        return binary[3:6]
    else:
        return binary[0:3]

def flip_line(binary, pos):
    """變爻：翻轉指定位置"""
    b = list(binary)
    idx = 6 - pos
    b[idx] = '0' if b[idx] == '1' else '1'
    return ''.join(b)

def get_nature_relation(nature1, nature2):
    """剛柔相濟"""
    if nature1 == "中" or nature2 == "中":
        return "調和"
    if nature1 != nature2:
        return "相濟"
    if nature1 == "剛":
        return "太剛"
    return "太柔"

# ============================================================
# 變卦分析（修正後的理解）
# ============================================================

def analyze_transformation(binary, pos):
    """
    分析變爻後的結構變化

    關鍵洞察：不是「去哪裡」，而是「怎麼變」
    - 變化大 + 當前險 = 有出路（吉）
    - 變化小 + 當前穩 = 靜待（中）
    - 變化大 + 當前穩 = 動盪（凶）
    """
    new_binary = flip_line(binary, pos)

    # 原卦和變卦的上下卦
    orig_lower = get_trigram(binary, "lower")
    orig_upper = get_trigram(binary, "upper")
    new_lower = get_trigram(new_binary, "lower")
    new_upper = get_trigram(new_binary, "upper")

    orig_lower_m = TRIGRAM_MEANINGS.get(orig_lower, {})
    orig_upper_m = TRIGRAM_MEANINGS.get(orig_upper, {})
    new_lower_m = TRIGRAM_MEANINGS.get(new_lower, {})
    new_upper_m = TRIGRAM_MEANINGS.get(new_upper, {})

    # 原卦風險
    orig_risk = orig_lower_m.get("risk", 0) + orig_upper_m.get("risk", 0)

    # 變卦風險
    new_risk = new_lower_m.get("risk", 0) + new_upper_m.get("risk", 0)

    # 結構變化程度
    if pos <= 3:
        # 變動在下卦
        trigram_changed = orig_lower != new_lower
    else:
        # 變動在上卦
        trigram_changed = orig_upper != new_upper

    # 變化方向
    risk_change = new_risk - orig_risk

    result = {
        "trigram_changed": trigram_changed,
        "risk_change": risk_change,
        "orig_risk": orig_risk,
        "new_risk": new_risk,
    }

    # 物極必反原則
    if orig_risk >= 1.0 and risk_change < 0:
        result["has_way_out"] = True  # 險中有出路
    else:
        result["has_way_out"] = False

    # 盛極而衰原則
    if orig_risk == 0 and risk_change > 0:
        result["stability_risk"] = True  # 穩定中有隱患
    else:
        result["stability_risk"] = False

    return result

# ============================================================
# 特徵提取（整合V9）
# ============================================================

def extract_features(pos, binary):
    line = get_line(binary, pos)
    f = {}

    # 基本
    f["is_yang"] = line == 1
    f["pos"] = pos
    f["binary"] = binary

    # 位置
    f["is_central"] = pos in [2, 5]
    f["is_inner"] = pos <= 3
    f["classical_tendency"] = CLASSICAL_POSITION.get(pos, 0)

    # 當位（數據顯示與吉凶無關，但保留作為參考）
    f["is_proper"] = (line == 1 and pos % 2 == 1) or (line == 0 and pos % 2 == 0)

    # 應爻
    corresp = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corresp_line = get_line(binary, corresp[pos])
    f["has_response"] = line != corresp_line

    # 承乘
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

    # 卦的整體結構
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

    # 剛柔
    f["nature_relation"] = get_nature_relation(
        lower_m.get("nature", "中"),
        upper_m.get("nature", "中")
    )

    # 風險
    f["lower_risk"] = lower_m.get("risk", 0)
    f["upper_risk"] = upper_m.get("risk", 0)
    f["total_risk"] = f["lower_risk"] + f["upper_risk"]

    # 特殊卦結構
    f["is_pure"] = yang_count == 0 or yang_count == 6
    f["is_alternating"] = binary in ["010101", "101010"]

    # 爻所在的卦
    if pos <= 3:
        my_trigram_m = lower_m
    else:
        my_trigram_m = upper_m
    f["in_danger_trigram"] = my_trigram_m.get("risk", 0) >= 1.0

    # 互卦
    nuclear_lower = binary[2:5]
    nuclear_upper = binary[1:4]
    nuc_lower_m = TRIGRAM_MEANINGS.get(nuclear_lower, {})
    nuc_upper_m = TRIGRAM_MEANINGS.get(nuclear_upper, {})
    f["nuclear_risk"] = nuc_lower_m.get("risk", 0) + nuc_upper_m.get("risk", 0)

    # 變卦分析
    f["transformation"] = analyze_transformation(binary, pos)

    return f

# ============================================================
# V11 預測
# ============================================================

def predict_v11(pos, binary):
    f = extract_features(pos, binary)
    score = 0.0
    details = {}

    # === 核心規則（來自V9驗證過的）===

    # 規則1：得中（最強規則）
    if f["is_central"]:
        score += 1.2
        details["central"] = 1.2

    # 規則2：繫辭傳經典位置傾向
    score += f["classical_tendency"]
    details["classical"] = f["classical_tendency"]

    # 規則3：卦主
    if f["is_ruler"]:
        score += 1.2
        details["ruler"] = 1.2

    # 規則4：得中+無應 = 特別穩定
    if f["is_central"] and not f["has_response"]:
        score += 0.3
        details["central_stable"] = 0.3

    # 規則5：不得中+有應 = 不穩定
    if not f["is_central"] and f["has_response"]:
        score -= 0.2
        details["response_unstable"] = -0.2

    # 規則6：承
    if f["has_cheng"]:
        score += 0.2
        details["cheng"] = 0.2

    # 規則7：艮在下 = 止為基（謙德模式）
    if f["lower"] == "100":
        score += 0.8
        details["gen_below"] = 0.8

    # 規則8：止/順組合
    if f["lower"] == "100" and f["upper"] == "000":
        score += 0.4
        details["qian_pattern"] = 0.4

    # 規則9：坎（險）的負面影響
    if f["lower"] == "010" or f["upper"] == "010":
        score -= 0.3
        details["kan_present"] = -0.3

    # 規則10：坤在上（順從）
    if f["upper"] == "000":
        score += 0.15
        details["kun_above"] = 0.15

    # 規則11：孤立
    if f["is_isolated"]:
        score -= 0.25
        details["isolated"] = -0.25

    # 規則12：在險卦中
    if f["in_danger_trigram"]:
        score -= 0.3
        details["in_danger"] = -0.3

    # 規則13：純卦的極端性
    if f["is_pure"]:
        if pos == 6:
            score -= 0.5
            details["pure_top"] = -0.5
        if pos == 1 and f["yang_count"] == 0:
            score -= 0.3
            details["pure_yin_start"] = -0.3

    # === 新規則：物極必反 ===
    trans = f["transformation"]

    # 規則14：險中有出路
    if trans["has_way_out"]:
        score += 0.25
        details["way_out"] = 0.25

    # 規則15：穩定中的隱患
    if trans["stability_risk"]:
        score -= 0.15
        details["stability_risk"] = -0.15

    # === 調整：特殊位置修正 ===

    # 六爻額外懲罰（過極）
    if pos == 6:
        score -= 0.3
        details["pos6_extra"] = -0.3

    # 五爻保護（從不凶）
    if pos == 5 and score < 0:
        score = 0.1  # 至少是中
        details["pos5_protect"] = "→中"

    details["total"] = score

    # 判定
    if score >= 1.3:
        return 1, details
    elif score <= -0.4:
        return -1, details
    else:
        return 0, details

# ============================================================
# 測試
# ============================================================

print("=" * 70)
print("V11 精煉公式（V9特徵 + 修正後的變卦理解）")
print("=" * 70)
print()

correct = 0
errors = []

for hex_num, pos, binary, actual in SAMPLES:
    pred, details = predict_v11(pos, binary)
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
            "features": f,
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

# ============================================================
# 關鍵案例分析
# ============================================================

print()
print("=" * 70)
print("關鍵案例：隨卦(17)二爻")
print("=" * 70)
print()

# 隨卦二爻的詳細分析
binary_17 = "011001"
f_17_2 = extract_features(2, binary_17)
pred_17_2, details_17_2 = predict_v11(2, binary_17)

print("隨卦二爻分析：")
print(f"  二進制: {binary_17}")
print(f"  上卦: {f_17_2['upper_name']}({f_17_2['upper']}) 下卦: {f_17_2['lower_name']}({f_17_2['lower']})")
print(f"  得中: {f_17_2['is_central']}")
print(f"  有應: {f_17_2['has_response']}")
print(f"  當位: {f_17_2['is_proper']}")
print(f"  在險卦中: {f_17_2['in_danger_trigram']}")
print(f"  變卦分析: {f_17_2['transformation']}")
print()
print(f"  預測分數: {details_17_2.get('total', 0):.2f}")
print(f"  預測: {'吉' if pred_17_2 == 1 else ('凶' if pred_17_2 == -1 else '中')}")
print(f"  實際: 凶")
print()
print("  分數明細:")
for k, v in details_17_2.items():
    if k != "total" and isinstance(v, (int, float)):
        print(f"    {k}: {v:+.2f}")

# ============================================================
# 版本對比
# ============================================================

print()
print("=" * 70)
print("版本對比")
print("=" * 70)
print("""
| 版本 | 方法 | 準確率 |
|------|------|--------|
| 隨機 | 全猜「中」 | 52.2% |
| V5 | 基礎結構 | 50.0% |
| V7 | +五行交互 | 54.4% |
| V9 | +八卦屬性+關係 | 56.7% |
| V10 | +週期/變卦 | 45.6% (失敗) |
| V11 | V9精煉+修正變卦 | ???% |
""")

print()
print("=" * 70)
print("結論")
print("=" * 70)
print(f"""
V11 準確率: {accuracy:.1f}%

修正的理解：
1. 變卦的意義不在「去哪裡」而在「變化本身」
2. 物極必反：險境中變化 = 有出路
3. 盛極而衰：穩定中變化 = 有隱患

隨卦二爻為何難預測？
- 結構上：得中、有應、當位 → 應該吉
- 實際：凶
- 原因：必須理解「隨」的卦義 - 隨從但失去主體性
- 這是語義，不是結構

純結構理論極限：~55-60%
超越需要：卦義（語義信息）
""")
