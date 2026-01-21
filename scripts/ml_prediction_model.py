#!/usr/bin/env python3
"""
ML Prediction Model for I Ching 吉凶 Classification
Uses features identified by expert group analysis:
- Position (most important, 9.2% variance)
- Positional harmony
- Hexagram balance
- Trigram composition
"""

import json
import numpy as np
from collections import defaultdict
import os

# Trigram mappings
TRIGRAM_BINARY = {
    '乾': '111', '兌': '110', '離': '101', '震': '100',
    '巽': '011', '坎': '010', '艮': '001', '坤': '000'
}

TRIGRAM_TO_NUM = {
    '乾': 0, '兌': 1, '離': 2, '震': 3,
    '巽': 4, '坎': 5, '艮': 6, '坤': 7
}

# Keyword weights for 吉凶 classification
JI_KEYWORDS = {
    '元吉': 2, '大吉': 2, '吉': 1, '無咎': 0.5, '利': 0.5,
    '亨': 0.5, '貞吉': 1, '終吉': 1, '有喜': 1, '有慶': 1
}

XIONG_KEYWORDS = {
    '凶': -1, '大凶': -2, '厲': -0.5, '吝': -0.3, '悔': -0.3,
    '咎': -0.3, '災': -1, '死': -1.5, '亡': -0.5, '困': -0.5
}

def load_hexagram_data():
    """Load hexagram data from JSON files"""
    # Load yaoci text from ctext
    yaoci_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ctext', 'zhouyi_64gua.json')
    with open(yaoci_path, 'r', encoding='utf-8') as f:
        yaoci_data = json.load(f)

    # Load structure data
    struct_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'structure', 'hexagrams_structure.json')
    with open(struct_path, 'r', encoding='utf-8') as f:
        struct_data = json.load(f)

    # Combine data
    hexagrams = []
    for hex_data in yaoci_data['hexagrams']:
        number = hex_data['metadata']['number']
        name = hex_data['title_zh']
        content = hex_data['content_zh']

        # Get structure info
        struct = struct_data.get(str(number), {})

        # Parse yaoci (lines 1-6 are indices 1-6 in content_zh, index 0 is guaci)
        lines = []
        for i in range(1, min(7, len(content))):
            lines.append({'text': content[i]})

        hexagrams.append({
            'number': number,
            'name': name,
            'lines': lines,
            'trigrams': {
                'upper': struct.get('upper_trigram', {}).get('name', ''),
                'lower': struct.get('lower_trigram', {}).get('name', '')
            },
            'binary': struct.get('binary', '')
        })

    return hexagrams

def classify_yao(text):
    """Classify yao text as 吉(1), 中(0), or 凶(-1)"""
    ji_score = sum(weight for kw, weight in JI_KEYWORDS.items() if kw in text)
    xiong_score = sum(weight for kw, weight in XIONG_KEYWORDS.items() if kw in text)

    total = ji_score + xiong_score
    if total > 0.3:
        return 1  # 吉
    elif total < -0.3:
        return -1  # 凶
    else:
        return 0  # 中

def extract_features(gua, position):
    """Extract features for ML prediction"""
    upper = gua.get('trigrams', {}).get('upper', '')
    lower = gua.get('trigrams', {}).get('lower', '')

    upper_bin = TRIGRAM_BINARY.get(upper, '000')
    lower_bin = TRIGRAM_BINARY.get(lower, '000')
    binary = upper_bin + lower_bin

    # Get yao value at position (0-indexed from bottom)
    yao_value = int(binary[5 - position]) if position < 6 else 0

    # Features
    features = {
        'position': position + 1,  # 1-6
        'is_yang': yao_value,  # 0 or 1
        'positional_harmony': 1 if (position % 2) == yao_value else 0,
        'hexagram_balance': sum(int(b) for b in binary) - 3,  # -3 to +3
        'upper_trigram': TRIGRAM_TO_NUM.get(upper, 0),
        'lower_trigram': TRIGRAM_TO_NUM.get(lower, 0),
        'is_center_lower': 1 if position == 1 else 0,  # Position 2 (center of lower)
        'is_center_upper': 1 if position == 4 else 0,  # Position 5 (center of upper)
        'is_extreme_lower': 1 if position == 2 else 0,  # Position 3 (top of lower)
        'is_top': 1 if position == 5 else 0,  # Position 6
        'is_bottom': 1 if position == 0 else 0,  # Position 1
        'same_trigram': 1 if upper == lower else 0,
        'upper_yang_count': sum(int(b) for b in upper_bin),
        'lower_yang_count': sum(int(b) for b in lower_bin),
        'is_kan_upper': 1 if upper == '坎' else 0,
        'is_kan_lower': 1 if lower == '坎' else 0,
    }

    return features

def build_dataset():
    """Build complete dataset with features and labels"""
    hexagrams = load_hexagram_data()

    X = []  # Features
    y = []  # Labels
    metadata = []  # For analysis

    for gua in hexagrams:
        lines = gua.get('lines', [])
        for i, line in enumerate(lines):
            text = line.get('text', '')
            if not text:
                continue

            features = extract_features(gua, i)
            label = classify_yao(text)

            # Convert features dict to list
            feature_list = [
                features['position'],
                features['is_yang'],
                features['positional_harmony'],
                features['hexagram_balance'],
                features['upper_trigram'],
                features['lower_trigram'],
                features['is_center_lower'],
                features['is_center_upper'],
                features['is_extreme_lower'],
                features['is_top'],
                features['is_bottom'],
                features['same_trigram'],
                features['upper_yang_count'],
                features['lower_yang_count'],
                features['is_kan_upper'],
                features['is_kan_lower'],
            ]

            X.append(feature_list)
            y.append(label)
            metadata.append({
                'hexagram': gua.get('name', ''),
                'position': i + 1,
                'text': text[:20] + '...' if len(text) > 20 else text
            })

    return np.array(X), np.array(y), metadata

def simple_decision_tree_predict(features):
    """Simple rule-based prediction based on expert findings"""
    position = features[0]
    is_center_lower = features[6]
    is_center_upper = features[7]
    is_extreme_lower = features[8]

    # Based on expert synthesis:
    # Position 5 (center upper) most auspicious
    if position == 5:
        return 1  # 吉
    # Position 2 (center lower) also favorable
    elif position == 2:
        return 0  # 中 (slightly positive)
    # Position 3 (extreme lower) most dangerous
    elif position == 3:
        return -1  # 凶
    # Position 6 (top) often excessive
    elif position == 6:
        return 0  # 中
    # Position 1 (bottom) beginning
    elif position == 1:
        return 0  # 中
    # Position 4 transition
    else:
        return 0  # 中

def naive_bayes_train(X, y):
    """Simple Naive Bayes implementation"""
    classes = [-1, 0, 1]
    class_counts = defaultdict(int)
    feature_sums = defaultdict(lambda: defaultdict(float))
    feature_sq_sums = defaultdict(lambda: defaultdict(float))

    # Calculate statistics per class
    for i, label in enumerate(y):
        class_counts[label] += 1
        for j, val in enumerate(X[i]):
            feature_sums[label][j] += val
            feature_sq_sums[label][j] += val ** 2

    # Calculate means and variances
    means = {}
    variances = {}
    for c in classes:
        n = class_counts[c]
        means[c] = {}
        variances[c] = {}
        for j in range(X.shape[1]):
            mean = feature_sums[c][j] / n if n > 0 else 0
            var = (feature_sq_sums[c][j] / n - mean ** 2) if n > 0 else 1
            var = max(var, 0.01)  # Prevent zero variance
            means[c][j] = mean
            variances[c][j] = var

    priors = {c: class_counts[c] / len(y) for c in classes}

    return {'means': means, 'variances': variances, 'priors': priors, 'classes': classes}

def naive_bayes_predict(model, x):
    """Predict using Naive Bayes"""
    best_class = 0
    best_log_prob = float('-inf')

    for c in model['classes']:
        log_prob = np.log(model['priors'][c] + 1e-10)
        for j, val in enumerate(x):
            mean = model['means'][c][j]
            var = model['variances'][c][j]
            # Gaussian likelihood
            log_prob += -0.5 * np.log(2 * np.pi * var) - (val - mean) ** 2 / (2 * var)

        if log_prob > best_log_prob:
            best_log_prob = log_prob
            best_class = c

    return best_class

def cross_validate(X, y, k=5):
    """K-fold cross-validation"""
    n = len(y)
    indices = np.random.permutation(n)
    fold_size = n // k

    accuracies = []
    confusion_matrices = []

    for fold in range(k):
        # Split data
        val_start = fold * fold_size
        val_end = (fold + 1) * fold_size if fold < k - 1 else n
        val_indices = indices[val_start:val_end]
        train_indices = np.concatenate([indices[:val_start], indices[val_end:]])

        X_train, X_val = X[train_indices], X[val_indices]
        y_train, y_val = y[train_indices], y[val_indices]

        # Train
        model = naive_bayes_train(X_train, y_train)

        # Predict
        y_pred = [naive_bayes_predict(model, x) for x in X_val]

        # Accuracy
        correct = sum(1 for pred, actual in zip(y_pred, y_val) if pred == actual)
        accuracy = correct / len(y_val)
        accuracies.append(accuracy)

        # Confusion matrix
        cm = np.zeros((3, 3), dtype=int)
        for pred, actual in zip(y_pred, y_val):
            cm[actual + 1][pred + 1] += 1
        confusion_matrices.append(cm)

    return accuracies, confusion_matrices

def feature_importance(X, y):
    """Calculate feature importance using correlation"""
    feature_names = [
        'position', 'is_yang', 'positional_harmony', 'hexagram_balance',
        'upper_trigram', 'lower_trigram', 'is_center_lower', 'is_center_upper',
        'is_extreme_lower', 'is_top', 'is_bottom', 'same_trigram',
        'upper_yang_count', 'lower_yang_count', 'is_kan_upper', 'is_kan_lower'
    ]

    correlations = []
    for i in range(X.shape[1]):
        corr = np.corrcoef(X[:, i], y)[0, 1]
        correlations.append((feature_names[i], abs(corr) if not np.isnan(corr) else 0))

    return sorted(correlations, key=lambda x: x[1], reverse=True)

def main():
    print("=" * 60)
    print("ML Prediction Model for I Ching 吉凶 Classification")
    print("=" * 60)

    # Build dataset
    print("\n1. Building dataset...")
    X, y, metadata = build_dataset()
    print(f"   Total samples: {len(y)}")
    print(f"   Features per sample: {X.shape[1]}")
    print(f"   Label distribution:")
    print(f"     吉 (1):  {sum(y == 1)}")
    print(f"     中 (0):  {sum(y == 0)}")
    print(f"     凶 (-1): {sum(y == -1)}")

    # Feature importance
    print("\n2. Feature Importance (by correlation with 吉凶):")
    importances = feature_importance(X, y)
    for name, corr in importances[:10]:
        print(f"   {name:20s}: {corr:.4f}")

    # Cross-validation
    print("\n3. 5-Fold Cross-Validation Results:")
    np.random.seed(42)
    accuracies, cms = cross_validate(X, y, k=5)

    print(f"   Fold accuracies: {[f'{a:.3f}' for a in accuracies]}")
    print(f"   Mean accuracy: {np.mean(accuracies):.3f} ± {np.std(accuracies):.3f}")

    # Aggregate confusion matrix
    total_cm = sum(cms)
    print("\n4. Confusion Matrix (rows=actual, cols=predicted):")
    print("        凶    中    吉")
    labels = ['凶', '中', '吉']
    for i, label in enumerate(labels):
        row = '   '.join(f'{total_cm[i][j]:3d}' for j in range(3))
        print(f"   {label}:  {row}")

    # Per-class accuracy
    print("\n5. Per-Class Accuracy:")
    for i, label in enumerate(['凶', '中', '吉']):
        total = sum(total_cm[i])
        correct = total_cm[i][i]
        acc = correct / total if total > 0 else 0
        print(f"   {label}: {acc:.3f} ({correct}/{total})")

    # Rule-based baseline
    print("\n6. Rule-Based Baseline (Expert Synthesis):")
    rule_preds = [simple_decision_tree_predict(x) for x in X]
    rule_correct = sum(1 for p, a in zip(rule_preds, y) if p == a)
    rule_accuracy = rule_correct / len(y)
    print(f"   Accuracy: {rule_accuracy:.3f}")

    # Train final model
    print("\n7. Training Final Model on Full Dataset...")
    final_model = naive_bayes_train(X, y)

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis', 'ml_model.json')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Convert numpy types to Python types for JSON serialization
    model_serializable = {
        'means': {str(k): dict(v) for k, v in final_model['means'].items()},
        'variances': {str(k): dict(v) for k, v in final_model['variances'].items()},
        'priors': {str(k): float(v) for k, v in final_model['priors'].items()},
        'classes': final_model['classes'],
        'feature_names': [
            'position', 'is_yang', 'positional_harmony', 'hexagram_balance',
            'upper_trigram', 'lower_trigram', 'is_center_lower', 'is_center_upper',
            'is_extreme_lower', 'is_top', 'is_bottom', 'same_trigram',
            'upper_yang_count', 'lower_yang_count', 'is_kan_upper', 'is_kan_lower'
        ],
        'feature_importance': importances,
        'cross_validation': {
            'accuracies': [float(a) for a in accuracies],
            'mean_accuracy': float(np.mean(accuracies)),
            'std_accuracy': float(np.std(accuracies))
        }
    }

    with open(model_path, 'w', encoding='utf-8') as f:
        json.dump(model_serializable, f, ensure_ascii=False, indent=2)
    print(f"   Model saved to: {model_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"• Naive Bayes CV Accuracy: {np.mean(accuracies):.1%}")
    print(f"• Rule-Based Baseline:     {rule_accuracy:.1%}")
    print(f"• Random Baseline (3-class): ~33.3%")
    print(f"\nTop 3 Most Important Features:")
    for name, corr in importances[:3]:
        print(f"  - {name}: correlation {corr:.3f}")

    print("\nConclusion:")
    if np.mean(accuracies) > 0.40:
        print("  ML model outperforms random chance, confirming structural patterns exist.")
    else:
        print("  Accuracy close to random suggests 吉凶 is largely determined by 爻辭 text, not structure.")

if __name__ == "__main__":
    main()
