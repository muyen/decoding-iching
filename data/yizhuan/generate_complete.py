#!/usr/bin/env python3
"""Generate the complete yizhuan_complete.json from all individual files"""

import json
from pathlib import Path

output_dir = Path("/Users/arsenelee/github/iching/data/yizhuan")

# Load all 10 wings
wings = {}
wing_files = {
    'tuan_upper': '彖传上',
    'tuan_lower': '彖传下',
    'xiang_upper': '象传上',
    'xiang_lower': '象传下',
    'xici_upper': '系辞上',
    'xici_lower': '系辞下',
    'wenyan': '文言传',
    'shuogua': '说卦传',
    'xugua': '序卦传',
    'zagua': '杂卦传'
}

for key, name in wing_files.items():
    filepath = output_dir / f"{key}.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            wings[key] = json.load(f)
        print(f"Loaded {name} ({len(wings[key]['content'])} chars)")
    else:
        print(f"Missing: {name}")

# Generate combined file
combined = {
    "title": "十翼",
    "title_en": "Ten Wings",
    "description": "Complete collection of the Ten Wings commentaries on the I Ching / Yi Jing",
    "source": "gushiwen.cn",
    "wings": wings,
    "total_wings": len(wings),
    "total_characters": sum(len(w['content']) for w in wings.values())
}

# Save
output_path = output_dir / "yizhuan_complete.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"\nSaved yizhuan_complete.json")
print(f"Total wings: {len(wings)}/10")
print(f"Total characters: {combined['total_characters']:,}")

# Print summary
print("\nSummary:")
for key, name in wing_files.items():
    if key in wings:
        chars = len(wings[key]['content'])
        paras = len(wings[key]['paragraphs'])
        print(f"  ✓ {name:8s} ({chars:,} chars, {paras} sections)")
    else:
        print(f"  ✗ {name}")
