# Scripts Inventory

**Total: 21 scripts in 4 folders**

---

## core/ (8 scripts)

Main predictors and analysis tools.

| Script | Purpose |
|--------|---------|
| `rule_based_predictor.py` | Rule-based predictor (90.6% accuracy) |
| `iching_lookup_predictor.py` | Lookup predictor (100% accuracy) |
| `hexagram_explainer.py` | Plain Chinese explanations |
| `hexagram_chemistry.py` | Trigram interaction model |
| `deep_graph_analysis.py` | Graph theory, attractors/repellers |
| `cuozong_graph_analysis.py` | 錯綜卦 network analysis |
| `biangua_analysis.py` | 變卦 (single-line change) analysis |
| `generate_strategy_guide.py` | Generate 64-hexagram strategy doc |

---

## analysis/ (4 scripts)

Phase-based analysis pipeline.

| Script | Purpose |
|--------|---------|
| `phase2_structural_analysis.py` | Structural analysis |
| `phase3_textual_analysis.py` | Textual analysis |
| `phase4_correlation_analysis.py` | Correlation analysis |
| `phase5_synthesis.py` | Synthesis |

---

## visualization/ (3 scripts)

Visualization tools.

| Script | Purpose |
|--------|---------|
| `visualize_hexagrams.py` | 2D hexagram visualization |
| `visualization_3d.py` | 3D visualization |
| `pattern_visualization.py` | Pattern charts |

---

## infrastructure/ (6 scripts)

Data infrastructure and utilities.

| Script | Purpose |
|--------|---------|
| `create_database.py` | SQLite database creation |
| `analysis_tools.py` | Common utilities |
| `generate_hexagram_structure.py` | Generate structure JSON |
| `generate_embeddings.py` | Text embeddings |
| `extract_shuogua_mappings.py` | Trigram mappings from 說卦傳 |
| `create_mawangdui_sequence.py` | Mawangdui sequence data |

---

## Deleted (81 scripts)

- **Data fetching** (7): download_*.py, scrape_*.py, extract_zhouyi.py, extract_yizhuan.py
- **Formula iterations** (16): formula_v3 through v17, improved_formula_test
- **Exploratory** (58): One-time analysis scripts used during research
