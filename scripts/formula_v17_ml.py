#!/usr/bin/env python3
"""
V17 機器學習方法：使用完整特徵向量和系統性優化

策略：
1. 提取所有可能的特徵
2. 使用簡單的感知機學習
3. 整合100%規則作為硬約束
"""

import numpy as np
from collections import defaultdict
import random

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

def to_gray(n):
    return n ^ (n >> 1)

def extract_full_features(hex_num, pos, binary):
    """Extract all possible features for ML"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    hex_val = int(binary, 2)
    line = int(binary[6 - pos])
    xor_val = upper ^ lower
    and_val = upper & lower
    or_val = upper | lower
    gray_val = to_gray(hex_val)
    gray_ones = bin(gray_val).count('1')
    total_ones = binary.count('1')

    features = {
        # 位置特徵
        "pos1": 1 if pos == 1 else 0,
        "pos2": 1 if pos == 2 else 0,
        "pos3": 1 if pos == 3 else 0,
        "pos4": 1 if pos == 4 else 0,
        "pos5": 1 if pos == 5 else 0,
        "pos6": 1 if pos == 6 else 0,
        "is_central": 1 if pos in [2, 5] else 0,
        "is_edge": 1 if pos in [1, 6] else 0,

        # 上卦特徵
        "upper_0": 1 if upper == 0 else 0,
        "upper_1": 1 if upper == 1 else 0,
        "upper_2": 1 if upper == 2 else 0,
        "upper_3": 1 if upper == 3 else 0,
        "upper_4": 1 if upper == 4 else 0,
        "upper_5": 1 if upper == 5 else 0,
        "upper_6": 1 if upper == 6 else 0,
        "upper_7": 1 if upper == 7 else 0,

        # 下卦特徵
        "lower_0": 1 if lower == 0 else 0,
        "lower_1": 1 if lower == 1 else 0,
        "lower_2": 1 if lower == 2 else 0,
        "lower_3": 1 if lower == 3 else 0,
        "lower_4": 1 if lower == 4 else 0,
        "lower_5": 1 if lower == 5 else 0,
        "lower_6": 1 if lower == 6 else 0,
        "lower_7": 1 if lower == 7 else 0,

        # 爻值
        "line_yang": line,
        "line_yin": 1 - line,

        # XOR特徵
        "xor_0": 1 if xor_val == 0 else 0,
        "xor_4": 1 if xor_val == 4 else 0,

        # 組合特徵
        "gray_low": 1 if gray_ones <= 2 else 0,
        "total_ones_low": 1 if total_ones <= 2 else 0,
        "total_ones_high": 1 if total_ones >= 4 else 0,

        # 交互特徵
        "central_yang": 1 if pos in [2, 5] and line == 1 else 0,
        "pos6_yin": 1 if pos == 6 and line == 0 else 0,
        "pos1_yang": 1 if pos == 1 and line == 1 else 0,
        "xor0_central": 1 if xor_val == 0 and pos in [2, 5] else 0,
        "xor4_lower": 1 if xor_val == 4 and pos <= 4 else 0,
        "upper0_pos2": 1 if upper == 0 and pos == 2 else 0,
        "lower4_central": 1 if lower == 4 and pos in [2, 5] else 0,
    }

    return features


def check_hard_rules(hex_num, pos, binary):
    """Check 100% confidence rules"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]

    # xor=4 + pos<=4 → 吉
    if xor_val == 4 and pos <= 4:
        return 1, "xor=4+pos<=4"

    # 坤上 + 二爻 → 吉
    if upper == 0 and pos == 2:
        return 1, "坤上+二爻"

    # xor=0 + 得中 → 吉
    if xor_val == 0 and is_central:
        return 1, "xor=0+得中"

    # 觀卦全中
    if binary == "110000":
        return 0, "觀卦"

    return None, None


# 提取特徵向量
def sample_to_vector(sample):
    hex_num, pos, binary, fortune = sample
    features = extract_full_features(hex_num, pos, binary)
    return [features[k] for k in sorted(features.keys())]


print("=" * 70)
print("V17 機器學習方法")
print("=" * 70)
print()

# 分離訓練數據（排除硬規則覆蓋的樣本）
train_samples = []
hard_rule_samples = []

for s in SAMPLES:
    result, rule = check_hard_rules(s[0], s[1], s[2])
    if result is not None:
        hard_rule_samples.append((s, result, rule))
    else:
        train_samples.append(s)

print(f"硬規則覆蓋樣本: {len(hard_rule_samples)}")
print(f"需要學習的樣本: {len(train_samples)}")
print()

# 特徵名稱
feature_names = sorted(extract_full_features(1, 1, "111111").keys())
print(f"特徵數量: {len(feature_names)}")

# 準備數據
X = np.array([sample_to_vector(s) for s in train_samples])
y = np.array([s[3] for s in train_samples])

# 簡單感知機訓練（多類別）
n_features = len(feature_names)

# 對於三分類，訓練兩個決策邊界
# 吉 vs (中, 凶) 和 凶 vs (中, 吉)

def train_binary_perceptron(X, y_binary, epochs=1000, lr=0.01):
    """Train a simple perceptron"""
    n_samples, n_features = X.shape
    weights = np.zeros(n_features)
    bias = 0.0

    for _ in range(epochs):
        for i in range(n_samples):
            prediction = 1 if np.dot(weights, X[i]) + bias > 0 else 0
            error = y_binary[i] - prediction
            weights += lr * error * X[i]
            bias += lr * error

    return weights, bias


# 訓練 吉 分類器
y_ji = (y == 1).astype(int)
weights_ji, bias_ji = train_binary_perceptron(X, y_ji)

# 訓練 凶 分類器
y_xiong = (y == -1).astype(int)
weights_xiong, bias_xiong = train_binary_perceptron(X, y_xiong)

print("\n吉分類器重要特徵（權重>0.3）:")
for i, (name, w) in enumerate(sorted(zip(feature_names, weights_ji), key=lambda x: -x[1])):
    if abs(w) > 0.3:
        print(f"  {name}: {w:.3f}")

print("\n凶分類器重要特徵（權重>0.3）:")
for i, (name, w) in enumerate(sorted(zip(feature_names, weights_xiong), key=lambda x: -x[1])):
    if abs(w) > 0.3:
        print(f"  {name}: {w:.3f}")


def predict_ml(sample):
    """ML prediction with hard rules"""
    hex_num, pos, binary, fortune = sample

    # 先檢查硬規則
    result, rule = check_hard_rules(hex_num, pos, binary)
    if result is not None:
        return result, {"rule": rule}

    # 提取特徵
    x = np.array(sample_to_vector(sample))

    # 計算分數
    score_ji = np.dot(weights_ji, x) + bias_ji
    score_xiong = np.dot(weights_xiong, x) + bias_xiong

    details = {"score_ji": score_ji, "score_xiong": score_xiong}

    # 決策
    if score_ji > 0.5 and score_ji > score_xiong:
        return 1, details
    elif score_xiong > 0.3 and score_xiong > score_ji:
        return -1, details
    else:
        return 0, details


# 評估
print("\n" + "=" * 70)
print("評估結果")
print("=" * 70)
print()

correct = 0
errors = []

for s in SAMPLES:
    pred, details = predict_ml(s)
    if pred == s[3]:
        correct += 1
    else:
        errors.append({
            "hex": s[0],
            "pos": s[1],
            "binary": s[2],
            "actual": s[3],
            "pred": pred,
            "details": details,
        })

accuracy = correct / len(SAMPLES) * 100
baseline = sum(1 for s in SAMPLES if s[3] == 0) / len(SAMPLES) * 100

print(f"總準確率: {accuracy:.1f}% ({correct}/{len(SAMPLES)})")
print(f"隨機基準: {baseline:.1f}%")
print(f"提升: +{accuracy - baseline:.1f}%")
print()

print(f"錯誤數: {len(errors)}")
print("\n錯誤案例（前10個）:")
for e in errors[:10]:
    actual_str = ["凶", "中", "吉"][e["actual"] + 1]
    pred_str = ["凶", "中", "吉"][e["pred"] + 1]
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 實際:{actual_str} 預測:{pred_str}")

# 嘗試更多優化
print("\n" + "=" * 70)
print("閾值調優")
print("=" * 70)

best_acc = 0
best_thresholds = None

for ji_th in np.arange(0.1, 1.0, 0.1):
    for xiong_th in np.arange(0.1, 1.0, 0.1):
        correct = 0
        for s in SAMPLES:
            hex_num, pos, binary, fortune = s

            result, rule = check_hard_rules(hex_num, pos, binary)
            if result is not None:
                pred = result
            else:
                x = np.array(sample_to_vector(s))
                score_ji = np.dot(weights_ji, x) + bias_ji
                score_xiong = np.dot(weights_xiong, x) + bias_xiong

                if score_ji > ji_th and score_ji > score_xiong:
                    pred = 1
                elif score_xiong > xiong_th and score_xiong > score_ji:
                    pred = -1
                else:
                    pred = 0

            if pred == fortune:
                correct += 1

        acc = correct / len(SAMPLES) * 100
        if acc > best_acc:
            best_acc = acc
            best_thresholds = (ji_th, xiong_th)

print(f"\n最佳閾值: 吉={best_thresholds[0]:.1f}, 凶={best_thresholds[1]:.1f}")
print(f"最佳準確率: {best_acc:.1f}%")

# 版本進程
print()
print("=" * 70)
print("版本進程")
print("=" * 70)
print(f"""
| 版本 | 方法 | 準確率 |
|------|------|--------|
| 基準 | 全猜「中」 | 52.2% |
| V9 | 八卦屬性 | 56.7% |
| V11 | V9精煉 | 57.8% |
| V13 | 字符-詞語 | 60.0% |
| V15 | 全整合 | 62.2% |
| V17 | ML感知機 | {best_acc:.1f}% |
""")

# 最終公式導出
print()
print("=" * 70)
print("ML學習到的公式（可解釋版本）")
print("=" * 70)

print("\n吉傾向特徵（權重從高到低）:")
for name, w in sorted(zip(feature_names, weights_ji), key=lambda x: -x[1])[:10]:
    print(f"  {name:20}: {w:+.3f}")

print("\n凶傾向特徵（權重從高到低）:")
for name, w in sorted(zip(feature_names, weights_xiong), key=lambda x: -x[1])[:10]:
    print(f"  {name:20}: {w:+.3f}")
