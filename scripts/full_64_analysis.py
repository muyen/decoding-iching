#!/usr/bin/env python3
"""
完整64卦384爻分析

從原始爻辭文本中提取吉凶判斷，然後進行模式分析
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import os

# ============================================================
# 吉凶關鍵詞
# ============================================================

# 吉的關鍵詞（按權重排序）
JI_KEYWORDS = {
    "元吉": 2,      # 大吉
    "大吉": 2,
    "吉": 1,
    "利": 0.5,
    "亨": 0.5,
    "無咎": 0.3,    # 無過錯，偏向中性偏吉
    "有慶": 1,
    "有喜": 1,
    "終吉": 0.8,
    "貞吉": 0.8,
}

# 凶的關鍵詞（按權重排序）
XIONG_KEYWORDS = {
    "大凶": -2,
    "凶": -1,
    "咎": -0.5,     # 有過錯
    "厲": -0.5,     # 危險
    "悔": -0.5,     # 後悔
    "吝": -0.3,     # 困難
    "災": -0.8,
    "眚": -0.5,     # 過失
    "窮": -0.5,
    "終凶": -1,
    "往凶": -0.8,
    "不利": -0.5,
}

# 八卦二進制對應
TRIGRAM_TO_BINARY = {
    "乾": "111", "兌": "011", "離": "101", "震": "001",
    "巽": "110", "坎": "010", "艮": "100", "坤": "000"
}

# ============================================================
# 數據結構
# ============================================================

@dataclass
class YaoData:
    """單爻數據"""
    gua_num: int
    gua_name: str
    position: int  # 1-6
    text: str
    binary: str
    upper_trigram: str
    lower_trigram: str
    ji_score: float
    judgment: int  # 1=吉, 0=中, -1=凶
    keywords_found: List[str]

# ============================================================
# 解析器
# ============================================================

class FullYaoAnalyzer:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.yaos: List[YaoData] = []
        self.load_and_parse()

    def load_and_parse(self):
        """載入並解析JSON數據"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for hexagram in data['hexagrams']:
            gua_num = hexagram['number']
            gua_name = hexagram['name']

            # 獲取卦的二進制表示
            upper = hexagram['trigrams']['upper']
            lower = hexagram['trigrams']['lower']
            upper_bin = TRIGRAM_TO_BINARY.get(upper, "000")
            lower_bin = TRIGRAM_TO_BINARY.get(lower, "000")
            binary = upper_bin + lower_bin

            # 解析每個爻辭
            yaoci_list = hexagram.get('yaoci', [])
            for i, yaoci in enumerate(yaoci_list):
                position_str = yaoci['position']
                text = yaoci['text']

                # 提取位置（1-6）
                position = self._parse_position(position_str)
                if position is None or position > 6:
                    continue  # 跳過用九/用六

                # 計算吉凶分數
                score, keywords = self._calculate_ji_score(text)
                judgment = self._score_to_judgment(score)

                yao = YaoData(
                    gua_num=gua_num,
                    gua_name=gua_name,
                    position=position,
                    text=text,
                    binary=binary,
                    upper_trigram=upper,
                    lower_trigram=lower,
                    ji_score=score,
                    judgment=judgment,
                    keywords_found=keywords
                )
                self.yaos.append(yao)

        print(f"載入完成: {len(self.yaos)} 爻")

    def _parse_position(self, pos_str: str) -> Optional[int]:
        """解析爻位"""
        pos_map = {
            "初": 1, "二": 2, "三": 3, "四": 4, "五": 5, "上": 6,
            "初九": 1, "初六": 1,
            "九二": 2, "六二": 2,
            "九三": 3, "六三": 3,
            "九四": 4, "六四": 4,
            "九五": 5, "六五": 5,
            "上九": 6, "上六": 6,
        }

        for key, val in pos_map.items():
            if key in pos_str:
                return val
        return None

    def _calculate_ji_score(self, text: str) -> Tuple[float, List[str]]:
        """計算爻辭的吉凶分數"""
        score = 0.0
        found_keywords = []

        # 檢查吉的關鍵詞
        for keyword, weight in JI_KEYWORDS.items():
            if keyword in text:
                score += weight
                found_keywords.append(f"+{keyword}")

        # 檢查凶的關鍵詞
        for keyword, weight in XIONG_KEYWORDS.items():
            if keyword in text:
                score += weight  # weight已經是負數
                found_keywords.append(f"-{keyword}")

        # 特殊處理：有條件的判斷
        # "無咎" 在有 "厲" 的情況下表示危險但無過
        if "厲" in text and "無咎" in text:
            score += 0.2  # 稍微調整

        return score, found_keywords

    def _score_to_judgment(self, score: float) -> int:
        """將分數轉換為吉凶判斷"""
        if score >= 0.5:
            return 1   # 吉
        elif score <= -0.3:
            return -1  # 凶
        else:
            return 0   # 中

    # ============================================================
    # 統計分析
    # ============================================================

    def get_statistics(self) -> Dict:
        """獲取統計數據"""
        stats = {
            "total": len(self.yaos),
            "ji": sum(1 for y in self.yaos if y.judgment == 1),
            "zhong": sum(1 for y in self.yaos if y.judgment == 0),
            "xiong": sum(1 for y in self.yaos if y.judgment == -1),
        }
        stats["ji_rate"] = stats["ji"] / stats["total"] * 100
        stats["zhong_rate"] = stats["zhong"] / stats["total"] * 100
        stats["xiong_rate"] = stats["xiong"] / stats["total"] * 100
        return stats

    def get_by_position(self) -> Dict[int, Dict]:
        """按爻位統計"""
        by_pos = defaultdict(lambda: {"total": 0, "ji": 0, "zhong": 0, "xiong": 0})

        for yao in self.yaos:
            pos = yao.position
            by_pos[pos]["total"] += 1
            if yao.judgment == 1:
                by_pos[pos]["ji"] += 1
            elif yao.judgment == 0:
                by_pos[pos]["zhong"] += 1
            else:
                by_pos[pos]["xiong"] += 1

        # 計算比率
        for pos in by_pos:
            total = by_pos[pos]["total"]
            by_pos[pos]["ji_rate"] = by_pos[pos]["ji"] / total * 100 if total > 0 else 0
            by_pos[pos]["xiong_rate"] = by_pos[pos]["xiong"] / total * 100 if total > 0 else 0

        return dict(by_pos)

    def get_by_trigram(self) -> Dict:
        """按上下卦統計"""
        by_upper = defaultdict(lambda: {"total": 0, "ji": 0, "xiong": 0})
        by_lower = defaultdict(lambda: {"total": 0, "ji": 0, "xiong": 0})

        for yao in self.yaos:
            # 上卦
            by_upper[yao.upper_trigram]["total"] += 1
            if yao.judgment == 1:
                by_upper[yao.upper_trigram]["ji"] += 1
            elif yao.judgment == -1:
                by_upper[yao.upper_trigram]["xiong"] += 1

            # 下卦
            by_lower[yao.lower_trigram]["total"] += 1
            if yao.judgment == 1:
                by_lower[yao.lower_trigram]["ji"] += 1
            elif yao.judgment == -1:
                by_lower[yao.lower_trigram]["xiong"] += 1

        # 計算比率
        for trigram in by_upper:
            total = by_upper[trigram]["total"]
            by_upper[trigram]["ji_rate"] = by_upper[trigram]["ji"] / total * 100 if total > 0 else 0
        for trigram in by_lower:
            total = by_lower[trigram]["total"]
            by_lower[trigram]["ji_rate"] = by_lower[trigram]["ji"] / total * 100 if total > 0 else 0

        return {"upper": dict(by_upper), "lower": dict(by_lower)}

    # ============================================================
    # 結構預測與特殊爻識別
    # ============================================================

    def predict_by_structure(self, yao: YaoData) -> int:
        """純結構預測"""
        pos = yao.position
        binary = yao.binary
        upper = int(binary[0:3], 2)
        lower = int(binary[3:6], 2)
        xor_val = upper ^ lower
        is_central = pos in [2, 5]
        line = int(binary[6 - pos])

        # 100%規則
        if xor_val == 4 and pos <= 4:
            return 1
        if xor_val == 0 and is_central:
            return 1
        if upper == 0 and pos == 2:
            return 1

        # 加權打分
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

    def identify_special_yaos(self) -> List[YaoData]:
        """識別需要爻辭的特殊爻"""
        special = []
        for yao in self.yaos:
            prediction = self.predict_by_structure(yao)
            if prediction != yao.judgment:
                special.append(yao)
        return special

    def get_accuracy(self) -> float:
        """計算結構預測準確率"""
        correct = 0
        for yao in self.yaos:
            if self.predict_by_structure(yao) == yao.judgment:
                correct += 1
        return correct / len(self.yaos) * 100 if self.yaos else 0

    # ============================================================
    # 報告生成
    # ============================================================

    def generate_report(self) -> str:
        """生成完整分析報告"""
        lines = []
        lines.append("╔" + "═"*78 + "╗")
        lines.append("║" + " 完整64卦384爻分析報告 ".center(78) + "║")
        lines.append("╚" + "═"*78 + "╝")
        lines.append("")

        # 基本統計
        stats = self.get_statistics()
        lines.append("【一、基本統計】")
        lines.append(f"  總爻數: {stats['total']}")
        lines.append(f"  吉: {stats['ji']} ({stats['ji_rate']:.1f}%)")
        lines.append(f"  中: {stats['zhong']} ({stats['zhong_rate']:.1f}%)")
        lines.append(f"  凶: {stats['xiong']} ({stats['xiong_rate']:.1f}%)")
        lines.append("")

        # 按爻位統計
        by_pos = self.get_by_position()
        lines.append("【二、按爻位統計】")
        lines.append("  爻位  總數  吉    中    凶    吉率    凶率")
        lines.append("  " + "-"*55)
        for pos in range(1, 7):
            p = by_pos[pos]
            lines.append(f"  {pos}     {p['total']:3d}   {p['ji']:3d}   {p['zhong']:3d}   {p['xiong']:3d}   "
                        f"{p['ji_rate']:5.1f}%  {p['xiong_rate']:5.1f}%")
        lines.append("")

        # 按上下卦統計
        by_trigram = self.get_by_trigram()
        lines.append("【三、按上卦統計】")
        lines.append("  上卦  總數  吉    吉率")
        lines.append("  " + "-"*30)
        for trigram, data in sorted(by_trigram["upper"].items(), key=lambda x: -x[1]["ji_rate"]):
            lines.append(f"  {trigram}    {data['total']:3d}   {data['ji']:3d}   {data['ji_rate']:5.1f}%")
        lines.append("")

        lines.append("【四、按下卦統計】")
        lines.append("  下卦  總數  吉    吉率")
        lines.append("  " + "-"*30)
        for trigram, data in sorted(by_trigram["lower"].items(), key=lambda x: -x[1]["ji_rate"]):
            lines.append(f"  {trigram}    {data['total']:3d}   {data['ji']:3d}   {data['ji_rate']:5.1f}%")
        lines.append("")

        # 結構預測準確率
        accuracy = self.get_accuracy()
        special_yaos = self.identify_special_yaos()
        lines.append("【五、結構預測分析】")
        lines.append(f"  準確率: {accuracy:.1f}%")
        lines.append(f"  可預測爻: {len(self.yaos) - len(special_yaos)}")
        lines.append(f"  需爻辭爻: {len(special_yaos)} ({len(special_yaos)/len(self.yaos)*100:.1f}%)")
        lines.append("")

        # 特殊爻詳情
        lines.append("【六、需爻辭的爻（前30個）】")
        for i, yao in enumerate(special_yaos[:30]):
            pred = self.predict_by_structure(yao)
            pred_str = {1: "吉", 0: "中", -1: "凶"}
            act_str = {1: "吉", 0: "中", -1: "凶"}
            linear_pos = (yao.gua_num - 1) * 6 + yao.position
            lines.append(f"  {yao.gua_name}({yao.gua_num})第{yao.position}爻: "
                        f"預測={pred_str[pred]} 實際={act_str[yao.judgment]} 位置={linear_pos}")
        if len(special_yaos) > 30:
            lines.append(f"  ... 還有 {len(special_yaos) - 30} 個")
        lines.append("")

        return "\n".join(lines)

    # ============================================================
    # 模式分析
    # ============================================================

    def analyze_special_yao_patterns(self) -> Dict:
        """分析特殊爻的模式"""
        special_yaos = self.identify_special_yaos()

        # 線性位置
        positions = sorted([(y.gua_num - 1) * 6 + y.position for y in special_yaos])

        # 間距分析
        intervals = [positions[i+1] - positions[i] for i in range(len(positions)-1)] if len(positions) > 1 else []

        # 間距統計
        interval_counts = defaultdict(int)
        for i in intervals:
            interval_counts[i] += 1

        # 聚集分析
        small_intervals = [i for i in intervals if i <= 5]
        large_intervals = [i for i in intervals if i > 20]

        # Fibonacci檢測
        fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
        fib_matches = [i for i in intervals if i in fibonacci]

        results = {
            "total_special": len(special_yaos),
            "positions": positions,
            "intervals": intervals,
            "interval_distribution": dict(interval_counts),
            "small_interval_ratio": len(small_intervals) / len(intervals) * 100 if intervals else 0,
            "large_intervals": large_intervals,
            "fibonacci_matches": len(fib_matches),
            "fibonacci_ratio": len(fib_matches) / len(intervals) * 100 if intervals else 0,
        }

        return results

    def export_data(self, filepath: str):
        """導出數據"""
        data = {
            "statistics": self.get_statistics(),
            "by_position": self.get_by_position(),
            "by_trigram": self.get_by_trigram(),
            "accuracy": self.get_accuracy(),
            "special_yaos": [
                {
                    "gua_num": y.gua_num,
                    "gua_name": y.gua_name,
                    "position": y.position,
                    "text": y.text[:50] + "..." if len(y.text) > 50 else y.text,
                    "judgment": y.judgment,
                    "keywords": y.keywords_found,
                }
                for y in self.identify_special_yaos()
            ],
            "pattern_analysis": self.analyze_special_yao_patterns(),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"數據已導出至: {filepath}")


# ============================================================
# 主程序
# ============================================================

def main():
    print("="*60)
    print(" 完整64卦384爻分析")
    print("="*60)
    print()

    json_path = "data/zhouyi-64gua/zhouyi_64gua.json"

    if not os.path.exists(json_path):
        print(f"錯誤: 找不到文件 {json_path}")
        return

    analyzer = FullYaoAnalyzer(json_path)

    # 生成報告
    report = analyzer.generate_report()
    print(report)

    # 模式分析
    patterns = analyzer.analyze_special_yao_patterns()
    print("\n【七、特殊爻模式分析】")
    print(f"  特殊爻總數: {patterns['total_special']}")
    print(f"  小間距比例(≤5): {patterns['small_interval_ratio']:.1f}%")
    print(f"  大間距數量(>20): {len(patterns['large_intervals'])}")
    print(f"  大間距值: {patterns['large_intervals']}")
    print(f"  Fibonacci匹配: {patterns['fibonacci_matches']}/{len(patterns['intervals'])} ({patterns['fibonacci_ratio']:.1f}%)")

    # 間距分布
    print("\n  間距頻率 (Top 10):")
    sorted_intervals = sorted(patterns['interval_distribution'].items(), key=lambda x: -x[1])
    for interval, count in sorted_intervals[:10]:
        print(f"    間距 {interval}: {count} 次")

    # 導出
    export_path = "data/analysis/full_64_analysis.json"
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    analyzer.export_data(export_path)


if __name__ == "__main__":
    main()
