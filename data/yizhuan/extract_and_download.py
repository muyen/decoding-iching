#!/usr/bin/env python3
"""
Extract Ten Wings from existing data and download missing ones.
This combines extraction from zhouyi_64gua.json and web scraping.
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
from typing import Dict, List, Optional

class TenWingsCollector:
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

    def extract_tuan_xiang(self):
        """Extract Tuan and Xiang from zhouyi_64gua.json"""
        print("="*60)
        print("Extracting Tuan and Xiang from existing data...")
        print("="*60)

        zhouyi_file = self.data_dir / "zhouyi-64gua" / "zhouyi_64gua.json"
        if not zhouyi_file.exists():
            print(f"Error: {zhouyi_file} not found")
            return

        with open(zhouyi_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        hexagrams = data.get('hexagrams', [])

        # Separate into upper and lower (1-30 and 31-64)
        tuan_upper_paragraphs = []
        tuan_lower_paragraphs = []
        xiang_upper_paragraphs = []
        xiang_lower_paragraphs = []

        for hex_data in hexagrams:
            hex_num = hex_data['number']
            hex_name = hex_data['name']

            # Tuan commentary
            tuan_text = hex_data.get('tuan', '')
            if tuan_text:
                entry = f"{hex_num}. {hex_name}\n{tuan_text}"
                if hex_num <= 30:
                    tuan_upper_paragraphs.append(entry)
                else:
                    tuan_lower_paragraphs.append(entry)

            # Xiang commentary (multiple entries per hexagram)
            xiang_texts = hex_data.get('xiang', [])
            if xiang_texts:
                xiang_combined = '\n'.join(xiang_texts)
                entry = f"{hex_num}. {hex_name}\n{xiang_combined}"
                if hex_num <= 30:
                    xiang_upper_paragraphs.append(entry)
                else:
                    xiang_lower_paragraphs.append(entry)

        # Save Tuan Upper
        tuan_upper = {
            "title": "彖传上",
            "english_title": "Tuan Zhuan Upper",
            "description": "Commentary on the Judgments, Part 1 (Hexagrams 1-30)",
            "content": '\n\n'.join(tuan_upper_paragraphs),
            "paragraphs": tuan_upper_paragraphs,
            "source": "Extracted from zhouyi_64gua.json",
            "hexagram_count": len(tuan_upper_paragraphs),
            "char_count": sum(len(p) for p in tuan_upper_paragraphs)
        }
        self.save_json("tuan_upper.json", tuan_upper)
        print(f"✓ Tuan Upper: {tuan_upper['hexagram_count']} hexagrams, {tuan_upper['char_count']:,} chars")

        # Save Tuan Lower
        tuan_lower = {
            "title": "彖传下",
            "english_title": "Tuan Zhuan Lower",
            "description": "Commentary on the Judgments, Part 2 (Hexagrams 31-64)",
            "content": '\n\n'.join(tuan_lower_paragraphs),
            "paragraphs": tuan_lower_paragraphs,
            "source": "Extracted from zhouyi_64gua.json",
            "hexagram_count": len(tuan_lower_paragraphs),
            "char_count": sum(len(p) for p in tuan_lower_paragraphs)
        }
        self.save_json("tuan_lower.json", tuan_lower)
        print(f"✓ Tuan Lower: {tuan_lower['hexagram_count']} hexagrams, {tuan_lower['char_count']:,} chars")

        # Save Xiang Upper
        xiang_upper = {
            "title": "象传上",
            "english_title": "Xiang Zhuan Upper",
            "description": "Commentary on the Images, Part 1 (Hexagrams 1-30)",
            "content": '\n\n'.join(xiang_upper_paragraphs),
            "paragraphs": xiang_upper_paragraphs,
            "source": "Extracted from zhouyi_64gua.json",
            "hexagram_count": len(xiang_upper_paragraphs),
            "char_count": sum(len(p) for p in xiang_upper_paragraphs)
        }
        self.save_json("xiang_upper.json", xiang_upper)
        print(f"✓ Xiang Upper: {xiang_upper['hexagram_count']} hexagrams, {xiang_upper['char_count']:,} chars")

        # Save Xiang Lower
        xiang_lower = {
            "title": "象传下",
            "english_title": "Xiang Zhuan Lower",
            "description": "Commentary on the Images, Part 2 (Hexagrams 31-64)",
            "content": '\n\n'.join(xiang_lower_paragraphs),
            "paragraphs": xiang_lower_paragraphs,
            "source": "Extracted from zhouyi_64gua.json",
            "hexagram_count": len(xiang_lower_paragraphs),
            "char_count": sum(len(p) for p in xiang_lower_paragraphs)
        }
        self.save_json("xiang_lower.json", xiang_lower)
        print(f"✓ Xiang Lower: {xiang_lower['hexagram_count']} hexagrams, {xiang_lower['char_count']:,} chars")

        return {
            "tuan_upper": tuan_upper,
            "tuan_lower": tuan_lower,
            "xiang_upper": xiang_upper,
            "xiang_lower": xiang_lower
        }

    def download_from_wengu(self, url: str, title: str) -> Optional[Dict]:
        """Download text from wengu.net (reliable classical Chinese text source)"""
        print(f"Downloading {title} from {url}...")

        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find content - wengu.net typically uses p tags for content
            paragraphs = []
            content_area = soup.find('div', {'class': 'cont'}) or soup.find('div', {'id': 'cont'})

            if content_area:
                for p in content_area.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        paragraphs.append(text)

            if not paragraphs:
                # Try alternative structure
                for p in soup.find_all('p'):
                    text = p.get_text(strip=True)
                    # Only include substantial Chinese text
                    if text and len(text) > 20 and text.count('章') + text.count('曰') > 0:
                        paragraphs.append(text)

            if paragraphs:
                full_content = '\n\n'.join(paragraphs)
                result = {
                    "title": title,
                    "source": url,
                    "content": full_content,
                    "paragraphs": paragraphs,
                    "char_count": len(full_content)
                }
                print(f"  ✓ Success: {len(paragraphs)} paragraphs, {len(full_content):,} chars")
                return result
            else:
                print(f"  ✗ No content found")
                return None

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None

    def create_from_text(self, title: str, english: str, description: str, text: str) -> Dict:
        """Create a wing entry from provided text"""
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        return {
            "title": title,
            "english_title": english,
            "description": description,
            "content": text,
            "paragraphs": paragraphs,
            "source": "Manual input",
            "char_count": len(text)
        }

    def save_json(self, filename: str, data: Dict):
        """Save data to JSON file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def download_remaining_wings(self) -> Dict:
        """Download or create the remaining 6 wings"""
        print("\n" + "="*60)
        print("Downloading remaining wings...")
        print("="*60)

        results = {}

        # These texts need to be downloaded from reliable sources
        # Using simplified texts from various classical Chinese databases

        # For now, create placeholders with source information
        wings_info = {
            "xici_upper": {
                "title": "系辞上传",
                "english": "Xi Ci Upper (Great Treatise, Part 1)",
                "description": "Discusses the philosophy and principles of the I Ching",
                "url": "https://ctext.org/book-of-changes/xi-ci-i/zhs"
            },
            "xici_lower": {
                "title": "系辞下传",
                "english": "Xi Ci Lower (Great Treatise, Part 2)",
                "description": "Continues philosophical discussion of the I Ching",
                "url": "https://ctext.org/book-of-changes/xi-ci-ii/zhs"
            },
            "wenyan": {
                "title": "文言传",
                "english": "Wen Yan (Commentary on the Words)",
                "description": "Detailed commentary on hexagrams 1 (Qian) and 2 (Kun)",
                "url": "https://ctext.org/book-of-changes/wen-yan/zhs"
            },
            "shuogua": {
                "title": "说卦传",
                "english": "Shuo Gua (Discussion of the Trigrams)",
                "description": "Explains the eight trigrams and their attributes",
                "url": "https://ctext.org/book-of-changes/shuo-gua/zhs"
            },
            "xugua": {
                "title": "序卦传",
                "english": "Xu Gua (Sequence of the Hexagrams)",
                "description": "Explains the order of the 64 hexagrams",
                "url": "https://ctext.org/book-of-changes/xu-gua/zhs"
            },
            "zagua": {
                "title": "杂卦传",
                "english": "Za Gua (Miscellaneous Notes)",
                "description": "Brief notes on hexagram relationships",
                "url": "https://ctext.org/book-of-changes/za-gua/zhs"
            }
        }

        for key, info in wings_info.items():
            # Create placeholder that indicates where to get the full text
            placeholder = {
                "title": info['title'],
                "english_title": info['english'],
                "description": info['description'],
                "content": f"[To be downloaded from {info['url']}]",
                "paragraphs": [],
                "source": info['url'],
                "char_count": 0,
                "status": "placeholder - needs browser automation or manual download"
            }

            results[key] = placeholder
            self.save_json(f"{key}.json", placeholder)
            print(f"✗ {info['title']}: Placeholder created - {info['url']}")
            time.sleep(0.5)

        return results

    def create_combined_file(self, extracted: Dict, downloaded: Dict):
        """Create combined yizhuan_complete.json file"""
        print("\n" + "="*60)
        print("Creating combined file...")
        print("="*60)

        all_wings = {**extracted, **downloaded}

        combined = {
            "title": "十翼 (Ten Wings) - Complete Collection",
            "description": "The Ten Wings are commentaries on the I Ching (Book of Changes)",
            "wings": all_wings,
            "total_wings": len(all_wings),
            "completed_wings": sum(1 for w in all_wings.values() if w.get('char_count', 0) > 0),
            "total_characters": sum(w.get('char_count', 0) for w in all_wings.values()),
            "note": "Tuan and Xiang extracted from zhouyi_64gua.json. Other wings need manual download or browser automation."
        }

        self.save_json("yizhuan_complete.json", combined)

        print(f"✓ Combined file created")
        print(f"  Total wings: {combined['total_wings']}/10")
        print(f"  Completed: {combined['completed_wings']}/10")
        print(f"  Total characters: {combined['total_characters']:,}")

        return combined

    def run(self):
        """Run the complete extraction and download process"""
        print("\nTen Wings (十翼) Extraction and Download Tool")
        print("="*60)

        # Extract Tuan and Xiang from existing data
        extracted = self.extract_tuan_xiang()

        # Download remaining wings
        downloaded = self.download_remaining_wings()

        # Create combined file
        combined = self.create_combined_file(extracted, downloaded)

        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        for key in ["tuan_upper", "tuan_lower", "xiang_upper", "xiang_lower",
                    "xici_upper", "xici_lower", "wenyan", "shuogua", "xugua", "zagua"]:
            wing = combined['wings'].get(key, {})
            title = wing.get('title', 'Unknown')
            char_count = wing.get('char_count', 0)
            status = "✓" if char_count > 0 else "✗"
            print(f"{status} {title}: {char_count:,} characters")

        print("\n" + "="*60)
        print("Next Steps:")
        print("1. Use browser automation to download remaining 6 wings")
        print("2. Or manually copy texts from ctext.org")
        print("3. Files saved to:", self.output_dir)
        print("="*60)

def main():
    data_dir = "/Users/arsenelee/github/iching/data"
    output_dir = "/Users/arsenelee/github/iching/data/yizhuan"

    collector = TenWingsCollector(data_dir, output_dir)
    collector.run()

if __name__ == "__main__":
    main()
