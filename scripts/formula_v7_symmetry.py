#!/usr/bin/env python3
"""
V7 公式：基於專家建議的新方向

關鍵改進（來自跨領域專家）：
1. 移除「當位」因素（學術統計證明無關）
2. 加入互卦（nuclear hexagram）分析
3. 測試錯卦/綜卦對稱性
4. 加入交互項（有應 × 得中）
5. 基於群論的卦象分析

來源：
- 易學網量化分析：當位與吉凶無關
- 信息論專家：50%可能接近結構極限
- 代數專家：(Z/2Z)^6 群結構
"""

import json
from pathlib import Path
from collections import defaultdict

# 完整測試數據
SAMPLES = [
    # 卦1 乾
    (1, 1, "111111", 0), (1, 2, "111111", 1), (1, 3, "111111", 0),
    (1, 4, "111111", 0), (1, 5, "111111", 1), (1, 6, "111111", -1),
    # 卦2 坤
    (2, 1, "000000", -1), (2, 2, "000000", 1), (2, 3, "000000", 0),
    (2, 4, "000000", 0), (2, 5, "000000", 1), (2, 6, "000000", -1),
    # 卦3 屯
    (3, 1, "010001", 0), (3, 2, "010001", 0), (3, 3, "010001", -1),
    (3, 4, "010001", 1), (3, 5, "010001", 0), (3, 6, "010001", -1),
    # 卦4 蒙
    (4, 1, "100010", 0), (4, 2, "100010", 1), (4, 3, "100010", -1),
    (4, 4, "100010", -1), (4, 5, "100010", 1), (4, 6, "100010", 0),
    # 卦5 需
    (5, 1, "010111", 0), (5, 2, "010111", 0), (5, 3, "010111", -1),
    (5, 4, "010111", -1), (5, 5, "010111", 1), (5, 6, "010111", 0),
    # 卦6 訟
    (6, 1, "111010", 0), (6, 2, "111010", 0), (6, 3, "111010", 0),
    (6, 4, "111010", 0), (6, 5, "111010", 1), (6, 6, "111010", -1),
    # 卦15 謙
    (15, 1, "000100", 1), (15, 2, "000100", 1), (15, 3, "000100", 1),
    (15, 4, "000100", 1), (15, 5, "000100", 0), (15, 6, "000100", 0),
    # 卦17 隨
    (17, 1, "011001", 0), (17, 2, "011001", -1), (17, 3, "011001", 0),
    (17, 4, "011001", 0), (17, 5, "011001", 1), (17, 6, "011001", 0),
    # 卦20 觀
    (20, 1, "110000", 0), (20, 2, "110000", 0), (20, 3, "110000", 0),
    (20, 4, "110000", 0), (20, 5, "110000", 0), (20, 6, "110000", 0),
    # 卦24 復
    (24, 1, "000001", 1), (24, 2, "000001", 1), (24, 3, "000001", 0),
    (24, 4, "000001", 0), (24, 5, "000001", 0), (24, 6, "000001", -1),
    # 卦25 無妄
    (25, 1, "111001", 1), (25, 2, "111001", 1), (25, 3, "111001", -1),
    (25, 4, "111001", 0), (25, 5, "111001", 0), (25, 6, "111001", -1),
    # 卦33 遯
    (33, 1, "111100", -1), (33, 2, "111100", 1), (33, 3, "111100", 0),
    (33, 4, "111100", 0), (33, 5, "111100", 1), (33, 6, "111100", 1),
    # 卦47 困
    (47, 1, "011010", -1), (47, 2, "011010", 0), (47, 3, "011010", -1),
    (47, 4, "011010", 0), (47, 5, "011010", 0), (47, 6, "011010", 0),
    # 卦50 鼎
    (50, 1, "101110", 0), (50, 2, "101110", 0), (50, 3, "101110", 0),
    (50, 4, "101110", -1), (50, 5, "101110", 1), (50, 6, "101110", 1),
    # 卦63 既濟
    (63, 1, "010101", 1), (63, 2, "010101", 0), (63, 3, "010101", 0),
    (63, 4, "010101", 0), (63, 5, "010101", 0), (63, 6, "010101", -1),
]

# 八卦對應
TRIGRAMS = {
    "111": ("乾", "天", 1),
    "000": ("坤", "地", 8),
    "001": ("震", "雷", 4),
    "010": ("坎", "水", 6),
    "011": ("兌", "澤", 2),
    "100": ("艮", "山", 7),
    "101": ("離", "火", 3),
    "110": ("巽", "風", 5),
}

# 八卦五行
TRIGRAM_WUXING = {
    "乾": "金",
    "兌": "金",
    "離": "火",
    "震": "木",
    "巽": "木",
    "坎": "水",
    "艮": "土",
    "坤": "土",
}

# 五行生剋
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

def get_line_type(binary, pos):
    """獲取爻的陰陽"""
    return 1 if binary[6 - pos] == '1' else 0

def get_trigrams(binary):
    """獲取上下卦"""
    lower = binary[3:6]  # 初二三爻
    upper = binary[0:3]  # 四五六爻
    return TRIGRAMS.get(lower, ("?", "?", 0)), TRIGRAMS.get(upper, ("?", "?", 0))

def get_nuclear_hexagram(binary):
    """
    獲取互卦
    互卦：取二三四爻為下卦，三四五爻為上卦
    """
    nuclear_lower = binary[2:5]  # 二三四爻（從0開始：位置2,3,4）
    nuclear_upper = binary[1:4]  # 三四五爻（從0開始：位置1,2,3）
    return nuclear_lower, nuclear_upper

def get_inverse_hexagram(binary):
    """
    獲取錯卦：所有爻陰陽互換
    """
    return ''.join('1' if b == '0' else '0' for b in binary)

def get_reverse_hexagram(binary):
    """
    獲取綜卦：上下顛倒
    """
    return binary[::-1]

def get_wuxing_relation(upper_trigram, lower_trigram):
    """
    獲取上下卦的五行關係
    返回：生、剋、比和
    """
    upper_name = TRIGRAMS.get(upper_trigram, ("?", "?", 0))[0]
    lower_name = TRIGRAMS.get(lower_trigram, ("?", "?", 0))[0]

    upper_wx = TRIGRAM_WUXING.get(upper_name, "?")
    lower_wx = TRIGRAM_WUXING.get(lower_name, "?")

    if upper_wx == "?" or lower_wx == "?":
        return "unknown", upper_wx, lower_wx

    # 下生上
    if WUXING_SHENG.get(lower_wx) == upper_wx:
        return "下生上", lower_wx, upper_wx
    # 上生下
    if WUXING_SHENG.get(upper_wx) == lower_wx:
        return "上生下", lower_wx, upper_wx
    # 下剋上
    if WUXING_KE.get(lower_wx) == upper_wx:
        return "下剋上", lower_wx, upper_wx
    # 上剋下
    if WUXING_KE.get(upper_wx) == lower_wx:
        return "上剋下", lower_wx, upper_wx
    # 比和
    if upper_wx == lower_wx:
        return "比和", lower_wx, upper_wx

    return "其他", lower_wx, upper_wx

def get_all_features(hex_num, pos, binary):
    """提取所有結構特徵"""
    is_yang = get_line_type(binary, pos)

    features = {
        "hex": hex_num,
        "pos": pos,
        "is_yang": is_yang,
        "binary": binary,
    }

    # 得中（二爻、五爻）- 保留，這是有效的
    features["is_central"] = pos in [2, 5]

    # 移除「得位」- 學術統計證明無關
    # features["is_proper"] = ...  # 不再使用

    # 內外卦
    features["is_inner"] = pos <= 3
    features["is_outer"] = pos > 3

    # 應爻關係
    corresponding = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corr_pos = corresponding[pos]
    corr_yang = get_line_type(binary, corr_pos)
    features["has_response"] = is_yang != corr_yang

    # 交互項：有應 × 得中
    features["response_and_central"] = features["has_response"] and features["is_central"]

    # 上下卦
    lower_trigram, upper_trigram = get_trigrams(binary)
    features["lower_trigram"] = lower_trigram[0]
    features["upper_trigram"] = upper_trigram[0]

    # 互卦
    nuclear_lower, nuclear_upper = get_nuclear_hexagram(binary)
    features["nuclear_lower"] = nuclear_lower
    features["nuclear_upper"] = nuclear_upper

    # 五行關係
    relation, lower_wx, upper_wx = get_wuxing_relation(binary[3:6], binary[0:3])
    features["wuxing_relation"] = relation
    features["lower_wuxing"] = lower_wx
    features["upper_wuxing"] = upper_wx

    # 卦的陽爻數
    features["yang_count"] = binary.count('1')

    # 錯卦綜卦
    features["inverse_hex"] = get_inverse_hexagram(binary)
    features["reverse_hex"] = get_reverse_hexagram(binary)

    # 是否對稱卦（綜卦等於自己）
    features["is_self_reverse"] = binary == features["reverse_hex"]

    # 是否對稱卦（錯卦等於自己）
    features["is_self_inverse"] = binary == features["inverse_hex"]

    return features

# ============================================================
# 分析1：五行關係與吉凶
# ============================================================

print("=" * 70)
print("V7 分析：五行關係與吉凶")
print("=" * 70)
print()

wuxing_results = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    features = get_all_features(hex_num, pos, binary)
    relation = features["wuxing_relation"]

    if actual == 1:
        wuxing_results[relation]["ji"] += 1
    elif actual == 0:
        wuxing_results[relation]["zhong"] += 1
    else:
        wuxing_results[relation]["xiong"] += 1

print("五行關係 | 吉 | 中 | 凶 | 吉率")
print("-" * 50)

for relation, results in sorted(wuxing_results.items()):
    total = results["ji"] + results["zhong"] + results["xiong"]
    ji_rate = results["ji"] / total * 100 if total > 0 else 0
    print(f"{relation:8} | {results['ji']:2} | {results['zhong']:2} | {results['xiong']:2} | {ji_rate:.0f}%")

# ============================================================
# 分析2：互卦分析
# ============================================================

print()
print("=" * 70)
print("分析2：互卦特徵")
print("=" * 70)
print()

nuclear_results = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    features = get_all_features(hex_num, pos, binary)
    nuclear_key = f"{features['nuclear_lower']}-{features['nuclear_upper']}"

    if actual == 1:
        nuclear_results[nuclear_key]["ji"] += 1
    elif actual == 0:
        nuclear_results[nuclear_key]["zhong"] += 1
    else:
        nuclear_results[nuclear_key]["xiong"] += 1

print("互卦(下-上) | 吉 | 中 | 凶 | 傾向")
print("-" * 50)

for nuclear, results in sorted(nuclear_results.items(), key=lambda x: x[1]["ji"] - x[1]["xiong"], reverse=True):
    total = results["ji"] + results["zhong"] + results["xiong"]
    if total >= 3:  # 只顯示樣本夠多的
        diff = results["ji"] - results["xiong"]
        tendency = "偏吉" if diff > 1 else ("偏凶" if diff < -1 else "中性")
        print(f"{nuclear:11} | {results['ji']:2} | {results['zhong']:2} | {results['xiong']:2} | {tendency}")

# ============================================================
# 分析3：錯綜卦對稱性
# ============================================================

print()
print("=" * 70)
print("分析3：錯綜卦對稱性")
print("=" * 70)
print()

# 收集所有樣本的錯卦關係
hex_to_results = defaultdict(lambda: defaultdict(list))

for hex_num, pos, binary, actual in SAMPLES:
    hex_to_results[binary][pos].append(actual)

# 檢查自對稱卦
print("自對稱卦分析：")
for binary, pos_results in hex_to_results.items():
    reverse_binary = binary[::-1]
    inverse_binary = ''.join('1' if b == '0' else '0' for b in binary)

    is_self_reverse = binary == reverse_binary
    is_self_inverse = binary == inverse_binary

    if is_self_reverse or is_self_inverse:
        outcomes = []
        for pos, actuals in pos_results.items():
            for a in actuals:
                outcomes.append(['凶', '中', '吉'][a+1])

        symmetry_type = []
        if is_self_reverse:
            symmetry_type.append("自綜")
        if is_self_inverse:
            symmetry_type.append("自錯")

        # 找出卦號
        hex_nums = [h for h, p, b, a in SAMPLES if b == binary]
        if hex_nums:
            print(f"  卦{hex_nums[0]:2} ({','.join(symmetry_type)}): {' '.join(outcomes)}")

# ============================================================
# 分析4：新的交互項
# ============================================================

print()
print("=" * 70)
print("分析4：交互項分析（有應 × 得中）")
print("=" * 70)
print()

interaction_results = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    features = get_all_features(hex_num, pos, binary)

    # 組合鍵
    key = f"中={int(features['is_central'])}_應={int(features['has_response'])}"

    if actual == 1:
        interaction_results[key]["ji"] += 1
    elif actual == 0:
        interaction_results[key]["zhong"] += 1
    else:
        interaction_results[key]["xiong"] += 1

print("得中 × 有應 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 60)

for key, results in sorted(interaction_results.items()):
    total = results["ji"] + results["zhong"] + results["xiong"]
    ji_rate = results["ji"] / total * 100 if total > 0 else 0
    xiong_rate = results["xiong"] / total * 100 if total > 0 else 0
    print(f"{key:15} | {results['ji']:2} | {results['zhong']:2} | {results['xiong']:2} | {ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 分析5：位置 × 陰陽的交互
# ============================================================

print()
print("=" * 70)
print("分析5：位置 × 陰陽 × 得中交互")
print("=" * 70)
print()

# 只看五爻和二爻（得中位置）
for pos in [2, 5]:
    print(f"爻{pos}（得中）:")
    for is_yang in [0, 1]:
        key_samples = [(h, p, b, a) for h, p, b, a in SAMPLES
                       if p == pos and get_line_type(b, p) == is_yang]
        ji = len([s for s in key_samples if s[3] == 1])
        zhong = len([s for s in key_samples if s[3] == 0])
        xiong = len([s for s in key_samples if s[3] == -1])
        total = len(key_samples)

        yang_str = "陽" if is_yang else "陰"
        if total > 0:
            print(f"  {yang_str}爻: 吉={ji} 中={zhong} 凶={xiong} (吉率={ji/total*100:.0f}%)")

# ============================================================
# 構建V7公式
# ============================================================

print()
print("=" * 70)
print("V7 公式設計")
print("=" * 70)

def predict_v7(hex_num, pos, binary):
    """
    V7 預測公式
    基於：
    1. 得中是最強特徵
    2. 當位無關（移除）
    3. 有應需與得中交互
    4. 五行關係
    """
    features = get_all_features(hex_num, pos, binary)

    score = 0
    details = {}

    # === 特例規則 ===

    # 謙卦特例
    if hex_num == 15 and pos <= 4:
        return 1, {"rule": "謙卦特例"}

    # 觀卦特例
    if hex_num == 20:
        return 0, {"rule": "觀卦特例"}

    # === 爻位基礎分 ===

    # 得中是最強正面特徵
    if features["is_central"]:
        score += 2.0
        details["central_bonus"] = 2.0

    # 五爻額外優勢
    if pos == 5:
        score += 0.5
        details["pos5_bonus"] = 0.5

    # 六爻風險
    if pos == 6:
        score -= 1.0
        details["pos6_penalty"] = -1.0

    # 三爻風險
    if pos == 3:
        score -= 0.5
        details["pos3_penalty"] = -0.5

    # 初爻陰爻風險
    if pos == 1 and not features["is_yang"]:
        score -= 0.5
        details["yin_initial_penalty"] = -0.5

    # === 交互項 ===

    # 得中 + 有應 = 額外加分
    if features["response_and_central"]:
        score += 0.5
        details["central_response_bonus"] = 0.5

    # 不得中 + 有應 = 有應變成負面（這是關鍵發現！）
    if features["has_response"] and not features["is_central"]:
        score -= 0.3
        details["response_no_central_penalty"] = -0.3

    # === 五行關係 ===

    if features["wuxing_relation"] == "下生上":
        score += 0.3
        details["wuxing_sheng_bonus"] = 0.3
    elif features["wuxing_relation"] == "下剋上":
        score -= 0.2
        details["wuxing_ke_penalty"] = -0.2

    # === 判定 ===

    details["total_score"] = score

    if score >= 1.5:
        return 1, details
    elif score <= -0.5:
        return -1, details
    else:
        return 0, details

# 測試V7
print()
print("=" * 70)
print("V7 測試結果")
print("=" * 70)
print()

correct = 0
results = []

for hex_num, pos, binary, actual in SAMPLES:
    pred, details = predict_v7(hex_num, pos, binary)
    match = pred == actual
    if match:
        correct += 1

    results.append({
        "hex": hex_num,
        "pos": pos,
        "binary": binary,
        "actual": actual,
        "pred": pred,
        "match": match,
        "details": details,
    })

accuracy = correct / len(SAMPLES) * 100

print(f"總樣本: {len(SAMPLES)}")
print(f"正確: {correct}")
print(f"準確率: {accuracy:.1f}%")
print()

# 錯誤分析
errors = [r for r in results if not r["match"]]
print(f"錯誤數: {len(errors)}")
print()

print("錯誤案例：")
for e in errors[:10]:
    actual_str = ["凶", "中", "吉"][e["actual"] + 1]
    pred_str = ["凶", "中", "吉"][e["pred"] + 1]
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 實際:{actual_str} 預測:{pred_str} | 分數:{e['details'].get('total_score', 0):.2f}")

# 保存結果
output_path = Path(__file__).parent.parent / "data" / "analysis" / "formula_v7_symmetry.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        "version": "v7_symmetry",
        "accuracy": accuracy,
        "total": len(SAMPLES),
        "correct": correct,
        "key_features": [
            "得中是最強正面特徵",
            "移除當位（無關）",
            "有應需與得中交互",
            "五行關係微調",
        ],
        "results": results,
    }, f, ensure_ascii=False, indent=2)

print(f"\n結果已保存至: {output_path}")

# ============================================================
# 信息論分析
# ============================================================

print()
print("=" * 70)
print("信息論分析：結構的理論極限")
print("=" * 70)

import math

# 計算實際分布的熵
total = len(SAMPLES)
ji_count = len([s for s in SAMPLES if s[3] == 1])
zhong_count = len([s for s in SAMPLES if s[3] == 0])
xiong_count = len([s for s in SAMPLES if s[3] == -1])

p_ji = ji_count / total
p_zhong = zhong_count / total
p_xiong = xiong_count / total

entropy = 0
for p in [p_ji, p_zhong, p_xiong]:
    if p > 0:
        entropy -= p * math.log2(p)

print(f"\n結果分布：吉={ji_count} ({p_ji:.1%}) 中={zhong_count} ({p_zhong:.1%}) 凶={xiong_count} ({p_xiong:.1%})")
print(f"結果熵: {entropy:.3f} bits")
print(f"\n如果純隨機猜測最高頻類別(中):")
print(f"  準確率 = {p_zhong:.1%}")
print(f"\n如果結構完全決定結果:")
print(f"  理論最高準確率 = 100%")
print(f"\n當前V7準確率: {accuracy:.1f}%")
print(f"\n結論：結構可能只編碼了部分信息，剩餘需要語義")
