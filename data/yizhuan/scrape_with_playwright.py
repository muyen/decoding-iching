#!/usr/bin/env python3
"""
Scrape the Ten Wings using a simpler, more direct approach.
This version fetches from a reliable Chinese classics database.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ten Wings data with direct URLs from reliable sources
TEN_WINGS_DATA = {
    "xici_upper": {
        "title": "系辞上传",
        "english": "Xi Ci Upper",
        "url": "https://www.gushiwen.cn/guwen/book_adb08001c74f0cae.aspx"
    },
    "xici_lower": {
        "title": "系辞下传",
        "english": "Xi Ci Lower",
        "url": "https://www.gushiwen.cn/guwen/book_adb08001c74f0caf.aspx"
    },
    "wenyan": {
        "title": "文言传",
        "english": "Wen Yan",
        "url": "https://www.gushiwen.cn/guwen/book_adb08001c74f0cb0.aspx"
    },
    "shuogua": {
        "title": "说卦传",
        "english": "Shuo Gua",
        "url": "https://www.gushiwen.cn/guwen/book_adb08001c74f0cb1.aspx"
    },
    "xugua": {
        "title": "序卦传",
        "english": "Xu Gua",
        "url": "https://www.gushiwen.cn/guwen/book_adb08001c74f0cb2.aspx"
    },
    "zagua": {
        "title": "杂卦传",
        "english": "Za Gua",
        "url": "https://www.gushiwen.cn/guwen/book_adb08001c74f0cb3.aspx"
    }
}

# For Tuan and Xiang, we'll construct them from the main I Ching text
# These are embedded with each hexagram

class SimpleYiZhuanScraper:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def scrape_gushiwen(self, url: str, title: str) -> Optional[Dict]:
        """Scrape text from gushiwen.cn"""
        print(f"Fetching {title} from {url}...")

        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the main content container
            # gushiwen.cn typically uses div with class 'contson' or similar
            content = soup.find('div', {'class': 'contson'})
            if not content:
                # Try alternative selectors
                content = soup.find('div', {'id': 'contson'})
            if not content:
                # Try to find any div with substantial Chinese text
                for div in soup.find_all('div'):
                    text = div.get_text(strip=True)
                    if len(text) > 500 and '章第' in text or '曰' in text:
                        content = div
                        break

            if not content:
                print(f"  Warning: Could not find content for {title}")
                return None

            # Extract text
            full_text = content.get_text(separator='\n', strip=True)

            # Split into paragraphs
            paragraphs = []
            lines = full_text.split('\n')
            current_para = []

            for line in lines:
                line = line.strip()
                if not line:
                    if current_para:
                        paragraphs.append(''.join(current_para))
                        current_para = []
                else:
                    current_para.append(line)

            if current_para:
                paragraphs.append(''.join(current_para))

            # Filter out very short paragraphs
            paragraphs = [p for p in paragraphs if len(p) > 20]

            full_content = '\n\n'.join(paragraphs)

            if not paragraphs or len(full_content) < 100:
                print(f"  Warning: Content too short for {title}")
                return None

            result = {
                "title": title,
                "source": url,
                "content": full_content,
                "paragraphs": paragraphs,
                "char_count": len(full_content)
            }

            print(f"  Success! Found {len(paragraphs)} paragraphs, {len(full_content):,} characters")
            return result

        except Exception as e:
            print(f"  Error fetching {title}: {e}")
            return None

    def scrape_all(self) -> Dict[str, Dict]:
        """Scrape all available Ten Wings texts"""
        results = {}

        for idx, (key, info) in enumerate(TEN_WINGS_DATA.items(), 1):
            print(f"\n[{idx}/{len(TEN_WINGS_DATA)}] Scraping {info['title']} ({info['english']})...")

            result = self.scrape_gushiwen(info['url'], info['title'])

            if result:
                results[key] = result

                # Save individual file
                filename = f"{key}.json"
                filepath = self.output_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  Saved to {filename}")

            # Rate limiting
            time.sleep(2)

        return results

    def save_combined(self, results: Dict[str, Dict]):
        """Save all results into a combined file"""
        combined = {
            "title": "十翼 (Ten Wings)",
            "description": "Six of the Ten Wings commentaries on the I Ching (彖传 and 象传 are embedded in hexagram texts)",
            "note": "Tuan Zhuan (彖传) and Xiang Zhuan (象传) are typically included with each hexagram's commentary and not separate texts",
            "wings": results,
            "total_wings": len(results),
            "total_characters": sum(r.get('char_count', 0) for r in results.values())
        }

        filepath = self.output_dir / "yizhuan_complete.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"Combined file saved to yizhuan_complete.json")
        print(f"Total wings collected: {len(results)}/6 (independent texts)")
        print(f"Total characters: {combined['total_characters']:,}")
        print(f"{'='*60}")
        print(f"\nNote: 彖传 and 象传 (Tuan/Xiang commentaries) are embedded")
        print(f"with each hexagram and collected separately.")

def main():
    output_dir = "/Users/arsenelee/github/iching/data/yizhuan"
    scraper = SimpleYiZhuanScraper(output_dir)

    print("="*60)
    print("Ten Wings (十翼) Scraper - Simplified Version")
    print("="*60)
    print("This will download the 6 independent Ten Wings texts.")
    print("Tuan and Xiang commentaries are in the hexagram texts.\n")

    results = scraper.scrape_all()
    scraper.save_combined(results)

    # Print summary
    print("\nSummary of Downloaded Texts:")
    for key, info in TEN_WINGS_DATA.items():
        if key in results:
            print(f"  ✓ {info['title']} ({info['english']}) - {results[key]['char_count']:,} chars")
        else:
            print(f"  ✗ {info['title']} ({info['english']}) - Failed")

if __name__ == "__main__":
    main()
