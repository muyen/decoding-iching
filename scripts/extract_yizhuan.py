#!/usr/bin/env python3
"""Extract 十翼 (Ten Wings) independent texts from ZHOUYI.pm"""
import json
from pathlib import Path

def extract_yizhuan(pm_file):
    with open(pm_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find __DATA__ section
    data_start = content.find('__DATA__')
    if data_start == -1:
        raise ValueError("No __DATA__ section found")

    data = content[data_start + len('__DATA__'):]
    lines = data.split('\n')

    yizhuan = {}
    current_section = None
    current_text = []

    section_markers = {
        '系辭上傳': 'xici_shang',
        '系辭下傳': 'xici_xia',
        '說卦': 'shuogua',
        '序卦': 'xugua',
        '雜卦': 'zagua'
    }

    for line in lines:
        line = line.strip()

        # Check for section markers
        found_section = None
        for marker, key in section_markers.items():
            if line == marker:
                # Save previous section
                if current_section and current_text:
                    yizhuan[current_section] = '\n'.join(current_text)
                current_section = key
                current_text = []
                found_section = True
                break

        if found_section:
            continue

        # Add content to current section
        if current_section and line:
            # Stop if we hit a new major section (hexagram marker)
            if line.startswith('《易經》第') or line in section_markers:
                if current_text:
                    yizhuan[current_section] = '\n'.join(current_text)
                current_section = None
                current_text = []
            else:
                current_text.append(line)

    # Save last section
    if current_section and current_text:
        yizhuan[current_section] = '\n'.join(current_text)

    return yizhuan

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    pm_file = base_dir / 'data/zhouyi-64gua/lib/ZHOUYI.pm'
    output_dir = base_dir / 'data/yizhuan'
    output_dir.mkdir(exist_ok=True)

    print(f"Extracting 十翼 texts from {pm_file}...")
    yizhuan = extract_yizhuan(pm_file)

    # Chinese names for each wing
    wing_names = {
        'xici_shang': {'chinese': '繫辭上傳', 'english': 'Xi Ci Shang (Great Commentary Part I)'},
        'xici_xia': {'chinese': '繫辭下傳', 'english': 'Xi Ci Xia (Great Commentary Part II)'},
        'shuogua': {'chinese': '說卦傳', 'english': 'Shuo Gua (Discussion of Trigrams)'},
        'xugua': {'chinese': '序卦傳', 'english': 'Xu Gua (Sequence of Hexagrams)'},
        'zagua': {'chinese': '雜卦傳', 'english': 'Za Gua (Miscellaneous Notes)'}
    }

    # Save each wing as separate JSON
    for key, text in yizhuan.items():
        if key in wing_names:
            output_file = output_dir / f'{key}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'title': wing_names[key]['chinese'],
                    'english_title': wing_names[key]['english'],
                    'source': 'bollwarm/ZHOUYI GitHub',
                    'language': '繁體中文 (Traditional Chinese)',
                    'content': text,
                    'char_count': len(text)
                }, f, ensure_ascii=False, indent=2)
            print(f"  Saved {wing_names[key]['chinese']} to {output_file.name} ({len(text)} chars)")

    # Save complete collection
    complete_file = output_dir / 'yizhuan_complete.json'
    complete_data = {
        'title': '十翼 (Ten Wings)',
        'description': 'Independent Ten Wings commentaries on the I Ching (繫辭, 說卦, 序卦, 雜卦)',
        'note': '彖傳 and 象傳 are embedded in hexagram texts in zhouyi_64gua.json',
        'language': '繁體中文 (Traditional Chinese)',
        'source': 'bollwarm/ZHOUYI GitHub',
        'wings': {}
    }

    total_chars = 0
    for key, text in yizhuan.items():
        if key in wing_names:
            complete_data['wings'][key] = {
                'title': wing_names[key]['chinese'],
                'english_title': wing_names[key]['english'],
                'content': text,
                'char_count': len(text)
            }
            total_chars += len(text)

    complete_data['total_wings'] = len(complete_data['wings'])
    complete_data['total_characters'] = total_chars

    with open(complete_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, ensure_ascii=False, indent=2)

    print(f"\nComplete collection saved to {complete_file.name}")
    print(f"Total: {len(yizhuan)} wings, {total_chars} characters")

if __name__ == '__main__':
    main()
