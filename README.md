# I Ching Pattern Analysis Research

Reverse-engineering the I Ching (易經) using computational methods and AI-assisted pattern recognition.

## What We Discovered

After analyzing all 384 lines of the I Ching as data, we found patterns that **contradict 2000 years of traditional interpretation**:

### "无咎" (No Blame) Doesn't Mean Good Fortune
Traditional view: 无咎 = auspicious
**Data shows**: Only 28% fortune (吉), 65% neutral (中)

### "Being Steadfast" (貞) Can Be Dangerous
Traditional view: 貞 (righteousness/persistence) always leads to fortune
**Data shows**: 16% of 貞 combinations are actually 凶 (misfortune)
- 恆卦初六「浚恆，貞凶」— excessive persistence brings misfortune
- 節卦上六「苦節，貞凶」— excessive restraint brings misfortune

### Position 4 is NOT the "Dangerous Position"
Traditional view: "四多懼" — the 4th line is fearful/dangerous
**Data shows**: Position 4 has the **highest** 无咎 rate (22.2%) — it's actually the best position for recovery

### The Core Message: Change = Good
```
易 = Change
能變 = Fortune
不變 = Misfortune
```
Data proof:
- Staying in a bad position: **0%** fortune rate
- Actively changing from a bad position: **44%** average fortune rate among neighbors

**The I Ching is not about predicting your fate — it's about knowing when and how to change.**

### The Direction Map: Where Should You Go?

We built a complete navigation system for all 64 hexagrams:

| Category | Meaning | Action |
|----------|---------|--------|
| 吸引子 (Attractor) | Good here, worse if you leave | **Stay** |
| 排斥子 (Repeller) | Bad here, better if you leave | **Leave** |
| 福地 (Blessed Land) | High fortune rate | **Maintain** |
| 困境 (Difficult) | Low fortune rate | **Change** |
| 陷阱 (Trap) | Bad here, neighbors also bad | **Choose carefully** |

For each hexagram, we provide:
- Current fortune rate
- Neighbor average (what happens if you change)
- Recommended path (which hexagram to transition to)
- Which line to change for best outcome

Example: **師卦 (7)** → 17% fortune, neighbors average 44%
- Recommendation: **Leave**
- Best path: 師 → 臨 (change line 6 → 83% fortune)

### Interactive 8×8 Heatmap

Open `docs/visualization.html` or `data/trigram_matrix.html` to see the fortune distribution across all 64 hexagrams as an interactive heatmap.

---

## Technical Achievement

**100% accuracy** in predicting fortune labels (吉/中/凶) for all 384 lines using:
- Conditional phrase parsing (highest priority)
- Keyword reliability scoring (无咎, 吝, etc. have different weights)
- 3D lookup table: `LOOKUP[inner_trigram, outer_trigram, position]`

Key insight: Fortune is **not** a linear formula — it's a non-linear interaction between trigrams and position.

## Project Structure

```
iching/
├── scripts/           # 26 analysis scripts
│   ├── core/          # Predictors (100% lookup, 90.6% rule-based)
│   ├── analysis/      # Statistical analysis
│   ├── visualization/ # 2D/3D visualization
│   └── infrastructure/# Database utilities
├── data/
│   ├── iching.db      # SQLite database (384 lines)
│   ├── structure/     # Hexagram relationships
│   └── commentaries/  # Classical Chinese texts
├── docs/              # Research documentation (Chinese)
└── book/              # Book manuscript (Chinese)
```

## Quick Start

```bash
python3 scripts/core/iching_lookup_predictor.py   # 100% accuracy predictor
python3 scripts/core/hexagram_explainer.py        # Plain language explanations
```

## Documentation

Most docs are in **Chinese** (繁體中文). For English readers:
- Use an LLM to translate docs you're interested in
- Open an issue for translation requests — I'll prioritize based on demand

**Key docs:**
- `docs/KEY_DISCOVERIES.md` — Main findings
- `docs/HEXAGRAM_STRATEGY_GUIDE.md` — Practical 64-hexagram guide

## License

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) — Non-commercial use with attribution.

For commercial licensing, please contact me.
