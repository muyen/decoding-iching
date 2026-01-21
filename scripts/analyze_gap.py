#!/usr/bin/env python3
"""
分析 V4 (100%) 與 V5 (50%) 的差距
找出缺失的結構規律
"""

import json
from pathlib import Path
from collections import defaultdict

# 載入V5結果
v5_path = Path(__file__).parent.parent / "data" / "analysis" / "formula_v5_honest.json"
with open(v5_path) as f:
    v5_data = json.load(f)

results = v5_data["results"]

# 分析錯誤模式
print("=" * 70)
print("V4 → V5 差距分析：找出缺失的結構規律")
print("=" * 70)
print()

errors = [r for r in results if not r["match"]]
correct = [r for r in results if r["match"]]

print(f"總樣本: {len(results)}")
print(f"正確: {len(correct)} ({len(correct)/len(results)*100:.1f}%)")
print(f"錯誤: {len(errors)} ({len(errors)/len(results)*100:.1f}%)")
print()

# ============================================================
# 模式1：實際「中」但預測「吉」或「凶」
# ============================================================
print("=" * 70)
print("模式1：實際「中」但預測錯誤")
print("=" * 70)

neutral_errors = [e for e in errors if e["actual"] == 0]
print(f"數量: {len(neutral_errors)}/{len(errors)} ({len(neutral_errors)/len(errors)*100:.1f}%)")
print()

# 分析預測傾向
pred_ji = [e for e in neutral_errors if e["pred"] == 1]
pred_xiong = [e for e in neutral_errors if e["pred"] == -1]

print(f"  預測「吉」但實際「中」: {len(pred_ji)}")
for e in pred_ji[:5]:
    print(f"    卦{e['hex']:2} 爻{e['pos']} | 分:{e['score']:5.2f} | 時義:{e['details']['time_type']} | 應:{e['details']['correlation']:+.1f}")

print(f"\n  預測「凶」但實際「中」: {len(pred_xiong)}")
for e in pred_xiong[:5]:
    print(f"    卦{e['hex']:2} 爻{e['pos']} | 分:{e['score']:5.2f} | 時義:{e['details']['time_type']} | 應:{e['details']['correlation']:+.1f}")

# ============================================================
# 模式2：實際「凶」但預測「中」或「吉」
# ============================================================
print()
print("=" * 70)
print("模式2：實際「凶」但預測錯誤（漏判凶）")
print("=" * 70)

xiong_errors = [e for e in errors if e["actual"] == -1]
print(f"數量: {len(xiong_errors)}/{len(errors)}")

for e in xiong_errors:
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 預測:{['凶','中','吉'][e['pred']+1]} | 分:{e['score']:5.2f} | 應:{e['details']['correlation']:+.1f}")

# ============================================================
# 模式3：實際「吉」但預測「中」或「凶」
# ============================================================
print()
print("=" * 70)
print("模式3：實際「吉」但預測錯誤（漏判吉）")
print("=" * 70)

ji_errors = [e for e in errors if e["actual"] == 1]
print(f"數量: {len(ji_errors)}/{len(errors)}")

for e in ji_errors:
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 預測:{['凶','中','吉'][e['pred']+1]} | 分:{e['score']:5.2f} | 應:{e['details']['correlation']:+.1f}")

# ============================================================
# 深度分析：「無咎」模式
# ============================================================
print()
print("=" * 70)
print("洞見1：「無咎」與結構不符的案例")
print("=" * 70)

# 結構預測凶（分數<0），但實際是中或吉
struct_neg_but_ok = [e for e in errors if e["score"] < 0 and e["actual"] >= 0]
print(f"\n結構預測凶（分數<0）但實際不凶: {len(struct_neg_but_ok)}")
print("→ 這些案例可能是「無咎」模式：結構不利但行為得當可化解")

for e in struct_neg_but_ok:
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 實際:{['凶','中','吉'][e['actual']+1]} | 分:{e['score']:5.2f}")

# ============================================================
# 深度分析：承乘比應失效的案例
# ============================================================
print()
print("=" * 70)
print("洞見2：承乘比應失效的案例")
print("=" * 70)

# 應爻高分但實際凶
high_corr_but_bad = [e for e in errors if e["details"]["correlation"] > 0.5 and e["actual"] == -1]
print(f"\n應爻高分（>0.5）但實際凶: {len(high_corr_but_bad)}")
print("→ 承乘比應不是萬能的，需要其他因素")

for e in high_corr_but_bad:
    print(f"  卦{e['hex']:2} 爻{e['pos']} | 應:{e['details']['correlation']:+.1f} | 分:{e['score']:5.2f}")

# ============================================================
# 爻位特異性分析
# ============================================================
print()
print("=" * 70)
print("洞見3：各爻位的錯誤模式")
print("=" * 70)

for pos in range(1, 7):
    pos_errors = [e for e in errors if e["pos"] == pos]
    pos_total = len([r for r in results if r["pos"] == pos])
    if pos_errors:
        print(f"\n爻{pos} 錯誤率: {len(pos_errors)}/{pos_total}")
        # 主要錯誤類型
        actual_counts = defaultdict(int)
        for e in pos_errors:
            actual_counts[e["actual"]] += 1
        for actual, count in sorted(actual_counts.items()):
            actual_name = ["凶", "中", "吉"][actual + 1]
            print(f"  實際「{actual_name}」被誤判: {count}次")

# ============================================================
# 核心發現
# ============================================================
print()
print("=" * 70)
print("核心發現：什麼結構規律能彌補差距？")
print("=" * 70)

print("""
1. 【無咎規律】
   - 三爻、四爻結構上確實不利（基礎分負）
   - 但「無咎」表示：雖有險，但可化解
   - 需要識別「化解條件」：得位？得中？時義？

2. 【中性判斷過窄】
   - 當前閾值：-0.5 < score < 2.0 = 中
   - 很多「中」被判為「吉」（分數高）或「凶」（分數低）
   - 可能需要更寬的中性區間

3. 【順時卦的負面爻】
   - 順時卦（favorable）中的三、四爻仍可能不利
   - 不能因為卦好就所有爻都好
   - 需要「卦時義 × 爻位風險」的更精細互動

4. 【承乘比應的局限】
   - 陰陽相應確實有用，但不是決定性因素
   - 有些「應」的爻仍然凶（因為其他因素）
   - 需要權重調整

5. 【行為指引未編碼】
   - 「勿用」= 不動則無過 → 中性
   - 「利貞」= 守正則吉 → 需要行為條件
   - 「往吉/凶」= 行動才見分曉
   - 這些需要結構化編碼
""")

# ============================================================
# 建議的改進
# ============================================================
print()
print("=" * 70)
print("建議的V6改進")
print("=" * 70)

print("""
1. 擴大「中性」區間
   - 當前: -0.5 ~ 2.0
   - 建議: -1.0 ~ 3.0 或更寬
   - 原因: 易經很多爻都是「有條件」的吉凶

2. 加入「爻位×時義」交互項
   - 順時卦的三爻仍可能有警告
   - 逆時卦的五爻可能有轉機
   - 不是簡單相乘

3. 區分「結構凶」vs「行為凶」
   - 結構凶: 位置本身不利
   - 行為凶: 行動導致不利
   - 「勿用」類爻辭 = 結構不利但不動則中

4. 減少承乘比應的權重
   - 當前貢獻太大
   - 應該只是微調，不是主因

5. 加入「卦主」識別
   - 一陽五陰卦的陽爻 = 卦主
   - 一陰五陽卦的陰爻 = 卦主
   - 卦主的吉凶權重更高
""")
