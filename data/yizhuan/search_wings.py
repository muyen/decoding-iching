#!/usr/bin/env python3
"""Search for Ten Wings on gushiwen.cn"""

import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

# Search for each wing
wings = [
    "彖传上", "彖传下",
    "象传上", "象传下",
    "系辞上", "系辞下",
    "文言传", "说卦传", "序卦传", "杂卦传"
]

for wing in wings:
    search_query = f"周易 {wing}"
    search_url = f"https://www.gushiwen.cn/search.aspx?value={search_query}"

    print(f"\nSearching for: {wing}")
    print(f"URL: {search_url}")

    try:
        time.sleep(2)
        response = session.get(search_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for result links
        results = soup.select('.sons a, .typecont a')
        found = False
        for a in results[:5]:  # Show top 5 results
            text = a.get_text(strip=True)
            href = a.get('href', '')
            if 'guwen' in href and len(text) > 0:
                if not href.startswith('http'):
                    href = 'https://www.gushiwen.cn' + href
                print(f"  -> {text[:40]:40s} {href}")
                found = True

        if not found:
            print(f"  No results found")

    except Exception as e:
        print(f"  Error: {e}")
