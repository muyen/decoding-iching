#!/usr/bin/env python3
"""
Scrape the Ten Wings (十翼) texts from online sources.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ten Wings mapping with Chinese titles and ctext.org paths
TEN_WINGS = {
    "tuan_upper": {
        "title": "彖传上",
        "english": "Tuan Zhuan Upper",
        "ctext_path": "tuan-zhuan-i/zhs"
    },
    "tuan_lower": {
        "title": "彖传下",
        "english": "Tuan Zhuan Lower",
        "ctext_path": "tuan-zhuan-ii/zhs"
    },
    "xiang_upper": {
        "title": "象传上",
        "english": "Xiang Zhuan Upper",
        "ctext_path": "xiang-zhuan-i/zhs"
    },
    "xiang_lower": {
        "title": "象传下",
        "english": "Xiang Zhuan Lower",
        "ctext_path": "xiang-zhuan-ii/zhs"
    },
    "xici_upper": {
        "title": "系辞上",
        "english": "Xi Ci Upper",
        "ctext_path": "xi-ci-i/zhs"
    },
    "xici_lower": {
        "title": "系辞下",
        "english": "Xi Ci Lower",
        "ctext_path": "xi-ci-ii/zhs"
    },
    "wenyan": {
        "title": "文言传",
        "english": "Wen Yan",
        "ctext_path": "wen-yan/zhs"
    },
    "shuogua": {
        "title": "说卦传",
        "english": "Shuo Gua",
        "ctext_path": "shuo-gua/zhs"
    },
    "xugua": {
        "title": "序卦传",
        "english": "Xu Gua",
        "ctext_path": "xu-gua/zhs"
    },
    "zagua": {
        "title": "杂卦传",
        "english": "Za Gua",
        "ctext_path": "za-gua/zhs"
    }
}

class YiZhuanScraper:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_ctext(self, path: str, title: str) -> Optional[Dict]:
        """Scrape text from ctext.org"""
        url = f"https://ctext.org/book-of-changes/{path}"
        print(f"Fetching {title} from {url}...")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the main content area
            content_div = soup.find('div', {'id': 'content3'})
            if not content_div:
                print(f"  Warning: Could not find content div for {title}")
                return None

            # Extract paragraphs
            paragraphs = []

            # Method 1: Look for table with td.ctext elements
            table = content_div.find('table')
            if table:
                cells = table.find_all('td', class_='ctext')
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text and len(text) > 3:  # Filter out very short texts
                        paragraphs.append(text)

            # Method 2: Look for div or span elements with Chinese text
            if not paragraphs:
                for elem in content_div.find_all(['div', 'p', 'span']):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and any('\u4e00' <= c <= '\u9fff' for c in text):
                        paragraphs.append(text)

            # Combine into full content
            full_content = '\n\n'.join(paragraphs)

            if not paragraphs:
                print(f"  Warning: No paragraphs found for {title}")
                return None

            result = {
                "title": title,
                "source": url,
                "content": full_content,
                "paragraphs": paragraphs,
                "char_count": len(full_content)
            }

            print(f"  Success! Found {len(paragraphs)} paragraphs, {len(full_content)} characters")
            return result

        except Exception as e:
            print(f"  Error fetching {title}: {e}")
            return None

    def scrape_all(self) -> Dict[str, Dict]:
        """Scrape all Ten Wings texts"""
        results = {}

        for key, info in TEN_WINGS.items():
            print(f"\n[{len(results)+1}/10] Scraping {info['title']} ({info['english']})...")

            # Try ctext.org first
            result = self.scrape_ctext(info['ctext_path'], info['title'])

            if result:
                results[key] = result

                # Save individual file
                filename = f"{key}.json"
                filepath = self.output_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  Saved to {filename}")
            else:
                print(f"  Failed to scrape {info['title']}")

            # Rate limiting
            time.sleep(1.5)

        return results

    def save_combined(self, results: Dict[str, Dict]):
        """Save all results into a combined file"""
        combined = {
            "title": "十翼 (Ten Wings Complete)",
            "description": "Complete collection of the Ten Wings commentaries on the I Ching",
            "wings": results,
            "total_wings": len(results),
            "total_characters": sum(r.get('char_count', 0) for r in results.values())
        }

        filepath = self.output_dir / "yizhuan_complete.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"Combined file saved to yizhuan_complete.json")
        print(f"Total wings collected: {len(results)}/10")
        print(f"Total characters: {combined['total_characters']:,}")
        print(f"{'='*60}")

def main():
    output_dir = "/Users/arsenelee/github/iching/data/yizhuan"
    scraper = YiZhuanScraper(output_dir)

    print("="*60)
    print("Ten Wings (十翼) Scraper")
    print("="*60)

    results = scraper.scrape_all()
    scraper.save_combined(results)

    # Print summary
    print("\nSummary:")
    for key, info in TEN_WINGS.items():
        status = "✓" if key in results else "✗"
        print(f"  {status} {info['title']} ({info['english']})")

if __name__ == "__main__":
    main()
