#!/usr/bin/env python3
"""
多模式探索分析

測試數十種不同的數學序列和模式，尋找與特殊爻分布的相關性。

測試的模式類型：
1. 經典數列：Fibonacci, Lucas, Pell, Tribonacci
2. 多邊形數：三角數, 平方數, 五角數, 六角數
3. 質數相關：質數, 半質數, 質數間隙
4. 二進制：Hamming權重, 二進制模式
5. 模運算：各種模數的週期性
6. 天文週期：月相(29.5), 太陽年(365.25), 節氣(15.2)
7. 音樂比例：八度(2:1), 五度(3:2), 四度(4:3)
8. 數學常數：π, e, φ, √2, √3
9. 中國傳統：天干(10), 地支(12), 甲子(60), 九宮(9), 八卦(8)
10. 幾何：對角線數, 完美數
"""

import math
from collections import defaultdict
from typing import List, Dict, Tuple, Set
import numpy as np
from dataclasses import dataclass

# ============================================================
# 數學常數
# ============================================================

PHI = (1 + math.sqrt(5)) / 2       # 黃金比例 ≈ 1.618
E = math.e                          # 自然對數底 ≈ 2.718
PI = math.pi                        # 圓周率 ≈ 3.14159
SQRT2 = math.sqrt(2)               # √2 ≈ 1.414
SQRT3 = math.sqrt(3)               # √3 ≈ 1.732
SQRT5 = math.sqrt(5)               # √5 ≈ 2.236
SILVER = 1 + SQRT2                 # 白銀比例 ≈ 2.414
PLASTIC = 1.324717957244746        # 塑料數

# 天文常數
LUNAR_MONTH = 29.53059             # 朔望月天數
SOLAR_YEAR = 365.2422              # 回歸年天數
SOLAR_TERM = SOLAR_YEAR / 24       # 節氣間隔 ≈ 15.2天
METONIC = 19                       # 默冬週期（年）
SAROS = 18.03                      # 沙羅週期（年）

# ============================================================
# 數列生成器
# ============================================================

def fibonacci(n: int) -> List[int]:
    """Fibonacci數列"""
    seq = [1, 1]
    for _ in range(n - 2):
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

def lucas(n: int) -> List[int]:
    """Lucas數列 (2, 1, 3, 4, 7, 11, 18, ...)"""
    seq = [2, 1]
    for _ in range(n - 2):
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

def pell(n: int) -> List[int]:
    """Pell數列 (0, 1, 2, 5, 12, 29, 70, ...)"""
    seq = [0, 1]
    for _ in range(n - 2):
        seq.append(2 * seq[-1] + seq[-2])
    return seq[:n]

def tribonacci(n: int) -> List[int]:
    """Tribonacci數列 (0, 0, 1, 1, 2, 4, 7, 13, 24, ...)"""
    seq = [0, 0, 1]
    for _ in range(n - 3):
        seq.append(seq[-1] + seq[-2] + seq[-3])
    return seq[:n]

def triangular(n: int) -> List[int]:
    """三角數 (1, 3, 6, 10, 15, 21, 28, ...)"""
    return [i * (i + 1) // 2 for i in range(1, n + 1)]

def square_numbers(n: int) -> List[int]:
    """平方數 (1, 4, 9, 16, 25, 36, ...)"""
    return [i * i for i in range(1, n + 1)]

def pentagonal(n: int) -> List[int]:
    """五角數 (1, 5, 12, 22, 35, 51, ...)"""
    return [i * (3 * i - 1) // 2 for i in range(1, n + 1)]

def hexagonal(n: int) -> List[int]:
    """六角數 (1, 6, 15, 28, 45, 66, ...)"""
    return [i * (2 * i - 1) for i in range(1, n + 1)]

def primes(n: int) -> List[int]:
    """前n個質數"""
    result = []
    candidate = 2
    while len(result) < n:
        is_prime = True
        for p in result:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            result.append(candidate)
        candidate += 1
    return result

def semiprimes(n: int) -> List[int]:
    """前n個半質數（兩個質數的乘積）"""
    prime_list = primes(50)
    semis = set()
    for i, p1 in enumerate(prime_list):
        for p2 in prime_list[i:]:
            semis.add(p1 * p2)
    return sorted(semis)[:n]

def catalan(n: int) -> List[int]:
    """Catalan數 (1, 1, 2, 5, 14, 42, 132, ...)"""
    result = [1]
    for i in range(1, n):
        result.append(result[-1] * 2 * (2 * i - 1) // (i + 1))
    return result

def powers_of_2(n: int) -> List[int]:
    """2的冪次 (1, 2, 4, 8, 16, 32, ...)"""
    return [2 ** i for i in range(n)]

def powers_of_3(n: int) -> List[int]:
    """3的冪次 (1, 3, 9, 27, 81, ...)"""
    return [3 ** i for i in range(n)]

def factorial_numbers(n: int) -> List[int]:
    """階乘數 (1, 2, 6, 24, 120, ...)"""
    result = [1]
    for i in range(1, n):
        result.append(result[-1] * (i + 1))
    return result

def perfect_numbers(n: int) -> List[int]:
    """完美數 (6, 28, 496, 8128, ...)"""
    # 只返回前幾個，因為完美數增長很快
    return [6, 28, 496, 8128][:n]

def highly_composite(n: int) -> List[int]:
    """高合成數 (1, 2, 4, 6, 12, 24, 36, 48, 60, 120, ...)"""
    return [1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720][:n]

# ============================================================
# 特殊爻數據
# ============================================================

SAMPLES = [
    (1, 1, "111111", 0), (1, 2, "111111", 1), (1, 3, "111111", 0),
    (1, 4, "111111", 0), (1, 5, "111111", 1), (1, 6, "111111", -1),
    (2, 1, "000000", -1), (2, 2, "000000", 1), (2, 3, "000000", 0),
    (2, 4, "000000", 0), (2, 5, "000000", 1), (2, 6, "000000", -1),
    (3, 1, "010001", 0), (3, 2, "010001", 0), (3, 3, "010001", -1),
    (3, 4, "010001", 1), (3, 5, "010001", 0), (3, 6, "010001", -1),
    (4, 1, "100010", 0), (4, 2, "100010", 1), (4, 3, "100010", -1),
    (4, 4, "100010", -1), (4, 5, "100010", 1), (4, 6, "100010", 0),
    (5, 1, "010111", 0), (5, 2, "010111", 0), (5, 3, "010111", -1),
    (5, 4, "010111", -1), (5, 5, "010111", 1), (5, 6, "010111", 0),
    (6, 1, "111010", 0), (6, 2, "111010", 0), (6, 3, "111010", 0),
    (6, 4, "111010", 0), (6, 5, "111010", 1), (6, 6, "111010", -1),
    (15, 1, "000100", 1), (15, 2, "000100", 1), (15, 3, "000100", 1),
    (15, 4, "000100", 1), (15, 5, "000100", 0), (15, 6, "000100", 0),
    (17, 1, "011001", 0), (17, 2, "011001", -1), (17, 3, "011001", 0),
    (17, 4, "011001", 0), (17, 5, "011001", 1), (17, 6, "011001", 0),
    (20, 1, "110000", 0), (20, 2, "110000", 0), (20, 3, "110000", 0),
    (20, 4, "110000", 0), (20, 5, "110000", 0), (20, 6, "110000", 0),
    (24, 1, "000001", 1), (24, 2, "000001", 1), (24, 3, "000001", 0),
    (24, 4, "000001", 0), (24, 5, "000001", 0), (24, 6, "000001", -1),
    (25, 1, "111001", 1), (25, 2, "111001", 1), (25, 3, "111001", -1),
    (25, 4, "111001", 0), (25, 5, "111001", 0), (25, 6, "111001", -1),
    (33, 1, "111100", -1), (33, 2, "111100", 1), (33, 3, "111100", 0),
    (33, 4, "111100", 0), (33, 5, "111100", 1), (33, 6, "111100", 1),
    (47, 1, "011010", -1), (47, 2, "011010", 0), (47, 3, "011010", -1),
    (47, 4, "011010", 0), (47, 5, "011010", 0), (47, 6, "011010", 0),
    (50, 1, "101110", 0), (50, 2, "101110", 0), (50, 3, "101110", 0),
    (50, 4, "101110", -1), (50, 5, "101110", 1), (50, 6, "101110", 1),
    (63, 1, "010101", 1), (63, 2, "010101", 0), (63, 3, "010101", 0),
    (63, 4, "010101", 0), (63, 5, "010101", 0), (63, 6, "010101", -1),
]

def get_special_positions() -> List[int]:
    """獲取需要爻辭的特殊爻位置"""
    special = []
    for gua_num, pos, binary, actual in SAMPLES:
        prediction = predict_structure(pos, binary)
        if prediction != actual:
            linear_pos = (gua_num - 1) * 6 + pos
            special.append(linear_pos)
    return sorted(special)

def predict_structure(pos: int, binary: str) -> int:
    """純結構預測"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]

    if xor_val == 4 and pos <= 4:
        return 1
    if xor_val == 0 and is_central:
        return 1
    if upper == 0 and pos == 2:
        return 1

    score = 0.0
    pos_weights = {5: 0.7, 2: 0.5, 6: -0.7, 3: -0.1}
    score += pos_weights.get(pos, 0)
    upper_weights = {0: 0.35, 7: 0.15, 4: 0.2, 3: -0.35, 6: -0.3}
    score += upper_weights.get(upper, 0)
    lower_weights = {4: 0.45, 6: 0.2, 1: 0.1}
    score += lower_weights.get(lower, 0)

    if score >= 0.6:
        return 1
    elif score <= -0.3:
        return -1
    return 0

# ============================================================
# 模式匹配分析
# ============================================================

@dataclass
class PatternResult:
    """模式匹配結果"""
    name: str
    category: str
    position_matches: int
    interval_matches: int
    total_positions: int
    total_intervals: int
    position_match_rate: float
    interval_match_rate: float
    p_value: float  # 統計顯著性
    details: Dict

def calculate_p_value(observed: int, total: int, expected_rate: float) -> float:
    """計算統計顯著性（簡化版）"""
    if total == 0:
        return 1.0
    expected = total * expected_rate
    if expected == 0:
        return 1.0
    # Chi-square approximation
    chi_sq = ((observed - expected) ** 2) / expected
    # Simplified p-value estimation
    return math.exp(-chi_sq / 2)

def test_sequence_pattern(positions: List[int], sequence: List[int],
                         name: str, category: str) -> PatternResult:
    """測試單個序列模式"""
    seq_set = set(sequence)

    # 位置匹配
    position_matches = sum(1 for p in positions if p in seq_set)

    # 間距匹配
    intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    interval_matches = sum(1 for i in intervals if i in seq_set)

    # 計算匹配率
    pos_rate = position_matches / len(positions) if positions else 0
    int_rate = interval_matches / len(intervals) if intervals else 0

    # 估計期望匹配率（基於序列密度）
    max_val = max(positions) if positions else 384
    expected_density = len([s for s in sequence if s <= max_val]) / max_val

    # P值
    p_pos = calculate_p_value(position_matches, len(positions), expected_density)
    p_int = calculate_p_value(interval_matches, len(intervals), expected_density)

    return PatternResult(
        name=name,
        category=category,
        position_matches=position_matches,
        interval_matches=interval_matches,
        total_positions=len(positions),
        total_intervals=len(intervals),
        position_match_rate=pos_rate,
        interval_match_rate=int_rate,
        p_value=min(p_pos, p_int),
        details={
            "matched_positions": [p for p in positions if p in seq_set],
            "matched_intervals": [i for i in intervals if i in seq_set],
            "sequence_sample": sequence[:15]
        }
    )

def test_modular_pattern(positions: List[int], modulus: int,
                        name: str) -> PatternResult:
    """測試模運算模式"""
    intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]

    # 統計各餘數的頻率
    mod_counts = defaultdict(int)
    for p in positions:
        mod_counts[p % modulus] += 1

    int_mod_counts = defaultdict(int)
    for i in intervals:
        int_mod_counts[i % modulus] += 1

    # 找出最頻繁的餘數
    max_pos_mod = max(mod_counts.items(), key=lambda x: x[1]) if mod_counts else (0, 0)
    max_int_mod = max(int_mod_counts.items(), key=lambda x: x[1]) if int_mod_counts else (0, 0)

    # 計算集中度（最大頻率/期望均勻分布）
    expected_uniform = len(positions) / modulus
    concentration = max_pos_mod[1] / expected_uniform if expected_uniform > 0 else 0

    return PatternResult(
        name=name,
        category="模運算",
        position_matches=max_pos_mod[1],
        interval_matches=max_int_mod[1],
        total_positions=len(positions),
        total_intervals=len(intervals),
        position_match_rate=max_pos_mod[1] / len(positions) if positions else 0,
        interval_match_rate=max_int_mod[1] / len(intervals) if intervals else 0,
        p_value=calculate_p_value(max_pos_mod[1], len(positions), 1/modulus),
        details={
            "modulus": modulus,
            "position_distribution": dict(mod_counts),
            "interval_distribution": dict(int_mod_counts),
            "concentration": concentration,
            "dominant_remainder": max_pos_mod[0]
        }
    )

def test_constant_pattern(positions: List[int], constant: float,
                         name: str) -> PatternResult:
    """測試數學常數相關模式"""
    max_pos = max(positions) if positions else 384

    # 生成常數相關的位置
    const_positions = set()
    for i in range(1, 50):
        val = int(constant * i)
        if val <= max_pos:
            const_positions.add(val)
        val = int(max_pos / (constant ** i))
        if val >= 1:
            const_positions.add(val)

    position_matches = sum(1 for p in positions if p in const_positions)
    intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    interval_matches = sum(1 for i in intervals if i in const_positions)

    return PatternResult(
        name=name,
        category="數學常數",
        position_matches=position_matches,
        interval_matches=interval_matches,
        total_positions=len(positions),
        total_intervals=len(intervals),
        position_match_rate=position_matches / len(positions) if positions else 0,
        interval_match_rate=interval_matches / len(intervals) if intervals else 0,
        p_value=0.5,  # 難以計算精確p值
        details={
            "constant": constant,
            "generated_positions": sorted(const_positions)[:20],
            "matched": [p for p in positions if p in const_positions]
        }
    )

# ============================================================
# 主分析器
# ============================================================

class MultiPatternExplorer:
    def __init__(self):
        self.positions = get_special_positions()
        self.results: List[PatternResult] = []

    def run_all_tests(self):
        """運行所有模式測試"""
        print("運行多模式探索分析...\n")
        print(f"特殊爻位置: {self.positions}")
        print(f"總數: {len(self.positions)}\n")

        # 1. 經典數列
        print("【1. 經典數列測試】")
        sequences = [
            (fibonacci(50), "Fibonacci", "經典數列"),
            (lucas(50), "Lucas", "經典數列"),
            (pell(30), "Pell", "經典數列"),
            (tribonacci(30), "Tribonacci", "經典數列"),
            (catalan(15), "Catalan", "經典數列"),
        ]
        for seq, name, cat in sequences:
            result = test_sequence_pattern(self.positions, seq, name, cat)
            self.results.append(result)
            self._print_result(result)

        # 2. 多邊形數
        print("\n【2. 多邊形數測試】")
        poly_sequences = [
            (triangular(30), "三角數", "多邊形數"),
            (square_numbers(20), "平方數", "多邊形數"),
            (pentagonal(20), "五角數", "多邊形數"),
            (hexagonal(20), "六角數", "多邊形數"),
        ]
        for seq, name, cat in poly_sequences:
            result = test_sequence_pattern(self.positions, seq, name, cat)
            self.results.append(result)
            self._print_result(result)

        # 3. 質數相關
        print("\n【3. 質數相關測試】")
        prime_sequences = [
            (primes(100), "質數", "質數相關"),
            (semiprimes(50), "半質數", "質數相關"),
        ]
        for seq, name, cat in prime_sequences:
            result = test_sequence_pattern(self.positions, seq, name, cat)
            self.results.append(result)
            self._print_result(result)

        # 4. 冪次數
        print("\n【4. 冪次數測試】")
        power_sequences = [
            (powers_of_2(10), "2的冪次", "冪次數"),
            (powers_of_3(8), "3的冪次", "冪次數"),
            (factorial_numbers(8), "階乘數", "冪次數"),
        ]
        for seq, name, cat in power_sequences:
            result = test_sequence_pattern(self.positions, seq, name, cat)
            self.results.append(result)
            self._print_result(result)

        # 5. 特殊數
        print("\n【5. 特殊數測試】")
        special_sequences = [
            (perfect_numbers(4), "完美數", "特殊數"),
            (highly_composite(14), "高合成數", "特殊數"),
        ]
        for seq, name, cat in special_sequences:
            result = test_sequence_pattern(self.positions, seq, name, cat)
            self.results.append(result)
            self._print_result(result)

        # 6. 模運算
        print("\n【6. 模運算測試】")
        for mod in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24, 60, 64]:
            result = test_modular_pattern(self.positions, mod, f"mod {mod}")
            self.results.append(result)
            if result.details["concentration"] > 1.5:  # 只顯示顯著的
                self._print_result(result)

        # 7. 數學常數
        print("\n【7. 數學常數測試】")
        constants = [
            (PHI, "黃金比例 φ"),
            (E, "自然對數 e"),
            (PI, "圓周率 π"),
            (SQRT2, "√2"),
            (SQRT3, "√3"),
            (SILVER, "白銀比例"),
            (PLASTIC, "塑料數"),
        ]
        for const, name in constants:
            result = test_constant_pattern(self.positions, const, name)
            self.results.append(result)
            self._print_result(result)

        # 8. 天文週期
        print("\n【8. 天文週期測試】")
        astro_periods = [
            (LUNAR_MONTH, "朔望月 29.53"),
            (SOLAR_TERM, "節氣 15.22"),
            (float(METONIC), "默冬週期 19"),
            (SAROS, "沙羅週期 18.03"),
        ]
        for period, name in astro_periods:
            result = test_constant_pattern(self.positions, period, name)
            self.results.append(result)
            self._print_result(result)

        # 9. 中國傳統數字
        print("\n【9. 中國傳統數字測試】")
        chinese_sequences = [
            ([i for i in range(8, 400, 8)], "八卦週期(8)", "中國傳統"),
            ([i for i in range(9, 400, 9)], "九宮週期(9)", "中國傳統"),
            ([i for i in range(10, 400, 10)], "天干週期(10)", "中國傳統"),
            ([i for i in range(12, 400, 12)], "地支週期(12)", "中國傳統"),
            ([i for i in range(60, 400, 60)], "甲子週期(60)", "中國傳統"),
            ([i for i in range(64, 400, 64)], "64卦週期", "中國傳統"),
        ]
        for seq, name, cat in chinese_sequences:
            result = test_sequence_pattern(self.positions, seq, name, cat)
            self.results.append(result)
            self._print_result(result)

        # 10. 音樂比例
        print("\n【10. 音樂比例測試】")
        music_ratios = [
            (2.0, "八度 2:1"),
            (1.5, "五度 3:2"),
            (4/3, "四度 4:3"),
            (5/4, "大三度 5:4"),
            (6/5, "小三度 6:5"),
        ]
        for ratio, name in music_ratios:
            result = test_constant_pattern(self.positions, ratio, name)
            self.results.append(result)
            self._print_result(result)

    def _print_result(self, r: PatternResult):
        """打印單個結果"""
        pos_pct = r.position_match_rate * 100
        int_pct = r.interval_match_rate * 100
        star = "**" if pos_pct > 20 or int_pct > 50 else ""
        print(f"  {r.name}: 位置={r.position_matches}/{r.total_positions} ({pos_pct:.1f}%), "
              f"間距={r.interval_matches}/{r.total_intervals} ({int_pct:.1f}%) {star}")

    def generate_summary(self) -> str:
        """生成總結報告"""
        lines = []
        lines.append("\n" + "="*80)
        lines.append(" 多模式探索分析總結 ")
        lines.append("="*80)

        # 按匹配率排序
        pos_sorted = sorted(self.results, key=lambda x: x.position_match_rate, reverse=True)
        int_sorted = sorted(self.results, key=lambda x: x.interval_match_rate, reverse=True)

        lines.append("\n【位置匹配率 Top 10】")
        for r in pos_sorted[:10]:
            lines.append(f"  {r.name}: {r.position_match_rate*100:.1f}% ({r.position_matches}/{r.total_positions})")

        lines.append("\n【間距匹配率 Top 10】")
        for r in int_sorted[:10]:
            lines.append(f"  {r.name}: {r.interval_match_rate*100:.1f}% ({r.interval_matches}/{r.total_intervals})")

        # 統計顯著的模式
        significant = [r for r in self.results if r.position_match_rate > 0.2 or r.interval_match_rate > 0.5]
        lines.append(f"\n【統計顯著模式數】: {len(significant)}")

        # 按類別總結
        categories = defaultdict(list)
        for r in self.results:
            categories[r.category].append(r)

        lines.append("\n【按類別總結】")
        for cat, results in categories.items():
            avg_pos = np.mean([r.position_match_rate for r in results])
            avg_int = np.mean([r.interval_match_rate for r in results])
            lines.append(f"  {cat}: 平均位置匹配={avg_pos*100:.1f}%, 平均間距匹配={avg_int*100:.1f}%")

        # 關鍵發現
        lines.append("\n【關鍵發現】")
        if int_sorted[0].interval_match_rate > 0.5:
            lines.append(f"  1. 間距最佳匹配: {int_sorted[0].name} ({int_sorted[0].interval_match_rate*100:.1f}%)")
        if pos_sorted[0].position_match_rate > 0.2:
            lines.append(f"  2. 位置最佳匹配: {pos_sorted[0].name} ({pos_sorted[0].position_match_rate*100:.1f}%)")

        # 模運算最佳
        mod_results = [r for r in self.results if r.category == "模運算"]
        if mod_results:
            best_mod = max(mod_results, key=lambda x: x.details.get("concentration", 0))
            if best_mod.details.get("concentration", 0) > 1.5:
                lines.append(f"  3. 最佳模運算: {best_mod.name}, 集中度={best_mod.details['concentration']:.2f}, "
                            f"主要餘數={best_mod.details['dominant_remainder']}")

        return "\n".join(lines)

    def export_results(self, filepath: str):
        """導出結果"""
        import json
        data = {
            "special_positions": self.positions,
            "results": [
                {
                    "name": r.name,
                    "category": r.category,
                    "position_match_rate": r.position_match_rate,
                    "interval_match_rate": r.interval_match_rate,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n結果已導出至: {filepath}")


# ============================================================
# 主程序
# ============================================================

def main():
    explorer = MultiPatternExplorer()
    explorer.run_all_tests()
    print(explorer.generate_summary())
    explorer.export_results("data/analysis/multi_pattern_results.json")


if __name__ == "__main__":
    main()
