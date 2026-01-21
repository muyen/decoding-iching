#!/usr/bin/env python3
"""
Scrape all Ten Wings texts from gushiwen.cn
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

# Hexagram URLs - First 30 for upper canon
UPPER_URLS = [f"/guwen/bookv_{id}.aspx" for id in [
    "5f3454cfdbc9", "4dafb366ae4b", "f3e0217a213e", "e18f6303d14d", "9bdab6b9d7e1",
    "8dd1491506ef", "c93215f5528e", "476a23ccebc8", "e5e791e97369", "bac028a07779",
    "fb4f1df4b64b", "0ea2c2b8d709", "8e39036d4982", "07df8e4f9377", "3c34e814ea2e",
    "5464aef56fd0", "d5d2a92596ee", "14a4760263f1", "141d4b00e731", "27284aff311c",
    "7217cfdf4e29", "47a21079ff1f", "c951bb9c0f75", "86c4e9155ed8", "37b6eed182cc",
    "02e4473eeb3d", "ba0790256dfd", "47e22c224e96", "19bde5773772", "2a43661a83dd"
]]

# Hexagrams 31-64 for lower canon
LOWER_URLS = [f"/guwen/bookv_{id}.aspx" for id in [
    "53d12a100fe1", "25717a825930", "98ea7c1242e0", "b9ecf83d95d5", "d2ec150c6d5e",
    "1ca694222e0e", "40db6c7edbf7", "6ecf3912d4ed", "b40919a45c42", "27b9a60c4d7c",
    "784b739ab52d", "0c560288b9f7", "92a00b39f6e3", "9b487a987862", "25d1f974679a",
    "f49ef6ca5f4c", "b970c3af86f7", "a0a32f044e1b", "3808c7a46ab1", "9dce24c077d5",
    "618281df810f", "ac0b361955a2", "c8d7bd2b9158", "69e33a90bd75", "7f6fb8ee6527",
    "366512e6074d", "c2d3f5548776", "156b55aedcf2", "5b858106654f", "0a8ff823fd4a",
    "3f2841826113", "f075bd586a3e", "a1db98007e2f", "a6294a2cceed"
]]

# URLs for Xiang Zhuan (second set, items 65+)
XIANG_UPPER_URLS = [f"/guwen/bookv_{id}.aspx" for id in [
    "8c2d6cf852bb", "ec9c1576e342", "935c7368e950", "9df98b2b71d7", "3886e30eab24",
    "76f1b3cd1336", "aeadc14c8195", "5f5bb1c05577", "b1489292e5e5", "c78e73a84ed5",
    "19ce5dd980d4", "c673bf0f2eb0", "9ab07af0f625", "8cd5a91ad4fd", "c2a78759ae5d",
    "f37d18e8288c", "0c39461359a6", "6903e6f6b706", "0a0a43466bb4", "7928e1ca4c60",
    "d327e6f6be10", "c0c55c99f90a", "23d3fd6afe63", "8280e855e3af", "f683c3cf2368",
    "78b831d9fe1e", "34e3344c052a", "7634b2ee7b44", "70e7ee3e7622", "0f34e24123f0"
]]

XIANG_LOWER_URLS = [f"/guwen/bookv_{id}.aspx" for id in [
    "b9d6eca27621", "eb0e2e19dc97", "e6f54a4c52de", "07fa3e5d0d1a", "cd63fdd26b9e",
    "d2e36f29053b", "df3f2fa29f6b", "4d7f7e13b2ad", "f8d3cc23d9b2", "17394bdf6c93",
    "c6e8e8e46929", "f56c3cd39f2c", "d7c478df8fb7", "e15a948dda7e", "f3d2bfd356ed",
    "00f8c7a1fa4d", "94ca8c1ce9e2", "6eb18cce7abb", "8af9e4d3e19f", "39daaae73cd1",
    "da31e5b79d0f", "a74ccebb952e", "e5e9f5a5829b", "e3e01f21a7a1", "86c4a10e6ff4",
    "d1d73ee32b22", "5a29b7e52e3b", "73a1b18c0f6c", "fddf89faa48a", "97c12c3be5eb",
    "8f0ae33b6e7a", "35e7c3c97c56", "51f0d37584ad", "a0b50f8c52e6"
]]


def clean_text(text: str) -> str:
    """Clean navigation and extra text"""
    # Remove navigation text
    text = re.sub(r'(上一章|下一章|目录|完善|原文\s*⇛\s*段译)', '', text)
    # Remove extra whitespace
    text = re.sub(r'\n\s*\n', '\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text.strip()


def extract_text_from_page(url: str) -> str:
    """Extract text content from a gushiwen page"""
    full_url = f"https://www.gushiwen.cn{url}"

    try:
        response = session.get(full_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find content
        for div in soup.select('.contson, .sons'):
            content = div.get_text(separator='\n', strip=True)
            # Skip audio player elements
            if '播放列表' in content or '循环' in content:
                continue
            content = clean_text(content)
            if content and len(content) > 20:
                return content

        return ""

    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""


def scrape_wing(name: str, title: str, pinyin: str, urls: List[str], output_dir: Path) -> Dict:
    """Scrape a complete wing"""
    print(f"\nScraping {title} ({pinyin})...")
    paragraphs = []

    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] Processing...")
        text = extract_text_from_page(url)
        if text:
            paragraphs.append(text)
        time.sleep(2)  # Rate limiting

    result = {
        "title": title,
        "title_pinyin": pinyin,
        "content": '\n\n'.join(paragraphs),
        "paragraphs": paragraphs
    }

    filename = f"{name}.json"
    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Saved {filename} ({len(result['content'])} chars, {len(paragraphs)} sections)")
    return result


def main():
    output_dir = Path("/Users/arsenelee/github/iching/data/yizhuan")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("Ten Wings Complete Scraper - gushiwen.cn")
    print("="*60)

    results = {}

    # 1. 彖传上 (Tuan Zhuan Upper)
    results['tuan_upper'] = scrape_wing(
        'tuan_upper', '彖传上', 'Tuan Zhuan Shang', UPPER_URLS, output_dir)

    # 2. 彖传下 (Tuan Zhuan Lower)
    results['tuan_lower'] = scrape_wing(
        'tuan_lower', '彖传下', 'Tuan Zhuan Xia', LOWER_URLS, output_dir)

    # 3. 象传上 (Xiang Zhuan Upper)
    results['xiang_upper'] = scrape_wing(
        'xiang_upper', '象传上', 'Xiang Zhuan Shang', XIANG_UPPER_URLS, output_dir)

    # 4. 象传下 (Xiang Zhuan Lower)
    results['xiang_lower'] = scrape_wing(
        'xiang_lower', '象传下', 'Xiang Zhuan Xia', XIANG_LOWER_URLS, output_dir)

    # 5-10. For remaining wings (系辞, 文言, etc), these need different URLs
    # These are typically standalone texts, not per-hexagram
    # For now, mark as TODO or try to find them separately

    print("\n" + "="*60)
    print(f"Phase 1 Complete: {len(results)}/10 wings collected")
    print("Note: 系辞上下, 文言, 说卦, 序卦, 杂卦 require different URLs")
    print("="*60)

    # Save combined file for what we have
    combined = {
        "title": "十翼",
        "title_en": "Ten Wings (Partial)",
        "wings": results,
        "total_wings": len(results),
        "total_characters": sum(len(r['content']) for r in results.values())
    }

    combined_path = output_dir / "yizhuan_complete.json"
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nSaved yizhuan_complete.json")
    print(f"Total characters: {combined['total_characters']:,}")


if __name__ == "__main__":
    main()
