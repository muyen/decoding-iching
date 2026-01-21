#!/usr/bin/env python3
"""Inspect the chapter links"""

import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

base = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"

response = session.get(base, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links
all_links = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if 'bookv_' in href and text:
        all_links.append((text, href))

# Look for specific items
targets = ['第一章', '第二章', '上篇', '下篇', '全文', '文言']

print("Checking specific links:")
print("-" * 80)

for text, href in all_links:
    if any(target in text for target in targets):
        full_url = f"https://www.gushiwen.cn{href}"
        print(f"\n{text} -> {href}")

        # Fetch to see what it is
        try:
            time.sleep(1)
            resp = session.get(full_url, timeout=10)
            resp.encoding = 'utf-8'
            page_soup = BeautifulSoup(resp.text, 'html.parser')

            # Get page title
            h1 = page_soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
                print(f"  Page title: {title}")

            # Get first bit of content
            content_div = page_soup.select_one('.contson, .sons')
            if content_div:
                text_preview = content_div.get_text(strip=True)[:100]
                print(f"  Content preview: {text_preview}...")

        except Exception as e:
            print(f"  Error: {e}")
