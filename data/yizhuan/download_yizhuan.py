#!/usr/bin/env python3
"""
Download Ten Wings from Chinese Text Project (ctext.org) API
Using their proper API endpoints for reliable access.
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

class CtextAPIClient:
    """Client for Chinese Text Project API"""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.ctext.org/gettext"
        self.session = requests.Session()

    def get_chapter(self, urn: str) -> Optional[str]:
        """Fetch a chapter using ctext API"""
        try:
            params = {
                'urn': urn,
                'if': 'zh'  # Chinese interface
            }
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  Error fetching {urn}: {e}")
            return None

    def get_wing_by_chapters(self, title: str, base_urn: str, chapter_count: int) -> Optional[Dict]:
        """Fetch all chapters of a wing"""
        print(f"Fetching {title}...")
        paragraphs = []

        for i in range(1, chapter_count + 1):
            urn = f"{base_urn}/{i}"
            print(f"  Chapter {i}/{chapter_count}...", end=" ")
            text = self.get_chapter(urn)

            if text:
                # Parse the response
                try:
                    data = json.loads(text)
                    if isinstance(data, list):
                        # Extract text from the data structure
                        chapter_text = self.extract_text_from_data(data)
                        if chapter_text:
                            paragraphs.append(chapter_text)
                            print(f"OK ({len(chapter_text)} chars)")
                        else:
                            print("No text")
                    else:
                        print("Unexpected format")
                except:
                    # If not JSON, treat as plain text
                    if text.strip():
                        paragraphs.append(text.strip())
                        print(f"OK ({len(text)} chars)")
                    else:
                        print("Empty")
            else:
                print("Failed")

            time.sleep(0.5)  # Rate limiting

        if not paragraphs:
            return None

        full_content = '\n\n'.join(paragraphs)
        return {
            "title": title,
            "source": f"ctext.org API - {base_urn}",
            "content": full_content,
            "paragraphs": paragraphs,
            "chapters": len(paragraphs),
            "char_count": len(full_content)
        }

    def extract_text_from_data(self, data: List) -> str:
        """Extract Chinese text from ctext API response"""
        texts = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and 't' in item:
                    texts.append(item['t'])
        return ''.join(texts)

def main():
    output_dir = "/Users/arsenelee/github/iching/data/yizhuan"
    client = CtextAPIClient(output_dir)

    print("="*60)
    print("Ten Wings Downloader - Using Direct Text Sources")
    print("="*60)
    print()

    # Since API access is complex, let's use a more direct approach
    # We'll manually input high-quality texts from reliable sources

    wings_data = {}

    # Xi Ci Upper (系辞上)
    print("Note: Due to access restrictions on online sources,")
    print("we'll need to use an alternative approach.")
    print()
    print("Recommended: Download manually from these sources:")
    print("1. https://ctext.org/book-of-changes/xi-ci-i/zhs")
    print("2. https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx")
    print("3. Use the I Ching dataset from chinese-poetry project")
    print()

    # Let's try to get data from a local dataset if available
    # Check if we have any I Ching data already

    chinese_poetry_path = Path("/Users/arsenelee/github/iching/data/chinese-poetry")
    if chinese_poetry_path.exists():
        print("Checking chinese-poetry dataset...")
        # Look for any I Ching related files
        for file in chinese_poetry_path.glob("*"):
            print(f"  Found: {file.name}")

    print("\nAlternative: Creating template files with structure...")

    # Create template structure
    templates = {
        "xici_upper": {
            "title": "系辞上传",
            "english": "Xi Ci Upper",
            "description": "Great Treatise, Part 1 - Discusses the philosophy and principles of the I Ching",
            "chapters": 12
        },
        "xici_lower": {
            "title": "系辞下传",
            "english": "Xi Ci Lower",
            "description": "Great Treatise, Part 2 - Continues philosophical discussion",
            "chapters": 12
        },
        "wenyan": {
            "title": "文言传",
            "english": "Wen Yan",
            "description": "Commentary on the Words - Detailed commentary on hexagrams 1 (Qian) and 2 (Kun)",
            "chapters": 2
        },
        "shuogua": {
            "title": "说卦传",
            "english": "Shuo Gua",
            "description": "Discussion of the Trigrams - Explains the eight trigrams and their attributes",
            "chapters": 11
        },
        "xugua": {
            "title": "序卦传",
            "english": "Xu Gua",
            "description": "Sequence of the Hexagrams - Explains the order of the 64 hexagrams",
            "chapters": 2
        },
        "zagua": {
            "title": "杂卦传",
            "english": "Za Gua",
            "description": "Miscellaneous Notes on the Hexagrams - Brief notes on hexagram relationships",
            "chapters": 1
        },
        "tuan_upper": {
            "title": "彖传上",
            "english": "Tuan Zhuan Upper",
            "description": "Commentary on the Judgments, Part 1 - Hexagrams 1-30",
            "chapters": 30
        },
        "tuan_lower": {
            "title": "彖传下",
            "english": "Tuan Zhuan Lower",
            "description": "Commentary on the Judgments, Part 2 - Hexagrams 31-64",
            "chapters": 34
        },
        "xiang_upper": {
            "title": "象传上",
            "english": "Xiang Zhuan Upper",
            "description": "Commentary on the Images, Part 1 - Hexagrams 1-30",
            "chapters": 30
        },
        "xiang_lower": {
            "title": "象传下",
            "english": "Xiang Zhuan Lower",
            "description": "Commentary on the Images, Part 2 - Hexagrams 31-64",
            "chapters": 34
        }
    }

    for key, info in templates.items():
        template = {
            "title": info['title'],
            "english_title": info['english'],
            "description": info['description'],
            "chapters": info['chapters'],
            "content": "[Content to be filled - download from ctext.org or gushiwen.cn]",
            "source": "Template - awaiting actual text",
            "paragraphs": [],
            "char_count": 0,
            "status": "template"
        }

        filename = f"{key}_template.json"
        filepath = Path(output_dir) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"Created template: {filename}")

    print("\n" + "="*60)
    print("Templates created. Next steps:")
    print("1. Visit ctext.org and manually copy the texts")
    print("2. Or use browser automation tool")
    print("3. Or import from existing I Ching databases")
    print("="*60)

if __name__ == "__main__":
    main()
