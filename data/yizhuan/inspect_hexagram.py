#!/usr/bin/env python3
"""Inspect a hexagram page to see if it contains commentary"""

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

# Check first hexagram (Qian)
url = "https://www.gushiwen.cn/guwen/bookv_5f3454cfdbc9.aspx"

print(f"Fetching: {url}\n")
response = session.get(url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Print page title
title = soup.find('h1')
if title:
    print(f"Page title: {title.get_text(strip=True)}\n")

# Look for section headers that might indicate commentary
print("Section headers:")
print("-" * 80)
for tag in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b']):
    text = tag.get_text(strip=True)
    if len(text) > 0 and len(text) < 50:
        print(f"  {text}")

# Look for content divs
print("\nContent areas:")
print("-" * 80)
for div in soup.select('.contson, .sons, [class*="cont"]'):
    text = div.get_text(strip=True)[:200]
    if text:
        print(f"  {text}...")
