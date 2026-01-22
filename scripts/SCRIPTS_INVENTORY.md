# Scripts Inventory

## KEEP - Core Analysis (Essential)

| Script | Purpose | Status |
|--------|---------|--------|
| `iching_lookup_predictor.py` | 100% accuracy predictor | ✅ Verified |
| `deep_graph_analysis.py` | Graph theory, attractors/repellers | ✅ Verified |
| `generate_strategy_guide.py` | 64-hexagram strategy guide | ✅ Verified |
| `cuozong_graph_analysis.py` | 錯綜卦 analysis | ✅ Verified |
| `hexagram_explainer.py` | Plain Chinese explanations | ✅ Keep |
| `hexagram_chemistry.py` | Trigram interaction model | ✅ Keep |

## KEEP - Data Infrastructure

| Script | Purpose |
|--------|---------|
| `create_database.py` | SQLite database creation |
| `analysis_tools.py` | Common utilities |
| `generate_hexagram_structure.py` | Structure JSON |
| `generate_embeddings.py` | Text embeddings |
| `extract_yizhuan.py` | Ten Wings extraction |
| `extract_shuogua_mappings.py` | Trigram mappings |

## KEEP - Phase Analysis

| Script | Purpose |
|--------|---------|
| `phase2_structural_analysis.py` | Structural analysis |
| `phase3_textual_analysis.py` | Textual analysis |
| `phase4_correlation_analysis.py` | Correlation analysis |
| `phase5_synthesis.py` | Synthesis |

## KEEP - Downloads

| Script | Purpose |
|--------|---------|
| `download_wikisource_*.py` | Commentary downloads |
| `create_mawangdui_sequence.py` | Mawangdui data |

## CAN DELETE - Formula Iterations (Superseded)

These were iterations leading to final predictor:
- `formula_v3_test.py` through `formula_v17_ml.py` (15 files)

## CAN DELETE - Exploratory (One-time use)

- `advanced_*.py` - Exploratory analysis
- `reverse_engineer*.py` - Exploration phase
- Various pattern exploration scripts

## CAN ARCHIVE - Useful but not essential

- `physics_analogy_analysis.py` - Quantum speculation
- `validate_yilin.py` - Jiaoshi Yilin (disproven)
- Various visualization scripts

---

## Summary

| Category | Count | Action |
|----------|-------|--------|
| Essential | ~15 | Keep |
| Infrastructure | ~10 | Keep |
| Phase Analysis | 4 | Keep |
| Downloads | 5 | Keep |
| Formula iterations | 15 | Delete |
| Exploratory | ~50 | Delete/Archive |

**Recommended: Keep ~35 scripts, delete/archive ~73**
