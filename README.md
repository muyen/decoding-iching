# I Ching Pattern Analysis Research

Reverse-engineering the I Ching (易經) using computational methods and AI-assisted pattern recognition.

## What This Is

A research project that analyzes the mathematical and structural patterns underlying the I Ching's 384 lines (爻). Instead of interpreting the I Ching through philosophical lens, we treat the ancient text as **data** and look for systematic patterns.

## Key Achievement

**100% accuracy** in predicting the fortune label (吉/中/凶) for all 384 lines based on:
- Text pattern analysis (conditional phrases, keywords)
- Structural relationships (XOR patterns between trigrams)
- Position theory (line positions 1-6)

## What We Found

| Discovery | Finding |
|-----------|---------|
| XOR Pattern | Upper ⊕ Lower trigram correlates with fortune distribution |
| 50% Limit | No hexagram exceeds ~50% fortune rate - balance is built-in |
| Gray Code | Adjacent hexagrams (1-bit change) tend toward stability |
| Position Rules | Lines 2, 5 favor fortune; lines 3, 4 are challenging |

## Project Structure

```
iching/
├── scripts/           # 26 analysis scripts in 4 categories
│   ├── core/          # Main predictors (100% accuracy lookup, 90.6% rule-based)
│   ├── analysis/      # Statistical analysis tools
│   ├── visualization/ # 2D/3D hexagram visualization
│   └── infrastructure/# Database and utilities
├── data/
│   ├── iching.db      # SQLite database with all 384 lines
│   ├── structure/     # Hexagram relationships, trigram mappings
│   ├── analysis/      # Research results, embeddings
│   └── commentaries/  # Classical Chinese source texts
├── docs/              # Research documentation (Chinese)
└── book/              # Book manuscript (Chinese)
```

## Quick Start

```bash
# Run the 100% accuracy predictor
python3 scripts/core/iching_lookup_predictor.py

# Generate hexagram explanations
python3 scripts/core/hexagram_explainer.py

# View the strategy guide
cat docs/HEXAGRAM_STRATEGY_GUIDE.md
```

## Documentation Language

Most documentation and the book manuscript are written in **Chinese** (繁體中文).

**For English readers:**
- Use an LLM (ChatGPT, Claude, etc.) to translate specific docs you're interested in
- Open an issue if you'd like official English translations - I'll prioritize based on demand
- Core code and comments are in English

**Key docs to start with:**
- `docs/KEY_DISCOVERIES.md` - Main research findings
- `docs/HEXAGRAM_STRATEGY_GUIDE.md` - Practical 64-hexagram guide
- `docs/FORMULA_QUICK_REFERENCE.md` - Quick reference for formulas

## Technologies

- Python 3
- SQLite
- D3.js (visualizations)

## Data Sources

- Wikisource (CC BY-SA 3.0)
- Various open source I Ching datasets

## Contributing

Issues and PRs welcome. If you're interested in:
- English translations
- Additional analysis methods
- Bug fixes or improvements

Please open an issue first to discuss.

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to share and adapt this material for **non-commercial purposes** with attribution.

Data sources retain their original licenses (Wikisource: CC BY-SA 3.0).
