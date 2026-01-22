#!/usr/bin/env python3
import json

# 原始腳本使用的樣本
SCRIPT_SAMPLES = [1, 2, 3, 4, 5, 6, 15, 17, 20, 24, 25, 33, 47, 50, 63]
print(f"原始腳本使用的卦數: {len(SCRIPT_SAMPLES)} 個")
print(f"樣本數: {len(SCRIPT_SAMPLES) * 6} = 90")

# 完整數據
with open('/Users/arsenelee/github/iching/data/analysis/verified_labels.json') as f:
    all_data = json.load(f)

print(f"完整數據樣本數: {len(all_data)}")

# 計算原始腳本中 XOR=4 + pos<=4 的樣本
script_samples_data = [
    (1, 1, "111111", 0), (1, 2, "111111", 1), (1, 3, "111111", 0),
    (1, 4, "111111", 0),
    (15, 1, "000100", 1), (15, 2, "000100", 1), (15, 3, "000100", 1),
    (15, 4, "000100", 1),
]

print("\n【原始腳本中 XOR=4 的情況】")
xor4_count = 0
xor4_pos4_count = 0
xor4_pos4_ji = 0

for hex_num, pos, binary, fortune in script_samples_data:
    lower = int(binary[0:3], 2)
    upper = int(binary[3:6], 2)
    xor = upper ^ lower
    print(f"Hex {hex_num}, pos {pos}: binary={binary}, XOR={xor}, fortune={fortune}")

# 在原始腳本中找所有 XOR=4 的
SCRIPT_FULL = [
    (1, 1, "111111", 0), (1, 2, "111111", 1), (1, 3, "111111", 0),
    (1, 4, "111111", 0), (1, 5, "111111", 1), (1, 6, "111111", -1),
    (2, 1, "000000", -1), (2, 2, "000000", 1), (2, 3, "000000", 0),
    (2, 4, "000000", 0), (2, 5, "000000", 1), (2, 6, "000000", -1),
    (15, 1, "000100", 1), (15, 2, "000100", 1), (15, 3, "000100", 1),
    (15, 4, "000100", 1), (15, 5, "000100", 0), (15, 6, "000100", 0),
]

print("\n【原始腳本中所有 XOR=4 樣本】")
for hex_num, pos, binary, fortune in SCRIPT_FULL:
    lower = int(binary[0:3], 2)
    upper = int(binary[3:6], 2)
    xor = upper ^ lower
    if xor == 4:
        print(f"Hex {hex_num}, pos {pos}: XOR={xor}, fortune={fortune}")

print("\n結論:")
print("原始腳本只包含謙卦(15)的XOR=4樣本")
print("謙卦是唯一六爻皆吉的卦，所以當然100%！")
print("但這只是1個卦，不能代表所有XOR=4的8個卦！")
