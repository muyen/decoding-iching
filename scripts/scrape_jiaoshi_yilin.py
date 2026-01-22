#!/usr/bin/env python3
"""
Scrape 焦氏易林 (Jiaoshi Yilin) from 8bei8.com

This script downloads all 4096 hexagram transformation verses.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

BASE_URL = "https://www.8bei8.com/book/jiaoshiyilin_{}.html"

# 64 hexagram names in sequence order
HEXAGRAM_NAMES = [
    "乾", "坤", "屯", "蒙", "需", "訟", "師", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "謙", "豫",
    "隨", "蠱", "臨", "觀", "噬嗑", "賁", "剝", "復",
    "無妄", "大畜", "頤", "大過", "坎", "離", "咸", "恆",
    "遯", "大壯", "晉", "明夷", "家人", "睽", "蹇", "解",
    "損", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "漸", "歸妹", "豐", "旅",
    "巽", "兌", "渙", "節", "中孚", "小過", "既濟", "未濟"
]

def fetch_page(page_num):
    """Fetch a single page from 8bei8.com"""
    url = BASE_URL.format(page_num)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def parse_volume(html_content, volume_num):
    """Parse a volume page and extract transformation verses"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main content div
    content_div = soup.find('div', class_='content') or soup.find('div', id='content')
    if not content_div:
        content_div = soup.find('body')

    text = content_div.get_text() if content_div else ""

    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def extract_transformations(text):
    """Extract individual transformation verses from text"""
    transformations = []

    # Remove header/footer noise
    text = re.sub(r'太极书馆.*?目录\s*', '', text)
    text = re.sub(r'焦氏易林<第.*?页>', '', text)

    # Pattern 1: 卦名下，卦名上。 (hexagram header)
    # Pattern 2: 之卦名，verse (transformation to another hexagram)
    # Pattern 3: 卦名，verse (direct reading without 之)

    # First find the main hexagram for this section
    header_pattern = r'易林卷第[一二三四五六七八九十]+\s*(\S+)下[，,](\S+)上'
    header_match = re.search(header_pattern, text)

    current_source = None
    if header_match:
        lower = header_match.group(1)
        upper = header_match.group(2)
        # For the source hexagram, use the upper+lower combo name if available
        current_source = f"{lower}{upper}" if lower != upper else lower

    # Split by common hexagram markers
    # Pattern: 之乾, 之坤, 乾, 坤 etc at start of sentence
    all_hexagrams = '|'.join(HEXAGRAM_NAMES)

    # Find all transformation patterns: 之卦名[，,]verse  or  卦名[，,。]verse
    trans_pattern = rf'(?:之({all_hexagrams})|^({all_hexagrams}))[，,。：:\s]+([^之]+?)(?=(?:之(?:{all_hexagrams})|(?:{all_hexagrams})[，,。]|$))'

    # Simpler approach: split by "之X" pattern
    parts = re.split(rf'之({all_hexagrams})[，,。]', text)

    for i in range(1, len(parts), 2):
        if i < len(parts):
            target = parts[i-1] if i > 0 else None
            verse = parts[i] if i < len(parts) else ''
            # Clean verse
            verse = re.sub(r'\s+', '', verse[:200])  # First 200 chars max
            if target and verse and len(verse) > 4:
                transformations.append({
                    'target': target.strip(),
                    'verse': verse[:100]  # Limit verse length
                })

    return transformations

def main():
    print("=" * 60)
    print("焦氏易林 (Jiaoshi Yilin) Scraper")
    print("=" * 60)

    all_data = {
        'title': '焦氏易林',
        'author': '焦延壽 (西漢)',
        'volumes': [],
        'transformations': []
    }

    # Scrape pages 2-17 (volumes 1-16)
    for page_num in range(2, 18):
        volume_num = page_num - 1
        print(f"\n正在下載卷{volume_num}...")

        html = fetch_page(page_num)
        if html:
            text = parse_volume(html, volume_num)
            transforms = extract_transformations(text)

            all_data['volumes'].append({
                'volume': volume_num,
                'raw_text': text[:500] + '...' if len(text) > 500 else text,
                'transformation_count': len(transforms)
            })
            all_data['transformations'].extend(transforms)

            print(f"  找到 {len(transforms)} 個變卦")

        time.sleep(1)  # Be polite

    # Save the data
    output_path = Path(__file__).parent.parent / 'data' / 'jiaoshi_yilin.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"完成！共提取 {len(all_data['transformations'])} 個變卦詩")
    print(f"數據保存至：{output_path}")

    return all_data

if __name__ == '__main__':
    main()
