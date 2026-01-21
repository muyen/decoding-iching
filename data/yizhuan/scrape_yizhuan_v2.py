#!/usr/bin/env python3
"""
Scrape the Ten Wings (十翼) texts from ctext.org with improved parsing.
This version tries to get the actual chapter links and content.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import re

# Ten Wings mapping with Chinese titles and ctext.org paths
TEN_WINGS = {
    "tuan_upper": {
        "title": "彖传上",
        "english": "Tuan Zhuan Upper",
        "ctext_chapters": list(range(1, 31))  # 30 hexagrams in upper
    },
    "tuan_lower": {
        "title": "彖传下",
        "english": "Tuan Zhuan Lower",
        "ctext_chapters": list(range(31, 65))  # 34 hexagrams in lower
    },
    "xiang_upper": {
        "title": "象传上",
        "english": "Xiang Zhuan Upper",
        "ctext_chapters": list(range(1, 31))
    },
    "xiang_lower": {
        "title": "象传下",
        "english": "Xiang Zhuan Lower",
        "ctext_chapters": list(range(31, 65))
    },
    "xici_upper": {
        "title": "系辞上",
        "english": "Xi Ci Upper",
        "ctext_chapters": list(range(1, 13))  # 12 chapters
    },
    "xici_lower": {
        "title": "系辞下",
        "english": "Xi Ci Lower",
        "ctext_chapters": list(range(1, 13))  # 12 chapters
    },
    "wenyan": {
        "title": "文言传",
        "english": "Wen Yan",
        "ctext_chapters": [1, 2]  # Qian and Kun
    },
    "shuogua": {
        "title": "说卦传",
        "english": "Shuo Gua",
        "ctext_chapters": list(range(1, 12))  # 11 chapters
    },
    "xugua": {
        "title": "序卦传",
        "english": "Xu Gua",
        "ctext_chapters": [1, 2]  # Upper and Lower
    },
    "zagua": {
        "title": "杂卦传",
        "english": "Za Gua",
        "ctext_chapters": [1]  # Single chapter
    }
}

# Hexagram names for Tuan and Xiang
HEXAGRAM_NAMES = [
    "乾", "坤", "屯", "蒙", "需", "讼", "师", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "謙", "豫",
    "隨", "蠱", "臨", "觀", "噬嗑", "賁", "剝", "復",
    "无妄", "大畜", "頤", "大過", "坎", "離", "咸", "恆",
    "遯", "大壯", "晉", "明夷", "家人", "睽", "蹇", "解",
    "損", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "漸", "歸妹", "豐", "旅",
    "巽", "兌", "渙", "節", "中孚", "小過", "既濟", "未濟"
]

class YiZhuanScraperV2:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        # Base URLs for different wings
        self.base_urls = {
            "tuan_upper": "https://ctext.org/book-of-changes/tuan-zhuan/zhs",
            "tuan_lower": "https://ctext.org/book-of-changes/tuan-zhuan/zhs",
            "xiang_upper": "https://ctext.org/book-of-changes/xiang-zhuan/zhs",
            "xiang_lower": "https://ctext.org/book-of-changes/xiang-zhuan/zhs",
            "xici_upper": "https://ctext.org/book-of-changes/xi-ci-shang/zhs",
            "xici_lower": "https://ctext.org/book-of-changes/xi-ci-xia/zhs",
            "wenyan": "https://ctext.org/book-of-changes/wen-yan/zhs",
            "shuogua": "https://ctext.org/book-of-changes/shuo-gua/zhs",
            "xugua": "https://ctext.org/book-of-changes/xu-gua/zhs",
            "zagua": "https://ctext.org/book-of-changes/za-gua/zhs"
        }

    def extract_text_from_page(self, soup: BeautifulSoup) -> List[str]:
        """Extract Chinese text paragraphs from a ctext.org page"""
        paragraphs = []

        # Try to find the main text container
        # ctext.org uses various structures, try multiple methods

        # Method 1: Look for td.ctext elements in tables
        for td in soup.find_all('td', class_='ctext'):
            text = td.get_text(strip=True)
            # Filter out English text and very short text
            if text and len(text) > 10 and re.search(r'[\u4e00-\u9fff]', text):
                # Remove English sentences
                chinese_only = re.sub(r'[a-zA-Z\s]+', '', text)
                if len(chinese_only) > 10:
                    paragraphs.append(text)

        # Method 2: Look for specific content divs
        if not paragraphs:
            content = soup.find('div', {'id': 'content3'})
            if content:
                for p in content.find_all(['p', 'div'], recursive=False):
                    text = p.get_text(strip=True)
                    if text and len(text) > 10 and re.search(r'[\u4e00-\u9fff]', text):
                        paragraphs.append(text)

        # Method 3: Look for text in span elements
        if not paragraphs:
            for span in soup.find_all('span', class_=''):
                text = span.get_text(strip=True)
                if text and len(text) > 10 and re.search(r'[\u4e00-\u9fff]', text):
                    paragraphs.append(text)

        return paragraphs

    def scrape_wing_from_chapter_pages(self, wing_key: str, info: Dict) -> Optional[Dict]:
        """Try to scrape a wing by fetching individual chapter pages"""
        print(f"Trying alternate method for {info['title']}...")

        # For now, use simple gushiwen.cn source
        # This is a more reliable source with cleaner HTML
        gushiwen_urls = {
            "xici_upper": "https://so.gushiwen.cn/guwen/bookv_46653FD803893E4F1F9D3E503091CF3D.aspx",
            "xici_lower": "https://so.gushiwen.cn/guwen/bookv_46653FD803893E4F6DB2F46F5BA956BD.aspx",
            "wenyan": "https://so.gushiwen.cn/guwen/bookv_46653FD803893E4F4C86BB2DA038D5FD.aspx",
            "shuogua": "https://so.gushiwen.cn/guwen/bookv_46653FD803893E4F9F3C9C0ED9F9FF10.aspx",
            "xugua": "https://so.gushiwen.cn/guwen/bookv_46653FD803893E4F7DD1B5CC3C215FEA.aspx",
            "zagua": "https://so.gushiwen.cn/guwen/bookv_46653FD803893E4F5A4ACB3CDC47CEEF.aspx"
        }

        url = gushiwen_urls.get(wing_key)
        if not url:
            return None

        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text from gushiwen.cn structure
            paragraphs = []
            content_div = soup.find('div', class_='contson')
            if content_div:
                text = content_div.get_text(strip=True)
                # Split by chapter markers or double newlines
                sections = re.split(r'\n\n+', text)
                for section in sections:
                    section = section.strip()
                    if len(section) > 20:
                        paragraphs.append(section)

            if paragraphs:
                full_content = '\n\n'.join(paragraphs)
                result = {
                    "title": info['title'],
                    "source": url,
                    "content": full_content,
                    "paragraphs": paragraphs,
                    "char_count": len(full_content)
                }
                print(f"  Success! Found {len(paragraphs)} sections, {len(full_content)} characters")
                return result

        except Exception as e:
            print(f"  Error: {e}")

        return None

    def scrape_all(self) -> Dict[str, Dict]:
        """Scrape all Ten Wings texts"""
        results = {}

        for key, info in TEN_WINGS.items():
            print(f"\n[{len(results)+1}/10] Scraping {info['title']} ({info['english']})...")

            # Try alternate method for certain wings
            if key in ['xici_upper', 'xici_lower', 'wenyan', 'shuogua', 'xugua', 'zagua']:
                result = self.scrape_wing_from_chapter_pages(key, info)
            else:
                # For Tuan and Xiang, we need a different approach
                # These are embedded in the hexagram pages
                result = None
                print(f"  Skipping {info['title']} - needs hexagram-by-hexagram extraction")

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
    scraper = YiZhuanScraperV2(output_dir)

    print("="*60)
    print("Ten Wings (十翼) Scraper V2")
    print("="*60)

    results = scraper.scrape_all()
    scraper.save_combined(results)

    # Print summary
    print("\nSummary:")
    for key, info in TEN_WINGS.items():
        status = "✓" if key in results else "✗"
        char_count = results[key]['char_count'] if key in results else 0
        print(f"  {status} {info['title']} ({info['english']}) - {char_count:,} chars")

if __name__ == "__main__":
    main()
