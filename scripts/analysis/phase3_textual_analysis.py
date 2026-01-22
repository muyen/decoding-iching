#!/usr/bin/env python3
"""
Phase 3: Textual Analysis of I Ching Hexagrams
==============================================

This script performs comprehensive textual analysis:
1. Character frequency and pattern analysis
2. Key concept extraction
3. Semantic profiling per hexagram
4. Cross-text pattern detection
5. Recurring phrase identification

Author: I Ching Research Project
Date: 2026-01-20
"""

import json
import sqlite3
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STRUCTURE_DIR = DATA_DIR / "structure"
DB_PATH = DATA_DIR / "iching.db"
OUTPUT_DIR = DATA_DIR / "analysis"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


class TextualAnalyzer:
    """Comprehensive textual analysis of I Ching texts."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

        # Key concept categories for I Ching analysis
        self.concept_categories = {
            'fortune': ['吉', '凶', '悔', '吝', '咎', '厲', '亨', '利', '元'],
            'action': ['往', '來', '行', '止', '進', '退', '動', '靜'],
            'virtue': ['德', '正', '中', '貞', '誠', '信', '仁', '義'],
            'nature': ['天', '地', '日', '月', '風', '雷', '水', '火', '山', '澤'],
            'person': ['君子', '小人', '大人', '王', '侯', '士', '民'],
            'time': ['初', '終', '始', '時', '日', '年', '久'],
            'position': ['上', '下', '中', '內', '外', '左', '右'],
            'state': ['大', '小', '盛', '衰', '安', '危', '得', '失'],
        }

        # Load hexagram data
        self.hexagrams = self._load_hexagrams()
        self.texts = self._load_all_texts()
        self.trigram_symbols = self._load_trigram_symbols()

    def _load_hexagrams(self) -> Dict:
        """Load hexagram information."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT h.*, t1.name as upper_name, t2.name as lower_name
            FROM hexagrams h
            LEFT JOIN trigrams t1 ON h.upper_trigram_id = t1.id
            LEFT JOIN trigrams t2 ON h.lower_trigram_id = t2.id
        """)
        return {row['king_wen_number']: dict(row) for row in cursor.fetchall()}

    def _load_all_texts(self) -> Dict:
        """Load all hexagram texts."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ht.*, h.king_wen_number, h.name as hexagram_name
            FROM hexagram_texts ht
            JOIN hexagrams h ON ht.hexagram_id = h.id
        """)

        texts = defaultdict(dict)
        for row in cursor.fetchall():
            texts[row['king_wen_number']][row['text_type']] = {
                'content': row['content'],
                'source': row['source'],
            }
        return dict(texts)

    def _load_trigram_symbols(self) -> Dict:
        """Load trigram symbol associations."""
        with open(STRUCTURE_DIR / "shuogua_trigram_mappings.json", 'r') as f:
            data = json.load(f)
            return data.get('mappings', {})

    # =========================================================================
    # Part 1: Character Frequency Analysis
    # =========================================================================

    def analyze_character_frequency(self) -> Dict:
        """Analyze character frequency across all texts."""
        all_text = ""
        text_by_type = defaultdict(str)

        for hex_num, texts in self.texts.items():
            for text_type, text_data in texts.items():
                content = text_data['content'] or ""
                all_text += content
                text_by_type[text_type] += content

        # Overall frequency
        overall_freq = Counter(all_text)

        # Remove punctuation and numbers
        chinese_chars = {c: count for c, count in overall_freq.items()
                        if '\u4e00' <= c <= '\u9fff'}

        # Frequency by text type
        freq_by_type = {}
        for text_type, text in text_by_type.items():
            type_freq = Counter(text)
            chinese_only = {c: count for c, count in type_freq.items()
                          if '\u4e00' <= c <= '\u9fff'}
            freq_by_type[text_type] = dict(Counter(chinese_only).most_common(50))

        # Find characters unique to each text type
        unique_chars = {}
        for text_type in freq_by_type:
            other_chars = set()
            for other_type, chars in freq_by_type.items():
                if other_type != text_type:
                    other_chars.update(chars.keys())
            unique = {c for c in freq_by_type[text_type] if c not in other_chars}
            unique_chars[text_type] = list(unique)[:20]

        return {
            'title': 'Character Frequency Analysis',
            'total_characters': sum(chinese_chars.values()),
            'unique_characters': len(chinese_chars),
            'top_50_overall': dict(Counter(chinese_chars).most_common(50)),
            'frequency_by_text_type': freq_by_type,
            'unique_by_text_type': unique_chars,
            'insights': [
                f"Total Chinese characters analyzed: {sum(chinese_chars.values())}",
                f"Unique characters used: {len(chinese_chars)}",
            ],
        }

    # =========================================================================
    # Part 2: Concept Extraction
    # =========================================================================

    def extract_concepts(self) -> Dict:
        """Extract key concepts from hexagram texts."""
        # Concept frequency by hexagram
        hexagram_concepts = {}

        for hex_num in range(1, 65):
            if hex_num not in self.texts:
                continue

            hex_name = self.hexagrams[hex_num]['name']
            concepts = defaultdict(list)

            # Combine all texts for this hexagram
            all_text = ""
            for text_type, text_data in self.texts[hex_num].items():
                all_text += text_data['content'] or ""

            # Count concepts by category
            for category, keywords in self.concept_categories.items():
                for keyword in keywords:
                    count = all_text.count(keyword)
                    if count > 0:
                        concepts[category].append({
                            'term': keyword,
                            'count': count,
                        })

            hexagram_concepts[hex_num] = {
                'name': hex_name,
                'concepts': dict(concepts),
                'total_length': len(all_text),
            }

        # Aggregate statistics
        category_totals = defaultdict(Counter)
        for hex_num, data in hexagram_concepts.items():
            for category, terms in data['concepts'].items():
                for term_data in terms:
                    category_totals[category][term_data['term']] += term_data['count']

        # Find most "fortunate" and "unfortunate" hexagrams
        fortune_scores = {}
        positive_terms = ['吉', '亨', '利', '元']
        negative_terms = ['凶', '悔', '吝', '咎', '厲']

        for hex_num, data in hexagram_concepts.items():
            fortune_concepts = data['concepts'].get('fortune', [])
            positive = sum(t['count'] for t in fortune_concepts if t['term'] in positive_terms)
            negative = sum(t['count'] for t in fortune_concepts if t['term'] in negative_terms)
            fortune_scores[hex_num] = {
                'name': data['name'],
                'positive': positive,
                'negative': negative,
                'net_fortune': positive - negative,
            }

        # Sort by net fortune
        sorted_fortune = sorted(fortune_scores.items(),
                               key=lambda x: x[1]['net_fortune'],
                               reverse=True)

        return {
            'title': 'Concept Extraction Analysis',
            'hexagram_concepts': hexagram_concepts,
            'category_totals': {cat: dict(counts) for cat, counts in category_totals.items()},
            'fortune_ranking': {
                'most_fortunate': [
                    {'number': num, **data}
                    for num, data in sorted_fortune[:10]
                ],
                'least_fortunate': [
                    {'number': num, **data}
                    for num, data in sorted_fortune[-10:]
                ],
            },
            'insights': [
                f"Analyzed {len(hexagram_concepts)} hexagrams for key concepts",
                f"Fortune terms most common: {list(category_totals['fortune'].most_common(5))}",
            ],
        }

    # =========================================================================
    # Part 3: Recurring Phrase Detection
    # =========================================================================

    def detect_recurring_phrases(self, min_length: int = 2, max_length: int = 8) -> Dict:
        """Detect recurring phrases across hexagram texts."""
        # Collect all phrases
        phrase_counts = Counter()
        phrase_locations = defaultdict(list)

        for hex_num, texts in self.texts.items():
            for text_type, text_data in texts.items():
                content = text_data['content'] or ""

                # Extract all substrings of varying lengths
                for length in range(min_length, min(max_length + 1, len(content) + 1)):
                    for i in range(len(content) - length + 1):
                        phrase = content[i:i+length]
                        # Only consider Chinese characters
                        if all('\u4e00' <= c <= '\u9fff' for c in phrase):
                            phrase_counts[phrase] += 1
                            phrase_locations[phrase].append({
                                'hexagram': hex_num,
                                'text_type': text_type,
                            })

        # Filter for phrases appearing at least 3 times
        recurring = {phrase: count for phrase, count in phrase_counts.items()
                    if count >= 3}

        # Group by length
        by_length = defaultdict(list)
        for phrase, count in sorted(recurring.items(), key=lambda x: -x[1]):
            by_length[len(phrase)].append({
                'phrase': phrase,
                'count': count,
                'locations': phrase_locations[phrase][:5],  # First 5 locations
            })

        # Find most common phrases
        most_common = Counter(recurring).most_common(100)

        # Identify formulaic phrases (appear in fixed patterns)
        formulaic = []
        common_patterns = [
            ('吉', '凶'),
            ('元亨', '利貞'),
            ('君子', '小人'),
            ('往', '來'),
        ]

        for pattern in common_patterns:
            pattern_str = ''.join(pattern)
            if pattern_str in recurring:
                formulaic.append({
                    'pattern': pattern_str,
                    'count': recurring[pattern_str],
                })

        return {
            'title': 'Recurring Phrase Analysis',
            'total_unique_phrases': len(recurring),
            'phrases_by_length': {
                length: phrases[:20]  # Top 20 per length
                for length, phrases in by_length.items()
            },
            'most_common_phrases': [
                {'phrase': phrase, 'count': count}
                for phrase, count in most_common[:50]
            ],
            'formulaic_patterns': formulaic,
            'insights': [
                f"Found {len(recurring)} recurring phrases",
                f"Most common 2-char phrases: {[p['phrase'] for p in by_length[2][:5]]}",
            ],
        }

    # =========================================================================
    # Part 4: Semantic Profiling
    # =========================================================================

    def create_semantic_profiles(self) -> Dict:
        """Create semantic profiles for each hexagram."""
        profiles = {}

        for hex_num in range(1, 65):
            if hex_num not in self.texts:
                continue

            hex_data = self.hexagrams[hex_num]
            texts = self.texts[hex_num]

            # Combine all text
            all_text = ""
            for text_data in texts.values():
                all_text += text_data['content'] or ""

            # Extract key features
            profile = {
                'hexagram_number': hex_num,
                'name': hex_data['name'],
                'trigrams': {
                    'upper': hex_data['upper_name'],
                    'lower': hex_data['lower_name'],
                },
                'text_lengths': {
                    text_type: len(text_data['content'] or "")
                    for text_type, text_data in texts.items()
                },
                'concept_vector': {},
                'top_characters': [],
                'fortune_indicators': {},
                'action_indicators': {},
            }

            # Build concept vector
            for category, keywords in self.concept_categories.items():
                category_count = sum(all_text.count(kw) for kw in keywords)
                profile['concept_vector'][category] = category_count

            # Top characters
            char_freq = Counter(c for c in all_text if '\u4e00' <= c <= '\u9fff')
            profile['top_characters'] = [
                {'char': c, 'count': count}
                for c, count in char_freq.most_common(10)
            ]

            # Fortune indicators
            profile['fortune_indicators'] = {
                'ji_count': all_text.count('吉'),
                'xiong_count': all_text.count('凶'),
                'heng_count': all_text.count('亨'),
                'li_count': all_text.count('利'),
                'hui_count': all_text.count('悔'),
                'lin_count': all_text.count('吝'),
            }

            # Action indicators
            profile['action_indicators'] = {
                'wang_count': all_text.count('往'),
                'lai_count': all_text.count('來'),
                'xing_count': all_text.count('行'),
                'zhi_count': all_text.count('止'),
            }

            profiles[hex_num] = profile

        # Calculate similarity between hexagrams based on concept vectors
        similarities = self._calculate_similarities(profiles)

        return {
            'title': 'Semantic Profiles',
            'profiles': profiles,
            'most_similar_pairs': similarities[:20],
            'insights': [
                f"Created semantic profiles for {len(profiles)} hexagrams",
                "Profiles include concept vectors, fortune indicators, and action indicators",
            ],
        }

    def _calculate_similarities(self, profiles: Dict) -> List[Dict]:
        """Calculate semantic similarity between hexagrams."""
        from math import sqrt

        def cosine_similarity(v1: Dict, v2: Dict) -> float:
            """Calculate cosine similarity between two concept vectors."""
            categories = set(v1.keys()) | set(v2.keys())
            dot_product = sum(v1.get(c, 0) * v2.get(c, 0) for c in categories)
            norm1 = sqrt(sum(v1.get(c, 0) ** 2 for c in categories))
            norm2 = sqrt(sum(v2.get(c, 0) ** 2 for c in categories))

            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot_product / (norm1 * norm2)

        similarities = []
        hex_nums = list(profiles.keys())

        for i, hex1 in enumerate(hex_nums):
            for hex2 in hex_nums[i+1:]:
                sim = cosine_similarity(
                    profiles[hex1]['concept_vector'],
                    profiles[hex2]['concept_vector']
                )
                similarities.append({
                    'hexagram_1': hex1,
                    'name_1': profiles[hex1]['name'],
                    'hexagram_2': hex2,
                    'name_2': profiles[hex2]['name'],
                    'similarity': round(sim, 4),
                })

        # Sort by similarity
        similarities.sort(key=lambda x: -x['similarity'])
        return similarities

    # =========================================================================
    # Part 5: Trigram Symbolism Analysis
    # =========================================================================

    def analyze_trigram_symbolism(self) -> Dict:
        """Analyze how trigram symbolism appears in hexagram texts."""
        trigram_symbol_usage = defaultdict(lambda: defaultdict(int))

        # Get all symbols for each trigram
        trigram_symbols = {}
        for trigram, data in self.trigram_symbols.items():
            symbols = data.get('all_symbols', [])
            trigram_symbols[trigram] = symbols

        # For each hexagram, check if trigram symbols appear in text
        for hex_num in range(1, 65):
            if hex_num not in self.texts:
                continue

            hex_data = self.hexagrams[hex_num]
            upper = hex_data['upper_name']
            lower = hex_data['lower_name']

            # Combine all text
            all_text = ""
            for text_data in self.texts[hex_num].values():
                all_text += text_data['content'] or ""

            # Check for upper trigram symbols
            for symbol in trigram_symbols.get(upper, []):
                if symbol in all_text:
                    trigram_symbol_usage[upper][symbol] += 1

            # Check for lower trigram symbols
            for symbol in trigram_symbols.get(lower, []):
                if symbol in all_text:
                    trigram_symbol_usage[lower][symbol] += 1

        # Analyze correlation between trigrams and symbol usage
        trigram_correlation = {}
        for trigram, symbols in trigram_symbol_usage.items():
            trigram_correlation[trigram] = {
                'total_mentions': sum(symbols.values()),
                'unique_symbols': len(symbols),
                'top_symbols': dict(Counter(symbols).most_common(10)),
            }

        return {
            'title': 'Trigram Symbolism Analysis',
            'trigram_symbol_usage': {k: dict(v) for k, v in trigram_symbol_usage.items()},
            'trigram_correlation': trigram_correlation,
            'insights': [
                "Analyzed correlation between trigram assignment and symbol usage in texts",
                "This tests the hypothesis that 說卦傳 symbolism predicts text content",
            ],
        }

    # =========================================================================
    # Part 6: Cross-Commentary Analysis Preparation
    # =========================================================================

    def prepare_commentary_analysis(self) -> Dict:
        """Prepare data structures for commentary analysis."""
        # This prepares the framework for analyzing commentaries
        # The actual commentaries need to be imported first

        # Load available commentaries
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM commentaries")
        commentary_count = cursor.fetchone()[0]

        # Check commentary files
        commentary_dir = DATA_DIR / "commentaries"
        available_files = []

        if commentary_dir.exists():
            for f in commentary_dir.iterdir():
                if f.is_file() and f.suffix in ['.txt', '.json']:
                    available_files.append({
                        'name': f.name,
                        'size': f.stat().st_size,
                        'type': f.suffix,
                    })
                elif f.is_dir():
                    file_count = len(list(f.glob('*')))
                    available_files.append({
                        'name': f.name,
                        'type': 'directory',
                        'file_count': file_count,
                    })

        return {
            'title': 'Commentary Analysis Preparation',
            'database_commentaries': commentary_count,
            'available_files': available_files,
            'recommended_next_steps': [
                'Import 周易正義 commentary into database',
                'Import 周易集解 commentary into database',
                'Import 東坡易傳 commentary into database',
                'Run cross-commentary concept extraction',
                'Compare interpretation patterns across eras',
            ],
            'insights': [
                f"Found {len(available_files)} commentary files/directories",
                f"Database has {commentary_count} commentary entries",
            ],
        }

    # =========================================================================
    # Main Analysis and Output
    # =========================================================================

    def run_full_analysis(self) -> Dict:
        """Run all Phase 3 textual analyses."""
        print("=" * 60)
        print("Phase 3: Textual Analysis of I Ching Hexagrams")
        print("=" * 60)

        results = {
            'metadata': {
                'analysis_date': '2026-01-20',
                'phase': 3,
                'description': 'Textual analysis of I Ching hexagram texts',
            },
            'sections': {},
        }

        # 1. Character Frequency
        print("\n[1/6] Analyzing character frequency...")
        results['sections']['character_frequency'] = self.analyze_character_frequency()
        print("  ✓ Character frequency analysis complete")

        # 2. Concept Extraction
        print("\n[2/6] Extracting key concepts...")
        results['sections']['concept_extraction'] = self.extract_concepts()
        print("  ✓ Concept extraction complete")

        # 3. Recurring Phrases
        print("\n[3/6] Detecting recurring phrases...")
        results['sections']['recurring_phrases'] = self.detect_recurring_phrases()
        print("  ✓ Recurring phrase detection complete")

        # 4. Semantic Profiles
        print("\n[4/6] Creating semantic profiles...")
        results['sections']['semantic_profiles'] = self.create_semantic_profiles()
        print("  ✓ Semantic profiles created")

        # 5. Trigram Symbolism
        print("\n[5/6] Analyzing trigram symbolism...")
        results['sections']['trigram_symbolism'] = self.analyze_trigram_symbolism()
        print("  ✓ Trigram symbolism analysis complete")

        # 6. Commentary Preparation
        print("\n[6/6] Preparing commentary analysis...")
        results['sections']['commentary_prep'] = self.prepare_commentary_analysis()
        print("  ✓ Commentary analysis preparation complete")

        # Save results
        output_path = OUTPUT_DIR / "phase3_textual_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Results saved to: {output_path}")

        # Print summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: Dict):
        """Print a summary of key findings."""
        print("\n" + "=" * 60)
        print("KEY FINDINGS SUMMARY")
        print("=" * 60)

        # Character frequency
        char_freq = results['sections']['character_frequency']
        print(f"\n1. CHARACTER FREQUENCY:")
        print(f"   - Total characters: {char_freq['total_characters']}")
        print(f"   - Unique characters: {char_freq['unique_characters']}")
        top_5 = list(char_freq['top_50_overall'].items())[:5]
        print(f"   - Top 5: {top_5}")

        # Concept extraction
        concepts = results['sections']['concept_extraction']
        print(f"\n2. CONCEPT EXTRACTION:")
        most_fortunate = concepts['fortune_ranking']['most_fortunate'][:3]
        print(f"   - Most fortunate: {[(h['name'], h['net_fortune']) for h in most_fortunate]}")
        least_fortunate = concepts['fortune_ranking']['least_fortunate'][:3]
        print(f"   - Least fortunate: {[(h['name'], h['net_fortune']) for h in least_fortunate]}")

        # Recurring phrases
        phrases = results['sections']['recurring_phrases']
        print(f"\n3. RECURRING PHRASES:")
        print(f"   - Total unique phrases: {phrases['total_unique_phrases']}")
        top_phrases = phrases['most_common_phrases'][:5]
        print(f"   - Top 5: {[(p['phrase'], p['count']) for p in top_phrases]}")

        # Semantic profiles
        profiles = results['sections']['semantic_profiles']
        print(f"\n4. SEMANTIC SIMILARITY:")
        similar = profiles['most_similar_pairs'][:3]
        print(f"   - Most similar pairs:")
        for pair in similar:
            print(f"     {pair['name_1']} ↔ {pair['name_2']}: {pair['similarity']}")

        # Trigram symbolism
        trigram = results['sections']['trigram_symbolism']
        print(f"\n5. TRIGRAM SYMBOLISM:")
        for trig, data in trigram['trigram_correlation'].items():
            print(f"   - {trig}: {data['total_mentions']} mentions, {data['unique_symbols']} unique symbols")

        print("\n" + "=" * 60)

    def close(self):
        """Close database connection."""
        self.conn.close()


if __name__ == "__main__":
    analyzer = TextualAnalyzer()
    try:
        results = analyzer.run_full_analysis()
    finally:
        analyzer.close()
