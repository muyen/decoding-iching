#!/usr/bin/env python3
"""Extract ALL chapter IDs from the main book page"""

import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

base = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"

print(f"Fetching: {base}\n")
response = session.get(base, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Extract ALL links and categorize them
all_links = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if 'bookv_' in href and text:
        # Extract the ID
        match = re.search(r'bookv_([a-f0-9]+)\.aspx', href)
        if match:
            id = match.group(1)
            all_links.append({'text': text, 'id': id, 'href': href})

print(f"Total links: {len(all_links)}\n")

# Filter by specific patterns
print("文言传 (Wen Yan):")
for link in all_links:
    if '文言' in link['text']:
        print(f"  {link['text']:30s} -> {link['id']}")

print("\n系辞传上 chapters (looking for '第.*章'):")
xici_upper = []
for link in all_links:
    if '系辞传上' in link['text'] or ('第' in link['text'] and '章' in link['text'] and '下' not in link['text']):
        xici_upper.append(link)
        print(f"  {link['text']:30s} -> {link['id']}")

print("\n系辞传下 chapters:")
xici_lower = []
for link in all_links:
    if '系辞传下' in link['text']:
        xici_lower.append(link)
        print(f"  {link['text']:30s} -> {link['id']}")

print("\n说卦传 chapters:")
shuogua = []
for link in all_links:
    if '说卦传' in link['text']:
        shuogua.append(link)
        print(f"  {link['text']:30s} -> {link['id']}")

print("\n序卦传:")
for link in all_links:
    if '序卦传' in link['text'] or ('上篇' in link['text'] or '下篇' in link['text']):
        print(f"  {link['text']:30s} -> {link['id']}")

print("\n杂卦传:")
for link in all_links:
    if '杂卦传' in link['text'] or '全文' in link['text']:
        print(f"  {link['text']:30s} -> {link['id']}")
