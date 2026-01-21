# 易經公式 V4 - 計算機科學/機器學習評審報告

**評審日期**: 2026-01-20
**評審文件**: `/scripts/formula_v4_test.py`
**評審角度**: CS/ML 工程師視角

---

## 1. 參數/特徵統計

### 1.1 結構特徵 (Structure Features)

| 類別 | 參數數量 | 說明 |
|------|---------|------|
| `TIME_TYPES` | 64 個卦號映射到 4 類 | 時義分類 |
| `POSITION_BASE` | 6 個 | 爻位基礎分 |
| `POSITION_RISK` | 6 個 | 爻位風險係數 |
| `UPPER_LINE_COMPLETION` | 6 個 | 上爻完成特例 |
| `UPPER_LINE_EXCESS` | 14 個 | 上爻過盈特例 |
| `FOURTH_LINE_REMEDIAL` | 14 個 | 四爻補救特例 |
| `FOURTH_LINE_DANGEROUS` | 4 個 | 四爻危險特例 |
| `HEXAGRAM_VIRTUE_ALIGNMENT` | ~50+ 個映射 | 卦德契合度 |

### 1.2 文本特徵 (Text Features)

| 關鍵詞類型 | 數量 | 權重範圍 |
|-----------|------|---------|
| 正面詞 (元吉, 大吉, 終吉, 吉, 悔亡, 利, 亨, 無不利) | 8 個 | +1 到 +5 |
| 負面詞 (凶, 厲, 咎, 吝, 悔, 泣血, 無首, 滅) | 8 個 | -1 到 -4 |
| 特殊模式 (何咎, 無咎, 條件句) | 3 個 | 邏輯標誌 |

### 1.3 總參數估計

```
結構參數:  ~110+ 個離散映射
文本權重:  ~19 個關鍵詞權重
閾值參數:  3 個 (final > 1.5, final < -0.5, text_score * 0.3)
總計:      ~130+ 個可調參數
```

**結論**: 對於 30 個數據點來說，130+ 個參數嚴重過參數化 (over-parameterized)。

---

## 2. 過擬合風險分析

### 2.1 統計學角度

- **樣本量**: n = 30
- **參數量**: p >= 130
- **自由度比**: p/n > 4.3

**經驗法則**: 建議 n/p >= 10，此處 n/p < 0.25，嚴重違反。

### 2.2 過擬合指標

```python
# 過擬合風險評估
VC_dimension_estimate = 130  # 近似 VC 維度
sample_complexity = VC_dimension_estimate * 10  # 至少需要 1300 樣本
actual_samples = 30
overfitting_risk = "極高 (Critical)"
```

### 2.3 具體風險

1. **完美記憶效應**: 100% 準確率在 30 樣本上達成，幾乎肯定是記憶而非泛化
2. **Cherry-picking 風險**: `HEXAGRAM_VIRTUE_ALIGNMENT` 等映射表可能就是為這 30 個樣本量身定製
3. **測試集污染**: 訓練和測試用的是同一批數據

### 2.4 預期泛化誤差

如果在獨立測試集上評估:

```
樂觀估計: 60-70% (若規則有一定普適性)
悲觀估計: 33% (三分類隨機猜測基準)
現實估計: 45-55%
```

---

## 3. 規則系統 vs. 學習模型

### 3.1 當前系統性質

**這是一個硬編碼的規則系統 (Rule-based Expert System)，不是機器學習模型。**

特徵:
- 所有規則手工編寫
- 沒有從數據中學習參數
- 沒有損失函數或優化過程
- 沒有梯度下降或參數更新

```python
# 這是規則，不是學習
HEXAGRAM_VIRTUE_ALIGNMENT = {
    1: {5: 2, 6: -2},  # 手工指定
    ...
}
```

### 3.2 適用性分析

| 方面 | 規則系統優勢 | 學習模型優勢 |
|------|------------|-------------|
| 可解釋性 | 高 (可以解釋每條規則) | 低 (黑箱) |
| 數據需求 | 低 (專家知識替代) | 高 (需要大量標註) |
| 泛化能力 | 取決於規則質量 | 取決於數據分布 |
| 領域適配 | 適合此問題 | 可能不適合 |

### 3.3 結論

**對於易經這個領域，規則系統可能更合適:**

1. **數據稀缺**: 僅 384 條爻辭，且標註 ground truth 困難
2. **領域知識豐富**: 數千年的注疏和解讀可轉化為規則
3. **可解釋性需求**: 用戶需要理解預測原因

---

## 4. 特殊案例分析：領域知識 vs. 數據學習

### 4.1 `HEXAGRAM_VIRTUE_ALIGNMENT` 來源分析

```python
HEXAGRAM_VIRTUE_ALIGNMENT = {
    1: {5: 2, 6: -2},   # 乾卦：五爻飛龍在天(+2)，上爻亢龍有悔(-2)
    15: {3: 3, 5: 1, 6: 1},  # 謙卦：三爻勞謙(+3)
    24: {1: 3, 6: -3},  # 復卦：初爻不遠復(+3)，上爻迷復(-3)
    ...
}
```

**判斷**: 這些數值**看起來像領域知識**，但：

1. **缺乏引用**: 沒有說明來源（傳統注疏？現代研究？）
2. **數值可疑**: 為什麼是 +2、+3 而不是其他值？
3. **可能是數據擬合**: 如果這些值是調整到測試通過的，那就是過擬合

### 4.2 `UPPER_LINE_COMPLETION` / `UPPER_LINE_EXCESS` 分析

```python
UPPER_LINE_COMPLETION = {33: 3, 50: 3, 53: 2, 48: 2, 46: 2, 15: 2}
UPPER_LINE_EXCESS = {1: -2, 3: -3, 8: -3, 21: -3, ...}
```

**判斷**: 這些選擇性映射高度可疑：

- 為什麼恰好是這幾個卦？
- 為什麼數值如此精確？
- 很可能是根據測試樣本 "調出來" 的

### 4.3 文本規則 `analyze_yaoci_text_v4`

```python
if "元吉" in text: score += 5
elif "終吉" in text: score += 4
elif "吉" in text: score += 3
```

**判斷**: 這些更像合理的領域知識：

- 「元吉」>「終吉」>「吉」的等級是易學共識
- 「何咎」是反問句的判斷是正確的語言學分析

---

## 5. 交叉驗證分析

### 5.1 可行性

```python
# 30 樣本的 k-fold CV
k = 5  # 每 fold 6 個樣本
# 或
k = 3  # 每 fold 10 個樣本

# Leave-one-out CV
k = 30  # 每次用 29 個訓練，1 個測試
```

### 5.2 問題

**交叉驗證對此系統無意義**，因為：

1. **沒有學習過程**: 規則是硬編碼的，不會因訓練集改變
2. **所有數據都用於構建規則**: 無法分離訓練/測試

### 5.3 預期 CV 準確率

如果強行做 CV（假設規則固定）:

```
預期結果: 仍然 ~100%，因為規則已經記住了所有樣本
這不能證明泛化能力
```

### 5.4 正確的驗證方法

1. **收集新樣本**: 從剩餘 354 條爻辭中標註
2. **時間分割**: 用傳統注疏訓練，用現代研究測試
3. **專家盲測**: 讓易學專家獨立標註，對比預測

---

## 6. 與其他 ML 方法比較

### 6.1 決策樹 (Decision Tree)

```python
# 決策樹可以自動發現規則
from sklearn.tree import DecisionTreeClassifier
# 特徵: [hex_num, position, is_yang, is_proper, is_central, text_features...]
# 30 樣本訓練
```

**預期表現**:
- 訓練集: 100% (會完美記憶)
- 測試集: 40-55% (過擬合嚴重)
- **可能不比當前規則系統更好**

### 6.2 隨機森林 (Random Forest)

```python
from sklearn.ensemble import RandomForestClassifier
# 集成方法可能減少過擬合
```

**預期表現**:
- 訓練集: 95-100%
- 測試集: 45-60% (略好於單棵樹)
- **數據太少，效果有限**

### 6.3 神經網路

```python
import torch.nn as nn
# MLP 或 Transformer
```

**預期表現**:
- 訓練集: 100% (輕鬆記憶 30 樣本)
- 測試集: 33-50% (嚴重過擬合，可能不如隨機)
- **完全不推薦**: 數據量遠低於神經網路需求

### 6.4 比較總結

| 方法 | 30 樣本預期測試準確率 | 推薦度 |
|------|---------------------|--------|
| 當前規則系統 | ~50% (未知) | 中 |
| 決策樹 | 40-55% | 低 |
| 隨機森林 | 45-60% | 低 |
| 神經網路 | 33-50% | 不推薦 |
| 樸素貝葉斯 | 50-60% | 中 |
| **專家系統 + 知識圖譜** | 60-75% | **推薦** |

---

## 7. 代碼質量評審

### 7.1 優點

1. **清晰的文檔**: 函數有說明，版本歷程清楚
2. **模塊化**: 文本分析、結構計算、預測分離
3. **可讀性**: 中文註釋，業務邏輯清晰
4. **測試框架**: 有測試數據和結果輸出

### 7.2 代碼異味 (Code Smells)

#### 7.2.1 魔數過多 (Magic Numbers)

```python
# 問題: 數字意義不明確
score += 5  # 為什麼是 5?
score += 4  # 為什麼是 4?
final = structure_score + text_score * 0.3  # 0.3 從哪來?
if final > 1.5:  # 1.5 怎麼確定的?
```

**建議**: 使用命名常量

```python
WEIGHT_YUAN_JI = 5
WEIGHT_ZHONG_JI = 4
TEXT_SCORE_RATIO = 0.3
POSITIVE_THRESHOLD = 1.5
```

#### 7.2.2 硬編碼配置 (Hardcoded Configuration)

```python
# 問題: 映射表應外部化
HEXAGRAM_VIRTUE_ALIGNMENT = { ... }  # 應該讀取配置文件
```

**建議**:

```python
import yaml
with open('config/hexagram_rules.yaml') as f:
    HEXAGRAM_VIRTUE_ALIGNMENT = yaml.safe_load(f)
```

#### 7.2.3 單一責任違反 (SRP Violation)

```python
def calculate_v4_formula(hex_num, position, is_yang, is_proper, is_central, yaoci_text=""):
    # 這個函數做了太多事:
    # 1. 計算基礎分
    # 2. 查找特殊規則
    # 3. 計算時義
    # 4. 分析文本
    # 5. 做預測
```

**建議**: 分拆為更小的函數

#### 7.2.4 缺乏類型提示 (Missing Type Hints)

```python
# 問題
def analyze_yaoci_text_v4(text):

# 建議
def analyze_yaoci_text_v4(text: str) -> tuple[int, dict[str, bool]]:
```

#### 7.2.5 測試數據與代碼混合

```python
# 問題: 測試數據應該分離
TEST_SAMPLES_V4 = [...]  # 應該在單獨的測試文件
```

### 7.3 代碼評分

| 維度 | 評分 (1-10) | 說明 |
|------|------------|------|
| 可讀性 | 7 | 結構清晰，但魔數多 |
| 可維護性 | 5 | 硬編碼過多，修改困難 |
| 可測試性 | 6 | 有測試但混在一起 |
| 擴展性 | 4 | 添加新規則需改代碼 |
| 文檔 | 7 | 有註釋但缺乏 API 文檔 |

**總評: 5.8/10** - 原型質量尚可，生產級別需重構

---

## 8. 更好的 ML 方法建議

### 8.1 短期改進 (現有框架內)

```python
# 1. 配置外部化
class ICHingPredictor:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)

# 2. 添加置信度
def predict_with_confidence(self, ...) -> tuple[int, float]:
    """返回預測和置信度 (0-1)"""

# 3. 日誌規則觸發
def predict_with_explanation(self, ...) -> dict:
    """返回預測和觸發的規則列表"""
```

### 8.2 中期改進 (數據收集後)

**收集 200+ 標註樣本後:**

```python
# 貝葉斯方法 - 結合先驗知識
from sklearn.naive_bayes import MultinomialNB

# 特徵工程
features = [
    'time_type_onehot',      # 4 維
    'position_onehot',        # 6 維
    'yang_yin',               # 1 維
    'proper_improper',        # 1 維
    'central',                # 1 維
    'text_tfidf_vector',      # N 維
]

# 訓練
clf = MultinomialNB(alpha=1.0)  # 拉普拉斯平滑
clf.fit(X_train, y_train)
```

### 8.3 長期改進 (理想方案)

**知識圖譜 + 規則學習:**

```python
# 1. 構建易經知識圖譜
from neo4j import GraphDatabase
# 節點: 卦、爻、象、辭
# 邊: 生成、對應、克制

# 2. 使用圖神經網路
from torch_geometric.nn import GCNConv
class ICHingGNN(nn.Module):
    def __init__(self):
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

# 3. 或使用符號 AI + 規則學習
from pylo import ILP  # 歸納邏輯編程
# 從數據中學習規則，而非手工編寫
```

### 8.4 推薦方案

考慮到:
- 數據量極小 (30 樣本)
- 領域知識豐富
- 可解釋性需求高

**最佳方案**: **專家系統 + 規則學習混合**

```python
class HybridICHingPredictor:
    def __init__(self):
        self.expert_rules = load_verified_rules()  # 經典注疏規則
        self.learned_rules = None  # 從數據學習的補充規則

    def predict(self, hex_num, position, text):
        # 1. 先用專家規則
        if expert_match := self.expert_rules.match(hex_num, position):
            return expert_match.outcome, confidence=0.9

        # 2. 再用學習規則
        if self.learned_rules:
            return self.learned_rules.predict(features)

        # 3. 回退到基準
        return self.baseline_predict(hex_num, position)
```

---

## 9. 總結

### 9.1 核心問題

1. **過參數化**: 130+ 參數 vs 30 樣本，過擬合風險極高
2. **非學習系統**: 這是硬編碼規則，不是 ML 模型
3. **測試無效**: 用訓練數據測試，100% 準確率無意義
4. **泛化存疑**: 預期真實準確率 50% 左右

### 9.2 積極方面

1. **規則系統適合此領域**: 數據少、知識多、需可解釋
2. **代碼結構基本合理**: 可作為原型進一步發展
3. **文本分析有價值**: 關鍵詞識別邏輯是合理的

### 9.3 建議行動

| 優先級 | 行動 | 預期收益 |
|--------|------|---------|
| 高 | 收集並標註 200+ 獨立測試樣本 | 真實評估準確率 |
| 高 | 將規則來源文檔化 | 區分知識 vs 過擬合 |
| 中 | 代碼重構，配置外部化 | 提高可維護性 |
| 中 | 添加置信度和解釋輸出 | 提高實用性 |
| 低 | 實驗 ML 方法作為基準對比 | 驗證規則系統優勢 |

### 9.4 最終評價

**這不是一個 ML 模型，而是一個手工調優的規則系統。**

在當前數據量下，這可能是最務實的選擇。但聲稱 "100% 準確率" 具有誤導性 - 這只是在 30 個手選樣本上的記憶，不代表泛化能力。

**建議改名**: 從 "預測模型" 改為 "專家規則系統"，更準確地描述其本質。

---

*評審完成*

*CS/ML 工程師 | 2026-01-20*
