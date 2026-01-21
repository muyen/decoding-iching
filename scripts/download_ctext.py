#!/usr/bin/env python3
"""
Download Zhou Yi (周易) texts from ctext.org

This script downloads:
1. The 64 hexagrams with their 卦辞 and 爻辞 (Yi Jing / 易經)
2. The Ten Wings (十翼):
   - 彖传 (Tuan Zhuan) - Commentary on the Judgment
   - 象传 (Xiang Zhuan) - Commentary on the Images
   - 繫辭上/下 (Xi Ci) - Great Commentary
   - 文言 (Wen Yan) - Commentary on the Words of the Text
   - 說卦 (Shuo Gua) - Discussion of the Trigrams
   - 序卦 (Xu Gua) - Sequence of the Hexagrams
   - 雜卦 (Za Gua) - Miscellaneous Notes on the Hexagrams

Note: The ctext.org API requires authentication for gettext calls.
This script uses web scraping as a fallback when API calls fail.
Rate limits apply - use --rate-limit to increase delay between requests.

Usage:
    python download_ctext.py [--api-key YOUR_API_KEY] [--rate-limit 2.0] [--resume]
"""

import os
import sys
import json
import time
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Try to import ctext library
try:
    from ctext import ctext
    CTEXT_AVAILABLE = True
except ImportError:
    CTEXT_AVAILABLE = False
    print("Warning: ctext library not available, using web scraping only")


# Configuration
BASE_URL = "https://ctext.org"
API_BASE = "http://api.ctext.org"
OUTPUT_DIR = Path("/Users/arsenelee/github/iching/data/ctext")
RATE_LIMIT_DELAY = 2.0  # seconds between requests (increased default)
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0

# Headers for web requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5,zh-CN;q=0.3,zh;q=0.2',
}

# The 64 hexagrams URN mapping (pinyin slug -> hexagram info)
HEXAGRAM_URNS = [
    ("qian", "乾", 1),
    ("kun", "坤", 2),
    ("zhun", "屯", 3),
    ("meng", "蒙", 4),
    ("xu", "需", 5),
    ("song", "訟", 6),
    ("shi", "師", 7),
    ("bi", "比", 8),
    ("xiao-xu", "小畜", 9),
    ("lu", "履", 10),
    ("tai", "泰", 11),
    ("pi", "否", 12),
    ("tong-ren", "同人", 13),
    ("da-you", "大有", 14),
    ("qian1", "謙", 15),
    ("yu", "豫", 16),
    ("sui", "隨", 17),
    ("gu", "蠱", 18),
    ("lin", "臨", 19),
    ("guan", "觀", 20),
    ("shi-he", "噬嗑", 21),
    ("bi1", "賁", 22),
    ("bo", "剝", 23),
    ("fu", "復", 24),
    ("wu-wang", "无妄", 25),
    ("da-xu", "大畜", 26),
    ("yi", "頤", 27),
    ("da-guo", "大過", 28),
    ("kan", "坎", 29),
    ("li", "離", 30),
    ("xian", "咸", 31),
    ("heng", "恆", 32),
    ("dun", "遯", 33),
    ("da-zhuang", "大壯", 34),
    ("jin", "晉", 35),
    ("ming-yi", "明夷", 36),
    ("jia-ren", "家人", 37),
    ("kui", "睽", 38),
    ("jian", "蹇", 39),
    ("jie", "解", 40),
    ("sun", "損", 41),
    ("yi1", "益", 42),
    ("guai", "夬", 43),
    ("gou", "姤", 44),
    ("cui", "萃", 45),
    ("sheng", "升", 46),
    ("kun1", "困", 47),
    ("jing", "井", 48),
    ("ge", "革", 49),
    ("ding", "鼎", 50),
    ("zhen", "震", 51),
    ("gen", "艮", 52),
    ("jian1", "漸", 53),
    ("gui-mei", "歸妹", 54),
    ("feng", "豐", 55),
    ("lu1", "旅", 56),
    ("xun", "巽", 57),
    ("dui", "兌", 58),
    ("huan", "渙", 59),
    ("jie1", "節", 60),
    ("zhong-fu", "中孚", 61),
    ("xiao-guo", "小過", 62),
    ("ji-ji", "既濟", 63),
    ("wei-ji", "未濟", 64),
]

# Ten Wings sections
TEN_WINGS = {
    "tuan-zhuan": {
        "name_zh": "彖傳",
        "name_en": "Tuan Zhuan",
        "description": "Commentary on the Judgment",
        "sections": [
            # Upper section (hexagrams 1-30)
            ("qian2", "乾", 1), ("kun2", "坤", 2), ("zhun1", "屯", 3), ("meng1", "蒙", 4),
            ("xu1", "需", 5), ("song1", "訟", 6), ("shi1", "師", 7), ("bi2", "比", 8),
            ("xiao-xu1", "小畜", 9), ("lu2", "履", 10), ("tai1", "泰", 11), ("pi1", "否", 12),
            ("tong-ren1", "同人", 13), ("da-you1", "大有", 14), ("qian3", "謙", 15), ("yu1", "豫", 16),
            ("sui1", "隨", 17), ("gu1", "蠱", 18), ("lin1", "臨", 19), ("guan1", "觀", 20),
            ("shi-he1", "噬嗑", 21), ("bi3", "賁", 22), ("bo1", "剝", 23), ("fu1", "復", 24),
            ("wu-wang1", "无妄", 25), ("da-xu1", "大畜", 26), ("yi2", "頤", 27), ("da-guo1", "大過", 28),
            ("kan1", "坎", 29), ("li1", "離", 30),
            # Lower section (hexagrams 31-64)
            ("xian1", "咸", 31), ("heng1", "恆", 32), ("dun1", "遯", 33), ("da-zhuang1", "大壯", 34),
            ("jin1", "晉", 35), ("ming-yi1", "明夷", 36), ("jia-ren1", "家人", 37), ("kui1", "睽", 38),
            ("jian2", "蹇", 39), ("jie2", "解", 40), ("sun1", "損", 41), ("yi3", "益", 42),
            ("guai1", "夬", 43), ("gou1", "姤", 44), ("cui1", "萃", 45), ("sheng1", "升", 46),
            ("kun3", "困", 47), ("jing1", "井", 48), ("ge1", "革", 49), ("ding1", "鼎", 50),
            ("zhen1", "震", 51), ("gen1", "艮", 52), ("jian3", "漸", 53), ("gui-mei1", "歸妹", 54),
            ("feng1", "豐", 55), ("lu3", "旅", 56), ("xun1", "巽", 57), ("dui1", "兌", 58),
            ("huan1", "渙", 59), ("jie3", "節", 60), ("zhong-fu1", "中孚", 61), ("xiao-guo1", "小過", 62),
            ("ji-ji1", "既濟", 63), ("wei-ji1", "未濟", 64),
        ]
    },
    "xiang-zhuan": {
        "name_zh": "象傳",
        "name_en": "Xiang Zhuan",
        "description": "Commentary on the Images",
        "sections": [
            # Different URL patterns for xiang zhuan
            ("gan", "乾", 1), ("kun4", "坤", 2), ("zhun2", "屯", 3), ("meng2", "蒙", 4),
            ("xu2", "需", 5), ("song2", "訟", 6), ("shi2", "師", 7), ("bi4", "比", 8),
            ("xiao-chu", "小畜", 9), ("lv", "履", 10), ("tai2", "泰", 11), ("fou", "否", 12),
            ("tong-ren2", "同人", 13), ("da-you2", "大有", 14), ("qian4", "謙", 15), ("yu2", "豫", 16),
            ("sui2", "隨", 17), ("gu2", "蠱", 18), ("lin2", "臨", 19), ("guan2", "觀", 20),
            ("shi-ke", "噬嗑", 21), ("bi5", "賁", 22), ("bo2", "剝", 23), ("fu2", "復", 24),
            ("wu-wang2", "无妄", 25), ("da-chu", "大畜", 26), ("yi4", "頤", 27), ("da-guo2", "大過", 28),
            ("kan2", "坎", 29), ("li2", "離", 30),
            ("xian2", "咸", 31), ("heng2", "恆", 32), ("dun2", "遯", 33), ("da-zhuang2", "大壯", 34),
            ("jin2", "晉", 35), ("ming-yi2", "明夷", 36), ("jia-ren2", "家人", 37), ("kui2", "睽", 38),
            ("jian4", "蹇", 39), ("jie4", "解", 40), ("sun2", "損", 41), ("yi5", "益", 42),
            ("guai2", "夬", 43), ("gou2", "姤", 44), ("cui2", "萃", 45), ("sheng2", "升", 46),
            ("kun5", "困", 47), ("jing2", "井", 48), ("ge2", "革", 49), ("ding2", "鼎", 50),
            ("zhen2", "震", 51), ("gen2", "艮", 52), ("jian5", "漸", 53), ("gui-mei2", "歸妹", 54),
            ("feng2", "豐", 55), ("lv1", "旅", 56), ("xun2", "巽", 57), ("dui2", "兌", 58),
            ("huan2", "渙", 59), ("jie5", "節", 60), ("zhong-fu2", "中孚", 61), ("xiao-guo2", "小過", 62),
            ("ji-ji2", "既濟", 63), ("wei-ji2", "未濟", 64),
        ]
    },
    "xi-ci": {
        "name_zh": "繫辭",
        "name_en": "Xi Ci",
        "description": "Great Commentary (Appended Statements)",
        "sections": [
            ("xi-ci-shang", "繫辭上", "upper"),
            ("xi-ci-xia", "繫辭下", "lower"),
        ]
    },
    "wen-yan": {
        "name_zh": "文言",
        "name_en": "Wen Yan",
        "description": "Commentary on the Words of the Text",
        "sections": [
            ("gan1", "乾", "qian"),
            ("kun6", "坤", "kun"),
        ]
    },
    "shuo-gua": {
        "name_zh": "說卦",
        "name_en": "Shuo Gua",
        "description": "Discussion of the Trigrams",
        "sections": [("shuo-gua", "說卦", "single")]
    },
    "xu-gua": {
        "name_zh": "序卦",
        "name_en": "Xu Gua",
        "description": "Sequence of the Hexagrams",
        "sections": [("xu-gua", "序卦", "single")]
    },
    "za-gua": {
        "name_zh": "雜卦",
        "name_en": "Za Gua",
        "description": "Miscellaneous Notes on the Hexagrams",
        "sections": [("za-gua", "雜卦", "single")]
    },
}


@dataclass
class TextContent:
    """Container for downloaded text content"""
    urn: str
    url: str
    title_zh: str
    title_en: str
    content_zh: List[str]
    content_en: Optional[List[str]]
    metadata: Dict[str, Any]


class CtextDownloader:
    """Download Zhou Yi texts from ctext.org"""

    def __init__(self, api_key: Optional[str] = None, resume: bool = False):
        self.api_key = api_key
        self.resume = resume
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.rate_limited = False
        self.current_delay = RATE_LIMIT_DELAY

        if api_key and CTEXT_AVAILABLE:
            ctext.setapikey(api_key)

        # Create output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "downloaded": 0,
            "failed": 0,
            "skipped": 0,
            "api_calls": 0,
            "web_scrapes": 0,
        }

    def _rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(self.current_delay)

    def _handle_rate_limit(self):
        """Handle rate limit by increasing delay"""
        self.rate_limited = True
        self.current_delay = min(self.current_delay * BACKOFF_FACTOR, 30.0)
        print(f"  Rate limited! Increasing delay to {self.current_delay:.1f}s")
        time.sleep(self.current_delay * 2)  # Extra wait after rate limit

    def _try_api(self, urn: str) -> Optional[Dict]:
        """Try to get text via API (requires authentication)"""
        if not CTEXT_AVAILABLE:
            return None

        for attempt in range(MAX_RETRIES):
            try:
                self.stats["api_calls"] += 1
                result = ctext.gettext(urn)
                return result
            except Exception as e:
                error_str = str(e)
                if "ERR_REQUIRES_AUTHENTICATION" in error_str:
                    return None
                if "ERR_REQUEST_LIMIT" in error_str:
                    self._handle_rate_limit()
                    if attempt < MAX_RETRIES - 1:
                        continue
                print(f"  API error for {urn}: {e}")
                return None
        return None

    def _scrape_page(self, url: str, lang: str = "zh") -> Optional[Dict]:
        """Scrape text content from web page"""
        for attempt in range(MAX_RETRIES):
            try:
                full_url = f"{BASE_URL}{url}" if not url.startswith("http") else url
                if lang == "zh" and "/zh" not in full_url and "/zhs" not in full_url:
                    full_url = full_url.rstrip("/") + "/zh"

                self._rate_limit()
                response = self.session.get(full_url, timeout=30)

                if response.status_code == 403:
                    self._handle_rate_limit()
                    if attempt < MAX_RETRIES - 1:
                        continue
                    return None

                response.raise_for_status()
                self.stats["web_scrapes"] += 1

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find text content
                content = []

                # Look for the main content area with Chinese text
                # The text is typically in td elements with class 'ctext'
                ctext_elements = soup.find_all('td', class_='ctext')
                for elem in ctext_elements:
                    text = elem.get_text(strip=True)
                    if text:
                        content.append(text)

                # Also try finding content in other patterns
                if not content:
                    # Try finding in div with id 'content3'
                    content_div = soup.find('div', {'id': 'content3'})
                    if content_div:
                        for p in content_div.find_all(['p', 'div']):
                            text = p.get_text(strip=True)
                            if text and len(text) > 2:
                                content.append(text)

                # Extract title
                title = ""
                title_elem = soup.find('title')
                if title_elem:
                    title = title_elem.get_text(strip=True)

                return {
                    "url": full_url,
                    "title": title,
                    "content": content
                }

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    self._handle_rate_limit()
                    if attempt < MAX_RETRIES - 1:
                        continue
                print(f"  Scrape error for {url}: {e}")
                return None
            except Exception as e:
                print(f"  Scrape error for {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(self.current_delay)
                    continue
                return None
        return None

    def _load_existing_data(self, filepath: Path) -> Optional[Dict]:
        """Load existing data file for resume functionality"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def download_hexagram(self, slug: str, name_zh: str, number: int) -> Optional[TextContent]:
        """Download a single hexagram's text"""
        urn = f"ctp:book-of-changes/{slug}"
        url = f"/book-of-changes/{slug}"

        print(f"  Downloading hexagram {number}: {name_zh} ({slug})...")

        # Try API first
        api_result = self._try_api(urn)

        if api_result:
            return TextContent(
                urn=urn,
                url=url,
                title_zh=name_zh,
                title_en=slug.replace("-", " ").title(),
                content_zh=api_result.get("fulltext", []),
                content_en=api_result.get("translation", []),
                metadata={"source": "api", "number": number}
            )

        # Fallback to web scraping
        scraped = self._scrape_page(url)
        if scraped:
            return TextContent(
                urn=urn,
                url=scraped["url"],
                title_zh=name_zh,
                title_en=slug.replace("-", " ").title(),
                content_zh=scraped["content"],
                content_en=None,
                metadata={"source": "web", "number": number}
            )

        return None

    def download_64_hexagrams(self) -> Dict[str, Any]:
        """Download all 64 hexagrams"""
        print("\n=== Downloading 64 Hexagrams (易經) ===")

        output_path = OUTPUT_DIR / "zhouyi_64gua.json"

        # Check for existing data if resume mode
        existing_data = None
        existing_hexagrams = {}
        if self.resume:
            existing_data = self._load_existing_data(output_path)
            if existing_data:
                for h in existing_data.get("hexagrams", []):
                    if "content_zh" in h and h["content_zh"]:
                        num = h.get("metadata", {}).get("number") or h.get("number")
                        if num:
                            existing_hexagrams[num] = h
                print(f"  Found {len(existing_hexagrams)} existing hexagrams")

        hexagrams = []

        for slug, name_zh, number in HEXAGRAM_URNS:
            # Check if already downloaded
            if number in existing_hexagrams:
                print(f"  Skipping hexagram {number}: {name_zh} (already downloaded)")
                hexagrams.append(existing_hexagrams[number])
                self.stats["skipped"] += 1
                continue

            result = self.download_hexagram(slug, name_zh, number)
            if result:
                hexagrams.append(asdict(result))
                self.stats["downloaded"] += 1
            else:
                self.stats["failed"] += 1
                hexagrams.append({
                    "number": number,
                    "name_zh": name_zh,
                    "slug": slug,
                    "error": "Failed to download"
                })

        output = {
            "title": "周易六十四卦",
            "title_en": "64 Hexagrams of Zhou Yi",
            "description": "The 64 hexagrams with 卦辞 and 爻辞",
            "source": "ctext.org",
            "download_date": datetime.now().isoformat(),
            "total_hexagrams": 64,
            "hexagrams": hexagrams
        }

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"  Saved to {output_path}")
        return output

    def download_wing_section(self, wing_key: str, section: tuple) -> Optional[Dict]:
        """Download a single section of a Ten Wing"""
        slug = section[0]
        name_zh = section[1]

        urn = f"ctp:book-of-changes/{slug}"
        url = f"/book-of-changes/{slug}"

        print(f"    Downloading {name_zh} ({slug})...")

        # Try API first
        api_result = self._try_api(urn)

        if api_result:
            return {
                "slug": slug,
                "name_zh": name_zh,
                "content_zh": api_result.get("fulltext", []),
                "content_en": api_result.get("translation", []),
                "source": "api"
            }

        # Fallback to web scraping
        scraped = self._scrape_page(url)
        if scraped:
            return {
                "slug": slug,
                "name_zh": name_zh,
                "url": scraped["url"],
                "content_zh": scraped["content"],
                "content_en": None,
                "source": "web"
            }

        return None

    def download_ten_wings(self) -> Dict[str, Any]:
        """Download all Ten Wings (十翼)"""
        print("\n=== Downloading Ten Wings (十翼) ===")

        all_wings = {}

        for wing_key, wing_info in TEN_WINGS.items():
            print(f"\n  Processing {wing_info['name_zh']} ({wing_info['name_en']})...")

            filename = f"yizhuan_{wing_key.replace('-', '')}.json"
            output_path = OUTPUT_DIR / filename

            # Check for existing data if resume mode
            existing_sections = {}
            if self.resume:
                existing_data = self._load_existing_data(output_path)
                if existing_data:
                    for s in existing_data.get("data", {}).get("sections", []):
                        if "content_zh" in s and s["content_zh"]:
                            existing_sections[s["slug"]] = s
                    print(f"    Found {len(existing_sections)} existing sections")

            sections = []
            for section in wing_info["sections"]:
                slug = section[0]

                # Check if already downloaded
                if slug in existing_sections:
                    print(f"    Skipping {section[1]} (already downloaded)")
                    sections.append(existing_sections[slug])
                    self.stats["skipped"] += 1
                    continue

                result = self.download_wing_section(wing_key, section)
                if result:
                    sections.append(result)
                    self.stats["downloaded"] += 1
                else:
                    self.stats["failed"] += 1
                    sections.append({
                        "slug": section[0],
                        "name_zh": section[1],
                        "error": "Failed to download"
                    })

            wing_data = {
                "name_zh": wing_info["name_zh"],
                "name_en": wing_info["name_en"],
                "description": wing_info["description"],
                "sections": sections
            }

            all_wings[wing_key] = wing_data

            # Save individual wing file
            output = {
                "title": wing_info["name_zh"],
                "title_en": wing_info["name_en"],
                "description": wing_info["description"],
                "source": "ctext.org",
                "download_date": datetime.now().isoformat(),
                "data": wing_data
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

            print(f"    Saved to {output_path}")

        return all_wings

    def download_all(self):
        """Download all Zhou Yi texts"""
        print("=" * 60)
        print("Zhou Yi (周易) Downloader")
        print("=" * 60)
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"API key: {'configured' if self.api_key else 'not configured'}")
        print(f"ctext library: {'available' if CTEXT_AVAILABLE else 'not available'}")
        print(f"Resume mode: {'enabled' if self.resume else 'disabled'}")
        print(f"Rate limit delay: {RATE_LIMIT_DELAY}s")

        start_time = time.time()

        # Download 64 hexagrams
        hexagrams = self.download_64_hexagrams()

        # Download Ten Wings
        wings = self.download_ten_wings()

        # Create summary file
        summary = {
            "title": "周易完整文本",
            "title_en": "Complete Zhou Yi Texts",
            "source": "ctext.org",
            "download_date": datetime.now().isoformat(),
            "statistics": self.stats,
            "duration_seconds": time.time() - start_time,
            "files": {
                "hexagrams": "zhouyi_64gua.json",
                "tuan_zhuan": "yizhuan_tuanzhuan.json",
                "xiang_zhuan": "yizhuan_xiangzhuan.json",
                "xi_ci": "yizhuan_xici.json",
                "wen_yan": "yizhuan_wenyan.json",
                "shuo_gua": "yizhuan_shuogua.json",
                "xu_gua": "yizhuan_xugua.json",
                "za_gua": "yizhuan_zagua.json",
            },
            "structure": {
                "hexagrams_count": 64,
                "ten_wings": list(TEN_WINGS.keys())
            },
            "notes": [
                "ctext.org API requires authentication for text content",
                "Rate limits may prevent full download in single run",
                "Use --resume flag to continue incomplete downloads",
                "Use --rate-limit to increase delay between requests"
            ]
        }

        summary_path = OUTPUT_DIR / "download_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # Print final statistics
        print("\n" + "=" * 60)
        print("Download Complete!")
        print("=" * 60)
        print(f"Total downloaded: {self.stats['downloaded']}")
        print(f"Total skipped (resume): {self.stats['skipped']}")
        print(f"Total failed: {self.stats['failed']}")
        print(f"API calls: {self.stats['api_calls']}")
        print(f"Web scrapes: {self.stats['web_scrapes']}")
        print(f"Duration: {time.time() - start_time:.1f} seconds")
        print(f"\nOutput directory: {OUTPUT_DIR}")
        print(f"Summary file: {summary_path}")

        if self.stats['failed'] > 0:
            print(f"\nNote: {self.stats['failed']} items failed to download.")
            print("Run with --resume flag to retry failed items later.")


def main():
    parser = argparse.ArgumentParser(
        description="Download Zhou Yi texts from ctext.org"
    )
    parser.add_argument(
        "--api-key",
        help="ctext.org API key (optional, enables authenticated API access)"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=2.0,
        help="Delay between requests in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume incomplete download, skipping already downloaded items"
    )

    args = parser.parse_args()

    global RATE_LIMIT_DELAY
    RATE_LIMIT_DELAY = args.rate_limit

    downloader = CtextDownloader(api_key=args.api_key, resume=args.resume)
    downloader.download_all()


if __name__ == "__main__":
    main()
