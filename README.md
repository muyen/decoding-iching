# I Ching Pattern Analysis Research Project

Using AI and computational methods to decode the underlying patterns in the I Ching (易經).

## Project Goal

Discover the mathematical structures and core meanings in the I Ching that have been obscured by 2000+ years of classical Chinese (文言文) commentary.

## Key Findings

### Overall Pattern Score: 0.5484 (Moderate Evidence)

Evidence that I Ching meanings are systematically related to hexagram structure.

### Validated Hypotheses

| Hypothesis | Evidence | Confidence |
|------------|----------|------------|
| Nuclear hexagrams (互卦) influence meaning | 0.7315 vs 0.1930 baseline | **95%** |
| King Wen pairs are complementary | 0.7565 similarity | 85% |
| Yang lines correlate with active meanings | r=0.2769 | 70% |
| Upper/Lower canon thematic division | Fortune score difference | 75% |

### The I Ching Algorithm v1.0

```
INPUT: 6-bit binary hexagram (e.g., "111000")

STEPS:
1. Yang Count → Activity level
2. Nuclear Hexagram → Inner nature (STRONGEST predictor)
3. King Wen Pair → Complementary context
4. Canon Position → Cosmic vs human domain
5. Trigram Analysis → Archetypal context
6. Symmetry Check → Special properties

OUTPUT: Predicted meaning domain
```

## Data Summary

| Category | Count |
|----------|-------|
| Hexagrams | 64 |
| Trigrams | 8 |
| Lines (爻) | 384 |
| Commentary characters | 500K+ |
| Trigram symbols | 112 |
| Analysis scripts | 17 |

## Quick Start

```bash
# View interactive hexagram grid
open data/hexagram_visualization.html

# View research findings
open data/discovery_visualization.html

# Run analysis
python3 scripts/phase2_structural_analysis.py
python3 scripts/phase3_textual_analysis.py
python3 scripts/phase4_correlation_analysis.py
python3 scripts/phase5_synthesis.py
```

## Project Structure

```
iching/
├── data/
│   ├── structure/           # Hexagram relationships, trigrams
│   ├── analysis/            # Phase 2-5 results, embeddings
│   ├── commentaries/        # Classical Chinese texts
│   ├── yizhuan/             # Ten Wings texts
│   └── iching.db            # SQLite database
├── scripts/                 # Analysis Python scripts
└── docs/
    ├── INVENTORY.md         # Complete data inventory
    └── RESEARCH_PLAN.md     # Research methodology & findings
```

## Key Files

| File | Description |
|------|-------------|
| `data/analysis/iching_algorithm.json` | Formal algorithm specification |
| `data/analysis/findings_report.json` | Comprehensive research report |
| `data/structure/hexagrams_structure.json` | All 64 hexagrams with relationships |
| `data/structure/shuogua_trigram_mappings.json` | 112 trigram symbol associations |
| `data/structure/hetu_luoshu.json` | River Chart & Luo Writing |
| `data/discovery_visualization.html` | Interactive findings display |

## Unexpected Discoveries

1. **Zero Fu Xi/King Wen overlap** - Not a single hexagram in same position
2. **蹇 (Obstruction) ranks fortunate** - Texts emphasize overcoming difficulty
3. **Zero graph clustering** - Transformation graph has unique mathematical properties

## Technologies

- Python 3 (analysis scripts)
- SQLite (database)
- D3.js (visualizations)
- HTML/CSS (interactive displays)

## Documentation

- [INVENTORY.md](docs/INVENTORY.md) - Complete data inventory
- [RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md) - Full research plan and findings

## License

Data from Wikisource: CC BY-SA 3.0
GitHub repositories: Various open source licenses
