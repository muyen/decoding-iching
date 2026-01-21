#!/usr/bin/env python3
"""Analysis tools for I Ching pattern recognition"""
import sqlite3
import json
from pathlib import Path
from collections import defaultdict
import math

class IChingAnalyzer:
    """Main analysis class for I Ching patterns"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path('/Users/arsenelee/github/iching/data/iching.db')
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    # ==================== Basic Queries ====================

    def get_hexagram(self, king_wen_number):
        """Get full hexagram data by King Wen number"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT h.*,
                   ut.name as upper_trigram_name,
                   lt.name as lower_trigram_name
            FROM hexagrams h
            LEFT JOIN trigrams ut ON h.upper_trigram_id = ut.id
            LEFT JOIN trigrams lt ON h.lower_trigram_id = lt.id
            WHERE h.king_wen_number = ?
        ''', (king_wen_number,))
        return dict(cursor.fetchone())

    def get_all_hexagrams(self):
        """Get all hexagrams"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT h.*,
                   ut.name as upper_trigram_name,
                   lt.name as lower_trigram_name
            FROM hexagrams h
            LEFT JOIN trigrams ut ON h.upper_trigram_id = ut.id
            LEFT JOIN trigrams lt ON h.lower_trigram_id = lt.id
            ORDER BY h.king_wen_number
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_trigram(self, name):
        """Get trigram by name"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM trigrams WHERE name = ?', (name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_trigram_symbols(self, trigram_name):
        """Get all symbols associated with a trigram"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT ts.* FROM trigram_symbols ts
            JOIN trigrams t ON ts.trigram_id = t.id
            WHERE t.name = ?
        ''', (trigram_name,))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== Structural Analysis ====================

    def analyze_yang_distribution(self):
        """Analyze distribution of yang lines across hexagrams"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT yang_count, COUNT(*) as count, GROUP_CONCAT(name) as hexagrams
            FROM hexagrams
            GROUP BY yang_count
            ORDER BY yang_count
        ''')
        results = {}
        for row in cursor.fetchall():
            results[row['yang_count']] = {
                'count': row['count'],
                'hexagrams': row['hexagrams'].split(','),
                'expected_binomial': math.comb(6, row['yang_count'])
            }
        return results

    def analyze_trigram_combinations(self):
        """Analyze which trigram combinations appear"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT ut.name as upper, lt.name as lower,
                   h.name as hexagram, h.king_wen_number
            FROM hexagrams h
            JOIN trigrams ut ON h.upper_trigram_id = ut.id
            JOIN trigrams lt ON h.lower_trigram_id = lt.id
            ORDER BY ut.name, lt.name
        ''')

        matrix = defaultdict(dict)
        for row in cursor.fetchall():
            matrix[row['upper']][row['lower']] = {
                'hexagram': row['hexagram'],
                'king_wen': row['king_wen_number']
            }
        return dict(matrix)

    def analyze_sequence_differences(self):
        """Compare King Wen, Fu Xi, and Mawangdui sequences"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT h.name, h.king_wen_number, h.fuxi_position, h.mawangdui_position,
                   h.binary_repr
            FROM hexagrams h
            ORDER BY h.king_wen_number
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'name': row['name'],
                'binary': row['binary_repr'],
                'king_wen': row['king_wen_number'],
                'fuxi': row['fuxi_position'],
                'mawangdui': row['mawangdui_position'],
                'kw_fx_diff': abs(row['king_wen_number'] - (row['fuxi_position'] or 0)),
                'kw_mw_diff': abs(row['king_wen_number'] - (row['mawangdui_position'] or 0))
            })
        return results

    def analyze_pairs(self):
        """Analyze King Wen hexagram pairs"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT h1.king_wen_number as kw1, h1.name as name1, h1.binary_repr as bin1,
                   h2.king_wen_number as kw2, h2.name as name2, h2.binary_repr as bin2,
                   h1.inverse_hexagram_id, h1.complement_hexagram_id
            FROM hexagrams h1
            JOIN hexagrams h2 ON h1.pair_number = h2.pair_number AND h1.id < h2.id
            ORDER BY h1.pair_number
        ''')

        pairs = []
        for row in cursor.fetchall():
            # Check relationship type
            bin1 = row['bin1']
            bin2 = row['bin2']

            is_inverse = bin1 == bin2[::-1]
            is_complement = all(b1 != b2 for b1, b2 in zip(bin1, bin2))

            pairs.append({
                'pair_number': (row['kw1'] + 1) // 2,
                'hex1': {'kw': row['kw1'], 'name': row['name1'], 'binary': bin1},
                'hex2': {'kw': row['kw2'], 'name': row['name2'], 'binary': bin2},
                'relationship': 'inverse' if is_inverse else ('complement' if is_complement else 'other')
            })
        return pairs

    def analyze_nuclear_hexagrams(self):
        """Analyze nuclear (互卦) hexagram relationships"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT h.king_wen_number, h.name,
                   nut.name as nuclear_upper, nlt.name as nuclear_lower
            FROM hexagrams h
            JOIN trigrams nut ON h.nuclear_upper_id = nut.id
            JOIN trigrams nlt ON h.nuclear_lower_id = nlt.id
        ''')

        results = []
        for row in cursor.fetchall():
            # Find the nuclear hexagram
            nuclear_upper = row['nuclear_upper']
            nuclear_lower = row['nuclear_lower']

            cursor.execute('''
                SELECT h.king_wen_number, h.name
                FROM hexagrams h
                JOIN trigrams ut ON h.upper_trigram_id = ut.id
                JOIN trigrams lt ON h.lower_trigram_id = lt.id
                WHERE ut.name = ? AND lt.name = ?
            ''', (nuclear_upper, nuclear_lower))

            nuclear_hex = cursor.fetchone()

            results.append({
                'hexagram': row['king_wen_number'],
                'name': row['name'],
                'nuclear_upper': nuclear_upper,
                'nuclear_lower': nuclear_lower,
                'nuclear_hexagram': nuclear_hex['king_wen_number'] if nuclear_hex else None,
                'nuclear_name': nuclear_hex['name'] if nuclear_hex else None
            })
        return results

    # ==================== Graph Analysis ====================

    def get_transformation_graph(self):
        """Get hexagram transformation network as adjacency list"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT h1.king_wen_number as from_kw, h2.king_wen_number as to_kw,
                   hr.changed_line
            FROM hexagram_relationships hr
            JOIN hexagrams h1 ON hr.from_hexagram_id = h1.id
            JOIN hexagrams h2 ON hr.to_hexagram_id = h2.id
            WHERE hr.relationship_type = 'single_line_change'
        ''')

        graph = defaultdict(list)
        for row in cursor.fetchall():
            graph[row['from_kw']].append({
                'to': row['to_kw'],
                'changed_line': row['changed_line']
            })
        return dict(graph)

    def find_path(self, from_kw, to_kw):
        """Find shortest transformation path between two hexagrams"""
        graph = self.get_transformation_graph()

        # BFS
        from collections import deque
        queue = deque([(from_kw, [from_kw])])
        visited = {from_kw}

        while queue:
            current, path = queue.popleft()
            if current == to_kw:
                return path

            for edge in graph.get(current, []):
                next_hex = edge['to']
                if next_hex not in visited:
                    visited.add(next_hex)
                    queue.append((next_hex, path + [next_hex]))

        return None  # No path found

    def calculate_graph_metrics(self):
        """Calculate basic graph metrics"""
        graph = self.get_transformation_graph()

        total_edges = sum(len(edges) for edges in graph.values())
        nodes = len(graph)

        # Degree distribution
        degrees = [len(edges) for edges in graph.values()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        return {
            'nodes': nodes,
            'edges': total_edges // 2,  # Undirected
            'avg_degree': avg_degree,
            'is_regular': len(set(degrees)) == 1,
            'degree_per_node': 6  # Each hexagram has exactly 6 neighbors
        }

    # ==================== Pattern Detection ====================

    def find_symmetric_hexagrams(self):
        """Find hexagrams that are symmetric (same when rotated 180°)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT king_wen_number, name, binary_repr
            FROM hexagrams
            WHERE is_symmetric = 1
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def find_complementary_pairs(self):
        """Find hexagrams that are complements (all lines opposite)"""
        hexagrams = self.get_all_hexagrams()
        pairs = []

        for h in hexagrams:
            complement_binary = ''.join('1' if c == '0' else '0' for c in h['binary_repr'])
            for h2 in hexagrams:
                if h2['binary_repr'] == complement_binary and h['king_wen_number'] < h2['king_wen_number']:
                    pairs.append({
                        'hex1': h['king_wen_number'],
                        'name1': h['name'],
                        'hex2': h2['king_wen_number'],
                        'name2': h2['name']
                    })
        return pairs

    def analyze_binary_patterns(self):
        """Analyze binary patterns in King Wen sequence"""
        hexagrams = self.get_all_hexagrams()

        patterns = {
            'alternating': [],  # 010101 or 101010
            'solid_top': [],     # xxx111
            'solid_bottom': [],  # 111xxx
            'symmetric': [],     # same forward and backward
        }

        for h in hexagrams:
            binary = h['binary_repr']

            if binary in ['010101', '101010']:
                patterns['alternating'].append(h['king_wen_number'])

            if binary[3:] == '111':
                patterns['solid_top'].append(h['king_wen_number'])

            if binary[:3] == '111':
                patterns['solid_bottom'].append(h['king_wen_number'])

            if binary == binary[::-1]:
                patterns['symmetric'].append(h['king_wen_number'])

        return patterns

    # ==================== Textual Analysis Preparation ====================

    def get_hexagram_texts(self, king_wen_number):
        """Get all texts for a hexagram"""
        cursor = self.conn.cursor()

        # Get hexagram texts
        cursor.execute('''
            SELECT text_type, content FROM hexagram_texts
            WHERE hexagram_id = (SELECT id FROM hexagrams WHERE king_wen_number = ?)
        ''', (king_wen_number,))
        texts = {row['text_type']: row['content'] for row in cursor.fetchall()}

        # Get line texts
        cursor.execute('''
            SELECT position, yaoci, xiaoxiang FROM lines
            WHERE hexagram_id = (SELECT id FROM hexagrams WHERE king_wen_number = ?)
            ORDER BY position
        ''', (king_wen_number,))
        texts['lines'] = [dict(row) for row in cursor.fetchall()]

        return texts

    def export_for_nlp(self, output_path=None):
        """Export all texts in format suitable for NLP analysis"""
        if output_path is None:
            output_path = Path('/Users/arsenelee/github/iching/data/nlp_export.json')

        hexagrams = self.get_all_hexagrams()
        export_data = []

        for h in hexagrams:
            texts = self.get_hexagram_texts(h['king_wen_number'])
            export_data.append({
                'king_wen_number': h['king_wen_number'],
                'name': h['name'],
                'binary': h['binary_repr'],
                'upper_trigram': h['upper_trigram_name'],
                'lower_trigram': h['lower_trigram_name'],
                'yang_count': h['yang_count'],
                'texts': texts
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"Exported {len(export_data)} hexagrams to {output_path}")
        return export_data


def run_full_analysis():
    """Run a comprehensive analysis and print results"""
    analyzer = IChingAnalyzer()

    print("=" * 60)
    print("I CHING STRUCTURAL ANALYSIS")
    print("=" * 60)

    # Yang distribution
    print("\n1. YANG LINE DISTRIBUTION")
    print("-" * 40)
    yang_dist = analyzer.analyze_yang_distribution()
    for yang_count, data in sorted(yang_dist.items()):
        print(f"  {yang_count} yang lines: {data['count']} hexagrams (expected: {data['expected_binomial']})")

    # Symmetric hexagrams
    print("\n2. SYMMETRIC HEXAGRAMS (same when rotated 180°)")
    print("-" * 40)
    symmetric = analyzer.find_symmetric_hexagrams()
    for h in symmetric:
        print(f"  #{h['king_wen_number']} {h['name']} ({h['binary_repr']})")

    # Graph metrics
    print("\n3. TRANSFORMATION GRAPH METRICS")
    print("-" * 40)
    metrics = analyzer.calculate_graph_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # Sequence comparison
    print("\n4. SEQUENCE COMPARISON (sample)")
    print("-" * 40)
    print(f"  {'Name':<6} {'KW':<4} {'FX':<4} {'MW':<4} {'Binary'}")
    seq = analyzer.analyze_sequence_differences()[:10]
    for s in seq:
        print(f"  {s['name']:<6} {s['king_wen']:<4} {s['fuxi']:<4} {s['mawangdui'] or 'N/A':<4} {s['binary']}")

    # Pairs analysis
    print("\n5. KING WEN PAIRS (sample)")
    print("-" * 40)
    pairs = analyzer.analyze_pairs()[:5]
    for p in pairs:
        print(f"  Pair {p['pair_number']}: {p['hex1']['name']} + {p['hex2']['name']} ({p['relationship']})")

    # Binary patterns
    print("\n6. BINARY PATTERNS")
    print("-" * 40)
    patterns = analyzer.analyze_binary_patterns()
    for pattern_name, hexagrams in patterns.items():
        print(f"  {pattern_name}: {len(hexagrams)} hexagrams - {hexagrams[:5]}{'...' if len(hexagrams) > 5 else ''}")

    # Example path
    print("\n7. TRANSFORMATION PATH EXAMPLE (1 → 2)")
    print("-" * 40)
    path = analyzer.find_path(1, 2)
    print(f"  Path length: {len(path) - 1} steps")
    print(f"  Path: {' → '.join(str(p) for p in path)}")

    analyzer.close()
    print("\n" + "=" * 60)
    print("Analysis complete!")


if __name__ == '__main__':
    run_full_analysis()
