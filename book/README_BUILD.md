# 書籍建置指南 | Book Build Guide

## Amazon KDP 格式指南

### Kindle 電子書 (eBook)
- **格式**: EPUB
- **說明**: 上傳 EPUB，Amazon 會自動轉換為 Kindle 格式

### 紙本書 (Paperback/Print-on-Demand)
- **格式**: PDF
- **尺寸**: 6" x 9" (標準) 或 5.5" x 8.5" (較小)
- **說明**: PDF 給你完整的排版控制

---

## 建置方式

### 方式一：使用建置腳本 (推薦)

```bash
cd /Users/arsenelee/github/iching/book

# 建置所有格式
./build.sh

# 只建置 EPUB
./build.sh epub

# 只建置 PDF
./build.sh pdf
```

### 方式二：手動使用 Pandoc

```bash
# EPUB (電子書)
pandoc full_book.md \
  --metadata-file=metadata.yaml \
  --toc \
  --epub-chapter-level=1 \
  -o output/decoding-iching.epub

# PDF (紙本書)
pandoc full_book.md \
  --metadata-file=metadata.yaml \
  --pdf-engine=xelatex \
  --toc \
  -V geometry:margin=1in \
  -V papersize:letter \
  -o output/decoding-iching.pdf
```

---

## 依賴套件

### macOS
```bash
# 安裝 Pandoc
brew install pandoc

# 安裝 LaTeX (PDF 需要)
brew install --cask mactex

# 安裝中文字型 (如果需要)
brew tap homebrew/cask-fonts
brew install --cask font-noto-sans-cjk
```

### Ubuntu/Debian
```bash
sudo apt install pandoc texlive-xetex fonts-noto-cjk
```

---

## 檔案結構

```
book/
├── front_matter/         # 前言
│   ├── 00_title_page.md
│   ├── 01_copyright.md
│   ├── 02_dedication.md
│   ├── 03_introduction.md
│   └── 04_table_of_contents.md
│
├── chapters/             # 章節內容
│   ├── 01_why_modern_people_need_iching.md
│   ├── 02_yin_yang_binary.md
│   ├── ...
│   └── 25_keyword_reliability.md
│
├── back_matter/          # 後記
│   ├── 01_about_author.md
│   └── 02_figure_index.md
│
├── images/               # 圖表
│   ├── 01_8x8_hexagram_grid.svg
│   ├── 02_position_effects.svg
│   ├── 03_three_layer_system.svg
│   ├── 04_keyword_reliability.svg
│   ├── 05_trigram_interaction.svg
│   └── 06_eight_trigrams.svg
│
├── output/               # 輸出檔案
│   ├── decoding-iching.epub
│   ├── decoding-iching.pdf
│   └── decoding-iching.html
│
├── metadata.yaml         # 書籍元資料
├── style.css            # HTML 樣式
├── build.sh             # 建置腳本
└── BOOK_MASTER.md       # 主文件
```

---

## Amazon KDP 上傳流程

### 1. Kindle 電子書

1. 登入 [KDP Dashboard](https://kdp.amazon.com)
2. 點擊「Create a New Kindle eBook」
3. 填寫書籍資訊（標題、作者、描述等）
4. 上傳 `output/decoding-iching.epub`
5. 上傳封面圖片 (1600 x 2560 pixels 推薦)
6. 設定價格
7. 預覽並發布

### 2. 紙本書

1. 點擊「Create a New Paperback」
2. 填寫書籍資訊
3. 選擇尺寸和紙張類型
4. 上傳 `output/decoding-iching.pdf`
5. 上傳封面 (需要包含書脊和背面，使用 KDP Cover Calculator)
6. 設定價格
7. 訂購樣書確認後發布

---

## 圖表說明

本書使用 SVG 格式的圖表，可直接嵌入 EPUB。

| 圖表 | 用途 |
|------|------|
| `01_8x8_hexagram_grid.svg` | 64卦棋盤視覺化 |
| `02_position_effects.svg` | 爻位效應直條圖 |
| `03_three_layer_system.svg` | 三層系統架構圖 |
| `04_keyword_reliability.svg` | 關鍵詞可信度圖 |
| `05_trigram_interaction.svg` | 卦德交互熱力圖 |
| `06_eight_trigrams.svg` | 八卦與卦德說明 |

---

## 封面設計指南

### Kindle 封面
- 尺寸: 1600 x 2560 pixels (1:1.6 比例)
- 格式: JPEG 或 TIFF
- DPI: 300

### 紙本封面
- 使用 Amazon KDP Cover Calculator 計算尺寸
- 需包含：前封面、書脊、後封面
- 格式: PDF
- 出血: 3.2mm (0.125")

---

## 注意事項

1. **中文字型**: 確保安裝了 Noto Sans CJK 或其他中文字型
2. **圖片大小**: 建議單張圖片不超過 5MB
3. **連結**: 外部連結在 Kindle 上可能無法點擊
4. **表格**: 複雜表格在電子書上可能需要調整

---

*建置日期: 2026-01-21*
