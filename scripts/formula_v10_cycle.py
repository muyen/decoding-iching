#!/usr/bin/env python3
"""
V10 公式：加入循環/週期概念

新特徵：
1. 卦序位置（在64卦循環中的位置）
2. 爻位週期（開始/中間/結束）
3. 變卦（當此爻變時，變成什麼卦）
4. 繫辭傳的經典規則：三多凶、五多功
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
# 卦序：文王64卦序列（周易卦序）
# ============================================================

# 卦的二進制 -> 文王卦序號
KING_WEN_ORDER = {
    "111111": 1,   # 乾
    "000000": 2,   # 坤
    "010001": 3,   # 屯
    "100010": 4,   # 蒙
    "010111": 5,   # 需
    "111010": 6,   # 訟
    "000010": 7,   # 師
    "010000": 8,   # 比
    "110111": 9,   # 小畜
    "111011": 10,  # 履
    "000111": 11,  # 泰
    "111000": 12,  # 否
    "111101": 13,  # 同人
    "101111": 14,  # 大有
    "000100": 15,  # 謙
    "001000": 16,  # 豫
    "011001": 17,  # 隨
    "100110": 18,  # 蠱
    "000011": 19,  # 臨
    "110000": 20,  # 觀
    "101001": 21,  # 噬嗑
    "100101": 22,  # 賁
    "100000": 23,  # 剝
    "000001": 24,  # 復
    "111001": 25,  # 無妄
    "100111": 26,  # 大畜
    "100001": 27,  # 頤
    "011110": 28,  # 大過
    "010010": 29,  # 坎
    "101101": 30,  # 離
    "011100": 31,  # 咸
    "001110": 32,  # 恆
    "111100": 33,  # 遯
    "001111": 34,  # 大壯
    "101000": 35,  # 晉
    "000101": 36,  # 明夷
    "110101": 37,  # 家人
    "101011": 38,  # 睽
    "010100": 39,  # 蹇
    "001010": 40,  # 解
    "100011": 41,  # 損
    "110001": 42,  # 益
    "011111": 43,  # 夬
    "111110": 44,  # 姤
    "011000": 45,  # 萃
    "000110": 46,  # 升
    "011010": 47,  # 困
    "010110": 48,  # 井
    "011101": 49,  # 革
    "101110": 50,  # 鼎
    "001001": 51,  # 震
    "100100": 52,  # 艮
    "110100": 53,  # 漸
    "001011": 54,  # 歸妹
    "001101": 55,  # 豐
    "101100": 56,  # 旅
    "110110": 57,  # 巽
    "011011": 58,  # 兌
    "110010": 59,  # 渙
    "010011": 60,  # 節
    "110011": 61,  # 中孚
    "001100": 62,  # 小過
    "010101": 63,  # 既濟
    "101010": 64,  # 未濟
}

# 反向映射
BINARY_TO_ORDER = KING_WEN_ORDER
ORDER_TO_BINARY = {v: k for k, v in KING_WEN_ORDER.items()}

# ============================================================
# 卦德/卦性：每個卦的固有傾向
# ============================================================

# 基於傳統分類
HEXAGRAM_NATURE = {
    # 大吉卦
    1: "strong",      # 乾 - 剛健
    2: "receptive",   # 坤 - 柔順
    11: "prosperous", # 泰 - 通泰
    14: "abundant",   # 大有
    15: "humble",     # 謙 - 唯謙有終

    # 困難卦
    3: "difficult",   # 屯 - 難
    4: "obscure",     # 蒙 - 蒙昧
    29: "dangerous",  # 坎 - 重險
    39: "obstruction",# 蹇
    47: "exhausted",  # 困

    # 過渡卦
    63: "completed",  # 既濟 - 已完成
    64: "incomplete", # 未濟 - 未完成

    # 其他標記
    5: "waiting",     # 需 - 等待
    6: "conflict",    # 訟 - 爭訟
    17: "following",  # 隨 - 跟隨
    20: "contemplation", # 觀 - 觀察
    24: "return",     # 復 - 回歸
    25: "innocence",  # 無妄
    33: "retreat",    # 遯 - 退避
    50: "cauldron",   # 鼎 - 鼎新
}

# 卦德傾向分數
HEXAGRAM_TENDENCY = {
    "strong": 0.3,
    "receptive": 0.2,
    "prosperous": 0.5,
    "abundant": 0.4,
    "humble": 0.8,        # 謙卦特別吉
    "difficult": -0.3,
    "obscure": -0.2,
    "dangerous": -0.5,
    "obstruction": -0.4,
    "exhausted": -0.5,    # 困卦特別凶
    "completed": 0,
    "incomplete": -0.1,
    "waiting": 0,
    "conflict": -0.2,
    "following": 0,
    "contemplation": 0.1,
    "return": 0.3,
    "innocence": 0.2,
    "retreat": 0.1,
    "cauldron": 0.3,
}

# ============================================================
# 變卦計算
# ============================================================

def flip_line(binary, pos):
    """翻轉指定位置的爻，返回新的二進制"""
    idx = 6 - pos  # 轉換為字符串索引
    new_char = '0' if binary[idx] == '1' else '1'
    return binary[:idx] + new_char + binary[idx+1:]

def get_bian_gua(binary, pos):
    """獲取變卦的信息"""
    new_binary = flip_line(binary, pos)
    new_order = BINARY_TO_ORDER.get(new_binary, 0)
    new_nature = HEXAGRAM_NATURE.get(new_order, "neutral")
    return {
        "binary": new_binary,
        "order": new_order,
        "nature": new_nature,
        "tendency": HEXAGRAM_TENDENCY.get(new_nature, 0),
    }

# ============================================================
# 繫辭傳的經典規則
# ============================================================

# 「二多譽，四多懼，三多凶，五多功」
CLASSICAL_POSITION_TENDENCY = {
    1: 0,      # 初難知
    2: 0.3,    # 二多譽
    3: -0.4,   # 三多凶
    4: -0.2,   # 四多懼
    5: 0.5,    # 五多功
    6: -0.1,   # 上易知
}

# ============================================================
# 週期特徵
# ============================================================

def get_cycle_features(hex_order, pos):
    """獲取週期相關特徵"""
    f = {}

    # 卦序位置（1-64）
    f["hex_order"] = hex_order

    # 卦序週期階段
    if hex_order <= 10:
        f["hex_phase"] = "beginning"      # 開創期
    elif hex_order <= 30:
        f["hex_phase"] = "development"    # 發展期
    elif hex_order <= 50:
        f["hex_phase"] = "maturity"       # 成熟期
    else:
        f["hex_phase"] = "completion"     # 完成期

    # 是否接近循環終點（既濟/未濟）
    f["near_cycle_end"] = hex_order >= 60

    # 爻位週期階段
    if pos == 1:
        f["line_phase"] = "start"
    elif pos == 6:
        f["line_phase"] = "end"
    elif pos <= 3:
        f["line_phase"] = "ascending"
    else:
        f["line_phase"] = "descending"

    # 是否在過渡點（三四爻 = 內外卦交界）
    f["at_transition"] = pos in [3, 4]

    return f

# ============================================================
# 完整特徵提取
# ============================================================

def extract_all_features(hex_num, pos, binary):
    """提取所有特徵"""
    f = {}

    # 基本
    f["hex_num"] = hex_num
    f["pos"] = pos
    f["binary"] = binary
    f["is_yang"] = binary[6-pos] == '1'

    # 卦序
    hex_order = BINARY_TO_ORDER.get(binary, 0)
    f["hex_order"] = hex_order

    # 週期特徵
    cycle_f = get_cycle_features(hex_order, pos)
    f.update(cycle_f)

    # 卦德
    nature = HEXAGRAM_NATURE.get(hex_order, "neutral")
    f["hex_nature"] = nature
    f["hex_tendency"] = HEXAGRAM_TENDENCY.get(nature, 0)

    # 經典爻位傾向
    f["classical_pos_tendency"] = CLASSICAL_POSITION_TENDENCY[pos]

    # 變卦
    bian = get_bian_gua(binary, pos)
    f["bian_gua_order"] = bian["order"]
    f["bian_gua_nature"] = bian["nature"]
    f["bian_gua_tendency"] = bian["tendency"]

    # 變卦是否更好或更差
    f["change_improves"] = bian["tendency"] > f["hex_tendency"]
    f["change_worsens"] = bian["tendency"] < f["hex_tendency"]

    # 得中
    f["is_central"] = pos in [2, 5]

    # 應爻
    corresp = {1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3}
    corresp_yang = binary[6 - corresp[pos]] == '1'
    f["has_response"] = f["is_yang"] != corresp_yang

    return f

# ============================================================
# V10 預測
# ============================================================

def predict_v10(hex_num, pos, binary):
    """V10 預測"""
    f = extract_all_features(hex_num, pos, binary)
    score = 0.0
    details = {}

    # === 1. 經典爻位傾向（繫辭傳）===
    score += f["classical_pos_tendency"]
    details["classical_pos"] = f["classical_pos_tendency"]

    # === 2. 卦德傾向 ===
    score += f["hex_tendency"] * 0.5
    details["hex_tendency"] = f["hex_tendency"] * 0.5

    # === 3. 變卦傾向 ===
    score += f["bian_gua_tendency"] * 0.3
    details["bian_tendency"] = f["bian_gua_tendency"] * 0.3

    # === 4. 變化方向 ===
    if f["change_worsens"]:
        score -= 0.2
        details["change_worse"] = -0.2
    elif f["change_improves"]:
        score += 0.1
        details["change_better"] = 0.1

    # === 5. 得中 ===
    if f["is_central"]:
        score += 0.4
        details["central"] = 0.4

    # === 6. 過渡點風險 ===
    if f["at_transition"]:
        score -= 0.15
        details["transition"] = -0.15

    # === 7. 上爻結束風險 ===
    if f["line_phase"] == "end":
        score -= 0.2
        details["end_phase"] = -0.2

    # === 8. 得中+無應更穩 ===
    if f["is_central"] and not f["has_response"]:
        score += 0.2
        details["central_stable"] = 0.2

    # === 9. 接近循環終點 ===
    if f["near_cycle_end"]:
        if pos == 1:
            score += 0.2  # 新開始
            details["new_start"] = 0.2
        elif pos == 6:
            score -= 0.2  # 真正的結束
            details["true_end"] = -0.2

    details["total"] = score
    details["hex_nature"] = f["hex_nature"]
    details["bian_nature"] = f["bian_gua_nature"]

    # 判定
    if score >= 0.4:
        return 1, details
    elif score <= -0.3:
        return -1, details
    else:
        return 0, details

# ============================================================
# 測試
# ============================================================

print("=" * 70)
print("V10 循環/週期公式測試")
print("=" * 70)
print()

correct = 0
errors = []

for hex_num, pos, binary, actual in SAMPLES:
    pred, details = predict_v10(hex_num, pos, binary)
    if pred == actual:
        correct += 1
    else:
        errors.append({
            "hex": hex_num,
            "pos": pos,
            "actual": actual,
            "pred": pred,
            "details": details,
        })

accuracy = correct / len(SAMPLES) * 100
baseline = sum(1 for s in SAMPLES if s[3] == 0) / len(SAMPLES) * 100

print(f"準確率: {accuracy:.1f}% ({correct}/{len(SAMPLES)})")
print(f"隨機基準: {baseline:.1f}%")
print(f"提升: +{accuracy - baseline:.1f}%")
print()

# 錯誤分析
print(f"錯誤數: {len(errors)}")
print("\n錯誤案例（前15個）：")
for e in errors[:15]:
    actual_str = ["凶", "中", "吉"][e["actual"] + 1]
    pred_str = ["凶", "中", "吉"][e["pred"] + 1]
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 實際:{actual_str} 預測:{pred_str} | "
          f"卦德:{e['details'].get('hex_nature','?')} 變卦:{e['details'].get('bian_nature','?')} | "
          f"分數:{e['details']['total']:.2f}")

# ============================================================
# 變卦分析
# ============================================================

print()
print("=" * 70)
print("變卦分析：變化方向與吉凶")
print("=" * 70)
print()

change_results = defaultdict(lambda: {"ji": 0, "zhong": 0, "xiong": 0})

for hex_num, pos, binary, actual in SAMPLES:
    f = extract_all_features(hex_num, pos, binary)

    if f["change_improves"]:
        key = "變好"
    elif f["change_worsens"]:
        key = "變差"
    else:
        key = "變平"

    if actual == 1:
        change_results[key]["ji"] += 1
    elif actual == 0:
        change_results[key]["zhong"] += 1
    else:
        change_results[key]["xiong"] += 1

print("變化方向 | 吉 | 中 | 凶 | 吉率 | 凶率")
print("-" * 55)
for key, r in sorted(change_results.items()):
    total = r["ji"] + r["zhong"] + r["xiong"]
    ji_rate = r["ji"] / total * 100 if total else 0
    xiong_rate = r["xiong"] / total * 100 if total else 0
    print(f"{key:8} | {r['ji']:2} | {r['zhong']:2} | {r['xiong']:2} | {ji_rate:4.0f}% | {xiong_rate:4.0f}%")

# ============================================================
# 隨卦二爻測試
# ============================================================

print()
print("=" * 70)
print("關鍵測試：隨卦(17)二爻")
print("=" * 70)
print()

# 隨卦二爻
hex_num, pos, binary = 17, 2, "011001"
f = extract_all_features(hex_num, pos, binary)
pred, details = predict_v10(hex_num, pos, binary)

print(f"隨卦二爻分析：")
print(f"  卦序: {f['hex_order']}")
print(f"  卦德: {f['hex_nature']}")
print(f"  經典爻位傾向: {f['classical_pos_tendency']}")
print(f"  變卦: {f['bian_gua_order']} ({f['bian_gua_nature']})")
print(f"  變卦傾向: {f['bian_gua_tendency']}")
print(f"  變化方向: {'變差' if f['change_worsens'] else ('變好' if f['change_improves'] else '變平')}")
print(f"  預測: {['凶','中','吉'][pred+1]} (分數: {details['total']:.2f})")
print(f"  實際: 凶")

# ============================================================
# 保存結果
# ============================================================

output_path = Path(__file__).parent.parent / "data" / "analysis" / "formula_v10_cycle.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        "version": "v10_cycle",
        "accuracy": accuracy,
        "features": [
            "經典爻位傾向（繫辭傳）",
            "卦德傾向",
            "變卦傾向",
            "週期階段",
            "得中+應爻",
        ],
        "total": len(SAMPLES),
        "correct": correct,
    }, f, ensure_ascii=False, indent=2)

print()
print("=" * 70)
print("結論")
print("=" * 70)
print(f"""
V10 準確率: {accuracy:.1f}%

新特徵貢獻：
1. 繫辭傳經典規則（三多凶、五多功）
2. 卦德/卦性
3. 變卦分析

Sources:
- 易學網：爻位吉凶理論的量化分析
- 繫辭傳：二多譽、三多凶、四多懼、五多功
""")
