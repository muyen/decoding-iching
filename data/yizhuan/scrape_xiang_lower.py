#!/usr/bin/env python3
"""Scrape Xiang Zhuan Lower (hexagrams 95-128, i.e., hexagrams 31-64 of lower canon)"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

# First, let me extract the IDs from the main page
base = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"
response = session.get(base, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Extract all IDs
all_links = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if 'bookv_' in href and text:
        match = re.search(r'bookv_([a-f0-9]+)\.aspx', href)
        if match:
            all_links.append({'text': text, 'id': match.group(1)})

# Find hexagrams 95-128 (these are labeled as "第九十五" through "第一百二十八")
xiang_lower_ids = []
for link in all_links:
    text = link['text']
    # Match hexagrams 95-128
    if '第九十五' in text or '第九十六' in text or '第九十七' in text or '第九十八' in text or '第九十九' in text:
        xiang_lower_ids.append(link['id'])
    elif '第一百' in text:
        xiang_lower_ids.append(link['id'])

print(f"Found {len(xiang_lower_ids)} hexagram IDs for 象传下")
print(f"IDs: {xiang_lower_ids[:5]}... (showing first 5)")

# Now scrape each one
def clean_text(text: str) -> str:
    text = re.sub(r'(上一章|下一章|目录|完善|原文\s*⇛\s*段译)', '', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

paragraphs = []
print("\nScraping 象传下...")
for i, id in enumerate(xiang_lower_ids, 1):
    print(f"  [{i}/{len(xiang_lower_ids)}] Processing hexagram {i+30}...")
    url = f"https://www.gushiwen.cn/guwen/bookv_{id}.aspx"

    try:
        time.sleep(2)
        resp = session.get(url, timeout=10)
        resp.encoding = 'utf-8'
        page_soup = BeautifulSoup(resp.text, 'html.parser')

        all_text = []
        for div in page_soup.select('.contson, .sons'):
            content = div.get_text(separator='\n', strip=True)
            if '播放列表' in content or '循环' in content or len(content) < 20:
                continue
            content = clean_text(content)
            if content:
                all_text.append(content)

        if all_text:
            text = max(all_text, key=len)
            paragraphs.append(text)

    except Exception as e:
        print(f"    Error: {e}")

# Save
result = {
    "title": "象传下",
    "title_pinyin": "Xiang Zhuan Xia",
    "content": '\n\n'.join(paragraphs),
    "paragraphs": paragraphs
}

output_dir = Path("/Users/arsenelee/github/iching/data/yizhuan")
output_path = output_dir / "xiang_lower.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nSaved xiang_lower.json ({len(result['content'])} chars, {len(paragraphs)} sections)")
