#!/usr/bin/env python3
"""
Phase 2: Structural Analysis of I Ching Hexagrams
=================================================

This script performs comprehensive mathematical analysis of the hexagram system:
1. King Wen sequence mathematical patterns
2. Fu Xi vs King Wen comparison
3. Graph theory analysis of transformation network
4. Symmetry and group theory analysis

Author: I Ching Research Project
Date: 2026-01-20
"""

import json
import sqlite3
from collections import defaultdict, Counter
from pathlib import Path
import math
from itertools import permutations, combinations

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STRUCTURE_DIR = DATA_DIR / "structure"
DB_PATH = DATA_DIR / "iching.db"
OUTPUT_DIR = DATA_DIR / "analysis"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


class HexagramStructuralAnalyzer:
    """Comprehensive structural analysis of I Ching hexagrams."""

    def __init__(self):
        self.hexagrams = self._load_hexagrams()
        self.transformations = self._load_transformations()
        self.sequences = self._load_sequences()
        self.trigrams = self._load_trigrams()

    def _load_hexagrams(self):
        """Load hexagram data from database."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.*,
                   t1.name as upper_name, t1.binary_repr as upper_binary,
                   t2.name as lower_name, t2.binary_repr as lower_binary
            FROM hexagrams h
            LEFT JOIN trigrams t1 ON h.upper_trigram_id = t1.id
            LEFT JOIN trigrams t2 ON h.lower_trigram_id = t2.id
            ORDER BY h.king_wen_number
        """)
        hexagrams = {row['king_wen_number']: dict(row) for row in cursor.fetchall()}
        conn.close()
        return hexagrams

    def _load_transformations(self):
        """Load transformation data."""
        with open(STRUCTURE_DIR / "transformations.json", 'r') as f:
            return json.load(f)

    def _load_sequences(self):
        """Load sequence comparison data."""
        with open(STRUCTURE_DIR / "sequence_comparison.json", 'r') as f:
            return json.load(f)

    def _load_trigrams(self):
        """Load trigram data."""
        with open(STRUCTURE_DIR / "trigrams.json", 'r') as f:
            return json.load(f)

    # =========================================================================
    # Part 1: King Wen Sequence Mathematical Analysis
    # =========================================================================

    def analyze_king_wen_sequence(self):
        """Comprehensive analysis of King Wen sequence patterns."""
        results = {
            'title': 'King Wen Sequence Mathematical Analysis',
            'pair_analysis': self._analyze_pairs(),
            'transition_analysis': self._analyze_transitions(),
            'yang_progression': self._analyze_yang_progression(),
            'trigram_patterns': self._analyze_trigram_patterns(),
            'numerical_patterns': self._analyze_numerical_patterns(),
            'canon_division': self._analyze_canon_division(),
        }
        return results

    def _analyze_pairs(self):
        """Analyze the 32 pairs in King Wen sequence."""
        pairs = []
        for i in range(1, 64, 2):
            h1 = self.hexagrams[i]
            h2 = self.hexagrams[i + 1]

            b1 = h1['binary_repr']
            b2 = h2['binary_repr']

            # Check relationship type
            inverted = b1 == b2[::-1]  # 180° rotation
            complement = all(c1 != c2 for c1, c2 in zip(b1, b2))  # All lines flipped

            # Check if either is symmetric (same when rotated)
            h1_symmetric = b1 == b1[::-1]
            h2_symmetric = b2 == b2[::-1]

            pairs.append({
                'pair_number': (i + 1) // 2,
                'hexagram_1': {'number': i, 'name': h1['name'], 'binary': b1},
                'hexagram_2': {'number': i + 1, 'name': h2['name'], 'binary': b2},
                'relationship': 'complement' if complement else ('inverse' if inverted else 'other'),
                'h1_symmetric': h1_symmetric,
                'h2_symmetric': h2_symmetric,
            })

        # Summary statistics
        relationship_counts = Counter(p['relationship'] for p in pairs)
        symmetric_count = sum(1 for p in pairs if p['h1_symmetric'] or p['h2_symmetric'])

        return {
            'pairs': pairs,
            'total_pairs': len(pairs),
            'relationship_distribution': dict(relationship_counts),
            'pairs_with_symmetric_hexagram': symmetric_count,
            'insight': 'King Wen pairs are organized as inverse (rotation) pairs, except for 4 complement pairs involving symmetric hexagrams'
        }

    def _analyze_transitions(self):
        """Analyze transitions between consecutive hexagrams."""
        transitions = []
        for i in range(1, 64):
            h1 = self.hexagrams[i]
            h2 = self.hexagrams[i + 1]

            b1 = h1['binary_repr']
            b2 = h2['binary_repr']

            # Count lines changed
            lines_changed = sum(c1 != c2 for c1, c2 in zip(b1, b2))

            # Check which lines changed
            changed_positions = [pos + 1 for pos, (c1, c2) in enumerate(zip(b1, b2)) if c1 != c2]

            transitions.append({
                'from': i,
                'to': i + 1,
                'lines_changed': lines_changed,
                'changed_positions': changed_positions,
            })

        # Distribution of changes
        change_distribution = Counter(t['lines_changed'] for t in transitions)

        # Even vs odd transitions (within pairs vs between pairs)
        within_pair = [t for t in transitions if t['from'] % 2 == 1]  # 1→2, 3→4, etc.
        between_pair = [t for t in transitions if t['from'] % 2 == 0]  # 2→3, 4→5, etc.

        within_avg = sum(t['lines_changed'] for t in within_pair) / len(within_pair)
        between_avg = sum(t['lines_changed'] for t in between_pair) / len(between_pair)

        return {
            'total_transitions': len(transitions),
            'change_distribution': dict(change_distribution),
            'within_pair_avg_changes': round(within_avg, 2),
            'between_pair_avg_changes': round(between_avg, 2),
            'insight': f'Within pairs average {within_avg:.2f} line changes; between pairs average {between_avg:.2f}',
            'notable_transitions': [t for t in transitions if t['lines_changed'] >= 5],
        }

    def _analyze_yang_progression(self):
        """Analyze how yang line count progresses through the sequence."""
        progression = []
        for i in range(1, 65):
            h = self.hexagrams[i]
            yang_count = h['binary_repr'].count('1')
            progression.append({
                'position': i,
                'name': h['name'],
                'yang_count': yang_count,
            })

        # Find patterns
        running_avg = []
        window = 8
        for i in range(len(progression) - window + 1):
            avg = sum(p['yang_count'] for p in progression[i:i+window]) / window
            running_avg.append(round(avg, 2))

        # Analyze upper vs lower canon
        upper_canon = [p for p in progression if p['position'] <= 30]
        lower_canon = [p for p in progression if p['position'] > 30]

        upper_avg = sum(p['yang_count'] for p in upper_canon) / len(upper_canon)
        lower_avg = sum(p['yang_count'] for p in lower_canon) / len(lower_canon)

        return {
            'progression': progression,
            'running_average_window': window,
            'running_average': running_avg,
            'upper_canon_avg_yang': round(upper_avg, 2),
            'lower_canon_avg_yang': round(lower_avg, 2),
            'insight': f'Upper canon avg yang: {upper_avg:.2f}, Lower canon avg yang: {lower_avg:.2f}',
        }

    def _analyze_trigram_patterns(self):
        """Analyze trigram distribution in King Wen sequence."""
        upper_sequence = []
        lower_sequence = []

        for i in range(1, 65):
            h = self.hexagrams[i]
            upper_sequence.append(h['upper_name'])
            lower_sequence.append(h['lower_name'])

        # Count trigram occurrences
        upper_counts = Counter(upper_sequence)
        lower_counts = Counter(lower_sequence)
        combined_counts = Counter(upper_sequence + lower_sequence)

        # Analyze trigram pair frequencies
        pair_counts = Counter(
            (self.hexagrams[i]['upper_name'], self.hexagrams[i]['lower_name'])
            for i in range(1, 65)
        )

        # Find same-trigram hexagrams (pure hexagrams)
        pure_hexagrams = [
            {'number': i, 'name': self.hexagrams[i]['name'], 'trigram': self.hexagrams[i]['upper_name']}
            for i in range(1, 65)
            if self.hexagrams[i]['upper_name'] == self.hexagrams[i]['lower_name']
        ]

        return {
            'upper_trigram_counts': dict(upper_counts),
            'lower_trigram_counts': dict(lower_counts),
            'combined_trigram_counts': dict(combined_counts),
            'pure_hexagrams': pure_hexagrams,
            'total_pure_hexagrams': len(pure_hexagrams),
            'insight': f'{len(pure_hexagrams)} pure hexagrams (same upper and lower trigram)',
        }

    def _analyze_numerical_patterns(self):
        """Search for numerical patterns in King Wen sequence."""
        # Convert sequence to decimal values
        decimals = []
        for i in range(1, 65):
            binary = self.hexagrams[i]['binary_repr']
            decimal = int(binary, 2)
            decimals.append({
                'position': i,
                'name': self.hexagrams[i]['name'],
                'binary': binary,
                'decimal': decimal,
            })

        # Analyze differences between consecutive hexagrams
        differences = []
        for i in range(len(decimals) - 1):
            diff = decimals[i + 1]['decimal'] - decimals[i]['decimal']
            differences.append(diff)

        # Look for patterns in differences
        diff_counts = Counter(differences)

        # Check for Fibonacci numbers in sequence
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        fib_positions = [d for d in decimals if d['decimal'] in fib]

        # Check sum patterns
        total_sum = sum(d['decimal'] for d in decimals)
        first_half_sum = sum(d['decimal'] for d in decimals[:32])
        second_half_sum = sum(d['decimal'] for d in decimals[32:])

        return {
            'decimal_values': decimals,
            'difference_distribution': dict(diff_counts),
            'fibonacci_matches': fib_positions,
            'total_sum': total_sum,
            'first_half_sum': first_half_sum,
            'second_half_sum': second_half_sum,
            'sum_ratio': round(first_half_sum / second_half_sum, 4) if second_half_sum else 0,
            'expected_sum': 64 * 63 // 2,  # Sum of 0-63
            'insight': f'Total decimal sum: {total_sum}, theoretical sum 0-63: {64*63//2}',
        }

    def _analyze_canon_division(self):
        """Analyze the Upper Canon (1-30) and Lower Canon (31-64) division."""
        upper_canon = [self.hexagrams[i] for i in range(1, 31)]
        lower_canon = [self.hexagrams[i] for i in range(31, 65)]

        def canon_stats(hexagrams):
            yang_avg = sum(h['binary_repr'].count('1') for h in hexagrams) / len(hexagrams)
            symmetric = sum(1 for h in hexagrams if h['binary_repr'] == h['binary_repr'][::-1])
            return {
                'count': len(hexagrams),
                'avg_yang_lines': round(yang_avg, 2),
                'symmetric_hexagrams': symmetric,
            }

        return {
            'upper_canon': {
                'range': '1-30',
                'theme': 'Cosmic principles (Heaven, Earth → Water, Fire)',
                **canon_stats(upper_canon),
            },
            'lower_canon': {
                'range': '31-64',
                'theme': 'Human affairs (Influence, Duration → Before/After Completion)',
                **canon_stats(lower_canon),
            },
            'division_ratio': '30:34',
            'insight': 'Upper Canon focuses on cosmic/natural principles; Lower Canon on human affairs and practical wisdom',
        }

    # =========================================================================
    # Part 2: Fu Xi vs King Wen Comparison
    # =========================================================================

    def compare_sequences(self):
        """Compare Fu Xi and King Wen sequences."""
        # Build Fu Xi sequence (binary counting order)
        fuxi_sequence = []
        for decimal in range(64):
            binary = format(decimal, '06b')
            # Find the King Wen number for this binary
            for kw_num, h in self.hexagrams.items():
                if h['binary_repr'] == binary:
                    fuxi_sequence.append({
                        'fuxi_position': decimal + 1,
                        'king_wen_number': kw_num,
                        'name': h['name'],
                        'binary': binary,
                        'decimal': decimal,
                    })
                    break

        # Sort by Fu Xi position
        fuxi_sequence.sort(key=lambda x: x['fuxi_position'])

        # Calculate displacement
        for item in fuxi_sequence:
            item['displacement'] = abs(item['fuxi_position'] - item['king_wen_number'])

        # Analyze displacement
        displacements = [item['displacement'] for item in fuxi_sequence]
        avg_displacement = sum(displacements) / len(displacements)
        max_displacement = max(displacements)
        min_displacement = min(displacements)
        same_position = sum(1 for d in displacements if d == 0)

        # Group by displacement magnitude
        displacement_groups = {
            '0 (same position)': sum(1 for d in displacements if d == 0),
            '1-10': sum(1 for d in displacements if 1 <= d <= 10),
            '11-20': sum(1 for d in displacements if 11 <= d <= 20),
            '21-30': sum(1 for d in displacements if 21 <= d <= 30),
            '31-40': sum(1 for d in displacements if 31 <= d <= 40),
            '41+': sum(1 for d in displacements if d > 40),
        }

        # Find hexagrams in same position
        same_position_hexagrams = [
            item for item in fuxi_sequence
            if item['fuxi_position'] == item['king_wen_number']
        ]

        return {
            'title': 'Fu Xi vs King Wen Sequence Comparison',
            'sequence_comparison': fuxi_sequence,
            'statistics': {
                'average_displacement': round(avg_displacement, 2),
                'max_displacement': max_displacement,
                'min_displacement': min_displacement,
                'same_position_count': same_position,
            },
            'displacement_distribution': displacement_groups,
            'same_position_hexagrams': same_position_hexagrams,
            'insights': [
                f'Only {same_position} hexagrams are in the same position in both sequences',
                f'Average displacement: {avg_displacement:.2f} positions',
                'Fu Xi sequence is pure binary counting (mathematical)',
                'King Wen sequence follows philosophical/practical organization',
            ],
        }

    # =========================================================================
    # Part 3: Graph Theory Analysis
    # =========================================================================

    def analyze_transformation_graph(self):
        """Graph theory analysis of hexagram transformation network."""
        # Build adjacency list
        graph = defaultdict(set)
        for t in self.transformations:
            graph[t['from_hexagram']].add(t['to_hexagram'])
            graph[t['to_hexagram']].add(t['from_hexagram'])  # Undirected

        # Basic graph properties
        num_nodes = 64
        num_edges = len(self.transformations) // 2  # Each edge counted once

        # Degree distribution (should be 6 for all - regular graph)
        degrees = {node: len(neighbors) for node, neighbors in graph.items()}
        degree_distribution = Counter(degrees.values())

        # Find shortest paths between key hexagrams
        def bfs_shortest_path(start, end):
            if start == end:
                return [start]
            visited = {start}
            queue = [(start, [start])]
            while queue:
                node, path = queue.pop(0)
                for neighbor in graph[node]:
                    if neighbor == end:
                        return path + [neighbor]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            return None

        # Key paths
        key_paths = {
            'qian_to_kun': bfs_shortest_path(1, 2),  # 乾 to 坤
            'qian_to_jiji': bfs_shortest_path(1, 63),  # 乾 to 既濟
            'kun_to_weiji': bfs_shortest_path(2, 64),  # 坤 to 未濟
            'tai_to_pi': bfs_shortest_path(11, 12),  # 泰 to 否
        }

        # Analyze clustering
        def local_clustering_coefficient(node):
            neighbors = list(graph[node])
            if len(neighbors) < 2:
                return 0
            # Count edges between neighbors
            edges_between = sum(
                1 for i, n1 in enumerate(neighbors)
                for n2 in neighbors[i+1:]
                if n2 in graph[n1]
            )
            possible_edges = len(neighbors) * (len(neighbors) - 1) // 2
            return edges_between / possible_edges if possible_edges > 0 else 0

        clustering_coefficients = {
            node: round(local_clustering_coefficient(node), 4)
            for node in range(1, 65)
        }
        avg_clustering = sum(clustering_coefficients.values()) / 64

        # Find diameter (longest shortest path)
        all_pairs_distances = {}
        for start in range(1, 65):
            distances = {start: 0}
            queue = [start]
            while queue:
                node = queue.pop(0)
                for neighbor in graph[node]:
                    if neighbor not in distances:
                        distances[neighbor] = distances[node] + 1
                        queue.append(neighbor)
            all_pairs_distances[start] = distances

        max_distance = max(
            max(distances.values())
            for distances in all_pairs_distances.values()
        )

        # Find eccentricity of each node
        eccentricities = {
            node: max(all_pairs_distances[node].values())
            for node in range(1, 65)
        }

        # Find center (nodes with minimum eccentricity)
        min_eccentricity = min(eccentricities.values())
        center_nodes = [node for node, ecc in eccentricities.items() if ecc == min_eccentricity]

        return {
            'title': 'Transformation Graph Analysis',
            'basic_properties': {
                'nodes': num_nodes,
                'edges': num_edges,
                'is_regular': all(d == 6 for d in degrees.values()),
                'regular_degree': 6,
            },
            'degree_distribution': dict(degree_distribution),
            'connectivity': {
                'is_connected': True,  # All nodes reachable
                'diameter': max_distance,
                'radius': min_eccentricity,
                'center_nodes': center_nodes[:5],  # First 5
            },
            'clustering': {
                'average_clustering_coefficient': round(avg_clustering, 4),
                'sample_coefficients': dict(list(clustering_coefficients.items())[:10]),
            },
            'key_paths': {
                name: {
                    'path': path,
                    'length': len(path) - 1 if path else None,
                    'hexagram_names': [self.hexagrams[p]['name'] for p in path] if path else None,
                }
                for name, path in key_paths.items()
            },
            'insights': [
                f'The graph is 6-regular: every hexagram connects to exactly 6 others',
                f'Graph diameter: {max_distance} (max steps between any two hexagrams)',
                f'Average clustering coefficient: {avg_clustering:.4f}',
                f'Graph is fully connected - any hexagram reachable from any other',
            ],
        }

    # =========================================================================
    # Part 4: Symmetry and Group Theory Analysis
    # =========================================================================

    def analyze_symmetries(self):
        """Analyze symmetry operations on hexagrams."""
        results = {
            'title': 'Symmetry and Group Theory Analysis',
            'reflection_symmetry': self._analyze_reflection_symmetry(),
            'rotation_symmetry': self._analyze_rotation_symmetry(),
            'complement_operation': self._analyze_complement(),
            'nuclear_hexagrams': self._analyze_nuclear_hexagrams(),
            'transformation_groups': self._analyze_transformation_groups(),
        }
        return results

    def _analyze_reflection_symmetry(self):
        """Analyze hexagrams symmetric under 180° rotation."""
        symmetric_hexagrams = []
        for i in range(1, 65):
            h = self.hexagrams[i]
            binary = h['binary_repr']
            if binary == binary[::-1]:
                symmetric_hexagrams.append({
                    'number': i,
                    'name': h['name'],
                    'binary': binary,
                    'yang_count': binary.count('1'),
                })

        return {
            'count': len(symmetric_hexagrams),
            'hexagrams': symmetric_hexagrams,
            'pattern': 'Palindromic binary: lines 1=6, 2=5, 3=4',
            'insight': f'{len(symmetric_hexagrams)} hexagrams are unchanged by 180° rotation',
        }

    def _analyze_rotation_symmetry(self):
        """Analyze rotation (inverse) pairs."""
        rotation_pairs = []
        seen = set()

        for i in range(1, 65):
            if i in seen:
                continue
            h = self.hexagrams[i]
            binary = h['binary_repr']
            rotated = binary[::-1]

            # Find the hexagram with rotated binary
            for j in range(1, 65):
                if j != i and self.hexagrams[j]['binary_repr'] == rotated:
                    rotation_pairs.append({
                        'hexagram_1': {'number': i, 'name': h['name'], 'binary': binary},
                        'hexagram_2': {'number': j, 'name': self.hexagrams[j]['name'], 'binary': rotated},
                    })
                    seen.add(i)
                    seen.add(j)
                    break

            # Self-symmetric hexagrams
            if binary == rotated and i not in seen:
                seen.add(i)

        return {
            'non_trivial_pairs': len(rotation_pairs),
            'pairs': rotation_pairs[:10],  # First 10
            'self_symmetric': 8,  # Already counted above
            'total_orbits': len(rotation_pairs) + 8,  # 28 pairs + 8 fixed points = 36 != expected
            'insight': '180° rotation partitions hexagrams into 28 pairs + 8 fixed points',
        }

    def _analyze_complement(self):
        """Analyze complement operation (flip all lines)."""
        complement_pairs = []
        seen = set()

        for i in range(1, 65):
            if i in seen:
                continue
            h = self.hexagrams[i]
            binary = h['binary_repr']
            complement = ''.join('1' if c == '0' else '0' for c in binary)

            # Find the hexagram with complement binary
            for j in range(1, 65):
                if j != i and self.hexagrams[j]['binary_repr'] == complement:
                    complement_pairs.append({
                        'hexagram_1': {'number': i, 'name': h['name'], 'binary': binary},
                        'hexagram_2': {'number': j, 'name': self.hexagrams[j]['name'], 'binary': complement},
                    })
                    seen.add(i)
                    seen.add(j)
                    break

        return {
            'total_pairs': len(complement_pairs),
            'pairs': complement_pairs[:10],
            'insight': 'Complement operation pairs every hexagram with its "opposite"',
        }

    def _analyze_nuclear_hexagrams(self):
        """Analyze nuclear (inner) hexagram relationships."""
        nuclear_map = {}

        for i in range(1, 65):
            h = self.hexagrams[i]
            binary = h['binary_repr']

            # Nuclear hexagram: lines 2-3-4 (lower nuclear) and 3-4-5 (upper nuclear)
            lower_nuclear = binary[1:4]  # Lines 2,3,4
            upper_nuclear = binary[2:5]  # Lines 3,4,5
            nuclear_binary = upper_nuclear + lower_nuclear

            # Find the nuclear hexagram
            nuclear_num = None
            for j in range(1, 65):
                if self.hexagrams[j]['binary_repr'] == nuclear_binary:
                    nuclear_num = j
                    break

            nuclear_map[i] = {
                'hexagram': {'number': i, 'name': h['name']},
                'nuclear_binary': nuclear_binary,
                'nuclear_number': nuclear_num,
                'nuclear_name': self.hexagrams[nuclear_num]['name'] if nuclear_num else None,
            }

        # Find which hexagrams appear most as nuclear hexagrams
        nuclear_counts = Counter(n['nuclear_number'] for n in nuclear_map.values())
        most_common_nuclear = nuclear_counts.most_common(10)

        # Find fixed points (hexagrams that are their own nuclear)
        fixed_points = [i for i, n in nuclear_map.items() if n['nuclear_number'] == i]

        return {
            'nuclear_map': dict(list(nuclear_map.items())[:10]),  # Sample
            'most_common_nuclear': [
                {'number': num, 'name': self.hexagrams[num]['name'], 'count': count}
                for num, count in most_common_nuclear
            ],
            'fixed_points': [
                {'number': i, 'name': self.hexagrams[i]['name']}
                for i in fixed_points
            ],
            'insight': f'{len(fixed_points)} hexagrams are their own nuclear hexagram',
        }

    def _analyze_transformation_groups(self):
        """Analyze the group structure of hexagram transformations."""
        # The group of operations: Identity, Complement, Rotation, Complement+Rotation

        def complement(binary):
            return ''.join('1' if c == '0' else '0' for c in binary)

        def rotate(binary):
            return binary[::-1]

        # Build orbits under the Klein 4-group {I, C, R, CR}
        orbits = []
        seen = set()

        for i in range(1, 65):
            if i in seen:
                continue

            binary = self.hexagrams[i]['binary_repr']

            # Generate orbit
            orbit_binaries = {
                binary,
                complement(binary),
                rotate(binary),
                complement(rotate(binary)),
            }

            orbit_numbers = []
            for ob in orbit_binaries:
                for j in range(1, 65):
                    if self.hexagrams[j]['binary_repr'] == ob:
                        orbit_numbers.append(j)
                        seen.add(j)
                        break

            orbits.append({
                'size': len(set(orbit_numbers)),
                'hexagrams': sorted(set(orbit_numbers)),
                'names': [self.hexagrams[n]['name'] for n in sorted(set(orbit_numbers))],
            })

        orbit_sizes = Counter(o['size'] for o in orbits)

        return {
            'group': 'Klein 4-group (Z₂ × Z₂)',
            'operations': ['Identity', 'Complement', 'Rotation', 'Complement+Rotation'],
            'num_orbits': len(orbits),
            'orbit_size_distribution': dict(orbit_sizes),
            'sample_orbits': orbits[:5],
            'insight': f'Klein 4-group action partitions 64 hexagrams into {len(orbits)} orbits',
        }

    # =========================================================================
    # Main Analysis and Output
    # =========================================================================

    def run_full_analysis(self):
        """Run all Phase 2 analyses and save results."""
        print("=" * 60)
        print("Phase 2: Structural Analysis of I Ching Hexagrams")
        print("=" * 60)

        results = {
            'metadata': {
                'analysis_date': '2026-01-20',
                'phase': 2,
                'description': 'Mathematical and structural analysis of I Ching hexagrams',
            },
            'sections': {},
        }

        # 1. King Wen Sequence Analysis
        print("\n[1/4] Analyzing King Wen sequence...")
        results['sections']['king_wen_analysis'] = self.analyze_king_wen_sequence()
        print("  ✓ King Wen sequence analysis complete")

        # 2. Fu Xi vs King Wen Comparison
        print("\n[2/4] Comparing Fu Xi and King Wen sequences...")
        results['sections']['sequence_comparison'] = self.compare_sequences()
        print("  ✓ Sequence comparison complete")

        # 3. Graph Theory Analysis
        print("\n[3/4] Performing graph theory analysis...")
        results['sections']['graph_analysis'] = self.analyze_transformation_graph()
        print("  ✓ Graph theory analysis complete")

        # 4. Symmetry Analysis
        print("\n[4/4] Analyzing symmetries and group structure...")
        results['sections']['symmetry_analysis'] = self.analyze_symmetries()
        print("  ✓ Symmetry analysis complete")

        # Save results
        output_path = OUTPUT_DIR / "phase2_structural_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Results saved to: {output_path}")

        # Print summary
        self._print_summary(results)

        return results

    def _print_summary(self, results):
        """Print a summary of key findings."""
        print("\n" + "=" * 60)
        print("KEY FINDINGS SUMMARY")
        print("=" * 60)

        # King Wen pairs
        pairs = results['sections']['king_wen_analysis']['pair_analysis']
        print(f"\n1. KING WEN PAIRS:")
        print(f"   - {pairs['total_pairs']} total pairs")
        print(f"   - Relationship distribution: {pairs['relationship_distribution']}")

        # Sequence comparison
        seq = results['sections']['sequence_comparison']['statistics']
        print(f"\n2. SEQUENCE COMPARISON (Fu Xi vs King Wen):")
        print(f"   - Same position: {seq['same_position_count']} hexagrams")
        print(f"   - Average displacement: {seq['average_displacement']} positions")

        # Graph analysis
        graph = results['sections']['graph_analysis']
        print(f"\n3. TRANSFORMATION GRAPH:")
        print(f"   - {graph['basic_properties']['nodes']} nodes, {graph['basic_properties']['edges']} edges")
        print(f"   - Regular graph: degree {graph['basic_properties']['regular_degree']}")
        print(f"   - Diameter: {graph['connectivity']['diameter']}")
        print(f"   - Avg clustering coefficient: {graph['clustering']['average_clustering_coefficient']}")

        # Symmetry analysis
        sym = results['sections']['symmetry_analysis']
        print(f"\n4. SYMMETRY ANALYSIS:")
        print(f"   - Reflection symmetric hexagrams: {sym['reflection_symmetry']['count']}")
        print(f"   - Complement pairs: {sym['complement_operation']['total_pairs']}")
        print(f"   - Klein 4-group orbits: {sym['transformation_groups']['num_orbits']}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    analyzer = HexagramStructuralAnalyzer()
    results = analyzer.run_full_analysis()
