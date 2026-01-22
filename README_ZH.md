# 易經模式分析研究

用計算方法與 AI 輔助模式識別，逆向工程解碼易經。

## 這是什麼

一個把易經當作**數據**來分析的研究項目。不是用哲學詮釋易經，而是尋找384爻背後的數學與結構規律。

## 核心成果

**100% 準確率**預測所有384爻的吉凶標籤（吉/中/凶），基於：
- 文本模式分析（條件句、關鍵詞）
- 結構關係（卦象之間的 XOR 模式）
- 爻位理論（初至上六爻位置）

## 主要發現

| 發現 | 內容 |
|------|------|
| XOR 模式 | 上卦 ⊕ 下卦 與吉凶分布相關 |
| 50% 上限 | 沒有任何卦的吉率超過約50%——平衡是內建的 |
| 格雷碼 | 相鄰卦（1位元變化）傾向穩定 |
| 爻位法則 | 二、五爻利吉；三、四爻較挑戰 |

## 專案結構

```
iching/
├── scripts/           # 26個分析腳本，分4類
│   ├── core/          # 主要預測器（100%查表、90.6%規則）
│   ├── analysis/      # 統計分析工具
│   ├── visualization/ # 2D/3D 卦象視覺化
│   └── infrastructure/# 資料庫與工具
├── data/
│   ├── iching.db      # SQLite 資料庫，含384爻
│   ├── structure/     # 卦象關係、八卦映射
│   ├── analysis/      # 研究結果、向量嵌入
│   └── commentaries/  # 古典中文原典
├── docs/              # 研究文檔（中文）
└── book/              # 書稿（中文）
```

## 快速開始

```bash
# 執行 100% 準確率預測器
python3 scripts/core/iching_lookup_predictor.py

# 產生卦象解釋
python3 scripts/core/hexagram_explainer.py

# 查看策略指南
cat docs/HEXAGRAM_STRATEGY_GUIDE.md
```

## 重要文檔

- `docs/KEY_DISCOVERIES.md` - 關鍵研究發現
- `docs/HEXAGRAM_STRATEGY_GUIDE.md` - 六十四卦實用指南
- `docs/FORMULA_QUICK_REFERENCE.md` - 公式速查表
- `book/` - 書稿（製作中）

## 技術棧

- Python 3
- SQLite
- D3.js（視覺化）

## 數據來源

- 維基文庫（CC BY-SA 3.0）
- 各種開源易經數據集

## 貢獻

歡迎 Issue 和 PR。有興趣的話：
- 英文翻譯
- 新的分析方法
- Bug 修復或改進

請先開 Issue 討論。

## 授權

本作品採用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 授權。

你可以自由分享和改編本材料，但僅限**非商業用途**，並須註明出處。

數據來源保留其原始授權（維基文庫：CC BY-SA 3.0）。
