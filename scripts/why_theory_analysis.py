#!/usr/bin/env python3
"""
探索「為什麼」的理論分析

核心假設：易經是一個「變化可行性評估系統」
- 吉 = 有發展空間、變化可行
- 凶 = 被阻塞、變化受阻
"""

import json
from pathlib import Path
from collections import defaultdict

# 卦序對應的上下卦
HEXAGRAM_TRIGRAMS = {
    1: ('乾', '乾'), 2: ('坤', '坤'), 3: ('震', '坎'), 4: ('坎', '艮'),
    5: ('乾', '坎'), 6: ('坎', '乾'), 7: ('坎', '坤'), 8: ('坤', '坎'),
    9: ('乾', '巽'), 10: ('兌', '乾'), 11: ('乾', '坤'), 12: ('坤', '乾'),
    13: ('離', '乾'), 14: ('乾', '離'), 15: ('艮', '坤'), 16: ('坤', '震'),
    17: ('兌', '震'), 18: ('巽', '艮'), 19: ('兌', '坤'), 20: ('坤', '巽'),
    21: ('震', '離'), 22: ('離', '艮'), 23: ('艮', '坤'), 24: ('坤', '震'),
    25: ('震', '乾'), 26: ('乾', '艮'), 27: ('震', '艮'), 28: ('兌', '巽'),
    29: ('坎', '坎'), 30: ('離', '離'), 31: ('兌', '艮'), 32: ('巽', '震'),
    33: ('艮', '乾'), 34: ('乾', '震'), 35: ('坤', '離'), 36: ('離', '坤'),
    37: ('離', '巽'), 38: ('兌', '離'), 39: ('艮', '坎'), 40: ('坎', '震'),
    41: ('兌', '艮'), 42: ('巽', '震'), 43: ('兌', '乾'), 44: ('乾', '巽'),
    45: ('兌', '坤'), 46: ('坤', '巽'), 47: ('兌', '坎'), 48: ('坎', '巽'),
    49: ('兌', '離'), 50: ('離', '巽'), 51: ('震', '震'), 52: ('艮', '艮'),
    53: ('艮', '巽'), 54: ('兌', '震'), 55: ('震', '離'), 56: ('離', '艮'),
    57: ('巽', '巽'), 58: ('兌', '兌'), 59: ('坎', '巽'), 60: ('兌', '坎'),
    61: ('兌', '巽'), 62: ('震', '艮'), 63: ('坎', '離'), 64: ('離', '坎'),
}

# 八卦德性 (說卦傳)
TRIGRAM_VIRTUES = {
    '乾': {'virtue': '健', 'nature': '不停向前', 'dynamics': 'active'},
    '坤': {'virtue': '順', 'nature': '柔順配合', 'dynamics': 'receptive'},
    '震': {'virtue': '動', 'nature': '突然爆發', 'dynamics': 'active'},
    '巽': {'virtue': '入', 'nature': '慢慢滲透', 'dynamics': 'receptive'},
    '坎': {'virtue': '陷', 'nature': '陷入危險', 'dynamics': 'blocking'},
    '離': {'virtue': '麗', 'nature': '需要依附', 'dynamics': 'expressive'},
    '艮': {'virtue': '止', 'nature': '停下阻塞', 'dynamics': 'blocking'},
    '兌': {'virtue': '說', 'nature': '喜悅交流', 'dynamics': 'expressive'},
}

# 位置效應
POSITION_EFFECTS = {
    1: {'score': +0.234, 'meaning': '起始，潛龍勿用'},
    2: {'score': +0.344, 'meaning': '得中，輔佐得力'},
    3: {'score': -0.219, 'meaning': '危位，進退兩難'},
    4: {'score': +0.266, 'meaning': '近君，謹慎補救'},
    5: {'score': +0.422, 'meaning': '君位，領導得正'},
    6: {'score': +0.031, 'meaning': '終結，亢龍有悔'},
}


def load_data():
    """載入384爻數據"""
    data_path = Path(__file__).parent.parent / 'data' / 'analysis' / 'corrected_yaoci_labels.json'
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 添加卦象信息和轉換label
            for item in data:
                hex_num = item.get('hex_num', 0)
                if hex_num in HEXAGRAM_TRIGRAMS:
                    item['lower_trigram'], item['upper_trigram'] = HEXAGRAM_TRIGRAMS[hex_num]
                label_num = item.get('label', 0)
                if label_num == 1:
                    item['label_str'] = '吉'
                elif label_num == -1:
                    item['label_str'] = '凶'
                else:
                    item['label_str'] = '中'
            return data
    return None


def analyze_dynamics_theory(data):
    """
    理論1：變化動態理論

    假設：吉凶取決於「變化的可行性」
    - 有動力 + 有基礎 = 吉（可以變化）
    - 被阻塞 + 沒出路 = 凶（無法變化）
    - 純靜態 = 中性（不需要變化）
    """
    print("\n" + "="*60)
    print("理論1：變化動態理論")
    print("="*60)

    # 分類八卦的動態屬性
    dynamic_types = {
        'active': ['乾', '震'],       # 主動型：推動變化
        'receptive': ['坤', '巽'],    # 接納型：支持變化
        'blocking': ['艮', '坎'],     # 阻塞型：阻礙變化
        'expressive': ['兌', '離'],   # 表達型：需要平台
    }

    # 計算不同組合的吉率
    combo_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0, 'total': 0})

    if data:
        for item in data:
            lower = item.get('lower_trigram', '')
            upper = item.get('upper_trigram', '')
            label = item.get('label_str', '中')

            # 判斷組合類型
            lower_type = None
            upper_type = None
            for dtype, trigrams in dynamic_types.items():
                if lower in trigrams:
                    lower_type = dtype
                if upper in trigrams:
                    upper_type = dtype

            if lower_type and upper_type:
                combo_key = f"{lower_type}→{upper_type}"
                combo_stats[combo_key][label] += 1
                combo_stats[combo_key]['total'] += 1

    # 輸出結果
    print("\n動態組合類型分析：")
    print("-" * 60)
    print(f"{'組合類型':25} {'吉率':>8} {'凶率':>8} {'樣本數':>8}")
    print("-" * 60)

    results = []
    for combo, stats in sorted(combo_stats.items(), key=lambda x: -x[1]['吉']/max(x[1]['total'],1)):
        if stats['total'] > 0:
            ji_rate = stats['吉'] / stats['total'] * 100
            xiong_rate = stats['凶'] / stats['total'] * 100
            results.append({
                'combo': combo,
                'ji_rate': ji_rate,
                'xiong_rate': xiong_rate,
                'total': stats['total']
            })
            print(f"{combo:25} {ji_rate:6.1f}%  {xiong_rate:6.1f}%   n={stats['total']}")

    # 分析驗證
    print("\n驗證「變化可行性」假設：")
    print("-" * 60)

    # 計算各類型的平均吉率
    type_ji = defaultdict(list)
    for r in results:
        combo = r['combo']
        lower, upper = combo.split('→')
        # 計算組合的「變化可行性」分數
        if lower == 'receptive' and upper == 'active':
            type_ji['有基礎+有動力'].append(r['ji_rate'])
        elif lower == 'blocking' and upper == 'blocking':
            type_ji['雙重阻塞'].append(r['ji_rate'])
        elif lower == 'active' and upper in ['receptive', 'active']:
            type_ji['有動力'].append(r['ji_rate'])

    for desc, rates in type_ji.items():
        avg = sum(rates) / len(rates) if rates else 0
        print(f"  {desc}: 平均吉率 = {avg:.1f}%")

    return results


def analyze_freedom_theory(data):
    """
    理論2：自由度理論

    假設：吉凶取決於「可選擇的空間」
    - 有多種選擇 = 吉
    - 只有一條路 = 中性
    - 無路可走 = 凶
    """
    print("\n" + "="*60)
    print("理論2：自由度理論")
    print("="*60)

    # 計算每個位置的「自由度」
    # 初爻：剛開始，選擇多
    # 三爻：卡在中間，進退兩難
    # 上爻：到頂了，沒有上升空間

    freedom_scores = {
        1: 3,  # 起點，多種可能
        2: 4,  # 得中，平衡選擇
        3: 1,  # 夾在中間，進退維谷
        4: 3,  # 可以向上也可以退守
        5: 4,  # 領導位，資源多
        6: 2,  # 到頂了，只能下來
    }

    if data:
        freedom_ji = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})
        for item in data:
            pos = item.get('position', 0)
            if pos == 0:
                continue
            label = item.get('label_str', '中')
            freedom = freedom_scores.get(pos, 0)
            freedom_ji[freedom][label] += 1

        print("\n自由度與吉凶關係：")
        print("-" * 40)
        for freedom in sorted(freedom_ji.keys()):
            stats = freedom_ji[freedom]
            total = sum(stats.values())
            if total > 0:
                ji_rate = stats['吉'] / total * 100
                xiong_rate = stats['凶'] / total * 100
                print(f"自由度={freedom}: 吉率={ji_rate:5.1f}% 凶率={xiong_rate:5.1f}% (n={total})")

        print("\n驗證：自由度越高，吉率越高？")
        print("-" * 40)
        # 計算相關性
        freedom_rates = []
        for freedom in sorted(freedom_ji.keys()):
            stats = freedom_ji[freedom]
            total = sum(stats.values())
            if total > 0:
                ji_rate = stats['吉'] / total
                freedom_rates.append((freedom, ji_rate))

        # 簡單的趨勢分析
        if len(freedom_rates) >= 2:
            low_freedom = [r[1] for r in freedom_rates if r[0] <= 2]
            high_freedom = [r[1] for r in freedom_rates if r[0] >= 3]
            low_avg = sum(low_freedom) / len(low_freedom) if low_freedom else 0
            high_avg = sum(high_freedom) / len(high_freedom) if high_freedom else 0
            print(f"  低自由度(1-2)平均吉率: {low_avg*100:.1f}%")
            print(f"  高自由度(3-4)平均吉率: {high_avg*100:.1f}%")
            if high_avg > low_avg:
                print("  ✓ 驗證通過：自由度越高，吉率越高")
            else:
                print("  ✗ 驗證失敗：自由度與吉率關係不明顯")


def analyze_trigram_interaction(data):
    """
    理論3：卦德交互理論

    分析具體的八卦組合效應
    """
    print("\n" + "="*60)
    print("理論3：卦德交互效應驗證")
    print("="*60)

    if not data:
        return

    # 計算每個卦（上下卦組合）的吉率
    combo_stats = defaultdict(lambda: {'吉': 0, '中': 0, '凶': 0})

    for item in data:
        lower = item.get('lower_trigram', '')
        upper = item.get('upper_trigram', '')
        label = item.get('label_str', '中')
        if lower and upper:
            combo = f"{lower}+{upper}"
            combo_stats[combo][label] += 1

    # 排序輸出
    print("\n卦德組合吉率排行（前10/後10）：")
    print("-" * 50)

    results = []
    for combo, stats in combo_stats.items():
        total = sum(stats.values())
        if total > 0:
            ji_rate = stats['吉'] / total * 100
            xiong_rate = stats['凶'] / total * 100
            results.append({
                'combo': combo,
                'ji_rate': ji_rate,
                'xiong_rate': xiong_rate,
                'total': total
            })

    results.sort(key=lambda x: -x['ji_rate'])

    print("\n【最佳組合 TOP 10】")
    for r in results[:10]:
        print(f"  {r['combo']:10} 吉率:{r['ji_rate']:5.1f}% 凶率:{r['xiong_rate']:5.1f}% (n={r['total']})")

    print("\n【最差組合 BOTTOM 10】")
    for r in results[-10:]:
        print(f"  {r['combo']:10} 吉率:{r['ji_rate']:5.1f}% 凶率:{r['xiong_rate']:5.1f}% (n={r['total']})")

    # 驗證已知規律
    print("\n驗證已知規律：")
    print("-" * 50)

    known_rules = [
        ('坤+震', '最佳', '坤（順）+震（動）= 穩定基礎+向上動力'),
        ('坤+巽', '極佳', '坤（順）+巽（入）= 穩定+滲透'),
        ('艮+艮', '最差', '艮（止）+艮（止）= 雙重阻塞'),
        ('離+震', '較差', '離（麗）+震（動）= 想穩定卻被搖晃'),
    ]

    for combo_name, expected, explanation in known_rules:
        for r in results:
            if r['combo'] == combo_name:
                actual_rank = results.index(r) + 1
                total_count = len(results)
                if expected == '最佳' and actual_rank <= 3:
                    status = '✓'
                elif expected == '極佳' and actual_rank <= 5:
                    status = '✓'
                elif expected == '最差' and actual_rank >= total_count - 3:
                    status = '✓'
                elif expected == '較差' and actual_rank >= total_count - 10:
                    status = '✓'
                else:
                    status = '?'
                print(f"  {status} {combo_name}: 預期{expected}, 實際排名 {actual_rank}/{total_count}")
                print(f"      說明: {explanation}")
                break


def analyze_origin_theory():
    """
    理論4：古人設計邏輯推測

    嘗試理解古人是如何建立這個系統的
    """
    print("\n" + "="*60)
    print("理論4：古人設計邏輯推測")
    print("="*60)

    print("""
╔══════════════════════════════════════════════════════════════╗
║                    古人可能的設計過程                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  第一步：建立基本框架（先驗設計）                               ║
║  ──────────────────────────────────────────                  ║
║  • 陰陽二分法 → 萬物可分為兩種基本狀態                         ║
║  • 三爻成卦 → 天地人三才 → 8種基本情境                         ║
║  • 六爻重卦 → 64種複雜情境                                    ║
║  • 爻位對應 → 身體（趾→頭）、社會（庶→君）                     ║
║                                                              ║
║  第二步：賦予意義（經驗總結）                                   ║
║  ──────────────────────────────────────────                  ║
║  • 觀察自然：雷動地承（震上坤下）→ 生機                        ║
║  • 觀察社會：初爻謹慎、五爻尊貴                                ║
║  • 觀察人生：起步艱難、中途危險、登頂寂寞                       ║
║                                                              ║
║  第三步：建立規則（歸納法則）                                   ║
║  ──────────────────────────────────────────                  ║
║  • 得中（2、5爻）→ 平衡 → 較吉                                ║
║  • 三爻 → 不上不下 → 較凶                                     ║
║  • 卦德相配 → 順+動 = 吉，止+止 = 凶                          ║
║                                                              ║
║  第四步：撰寫爻辭（具體判斷）                                   ║
║  ──────────────────────────────────────────                  ║
║  • 結構決定基調（~50%）                                       ║
║  • 具體情境微調（+50%）                                       ║
║  • 用關鍵詞標記：吉、凶、无咎、吝、厲...                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def propose_unified_theory():
    """
    提出統一理論
    """
    print("\n" + "="*60)
    print("統一理論：易經是「變化可行性評估系統」")
    print("="*60)

    print("""
╔══════════════════════════════════════════════════════════════╗
║                        統一理論                               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  核心假設：                                                   ║
║  ─────────                                                   ║
║  易經評估的不是「好壞」，而是「變化的可行性」                    ║
║                                                              ║
║  • 吉 = 有發展空間，變化可行，能量可以流動                      ║
║  • 凶 = 被阻塞，變化受阻，能量無法流動                         ║
║  • 中 = 穩定狀態，不需要變化，維持現狀                         ║
║                                                              ║
║  驗證：                                                       ║
║  ─────                                                       ║
║  1. 坤+震最吉 → 有基礎+有動力 = 變化可行 ✓                     ║
║  2. 艮+艮最凶 → 雙重阻塞 = 變化不可行 ✓                        ║
║  3. 三爻最凶 → 進退兩難 = 變化受阻 ✓                           ║
║  4. 五爻最吉 → 有資源有權力 = 變化可主導 ✓                      ║
║  5. 下剋上吉 → 內在能量可釋放 = 變化可行 ✓                      ║
║  6. 比和反凶 → 太穩定 = 沒有變化動力 ✓                         ║
║                                                              ║
║  延伸：                                                       ║
║  ─────                                                       ║
║  易經的「變」字不只是書名                                      ║
║  而是整個系統的評估標準                                        ║
║                                                              ║
║  吉 ≠ 靜態的好                                               ║
║  吉 = 動態的順暢                                              ║
║                                                              ║
║  凶 ≠ 靜態的壞                                               ║
║  凶 = 動態的阻塞                                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def explain_ancient_method():
    """
    解釋古人可能的方法
    """
    print("\n" + "="*60)
    print("古人是怎麼知道的？")
    print("="*60)

    print("""
╔══════════════════════════════════════════════════════════════╗
║              古人的方法 vs 現代計算機的差異                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  古人的方法：象思維                                           ║
║  ──────────────────                                          ║
║  1. 觀察自然現象（天地雷風水火山澤）                            ║
║  2. 建立象徵對應（八卦 ↔ 自然現象）                            ║
║  3. 歸納組合效應（64卦 ↔ 情境故事）                            ║
║  4. 總結經驗法則（爻辭 ↔ 具體指導）                            ║
║                                                              ║
║  現代計算機的方法：數思維                                      ║
║  ──────────────────────                                      ║
║  1. 將現象編碼為數字                                          ║
║  2. 尋找數學公式                                              ║
║  3. 建立預測模型                                              ║
║  4. 驗證準確率                                                ║
║                                                              ║
║  為什麼計算機「理解」不了易經？                                 ║
║  ────────────────────────────                                ║
║  易經不是用「計算」建立的                                      ║
║  而是用「類比」和「象徵」建立的                                 ║
║                                                              ║
║  例：坤上震下 = 復卦                                          ║
║  古人：看到春雷在大地下湧動 → 這是復甦的象徵                    ║
║  計算機：坤=0b000, 震=0b100, 組合=??? → 無法計算               ║
║                                                              ║
║  古人的「知道」不是「計算出來」                                 ║
║  而是「觀察+類比+總結」                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║                    兩種認知方式                               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  象思維（古人）                                               ║
║  ──────────────                                              ║
║  • 從具體到抽象                                              ║
║  • 用比喻理解世界                                            ║
║  • 整體感知                                                  ║
║  • 重視「意義」                                              ║
║                                                              ║
║  數思維（計算機）                                             ║
║  ────────────────                                            ║
║  • 從抽象到具體                                              ║
║  • 用公式描述世界                                            ║
║  • 分解分析                                                  ║
║  • 重視「數值」                                              ║
║                                                              ║
║  結論：                                                       ║
║  ─────                                                       ║
║  易經用象思維建立，所以數思維無法完全解構                        ║
║  我們能做的是「翻譯」，不是「還原」                             ║
║  用數字描述已有的規律，而不是用公式推導新規律                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def main():
    data = load_data()

    # 執行各項分析
    analyze_dynamics_theory(data)
    analyze_freedom_theory(data)
    analyze_trigram_interaction(data)
    analyze_origin_theory()
    propose_unified_theory()
    explain_ancient_method()

    print("\n" + "="*60)
    print("總結")
    print("="*60)
    print("""
1. 易經是「變化可行性評估系統」，不是「好壞判定系統」
   - 吉 = 變化可行，能量流動
   - 凶 = 變化受阻，能量停滯

2. 古人用「象思維」建立易經，不是用「計算」
   - 觀察自然 → 建立象徵 → 歸納規律 → 總結經驗
   - 這是「類比認知」，不是「數學推導」

3. 結構只能預測50%是刻意設計
   - 體現「陰陽平衡」原則
   - 避免「命定論」教條
   - 強調「德可補位，行可轉運」

4. 現代計算機無法「完全理解」易經
   - 因為易經不是用數學建立的
   - 我們能做「翻譯」（描述規律）
   - 但無法「還原」（推導公式）
    """)


if __name__ == '__main__':
    main()
