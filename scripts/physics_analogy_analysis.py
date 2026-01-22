#!/usr/bin/env python3
"""
物理定律與易經規律的對應分析

假設：易經觀察自然規律，物理定律應該能解釋易經模式

可能的對應：
1. 熱力學 - 熵、能量流動、平衡
2. 資訊理論 - 熵、狀態數
3. 動力學 - 穩定性、相變
4. 博弈論 - 選擇空間、優勢
"""

import json
import math
from pathlib import Path
from collections import defaultdict


def load_data():
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_entropy(binary):
    """
    計算卦象的資訊熵

    熵 = 系統的無序程度 / 可能狀態數
    高熵 = 更多變化可能 = 更吉？
    """
    ones = binary.count('1')
    zeros = binary.count('0')
    n = len(binary)

    if ones == 0 or zeros == 0:
        return 0  # 純陽或純陰，熵為0

    p1 = ones / n
    p0 = zeros / n

    entropy = -p1 * math.log2(p1) - p0 * math.log2(p0)
    return entropy


def calculate_potential_energy(binary, position):
    """
    位能類比

    高位置 = 高位能 = 可以「做功」= 有發展空間？
    三爻在「山谷」= 位能最低？
    """
    # 位置的「高度」
    height_map = {
        1: 1,  # 初爻，最底
        2: 2,  # 二爻
        3: 2,  # 三爻，下卦頂但也是低谷
        4: 3,  # 四爻
        5: 4,  # 五爻，最高
        6: 3,  # 上爻，開始下降
    }
    return height_map.get(position, 2)


def calculate_kinetic_energy(binary, position):
    """
    動能類比

    變化的「速度」= 周圍的陰陽轉換
    更多轉換 = 更多動能 = 更活躍？
    """
    yao = [int(b) for b in reversed(binary)]  # 從初爻開始
    pos_idx = position - 1

    # 計算該爻與相鄰爻的差異
    transitions = 0
    if pos_idx > 0 and yao[pos_idx] != yao[pos_idx - 1]:
        transitions += 1
    if pos_idx < 5 and yao[pos_idx] != yao[pos_idx + 1]:
        transitions += 1

    return transitions


def calculate_degrees_of_freedom(position):
    """
    自由度類比 (來自統計力學)

    自由度 = 系統可以獨立變化的方向數
    更多自由度 = 更多可能性 = 更吉？
    """
    freedom_map = {
        1: 2,  # 初爻：可上、可變
        2: 3,  # 二爻：可上、可下、得中
        3: 1,  # 三爻：卡住，只能往上
        4: 2,  # 四爻：可上、可退
        5: 3,  # 五爻：可上、可下、得中且有權
        6: 1,  # 上爻：只能下
    }
    return freedom_map.get(position, 2)


def calculate_stability(binary):
    """
    穩定性類比 (動力學)

    穩定態 = 小擾動後會回復
    不穩定態 = 小擾動後會崩潰

    對稱結構 = 更穩定？
    """
    yao = [int(b) for b in reversed(binary)]

    # 檢查上下卦的對稱性
    lower = yao[:3]
    upper = yao[3:]

    # XOR對稱 (互為錯卦)
    xor_symmetric = all(l != u for l, u in zip(lower, upper))

    # 鏡像對稱
    mirror_symmetric = lower == upper[::-1]

    # 相同
    same = lower == upper

    if xor_symmetric:
        return "XOR對稱"
    elif mirror_symmetric:
        return "鏡像對稱"
    elif same:
        return "上下相同"
    else:
        return "不對稱"


def analyze_thermodynamics(data):
    """熱力學第二定律：熵增原理"""
    print("\n" + "=" * 70)
    print("物理類比1：熱力學（熵）")
    print("=" * 70)
    print("\n假設：高熵 = 更多可能狀態 = 更吉？")

    entropy_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})

    for item in data:
        entropy = calculate_entropy(item['binary'])
        label = item['label']

        # 分組
        if entropy == 0:
            group = "熵=0 (純陽/純陰)"
        elif entropy < 0.9:
            group = "低熵 (<0.9)"
        else:
            group = "高熵 (≈1.0)"

        entropy_stats[group]['total'] += 1
        if label == 1:
            entropy_stats[group]['ji'] += 1
        elif label == -1:
            entropy_stats[group]['xiong'] += 1

    print("\n結果：")
    print("-" * 50)
    for group in ["熵=0 (純陽/純陰)", "低熵 (<0.9)", "高熵 (≈1.0)"]:
        if group in entropy_stats:
            stats = entropy_stats[group]
            if stats['total'] > 0:
                ji_rate = stats['ji'] / stats['total'] * 100
                print(f"  {group}: 吉率={ji_rate:.1f}% (n={stats['total']})")

    print("\n物理解釋：")
    print("  熵=0 意味著系統處於「有序極限」")
    print("  高熵意味著系統有更多可能的微觀狀態")
    print("  熱力學告訴我們：封閉系統趨向高熵")


def analyze_potential_energy(data):
    """位能分析"""
    print("\n" + "=" * 70)
    print("物理類比2：力學（位能）")
    print("=" * 70)
    print("\n假設：高位能 = 可以做功 = 有發展空間 = 更吉？")

    pe_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})

    for item in data:
        pe = calculate_potential_energy(item['binary'], item['position'])
        label = item['label']

        pe_stats[pe]['total'] += 1
        if label == 1:
            pe_stats[pe]['ji'] += 1
        elif label == -1:
            pe_stats[pe]['xiong'] += 1

    print("\n結果：")
    print("-" * 50)
    for pe in sorted(pe_stats.keys()):
        stats = pe_stats[pe]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            print(f"  位能={pe}: 吉率={ji_rate:.1f}% (n={stats['total']})")

    print("\n物理解釋：")
    print("  位能高 = 有勢能可以轉化 = 有發展空間")
    print("  位能低 = 在低谷 = 難以發展")


def analyze_degrees_of_freedom(data):
    """自由度分析（統計力學）"""
    print("\n" + "=" * 70)
    print("物理類比3：統計力學（自由度）")
    print("=" * 70)
    print("\n假設：更多自由度 = 更多可能的變化方向 = 更吉？")

    dof_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})

    for item in data:
        dof = calculate_degrees_of_freedom(item['position'])
        label = item['label']

        dof_stats[dof]['total'] += 1
        if label == 1:
            dof_stats[dof]['ji'] += 1
        elif label == -1:
            dof_stats[dof]['xiong'] += 1

    print("\n結果：")
    print("-" * 50)
    for dof in sorted(dof_stats.keys()):
        stats = dof_stats[dof]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            xiong_rate = stats['xiong'] / stats['total'] * 100
            print(f"  自由度={dof}: 吉率={ji_rate:.1f}%, 凶率={xiong_rate:.1f}% (n={stats['total']})")

    print("\n物理解釋：")
    print("  自由度 = 系統可以獨立變化的方向數")
    print("  更多自由度 = 更靈活 = 更能適應變化")
    print("  三爻和上爻自由度最低 = 最受限 = 最凶")


def analyze_stability(data):
    """穩定性分析（動力學）"""
    print("\n" + "=" * 70)
    print("物理類比4：動力學（穩定性）")
    print("=" * 70)
    print("\n假設：對稱結構更穩定？還是更僵化？")

    stability_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})

    for item in data:
        stability = calculate_stability(item['binary'])
        label = item['label']

        stability_stats[stability]['total'] += 1
        if label == 1:
            stability_stats[stability]['ji'] += 1
        elif label == -1:
            stability_stats[stability]['xiong'] += 1

    print("\n結果：")
    print("-" * 50)
    for stability, stats in stability_stats.items():
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            print(f"  {stability}: 吉率={ji_rate:.1f}% (n={stats['total']})")


def analyze_yang_count_as_energy(data):
    """陽爻數量作為總能量"""
    print("\n" + "=" * 70)
    print("物理類比5：能量守恆")
    print("=" * 70)
    print("\n假設：陽爻數 = 系統總能量")

    energy_stats = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})

    for item in data:
        yang_count = item['binary'].count('1')
        label = item['label']

        energy_stats[yang_count]['total'] += 1
        if label == 1:
            energy_stats[yang_count]['ji'] += 1
        elif label == -1:
            energy_stats[yang_count]['xiong'] += 1

    print("\n結果：")
    print("-" * 50)
    for energy in sorted(energy_stats.keys()):
        stats = energy_stats[energy]
        if stats['total'] > 0:
            ji_rate = stats['ji'] / stats['total'] * 100
            bar = '█' * int(ji_rate / 5)
            print(f"  {energy}陽爻: 吉率={ji_rate:5.1f}% (n={stats['total']:3d}) {bar}")

    print("\n物理解釋：")
    print("  最佳不是最高能量(6陽)，而是中等能量(3-4陽)")
    print("  類似熱力學：最穩定不是最高能量，而是適中狀態")


def print_physics_theory():
    """輸出物理理論總結"""
    print("\n" + "=" * 70)
    print("物理定律與易經的對應")
    print("=" * 70)
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    物理定律 ↔ 易經規律                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  【熱力學第二定律】                                                  │
│  熵增原理：封閉系統趨向無序                                         │
│  ↔ 易經：純陽(乾)=有序極限=無法再變=凶                             │
│     混合陰陽=高熵=更多可能=吉                                       │
│                                                                     │
│  【力學能量守恆】                                                    │
│  位能+動能=常數，位能可轉化                                         │
│  ↔ 易經：五爻位高=有勢能=可做功=吉                                 │
│     三爻位低=在低谷=無勢能=凶                                       │
│                                                                     │
│  【統計力學】                                                        │
│  自由度=獨立變化的方向數                                            │
│  ↔ 易經：二五爻自由度高=靈活=吉                                    │
│     三爻上爻自由度低=受限=凶                                        │
│                                                                     │
│  【動力系統理論】                                                    │
│  穩定態vs不穩定態                                                   │
│  ↔ 易經：過於穩定(對稱)=僵化=不一定吉                              │
│     適度不穩定=有變化空間=吉                                        │
│                                                                     │
│  【耗散結構理論】(普里高津)                                          │
│  遠離平衡態的系統可以自組織                                         │
│  ↔ 易經：體用平衡=凶，體強用弱(不平衡)=吉                          │
│     不平衡創造變化的動力！                                          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    統一洞見                                          │
│                                                                     │
│  易經的「吉」= 物理的「能做功的狀態」                               │
│                                                                     │
│  - 有位能差 = 能做功 = 吉                                           │
│  - 有自由度 = 能變化 = 吉                                           │
│  - 有熵增空間 = 能演化 = 吉                                         │
│  - 不平衡 = 有驅動力 = 吉                                           │
│                                                                     │
│  易經的「凶」= 物理的「平衡/極限狀態」                              │
│                                                                     │
│  - 位能最低 = 無法做功 = 凶                                         │
│  - 自由度為零 = 無法變化 = 凶                                       │
│  - 熵已最大 = 無法演化 = 凶                                         │
│  - 完美平衡 = 無驅動力 = 凶                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
    """)


def main():
    print("=" * 70)
    print("物理定律與易經規律對應分析")
    print("=" * 70)

    data = load_data()
    print(f"\n載入 {len(data)} 條爻數據")

    analyze_thermodynamics(data)
    analyze_potential_energy(data)
    analyze_degrees_of_freedom(data)
    analyze_stability(data)
    analyze_yang_count_as_energy(data)

    print_physics_theory()


if __name__ == '__main__':
    main()
