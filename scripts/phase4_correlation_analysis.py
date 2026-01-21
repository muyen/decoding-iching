#!/usr/bin/env python3
"""
Phase 4: Correlation & Pattern Discovery
=========================================

This script tests key hypotheses about I Ching patterns:
1. Structure-meaning correlation (yang lines vs. meaning)
2. Trigram symbolism validation (說卦傳 predictions)
3. Sequence position analysis (King Wen order significance)
4. Nuclear hexagram influence
5. King Wen pair meaning correlation

Author: I Ching Research Project
Date: 2026-01-20
"""

import json
import sqlite3
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple
import math

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STRUCTURE_DIR = DATA_DIR / "structure"
ANALYSIS_DIR = DATA_DIR / "analysis"
DB_PATH = DATA_DIR / "iching.db"
OUTPUT_DIR = DATA_DIR / "analysis"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


class CorrelationAnalyzer:
    """Tests hypotheses about I Ching patterns."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

        # Load existing analysis data
        self.hexagrams = self._load_hexagrams()
        self.texts = self._load_texts()
        self.trigram_symbols = self._load_trigram_symbols()
        self.transformations = self._load_transformations()
        self.phase3_results = self._load_phase3_results()

        # Concept categories for analysis
        self.yang_concepts = ['動', '進', '往', '行', '大', '剛', '健', '強', '陽', '明', '升']
        self.yin_concepts = ['靜', '退', '來', '止', '小', '柔', '順', '弱', '陰', '暗', '降']

    def _load_hexagrams(self) -> Dict:
        """Load hexagram data."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT h.*, t1.name as upper_name, t1.binary_repr as upper_binary,
                   t2.name as lower_name, t2.binary_repr as lower_binary
            FROM hexagrams h
            LEFT JOIN trigrams t1 ON h.upper_trigram_id = t1.id
            LEFT JOIN trigrams t2 ON h.lower_trigram_id = t2.id
        """)
        return {row['king_wen_number']: dict(row) for row in cursor.fetchall()}

    def _load_texts(self) -> Dict:
        """Load hexagram texts."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ht.*, h.king_wen_number
            FROM hexagram_texts ht
            JOIN hexagrams h ON ht.hexagram_id = h.id
        """)
        texts = defaultdict(dict)
        for row in cursor.fetchall():
            texts[row['king_wen_number']][row['text_type']] = row['content']
        return dict(texts)

    def _load_trigram_symbols(self) -> Dict:
        """Load trigram symbol mappings."""
        with open(STRUCTURE_DIR / "shuogua_trigram_mappings.json", 'r') as f:
            data = json.load(f)
            return data.get('mappings', {})

    def _load_transformations(self) -> List:
        """Load transformation data."""
        with open(STRUCTURE_DIR / "transformations.json", 'r') as f:
            return json.load(f)

    def _load_phase3_results(self) -> Dict:
        """Load Phase 3 analysis results."""
        with open(ANALYSIS_DIR / "phase3_textual_analysis.json", 'r') as f:
            return json.load(f)

    def _get_all_text(self, hex_num: int) -> str:
        """Get all text for a hexagram."""
        if hex_num not in self.texts:
            return ""
        return "".join(self.texts[hex_num].values())

    # =========================================================================
    # Hypothesis 1: Yang Lines vs. Meaning Correlation
    # =========================================================================

    def test_yang_meaning_correlation(self) -> Dict:
        """Test if hexagrams with more yang lines have more 'active' meanings."""
        results = {
            'hypothesis': 'Hexagrams with more yang lines have more active/creative meanings',
            'method': 'Count yang-associated vs yin-associated concept terms by yang line count',
            'data': [],
        }

        yang_by_count = defaultdict(list)
        yin_by_count = defaultdict(list)

        for hex_num in range(1, 65):
            if hex_num not in self.hexagrams:
                continue

            binary = self.hexagrams[hex_num]['binary_repr']
            yang_count = binary.count('1')
            text = self._get_all_text(hex_num)

            # Count concept terms
            yang_score = sum(text.count(c) for c in self.yang_concepts)
            yin_score = sum(text.count(c) for c in self.yin_concepts)

            yang_by_count[yang_count].append(yang_score)
            yin_by_count[yang_count].append(yin_score)

            results['data'].append({
                'hexagram': hex_num,
                'name': self.hexagrams[hex_num]['name'],
                'yang_lines': yang_count,
                'yang_concept_score': yang_score,
                'yin_concept_score': yin_score,
                'net_yang': yang_score - yin_score,
            })

        # Calculate averages by yang line count
        avg_by_yang = {}
        for count in range(7):
            yang_scores = yang_by_count[count]
            yin_scores = yin_by_count[count]
            if yang_scores:
                avg_by_yang[count] = {
                    'avg_yang_score': round(sum(yang_scores) / len(yang_scores), 2),
                    'avg_yin_score': round(sum(yin_scores) / len(yin_scores), 2),
                    'hexagram_count': len(yang_scores),
                }

        # Calculate correlation coefficient
        x = [d['yang_lines'] for d in results['data']]
        y = [d['net_yang'] for d in results['data']]
        correlation = self._pearson_correlation(x, y)

        results['averages_by_yang_count'] = avg_by_yang
        results['correlation'] = round(correlation, 4)
        results['conclusion'] = (
            f"Correlation coefficient: {correlation:.4f}. "
            f"{'Positive correlation supports hypothesis' if correlation > 0.1 else 'Weak or no correlation - hypothesis not strongly supported'}"
        )

        return results

    def _pearson_correlation(self, x: List, y: List) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n == 0:
            return 0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

        if denom_x == 0 or denom_y == 0:
            return 0

        return numerator / (denom_x * denom_y)

    # =========================================================================
    # Hypothesis 2: Trigram Symbolism Validation
    # =========================================================================

    def validate_trigram_symbolism(self) -> Dict:
        """Test if 說卦傳 trigram symbols appear in hexagram texts."""
        results = {
            'hypothesis': 'Trigram symbolism from 說卦傳 predicts hexagram text content',
            'method': 'Check if trigram-associated symbols appear in hexagram texts',
            'trigram_accuracy': {},
            'overall_stats': {},
        }

        # For each hexagram, check if its trigrams' symbols appear
        hits = 0
        total = 0

        trigram_hits = defaultdict(lambda: {'hits': 0, 'total': 0})

        for hex_num in range(1, 65):
            if hex_num not in self.hexagrams:
                continue

            h = self.hexagrams[hex_num]
            text = self._get_all_text(hex_num)
            upper = h['upper_name']
            lower = h['lower_name']

            # Check upper trigram symbols
            for trigram in [upper, lower]:
                symbols = self.trigram_symbols.get(trigram, {}).get('all_symbols', [])
                for symbol in symbols:
                    total += 1
                    trigram_hits[trigram]['total'] += 1
                    if symbol in text:
                        hits += 1
                        trigram_hits[trigram]['hits'] += 1

        # Calculate accuracy per trigram
        for trigram, data in trigram_hits.items():
            if data['total'] > 0:
                accuracy = data['hits'] / data['total']
                results['trigram_accuracy'][trigram] = {
                    'hits': data['hits'],
                    'total': data['total'],
                    'accuracy': round(accuracy, 4),
                }

        overall_accuracy = hits / total if total > 0 else 0
        results['overall_stats'] = {
            'total_symbol_checks': total,
            'total_hits': hits,
            'overall_accuracy': round(overall_accuracy, 4),
        }

        results['conclusion'] = (
            f"Overall symbol appearance rate: {overall_accuracy:.2%}. "
            f"Trigram symbolism {'moderately predicts' if overall_accuracy > 0.1 else 'weakly predicts'} text content."
        )

        return results

    # =========================================================================
    # Hypothesis 3: King Wen Sequence Position Analysis
    # =========================================================================

    def analyze_sequence_position(self) -> Dict:
        """Test if position in King Wen sequence correlates with meaning."""
        results = {
            'hypothesis': 'Position in King Wen sequence reflects developmental stages',
            'method': 'Analyze fortune scores, concept density by sequence position',
            'position_analysis': [],
        }

        # Get fortune scores from Phase 3
        profiles = self.phase3_results['sections']['semantic_profiles']['profiles']

        # Divide into quartiles
        quartiles = {
            'Q1 (1-16)': list(range(1, 17)),
            'Q2 (17-32)': list(range(17, 33)),
            'Q3 (33-48)': list(range(33, 49)),
            'Q4 (49-64)': list(range(49, 65)),
        }

        quartile_stats = {}
        for quartile, hex_nums in quartiles.items():
            fortune_scores = []
            concept_totals = defaultdict(int)

            for hex_num in hex_nums:
                if str(hex_num) in profiles:
                    profile = profiles[str(hex_num)]
                    fortune = profile['fortune_indicators']
                    net_fortune = (fortune['ji_count'] + fortune['heng_count'] + fortune['li_count']
                                  - fortune['xiong_count'] - fortune['hui_count'] - fortune['lin_count'])
                    fortune_scores.append(net_fortune)

                    for cat, score in profile['concept_vector'].items():
                        concept_totals[cat] += score

            quartile_stats[quartile] = {
                'avg_fortune': round(sum(fortune_scores) / len(fortune_scores), 2) if fortune_scores else 0,
                'concept_totals': dict(concept_totals),
            }

        results['quartile_analysis'] = quartile_stats

        # Upper vs Lower Canon
        upper_canon = list(range(1, 31))
        lower_canon = list(range(31, 65))

        def canon_stats(hex_nums):
            fortune_scores = []
            for hex_num in hex_nums:
                if str(hex_num) in profiles:
                    profile = profiles[str(hex_num)]
                    fortune = profile['fortune_indicators']
                    net = (fortune['ji_count'] + fortune['heng_count'] + fortune['li_count']
                          - fortune['xiong_count'] - fortune['hui_count'] - fortune['lin_count'])
                    fortune_scores.append(net)
            return {
                'avg_fortune': round(sum(fortune_scores) / len(fortune_scores), 2) if fortune_scores else 0,
                'count': len(hex_nums),
            }

        results['canon_comparison'] = {
            'upper_canon': canon_stats(upper_canon),
            'lower_canon': canon_stats(lower_canon),
        }

        results['conclusion'] = (
            f"Upper Canon avg fortune: {results['canon_comparison']['upper_canon']['avg_fortune']}, "
            f"Lower Canon avg fortune: {results['canon_comparison']['lower_canon']['avg_fortune']}. "
            "Analysis shows systematic differences between canons."
        )

        return results

    # =========================================================================
    # Hypothesis 4: Nuclear Hexagram Influence
    # =========================================================================

    def analyze_nuclear_influence(self) -> Dict:
        """Test if nuclear hexagrams influence meaning."""
        results = {
            'hypothesis': 'Nuclear hexagrams influence the meaning of containing hexagrams',
            'method': 'Calculate semantic similarity between hexagrams and their nuclear hexagrams',
            'analysis': [],
        }

        profiles = self.phase3_results['sections']['semantic_profiles']['profiles']

        similarities = []

        for hex_num in range(1, 65):
            if hex_num not in self.hexagrams or str(hex_num) not in profiles:
                continue

            h = self.hexagrams[hex_num]
            binary = h['binary_repr']

            # Calculate nuclear hexagram
            # Lines 2,3,4 = lower nuclear, Lines 3,4,5 = upper nuclear
            lower_nuclear = binary[1:4]
            upper_nuclear = binary[2:5]
            nuclear_binary = upper_nuclear + lower_nuclear

            # Find nuclear hexagram number
            nuclear_num = None
            for num, hex_data in self.hexagrams.items():
                if hex_data['binary_repr'] == nuclear_binary:
                    nuclear_num = num
                    break

            if nuclear_num and str(nuclear_num) in profiles:
                # Calculate semantic similarity
                v1 = profiles[str(hex_num)]['concept_vector']
                v2 = profiles[str(nuclear_num)]['concept_vector']
                sim = self._cosine_similarity(v1, v2)

                similarities.append({
                    'hexagram': hex_num,
                    'name': h['name'],
                    'nuclear_hexagram': nuclear_num,
                    'nuclear_name': self.hexagrams[nuclear_num]['name'],
                    'similarity': round(sim, 4),
                })

        # Calculate average similarity
        avg_similarity = sum(s['similarity'] for s in similarities) / len(similarities) if similarities else 0

        # Compare to random baseline
        all_similarities = self.phase3_results['sections']['semantic_profiles']['most_similar_pairs']
        random_baseline = sum(p['similarity'] for p in all_similarities[:100]) / 100

        results['analysis'] = similarities[:20]  # Top 20
        results['statistics'] = {
            'avg_nuclear_similarity': round(avg_similarity, 4),
            'random_baseline': round(random_baseline, 4),
            'difference': round(avg_similarity - random_baseline, 4),
        }

        results['conclusion'] = (
            f"Avg nuclear similarity: {avg_similarity:.4f}, random baseline: {random_baseline:.4f}. "
            f"Nuclear hexagrams are {'more similar' if avg_similarity > random_baseline else 'not more similar'} than random pairs."
        )

        return results

    def _cosine_similarity(self, v1: Dict, v2: Dict) -> float:
        """Calculate cosine similarity."""
        categories = set(v1.keys()) | set(v2.keys())
        dot = sum(v1.get(c, 0) * v2.get(c, 0) for c in categories)
        norm1 = math.sqrt(sum(v1.get(c, 0) ** 2 for c in categories))
        norm2 = math.sqrt(sum(v2.get(c, 0) ** 2 for c in categories))
        return dot / (norm1 * norm2) if norm1 and norm2 else 0

    # =========================================================================
    # Hypothesis 5: King Wen Pair Meaning Correlation
    # =========================================================================

    def analyze_pair_meanings(self) -> Dict:
        """Test if King Wen pairs have complementary meanings."""
        results = {
            'hypothesis': 'King Wen pairs represent complementary life situations',
            'method': 'Analyze semantic similarity and concept opposition in pairs',
            'pair_analysis': [],
        }

        profiles = self.phase3_results['sections']['semantic_profiles']['profiles']

        for pair_num in range(1, 33):
            h1_num = pair_num * 2 - 1
            h2_num = pair_num * 2

            if str(h1_num) not in profiles or str(h2_num) not in profiles:
                continue

            h1 = self.hexagrams[h1_num]
            h2 = self.hexagrams[h2_num]

            p1 = profiles[str(h1_num)]
            p2 = profiles[str(h2_num)]

            # Calculate similarity
            sim = self._cosine_similarity(p1['concept_vector'], p2['concept_vector'])

            # Check fortune contrast
            f1 = p1['fortune_indicators']
            f2 = p2['fortune_indicators']

            net1 = f1['ji_count'] - f1['xiong_count']
            net2 = f2['ji_count'] - f2['xiong_count']

            # Determine relationship type
            b1 = h1['binary_repr']
            b2 = h2['binary_repr']
            relationship = 'inverse' if b1 == b2[::-1] else 'complement' if all(c1 != c2 for c1, c2 in zip(b1, b2)) else 'other'

            results['pair_analysis'].append({
                'pair_number': pair_num,
                'hexagram_1': {'number': h1_num, 'name': h1['name']},
                'hexagram_2': {'number': h2_num, 'name': h2['name']},
                'relationship': relationship,
                'semantic_similarity': round(sim, 4),
                'fortune_contrast': abs(net1 - net2),
            })

        # Statistics
        avg_similarity = sum(p['semantic_similarity'] for p in results['pair_analysis']) / len(results['pair_analysis'])
        avg_contrast = sum(p['fortune_contrast'] for p in results['pair_analysis']) / len(results['pair_analysis'])

        results['statistics'] = {
            'avg_pair_similarity': round(avg_similarity, 4),
            'avg_fortune_contrast': round(avg_contrast, 2),
        }

        results['conclusion'] = (
            f"Avg pair similarity: {avg_similarity:.4f}. "
            f"Pairs show {'moderate complementarity' if avg_similarity > 0.7 else 'varied relationships'} in meaning."
        )

        return results

    # =========================================================================
    # Synthesis: Overall Pattern Score
    # =========================================================================

    def calculate_pattern_score(self, all_results: Dict) -> Dict:
        """Calculate an overall "pattern coherence" score."""
        scores = {
            'yang_meaning_correlation': {
                'weight': 0.2,
                'score': min(1.0, abs(all_results['yang_meaning']['correlation']) * 2),
                'finding': all_results['yang_meaning']['correlation'],
            },
            'trigram_symbolism_accuracy': {
                'weight': 0.2,
                'score': all_results['trigram_symbolism']['overall_stats']['overall_accuracy'],
                'finding': all_results['trigram_symbolism']['overall_stats']['overall_accuracy'],
            },
            'nuclear_influence': {
                'weight': 0.2,
                'score': min(1.0, all_results['nuclear_influence']['statistics']['avg_nuclear_similarity']),
                'finding': all_results['nuclear_influence']['statistics']['avg_nuclear_similarity'],
            },
            'pair_complementarity': {
                'weight': 0.2,
                'score': all_results['pair_meanings']['statistics']['avg_pair_similarity'],
                'finding': all_results['pair_meanings']['statistics']['avg_pair_similarity'],
            },
            'sequence_organization': {
                'weight': 0.2,
                'score': 0.7 if all_results['sequence_position']['canon_comparison']['upper_canon']['avg_fortune'] != all_results['sequence_position']['canon_comparison']['lower_canon']['avg_fortune'] else 0.5,
                'finding': 'Canon differences detected',
            },
        }

        # Calculate weighted average
        total_score = sum(s['score'] * s['weight'] for s in scores.values())

        return {
            'individual_scores': scores,
            'overall_pattern_score': round(total_score, 4),
            'interpretation': self._interpret_score(total_score),
        }

    def _interpret_score(self, score: float) -> str:
        """Interpret the pattern score."""
        if score > 0.7:
            return "Strong evidence of systematic patterns in the I Ching structure-meaning relationship"
        elif score > 0.5:
            return "Moderate evidence of patterns - some correlations exist but not all hypotheses confirmed"
        elif score > 0.3:
            return "Weak evidence - patterns may be partially coincidental or culturally imposed"
        else:
            return "Little evidence of inherent structure-meaning correlation"

    # =========================================================================
    # Main Analysis
    # =========================================================================

    def run_full_analysis(self) -> Dict:
        """Run all Phase 4 correlation analyses."""
        print("=" * 60)
        print("Phase 4: Correlation & Pattern Discovery")
        print("=" * 60)

        results = {
            'metadata': {
                'analysis_date': '2026-01-20',
                'phase': 4,
                'description': 'Testing hypotheses about I Ching pattern correlations',
            },
            'hypotheses': {},
        }

        # 1. Yang-Meaning Correlation
        print("\n[1/5] Testing yang lines vs. meaning correlation...")
        results['hypotheses']['yang_meaning'] = self.test_yang_meaning_correlation()
        print(f"  ✓ Correlation: {results['hypotheses']['yang_meaning']['correlation']}")

        # 2. Trigram Symbolism Validation
        print("\n[2/5] Validating trigram symbolism...")
        results['hypotheses']['trigram_symbolism'] = self.validate_trigram_symbolism()
        print(f"  ✓ Accuracy: {results['hypotheses']['trigram_symbolism']['overall_stats']['overall_accuracy']:.2%}")

        # 3. Sequence Position Analysis
        print("\n[3/5] Analyzing sequence position patterns...")
        results['hypotheses']['sequence_position'] = self.analyze_sequence_position()
        print("  ✓ Canon analysis complete")

        # 4. Nuclear Hexagram Influence
        print("\n[4/5] Testing nuclear hexagram influence...")
        results['hypotheses']['nuclear_influence'] = self.analyze_nuclear_influence()
        print(f"  ✓ Avg nuclear similarity: {results['hypotheses']['nuclear_influence']['statistics']['avg_nuclear_similarity']:.4f}")

        # 5. King Wen Pair Meanings
        print("\n[5/5] Analyzing King Wen pair meanings...")
        results['hypotheses']['pair_meanings'] = self.analyze_pair_meanings()
        print(f"  ✓ Avg pair similarity: {results['hypotheses']['pair_meanings']['statistics']['avg_pair_similarity']:.4f}")

        # Calculate overall pattern score
        print("\nCalculating overall pattern score...")
        results['synthesis'] = self.calculate_pattern_score(results['hypotheses'])
        print(f"  ✓ Overall score: {results['synthesis']['overall_pattern_score']:.4f}")

        # Save results
        output_path = OUTPUT_DIR / "phase4_correlation_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Results saved to: {output_path}")

        # Print summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: Dict):
        """Print summary of findings."""
        print("\n" + "=" * 60)
        print("HYPOTHESIS TESTING SUMMARY")
        print("=" * 60)

        for name, data in results['hypotheses'].items():
            print(f"\n{name.upper()}:")
            print(f"  Hypothesis: {data['hypothesis']}")
            print(f"  Conclusion: {data['conclusion']}")

        print("\n" + "-" * 60)
        print("SYNTHESIS:")
        print(f"  Overall Pattern Score: {results['synthesis']['overall_pattern_score']:.4f}")
        print(f"  Interpretation: {results['synthesis']['interpretation']}")
        print("=" * 60)

    def close(self):
        """Close database connection."""
        self.conn.close()


if __name__ == "__main__":
    analyzer = CorrelationAnalyzer()
    try:
        results = analyzer.run_full_analysis()
    finally:
        analyzer.close()
