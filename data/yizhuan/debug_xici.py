#!/usr/bin/env python3
"""Debug Xi Ci page structure"""

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

url = "https://www.gushiwen.cn/guwen/bookv_bb689e6439c3.aspx"  # Xi Ci Chapter 1

print(f"Fetching: {url}\n")
response = session.get(url, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Find all potential content containers
print("All divs with class containing 'cont' or 'sons':")
print("-" * 80)

for i, div in enumerate(soup.find_all('div'), 1):
    classes = div.get('class', [])
    if any('cont' in c or 'sons' in c for c in classes):
        text = div.get_text(separator=' ', strip=True)[:150]
        print(f"{i}. Classes: {classes}")
        print(f"   Text: {text}...")
        print()

print("\n" + "=" * 80)
print("Specifically looking for .contson and .sons:")
print("-" * 80)

for i, div in enumerate(soup.select('.contson, .sons'), 1):
    text = div.get_text(strip=True)
    print(f"{i}. Length: {len(text)} chars")
    print(f"   First 200 chars: {text[:200]}...")
    print()
