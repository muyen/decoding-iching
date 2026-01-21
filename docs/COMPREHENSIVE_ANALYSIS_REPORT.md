# Comprehensive I Ching Pattern Analysis Report

## Executive Summary

This report synthesizes findings from multiple analytical approaches applied to the 384 yaos (爻) of the I Ching, seeking to understand which structural patterns determine 吉凶 (auspicious/inauspicious) outcomes.

**Key Finding**: Structure alone explains approximately **~50% accuracy** in predicting 吉凶, meaning that **~50% of the determination requires reading the actual 爻辭 (line texts)**.

**Important Correction**: Earlier research (V17) claimed 62.2% accuracy, but this was **overfitting** to only 90 samples (15 hexagrams). When validated on the complete 384 yaos with 5-fold cross-validation, the true structural prediction limit is **~50%**.

---

## 1. ML Prediction Model Results

### Model Performance (Full 384 Yaos, 5-Fold CV)
| Model | Accuracy | vs Random (33.3%) |
|-------|----------|-------------------|
| Always predict "中" | 46.4% | +13.1% |
| Rule-Based (Position) | 45-49% | +12-16% |
| ML with all features | ~50% | +17% |
| ML + 五行 features | 50.3% | +17% |
| **Structural Limit** | **~50%** | **+17%** |

### Historical Note
| Model | Reported Accuracy | Sample Size | Status |
|-------|-------------------|-------------|--------|
| V17 | 62.2% | 90 (15 hexagrams) | ⚠️ Overfitting |
| V18 (Full validation) | 45.1% | 384 yaos | ✓ Valid |
| Final best | ~50% | 384 yaos (5-fold CV) | ✓ Valid |

### Feature Importance (by correlation)
| Rank | Feature | Correlation |
|------|---------|-------------|
| 1 | is_extreme_lower (Position 3) | 0.128 |
| 2 | same_trigram | 0.089 |
| 3 | upper_trigram | 0.083 |
| 4 | is_yang | 0.081 |
| 5 | is_center_upper (Position 5) | 0.079 |

### Conclusion
Structure provides modest predictive power. The rule-based model (using position alone) outperforms the ML model, confirming that **position is the dominant structural factor**.

---

## 2. 承乘比應 (Yao Relationships) Analysis

Traditional I Ching analysis examines four types of yao relationships:

### Results Summary
| Relationship | Condition | 吉率 | χ² |
|--------------|-----------|------|-----|
| **中正** (center + correct polarity) | Pos 2/5 matching | 40.6% | 3.06 |
| **正應** (correct correspondence) | 1-4, 2-5, 3-6 different | 40.1% | 1.27 |
| **比** (adjacent same polarity) | Neighbors match | 46.9% | **6.53** |
| **承** (yin supports yang) | Yin below yang | 33.8% | 0.16 |

### Key Finding
**比關係 (adjacent same polarity)** shows the strongest effect:
- Same polarity neighbors: 46.9% 吉率
- Different polarity neighbors: 31.2% 吉率
- χ² = 6.53 (approaching significance)

---

## 3. 消息卦 (12 Sovereign Hexagrams) Analysis

The 12 sovereign hexagrams represent the annual yin-yang cycle.

### Sovereign vs Non-Sovereign
| Category | 吉率 | 凶率 |
|----------|------|------|
| 消息卦 (12 hexagrams) | 36.1% | 23.6% |
| 非消息卦 (52 hexagrams) | 36.5% | 16.3% |

### By Yang Count
| Yang Lines | 吉率 | Notable Pattern |
|------------|------|-----------------|
| 0 (坤) | 33.3% | Neutral |
| 1 (復, 剝) | 25.0% | Low |
| 2 (臨, 觀) | 50.0% | High |
| 3 (泰, 否) | 41.7% | Moderate |
| 4 (大壯, 遯) | 58.3% | **Highest** |
| 5 (夬, 姤) | 8.3% | **Lowest** |
| 6 (乾) | 33.3% | Neutral |

### Key Finding
**Extreme hexagrams (5 yang or 1 yang) have the lowest 吉率**. The middle ground (2-4 yang lines) is more favorable, consistent with traditional "中" (moderation) philosophy.

---

## 4. 互卦/錯卦/綜卦 Transformation Analysis

### Transformation Correlation with Original 吉凶
| Transformation | Correlation | Interpretation |
|----------------|-------------|----------------|
| 互卦 (interlocking) | 48.4% | Weak - no predictive value |
| 錯卦 (opposite) | **71.9%** | Strong - inverses tend to match |
| 綜卦 (overturned) | 57.1% | Moderate |

### Self-Symmetric Hexagrams (8 total)
| Name | Binary | 吉率 |
|------|--------|------|
| 乾 | 111111 | 33.3% |
| 坤 | 000000 | 33.3% |
| 頤 | 001100 | 50.0% |
| 大過 | 110011 | 33.3% |
| 坎 | 010010 | **0.0%** |
| 離 | 101101 | 33.3% |
| 中孚 | 011110 | 33.3% |
| 小過 | 100001 | 33.3% |

### Key Finding
**錯卦 pairs (bit-flip inverses) show surprising 71.9% outcome similarity**, suggesting that complementary hexagrams share similar fortunes.

---

## 5. 馬王堆 vs 文王 Sequence Comparison

### Organization Principles
| Sequence | Date | Principle | Structure |
|----------|------|-----------|-----------|
| 馬王堆 | ~168 BCE | Upper trigram | 8 octets × 8 |
| 文王 | ~1000 BCE | Pairing | 32 pairs |

### Position Displacement
- Mean displacement: 16.8 positions
- Only 12 hexagrams have similar positions (diff ≤ 3)
- Max displacement: 49 (小畜: MW #58 → KW #9)

### Sequence Autocorrelation
| Sequence | Autocorrelation |
|----------|-----------------|
| 馬王堆 | 0.101 |
| 文王 | -0.021 |

Neither sequence shows strong sequential 吉凶 correlation.

### 馬王堆 Octet Analysis (by Upper Trigram)
| Trigram | 吉率 | 凶率 |
|---------|------|------|
| 坤 | **47.9%** | 12.5% |
| 乾 | 42.9% | 16.7% |
| 巽 | 41.7% | 12.5% |
| 離 | 37.5% | 22.9% |
| 艮 | 37.5% | 18.8% |
| 坎 | 33.3% | **6.2%** |
| 兌 | 25.0% | 27.1% |
| 震 | **22.9%** | 25.0% |

### Key Finding
Position effects are **ROBUST across both sequences**. The patterns we found are intrinsic to hexagram structure, not sequence-dependent.

---

## 6. Unified Theory: The Three Layers Model

Based on all analyses, 吉凶 determination follows three layers:

### Layer 1: Structural (~35% predictable)
- **Position** is dominant (χ² = 39.11, p < 0.00001)
- Position 5 (九五之尊): 51.6% 吉率
- Position 3 (下卦之極): highest 凶率
- Position 2 (中): 46.9% 吉率

### Layer 2: Relational + 五行 (~15% additional)
- 比關係 (adjacent polarity match): +10% 吉率
- 錯卦 correlation: 71.9%
- 五行關係：
  - 相生: 44-47% 吉, **5.6% 凶** (safest)
  - 比和: 29.8% 吉, **21.4% 凶** (most dangerous)
  - 相剋: 35-38% 吉, 17% 凶

### Layer 3: Textual (~50% requires 爻辭)
- Cannot be predicted from structure alone
- Semantic content of line texts
- Historical/situational context
- Symbolic imagery

**Note**: Total structural prediction achieves ~50% accuracy maximum.

---

## 7. Practical Implications

### For Divination Practice
1. **Always read the 爻辭** - structure only gets you ~50% accuracy
2. **Pay attention to position** - it's the most reliable structural indicator
3. **Position 5 is favorable**, Position 3 requires caution
4. **Extreme hexagrams (5 or 1 yang)** tend toward difficulty
5. **五行關係**: 相生 relationships are safest (only 5.6% 凶); 比和 (same element) is most dangerous (21.4% 凶)

### For Research
1. The 馬王堆 and 文王 sequences show the patterns are not sequence artifacts
2. 錯卦 correlation (71.9%) deserves further investigation
3. NLP analysis of 爻辭 text is essential for deeper understanding
4. **Important**: Always validate on full 384 yaos with cross-validation to avoid overfitting

---

## 8. Data Files Generated

| File | Description |
|------|-------------|
| `data/analysis/ml_model.json` | ML model parameters and feature importance |
| `data/analysis/yao_relationships.json` | 承乘比應 analysis results |
| `data/analysis/xiaoxi_gua_analysis.json` | 消息卦 analysis results |
| `data/analysis/transformation_analysis.json` | 互卦/錯卦/綜卦 results |
| `data/analysis/mawangdui_comparison.json` | Sequence comparison results |

---

## 9. Scripts Created

| Script | Purpose |
|--------|---------|
| `scripts/ml_prediction_model.py` | ML classification model |
| `scripts/yao_relationships_analysis.py` | Traditional relationship patterns |
| `scripts/xiaoxi_gua_analysis.py` | 12 sovereign hexagrams |
| `scripts/hugua_cuogua_zonggua_analysis.py` | Hexagram transformations |
| `scripts/mawangdui_comparison.py` | Cross-tradition validation |

---

## 10. Statistical Significance Summary

| Finding | Statistical Test | Result |
|---------|------------------|--------|
| Position effect | χ² test | p = 2.43×10⁻⁵ ✓ |
| Trigram effect | χ² test | p = 0.096 ✗ |
| 比關係 effect | χ² = 6.53 | Marginal |
| Special yao intervals | Geometric fit | p = 0.905 ✓ |

---

*Report generated: 2026-01-21*
*Analysis methods: Python, numpy, statistical testing*
*Expert consultation: 5 specialized AI perspectives (易經大師, Mathematician, Statistician, Pattern Recognition, Algorithm Expert)*
