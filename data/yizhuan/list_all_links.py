#!/usr/bin/env python3
"""List all links on the main page"""

import requests
from bs4 import BeautifulSoup

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
    if 'bookv_' in href and text and len(text) < 50:
        all_links.append((text, href))

print(f"Total links: {len(all_links)}\n")

# Print all unique ones
seen = set()
for i, (text, href) in enumerate(all_links):
    if text not in seen:
        print(f"{i+1:3d}. {text}")
        seen.add(text)
