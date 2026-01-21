#!/usr/bin/env python3
"""
Find the remaining Ten Wings texts on gushiwen.cn
Looking for: 系辞上/下, 文言, 说卦, 序卦, 杂卦
"""

import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

# The main book page showed items 1-128+
# Likely the remaining commentaries are at higher numbers
# Let's check a broader range

base = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"

print(f"Fetching main page: {base}\n")
response = session.get(base, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Find ALL links on the page
all_links = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if 'bookv_' in href and text:
        all_links.append({'text': text, 'href': href})

print(f"Total links with bookv_: {len(all_links)}\n")

# Group by prefix/pattern
print("Looking for commentaries (传, 辞):")
print("-" * 80)
for link in all_links:
    text = link['text']
    if any(keyword in text for keyword in ['传', '辞', '卦', '言']):
        # Check if it's not just a hexagram number
        if not any(f'第{i}' in text for i in range(1, 200)):
            print(f"  {text:40s} -> {link['href']}")

# Look specifically by hexagram number patterns
print("\nLinks by number range:")
print("-" * 80)

# Group by number
numbered = {}
for link in all_links:
    text = link['text']
    # Extract number if present
    import re
    match = re.search(r'第([一二三四五六七八九十百]+)', text)
    if not match:
        match = re.search(r'第(\d+)', text)

    if match:
        num_str = match.group(1)
        # Convert Chinese numerals or use as-is
        try:
            # Try to extract meaning from the number pattern
            if '百' in num_str or int(num_str) > 100:
                if text not in numbered:
                    numbered[text] = link['href']
        except:
            pass

if numbered:
    print("High-numbered items (likely commentaries):")
    for text, href in sorted(numbered.items())[:20]:
        print(f"  {text:40s} -> {href}")
