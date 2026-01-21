#!/usr/bin/env python3
"""
爻辭特殊標記模式分析

目標：找出哪些卦/爻需要額外語義信息（爻辭），
並分析這些「特殊爻」是否存在隱藏的數學或天文模式。

兩種分析方法：
1. 線性位置分析 (1D): 將384爻排成一線，分析間距模式
2. 八卦布局分析 (2D): 將卦映射到8×8網格，分析空間分布
"""

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import json

# ============================================================
# 數據定義
# ============================================================

# 已知樣本：(卦號, 爻位, 二進制, 實際吉凶)
# 吉=1, 中=0, 凶=-1
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

# 卦名對應
GUA_NAMES = {
    1: "乾", 2: "坤", 3: "屯", 4: "蒙", 5: "需", 6: "訟",
    15: "謙", 17: "隨", 20: "觀", 24: "復", 25: "無妄",
    33: "遯", 47: "困", 50: "鼎", 63: "既濟"
}

# 八卦對應
BAGUA = {
    "000": ("坤", 0), "001": ("震", 1), "010": ("坎", 2), "011": ("兌", 3),
    "100": ("艮", 4), "101": ("離", 5), "110": ("巽", 6), "111": ("乾", 7)
}

# 文王卦序 (King Wen sequence)
KING_WEN_SEQUENCE = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
    49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64
]

# 二十四節氣
SOLAR_TERMS_24 = [
    "立春", "雨水", "驚蟄", "春分", "清明", "穀雨",
    "立夏", "小滿", "芒種", "夏至", "小暑", "大暑",
    "立秋", "處暑", "白露", "秋分", "寒露", "霜降",
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"
]

# 數學常數
PHI = (1 + math.sqrt(5)) / 2  # 黃金比例 ≈ 1.618
SILVER_RATIO = 1 + math.sqrt(2)  # 白銀比例 ≈ 2.414
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

# ============================================================
# 輔助函數
# ============================================================

def binary_to_upper_lower(binary: str) -> Tuple[int, int]:
    """提取上卦和下卦的數值"""
    upper = int(binary[0:3], 2)
    lower = int(binary[3:6], 2)
    return upper, lower

def get_gua_position_in_sequence(gua_num: int) -> int:
    """獲取卦在文王序中的位置（1-64）"""
    return gua_num

def get_linear_position(gua_num: int, yao_pos: int) -> int:
    """計算爻在線性排列中的絕對位置 (1-384)"""
    return (gua_num - 1) * 6 + yao_pos

def is_structure_predictable(gua_num: int, pos: int, binary: str, actual: int) -> bool:
    """
    判斷某爻是否可由純結構預測

    基於已發現的100%規則：
    1. xor=4 且 pos≤4 → 吉
    2. xor=0 且 得中 → 吉
    3. 上卦=坤 且 pos=2 → 吉
    4. pos=5 → 不凶
    5. 得中且陽爻 → 不凶
    """
    upper, lower = binary_to_upper_lower(binary)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]
    line = int(binary[6 - pos])

    # 100%規則
    if xor_val == 4 and pos <= 4:
        return actual == 1  # 預測為吉
    if xor_val == 0 and is_central:
        return actual == 1  # 預測為吉
    if upper == 0 and pos == 2:
        return actual == 1  # 預測為吉
    if pos == 5:
        return actual != -1  # 預測不凶
    if is_central and line == 1:
        return actual != -1  # 預測不凶

    # 無法確定預測
    return None

def predict_by_structure(pos: int, binary: str) -> Optional[int]:
    """
    純結構預測
    返回: 1(吉), 0(中), -1(凶), None(無法預測)
    """
    upper, lower = binary_to_upper_lower(binary)
    xor_val = upper ^ lower
    is_central = pos in [2, 5]
    line = int(binary[6 - pos])

    # 強規則
    if xor_val == 4 and pos <= 4:
        return 1
    if xor_val == 0 and is_central:
        return 1
    if upper == 0 and pos == 2:
        return 1

    # 一般規則 - 使用加權打分
    score = 0.0

    # 位置權重
    pos_weights = {5: 0.7, 2: 0.5, 6: -0.7, 3: -0.1, 1: 0, 4: 0}
    score += pos_weights.get(pos, 0)

    # 上卦權重
    upper_weights = {0: 0.35, 7: 0.15, 4: 0.2, 3: -0.35, 6: -0.3}
    score += upper_weights.get(upper, 0)

    # 下卦權重
    lower_weights = {4: 0.45, 6: 0.2, 1: 0.1}
    score += lower_weights.get(lower, 0)

    # 閾值判斷
    if score >= 0.6:
        return 1
    elif score <= -0.3:
        return -1
    else:
        return 0

@dataclass
class YaoAnalysis:
    """爻分析結果"""
    gua_num: int
    yao_pos: int
    binary: str
    actual_result: int
    structure_prediction: Optional[int]
    is_predictable: bool
    linear_position: int
    grid_x: int  # 上卦
    grid_y: int  # 下卦
    gua_name: str
    needs_yici: bool  # 需要讀爻辭

# ============================================================
# 主分析類
# ============================================================

class PatternAnalyzer:
    def __init__(self):
        self.samples = SAMPLES
        self.analyzed_yaos: List[YaoAnalysis] = []
        self.special_yaos: List[YaoAnalysis] = []  # 需要爻辭的

    def analyze_all(self):
        """分析所有樣本"""
        for gua_num, pos, binary, actual in self.samples:
            upper, lower = binary_to_upper_lower(binary)
            prediction = predict_by_structure(pos, binary)

            # 判斷是否可預測
            is_predictable = (prediction == actual) if prediction is not None else False
            needs_yici = not is_predictable

            analysis = YaoAnalysis(
                gua_num=gua_num,
                yao_pos=pos,
                binary=binary,
                actual_result=actual,
                structure_prediction=prediction,
                is_predictable=is_predictable,
                linear_position=get_linear_position(gua_num, pos),
                grid_x=upper,
                grid_y=lower,
                gua_name=GUA_NAMES.get(gua_num, f"卦{gua_num}"),
                needs_yici=needs_yici
            )

            self.analyzed_yaos.append(analysis)
            if needs_yici:
                self.special_yaos.append(analysis)

    # ============================================================
    # 1D 線性位置分析
    # ============================================================

    def analyze_1d_linear(self) -> Dict:
        """1D線性位置分析"""
        results = {
            "total_samples": len(self.analyzed_yaos),
            "special_count": len(self.special_yaos),
            "special_positions": [],
            "intervals": [],
            "fibonacci_matches": [],
            "golden_ratio_analysis": {},
            "periodicity": {},
        }

        # 收集特殊爻的位置
        positions = sorted([y.linear_position for y in self.special_yaos])
        results["special_positions"] = positions

        # 計算間距
        if len(positions) > 1:
            intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            results["intervals"] = intervals

            # 檢查Fibonacci匹配
            for i, interval in enumerate(intervals):
                if interval in FIBONACCI:
                    results["fibonacci_matches"].append({
                        "position_pair": (positions[i], positions[i+1]),
                        "interval": interval,
                        "fibonacci_index": FIBONACCI.index(interval)
                    })

        # 黃金比例分析
        total_positions = 384
        golden_point = total_positions / PHI  # ≈ 237
        results["golden_ratio_analysis"] = {
            "golden_point": round(golden_point, 2),
            "special_near_golden": [p for p in positions if abs(p - golden_point) < 20],
            "phi": PHI,
        }

        # 週期性分析
        for period in [7, 8, 12, 24, 60]:
            mod_counts = defaultdict(int)
            for p in positions:
                mod_counts[p % period] += 1
            results["periodicity"][f"mod_{period}"] = dict(mod_counts)

        return results

    def visualize_1d(self) -> str:
        """生成1D線性可視化"""
        lines = []
        lines.append("="*80)
        lines.append("1D 線性位置分析 - 特殊爻位置分布")
        lines.append("="*80)

        # 收集位置
        positions = sorted([y.linear_position for y in self.special_yaos])

        # ASCII 可視化
        lines.append("\n位置圖 (. = 可預測, X = 需爻辭):\n")

        # 每行顯示64個位置（對應1卦=6爻，約10卦/行）
        for row_start in range(0, 384, 64):
            row_end = min(row_start + 64, 384)
            row = ""
            for pos in range(row_start + 1, row_end + 1):
                if pos in positions:
                    row += "X"
                else:
                    row += "."
            lines.append(f"{row_start+1:3d}-{row_end:3d}: {row}")

        # 統計
        lines.append(f"\n總樣本數: {len(self.analyzed_yaos)}")
        lines.append(f"特殊爻數: {len(self.special_yaos)} ({len(self.special_yaos)/len(self.analyzed_yaos)*100:.1f}%)")
        lines.append(f"特殊爻位置: {positions}")

        return "\n".join(lines)

    # ============================================================
    # 2D 八卦布局分析
    # ============================================================

    def analyze_2d_bagua(self) -> Dict:
        """2D八卦布局分析"""
        results = {
            "grid": [[[] for _ in range(8)] for _ in range(8)],
            "special_grid": [[0 for _ in range(8)] for _ in range(8)],
            "quadrant_analysis": {},
            "diagonal_analysis": {},
            "symmetry_analysis": {},
        }

        # 填充網格
        for yao in self.analyzed_yaos:
            x, y = yao.grid_x, yao.grid_y
            results["grid"][y][x].append(yao)
            if yao.needs_yici:
                results["special_grid"][y][x] += 1

        # 象限分析 (四象限)
        quadrants = {
            "Q1_upper_right": {"range": ((4,8), (4,8)), "total": 0, "special": 0},
            "Q2_upper_left": {"range": ((0,4), (4,8)), "total": 0, "special": 0},
            "Q3_lower_left": {"range": ((0,4), (0,4)), "total": 0, "special": 0},
            "Q4_lower_right": {"range": ((4,8), (0,4)), "total": 0, "special": 0},
        }

        for yao in self.analyzed_yaos:
            x, y = yao.grid_x, yao.grid_y
            for q_name, q_data in quadrants.items():
                x_range, y_range = q_data["range"]
                if x_range[0] <= x < x_range[1] and y_range[0] <= y < y_range[1]:
                    q_data["total"] += 1
                    if yao.needs_yici:
                        q_data["special"] += 1

        results["quadrant_analysis"] = quadrants

        # 對角線分析
        main_diag = []  # 主對角線 (x == y)
        anti_diag = []  # 反對角線 (x + y == 7)

        for yao in self.analyzed_yaos:
            x, y = yao.grid_x, yao.grid_y
            if x == y:
                main_diag.append(yao)
            if x + y == 7:
                anti_diag.append(yao)

        results["diagonal_analysis"] = {
            "main_diagonal": {
                "total": len(main_diag),
                "special": sum(1 for y in main_diag if y.needs_yici)
            },
            "anti_diagonal": {
                "total": len(anti_diag),
                "special": sum(1 for y in anti_diag if y.needs_yici)
            }
        }

        return results

    def visualize_2d(self) -> str:
        """生成2D網格可視化"""
        lines = []
        lines.append("="*80)
        lines.append("2D 八卦布局分析 - 特殊爻空間分布")
        lines.append("="*80)

        # 八卦名稱
        bagua_names = ["坤", "震", "坎", "兌", "艮", "離", "巽", "乾"]

        # 建立網格統計
        special_grid = [[0 for _ in range(8)] for _ in range(8)]
        total_grid = [[0 for _ in range(8)] for _ in range(8)]

        for yao in self.analyzed_yaos:
            x, y = yao.grid_x, yao.grid_y
            total_grid[y][x] += 1
            if yao.needs_yici:
                special_grid[y][x] += 1

        # 顯示網格
        lines.append("\n特殊爻分布網格 (數字=需爻辭的爻數/總爻數):\n")
        lines.append("上卦→  " + "   ".join(f"{name}" for name in bagua_names))
        lines.append("下卦↓  " + "   ".join(f" {i} " for i in range(8)))
        lines.append("      ╔" + "═══╤"*7 + "═══╗")

        for y in range(7, -1, -1):
            row = f"{bagua_names[y]} {y} ║"
            for x in range(8):
                total = total_grid[y][x]
                special = special_grid[y][x]
                if total > 0:
                    row += f"{special}/{total}│"
                else:
                    row += " · │"
            lines.append(row[:-1] + "║")
            if y > 0:
                lines.append("      ╟" + "───┼"*7 + "───╢")

        lines.append("      ╚" + "═══╧"*7 + "═══╝")

        return "\n".join(lines)

    # ============================================================
    # 數學模式分析
    # ============================================================

    def analyze_mathematical_patterns(self) -> Dict:
        """分析數學模式"""
        results = {
            "fibonacci_correlation": {},
            "golden_ratio": {},
            "prime_numbers": {},
            "modular_patterns": {},
        }

        positions = sorted([y.linear_position for y in self.special_yaos])

        # Fibonacci相關性
        fib_matches = 0
        for p in positions:
            if p in FIBONACCI or (p - 1) in FIBONACCI:
                fib_matches += 1
        results["fibonacci_correlation"] = {
            "matches": fib_matches,
            "total": len(positions),
            "ratio": fib_matches / len(positions) if positions else 0
        }

        # 黃金比例測試
        golden_positions = []
        for i in range(1, 10):
            gp = round(384 * (PHI ** (-i)), 0)
            if 1 <= gp <= 384:
                golden_positions.append(int(gp))

        gp_matches = sum(1 for p in positions if p in golden_positions)
        results["golden_ratio"] = {
            "golden_positions": golden_positions,
            "matches": gp_matches,
            "positions": positions
        }

        # 質數測試
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True

        prime_count = sum(1 for p in positions if is_prime(p))
        results["prime_numbers"] = {
            "prime_positions": [p for p in positions if is_prime(p)],
            "prime_count": prime_count,
            "prime_ratio": prime_count / len(positions) if positions else 0
        }

        return results

    # ============================================================
    # 節氣對應分析
    # ============================================================

    def analyze_solar_terms(self) -> Dict:
        """分析與節氣的對應關係"""
        results = {
            "gua_to_term_mapping": {},
            "special_in_term": {},
        }

        # 64卦對應24節氣（每節氣約2.67卦）
        # 簡化映射：每3卦對應1節氣
        for gua_num in range(1, 65):
            term_index = ((gua_num - 1) // 3) % 24
            results["gua_to_term_mapping"][gua_num] = {
                "term_index": term_index,
                "term_name": SOLAR_TERMS_24[term_index]
            }

        # 統計特殊爻在各節氣的分布
        term_special_count = defaultdict(int)
        term_total_count = defaultdict(int)

        for yao in self.analyzed_yaos:
            term_index = ((yao.gua_num - 1) // 3) % 24
            term_total_count[term_index] += 1
            if yao.needs_yici:
                term_special_count[term_index] += 1

        for i, term in enumerate(SOLAR_TERMS_24):
            results["special_in_term"][term] = {
                "special": term_special_count[i],
                "total": term_total_count[i],
                "ratio": term_special_count[i] / term_total_count[i] if term_total_count[i] > 0 else 0
            }

        return results

    # ============================================================
    # 綜合報告
    # ============================================================

    def generate_report(self) -> str:
        """生成完整分析報告"""
        self.analyze_all()

        lines = []
        lines.append("╔" + "═"*78 + "╗")
        lines.append("║" + " 爻辭特殊標記模式分析報告 ".center(78) + "║")
        lines.append("╚" + "═"*78 + "╝")
        lines.append("")

        # 基本統計
        lines.append("【基本統計】")
        lines.append(f"  總樣本數: {len(self.analyzed_yaos)}")
        lines.append(f"  可預測爻: {len(self.analyzed_yaos) - len(self.special_yaos)}")
        lines.append(f"  需爻辭爻: {len(self.special_yaos)} ({len(self.special_yaos)/len(self.analyzed_yaos)*100:.1f}%)")
        lines.append("")

        # 1D分析
        lines.append(self.visualize_1d())
        lines.append("")

        linear_results = self.analyze_1d_linear()
        lines.append("\n【1D間距分析】")
        lines.append(f"  位置間距: {linear_results['intervals']}")
        lines.append(f"  Fibonacci匹配: {linear_results['fibonacci_matches']}")
        lines.append(f"  黃金分割點 (384/φ): {linear_results['golden_ratio_analysis']['golden_point']}")
        lines.append("")

        # 2D分析
        lines.append(self.visualize_2d())
        lines.append("")

        bagua_results = self.analyze_2d_bagua()
        lines.append("\n【2D象限分析】")
        for q_name, q_data in bagua_results["quadrant_analysis"].items():
            if q_data["total"] > 0:
                ratio = q_data["special"] / q_data["total"] * 100
                lines.append(f"  {q_name}: {q_data['special']}/{q_data['total']} ({ratio:.1f}%)")
        lines.append("")

        # 數學模式
        math_results = self.analyze_mathematical_patterns()
        lines.append("\n【數學模式分析】")
        lines.append(f"  Fibonacci相關: {math_results['fibonacci_correlation']}")
        lines.append(f"  黃金比例相關: {math_results['golden_ratio']['matches']}個位置匹配")
        lines.append(f"  質數位置: {math_results['prime_numbers']['prime_positions']}")
        lines.append("")

        # 節氣分析
        solar_results = self.analyze_solar_terms()
        lines.append("\n【節氣對應分析】")
        high_ratio_terms = [(t, d) for t, d in solar_results["special_in_term"].items()
                           if d["ratio"] > 0.5 and d["total"] > 0]
        if high_ratio_terms:
            lines.append("  高比例節氣 (>50%需爻辭):")
            for term, data in high_ratio_terms:
                lines.append(f"    {term}: {data['special']}/{data['total']} ({data['ratio']*100:.0f}%)")
        lines.append("")

        # 詳細清單
        lines.append("\n【需爻辭的爻清單】")
        for yao in self.special_yaos:
            pred_str = {1: "吉", 0: "中", -1: "凶", None: "?"}
            act_str = {1: "吉", 0: "中", -1: "凶"}
            lines.append(f"  {yao.gua_name}({yao.gua_num})第{yao.yao_pos}爻: "
                        f"預測={pred_str[yao.structure_prediction]} 實際={act_str[yao.actual_result]} "
                        f"位置={yao.linear_position} 網格=({yao.grid_x},{yao.grid_y})")

        return "\n".join(lines)

    def export_data(self, filepath: str):
        """導出數據為JSON"""
        self.analyze_all()

        data = {
            "summary": {
                "total_samples": len(self.analyzed_yaos),
                "predictable_count": len(self.analyzed_yaos) - len(self.special_yaos),
                "special_count": len(self.special_yaos),
                "accuracy": (len(self.analyzed_yaos) - len(self.special_yaos)) / len(self.analyzed_yaos)
            },
            "special_yaos": [
                {
                    "gua_num": y.gua_num,
                    "gua_name": y.gua_name,
                    "yao_pos": y.yao_pos,
                    "binary": y.binary,
                    "actual_result": y.actual_result,
                    "structure_prediction": y.structure_prediction,
                    "linear_position": y.linear_position,
                    "grid_x": y.grid_x,
                    "grid_y": y.grid_y,
                }
                for y in self.special_yaos
            ],
            "linear_analysis": self.analyze_1d_linear(),
            "bagua_analysis": {
                "quadrant_analysis": self.analyze_2d_bagua()["quadrant_analysis"],
                "diagonal_analysis": self.analyze_2d_bagua()["diagonal_analysis"],
            },
            "mathematical_patterns": self.analyze_mathematical_patterns(),
            "solar_terms": self.analyze_solar_terms(),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath


# ============================================================
# 主程序
# ============================================================

def main():
    print("開始爻辭特殊標記模式分析...\n")

    analyzer = PatternAnalyzer()

    # 生成報告
    report = analyzer.generate_report()
    print(report)

    # 導出數據
    export_path = "pattern_analysis_data.json"
    analyzer.export_data(export_path)
    print(f"\n數據已導出至: {export_path}")


if __name__ == "__main__":
    main()
