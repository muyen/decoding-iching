#!/usr/bin/env python3
"""Extract 64 hexagrams from ZHOUYI.pm and convert to JSON"""
import re
import json
from pathlib import Path

def extract_hexagrams(pm_file):
    with open(pm_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find __DATA__ section
    data_start = content.find('__DATA__')
    if data_start == -1:
        raise ValueError("No __DATA__ section found")

    data = content[data_start + len('__DATA__'):]

    # Split by hexagram pattern
    pattern = r'《易經》第(\d+)卦(\S+)\s+(\S+)\s+(\S+)'

    # Find all hexagram starts
    matches = list(re.finditer(pattern, data))
    print(f"Found {len(matches)} hexagram headers")

    hexagrams = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(data)

        hex_content = data[start:end].strip()

        hexagram = {
            'number': int(match.group(1)),
            'name': match.group(2),
            'full_name': match.group(3),
            'trigrams': match.group(4),
            'guaci': '',
            'yaoci': [],
            'tuan': [],
            'xiang': [],
            'wenyan': []
        }

        # Parse trigrams
        trigrams = match.group(4)
        if '上' in trigrams:
            parts = trigrams.split('上')
            hexagram['upper_trigram'] = parts[0]
            hexagram['lower_trigram'] = parts[1].replace('下', '') if len(parts) > 1 else ''

        # Parse content lines
        lines = hex_content.split('\n')

        guaci_done = False
        in_wenyan = False

        for line in lines[2:]:  # Skip header lines
            line = line.strip()
            if not line:
                continue

            if line.startswith('《文言》'):
                in_wenyan = True
                hexagram['wenyan'].append(line)
            elif in_wenyan and not line.startswith('《易經》'):
                hexagram['wenyan'].append(line)
            elif line.startswith('《彖》'):
                hexagram['tuan'].append(line)
                guaci_done = True
            elif line.startswith('《象》'):
                hexagram['xiang'].append(line)
                guaci_done = True
            elif re.match(r'^(初[六九]|[六九][二三四五]|上[六九]|用[六九])[:：]', line):
                hexagram['yaoci'].append(line)
                guaci_done = True
            elif not guaci_done and not line.startswith('《'):
                hexagram['guaci'] += line + '\n'

        hexagram['guaci'] = hexagram['guaci'].strip()
        hexagram['wenyan'] = '\n'.join(hexagram['wenyan'])

        hexagrams.append(hexagram)

    return hexagrams

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    pm_file = base_dir / 'data/zhouyi-64gua/lib/ZHOUYI.pm'
    output_file = base_dir / 'data/zhouyi-64gua/zhouyi_64gua.json'

    print(f"Extracting hexagrams from {pm_file}...")
    hexagrams = extract_hexagrams(pm_file)

    print(f"Parsed {len(hexagrams)} hexagrams")

    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'title': '周易六十四卦',
            'source': 'bollwarm/ZHOUYI GitHub',
            'description': '64 hexagrams with 卦辞, 爻辞, 彖传, 象传, 文言传',
            'count': len(hexagrams),
            'hexagrams': hexagrams
        }, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_file}")

    # Print summary
    for h in hexagrams[:3]:
        print(f"\n第{h['number']}卦 {h['name']} ({h['full_name']})")
        print(f"  卦辞: {h['guaci'][:60]}..." if len(h['guaci']) > 60 else f"  卦辞: {h['guaci']}")
        print(f"  爻辞: {len(h['yaoci'])} lines, 彖: {len(h['tuan'])}, 象: {len(h['xiang'])}")

if __name__ == '__main__':
    main()
