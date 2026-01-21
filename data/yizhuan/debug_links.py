#!/usr/bin/env python3
"""Debug script to see what links are on gushiwen.cn"""

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

base_url = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"

print(f"Fetching: {base_url}\n")
response = session.get(base_url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Print all links with their text
print("All links on page:")
print("-" * 80)
for i, a in enumerate(soup.find_all('a'), 1):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if text and 'guwen' in href:
        print(f"{i:3d}. {text:30s} -> {href}")

# Look for specific patterns
print("\n" + "=" * 80)
print("Links with '传' character:")
print("-" * 80)
for a in soup.find_all('a'):
    text = a.get_text(strip=True)
    if '传' in text:
        href = a.get('href', '')
        print(f"  {text:30s} -> {href}")
