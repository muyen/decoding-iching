#!/usr/bin/env python3
"""
Check specific numbered items to find remaining wings
"""

import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

base = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"

print(f"Fetching main page...\n")
response = session.get(base, timeout=10)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links and extract those with numbers >= 129
all_items = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    if 'bookv_' in href and text:
        # Try to extract number
        match = re.search(r'第(\d+)', text)
        if not match:
            # Try Chinese numerals
            match = re.search(r'第([一二三四五六七八九十百零]+)', text)

        if match:
            num_text = match.group(1)
            try:
                # If it's a digit, use directly
                if num_text.isdigit():
                    num = int(num_text)
                else:
                    # For Chinese numerals >= 100, we want those
                    if '百' in num_text:
                        num = 100  # Approximate
                        if '一百一' in text:
                            num = 110
                        elif '一百二' in text:
                            num = 120
                        elif '一百三' in text:
                            num = 130
                    else:
                        continue

                if num >= 129:
                    all_items.append({'num': num, 'text': text, 'href': href})
            except:
                pass

# Sort by number
all_items.sort(key=lambda x: x['num'])

print("Items >= 129:")
print("-" * 80)
for item in all_items[:30]:  # Show first 30
    print(f"{item['num']:3d}. {item['text']:40s} -> {item['href']}")
