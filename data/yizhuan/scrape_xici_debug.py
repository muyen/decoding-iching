#!/usr/bin/env python3
"""Debug scraper for Xi Ci with verbose output"""

import requests
from bs4 import BeautifulSoup
import time
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})


def clean_text(text: str) -> str:
    """Clean navigation and extra text"""
    text = re.sub(r'(上一章|下一章|目录|完善|原文\s*⇛\s*段译)', '', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)


# Xi Ci Upper IDs
xici_upper_ids = [
    "bb689e6439c3", "ee671638f6bb", "e89a903b3cc8", "fdf70db3c61c",
    "75ec81a11dd8", "6cf95dec7d91", "69fe1f3e2c35", "b12ca8e9c65e",
    "34bda38889d2", "a6e5a79e1343", "e7cfef03de05", "a88e0ec5d75b"
]

print("Scraping Xi Ci Upper - 12 chapters")
print("=" * 80)

for i, id in enumerate(xici_upper_ids, 1):
    url = f"https://www.gushiwen.cn/guwen/bookv_{id}.aspx"
    print(f"\nChapter {i}/12: {id}")
    print(f"URL: {url}")

    try:
        response = session.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find ALL content divs
        all_divs = soup.select('.contson, .sons')
        print(f"  Found {len(all_divs)} content divs")

        for j, div in enumerate(all_divs, 1):
            text = div.get_text(separator='\n', strip=True)
            cleaned = clean_text(text)

            # Check if it's skip-worthy
            if '播放列表' in text or '循环' in text:
                print(f"    Div {j}: SKIPPED (audio player) - {len(text)} chars")
                continue

            print(f"    Div {j}: {len(cleaned)} chars")
            print(f"      Preview: {cleaned[:80]}...")

        time.sleep(1)

    except Exception as e:
        print(f"  ERROR: {e}")
