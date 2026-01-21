#!/usr/bin/env python3
"""
Final comprehensive scraper for all Ten Wings from gushiwen.cn
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


def clean_text(text: str) -> str:
    """Clean navigation and extra text"""
    text = re.sub(r'(上一章|下一章|目录|完善|原文\s*⇛\s*段译)', '', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)


def extract_text_from_page(url: str) -> str:
    """Extract text content from a page"""
    full_url = f"https://www.gushiwen.cn{url}"

    try:
        response = session.get(full_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find ALL content divs (there may be multiple sections)
        all_text = []
        for div in soup.select('.contson, .sons'):
            content = div.get_text(separator='\n', strip=True)
            # Skip audio player elements
            if '播放列表' in content or '循环' in content or len(content) < 20:
                continue
            content = clean_text(content)
            if content:
                all_text.append(content)

        # Return the longest one (most likely to be the actual content)
        if all_text:
            return max(all_text, key=len)

        return ""

    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""


def save_wing(name: str, title: str, pinyin: str, paragraphs: List[str], output_dir: Path) -> Dict:
    """Save a wing to JSON"""
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
    print("Final Ten Wings Scraper - gushiwen.cn")
    print("="*60)

    results = {}

    # Check which files already exist and have good content
    existing_files = {
        'tuan_upper': output_dir / 'tuan_upper.json',
        'tuan_lower': output_dir / 'tuan_lower.json',
        'xiang_upper': output_dir / 'xiang_upper.json',
        'xiang_lower': output_dir / 'xiang_lower.json',
        'wenyan': output_dir / 'wenyan.json'
    }

    for key, filepath in existing_files.items():
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if len(data.get('content', '')) > 1000:  # Has substantial content
                    results[key] = data
                    print(f"Using existing {key}.json ({len(data['content'])} chars)")

    # 5. 系辞上 (Xi Ci Upper) - Chapters 1-12
    print("\nScraping 系辞上 (Xi Ci Shang) - 12 chapters...")
    xici_upper_ids = [
        "bb689e6439c3", "ee671638f6bb", "e89a903b3cc8", "fdf70db3c61c",
        "75ec81a11dd8", "6cf95dec7d91", "69fe1f3e2c35", "b12ca8e9c65e",
        "34bda38889d2", "a6e5a79e1343", "e7cfef03de05", "a88e0ec5d75b"
    ]
    paragraphs = []
    for i, id in enumerate(xici_upper_ids, 1):
        print(f"  Chapter {i}/12...")
        text = extract_text_from_page(f"/guwen/bookv_{id}.aspx")
        if text:
            paragraphs.append(text)
        time.sleep(2)
    results['xici_upper'] = save_wing('xici_upper', '系辞上', 'Xi Ci Shang', paragraphs, output_dir)

    # 6. 系辞下 (Xi Ci Lower) - Chapters 1-12
    print("\nScraping 系辞下 (Xi Ci Xia) - 12 chapters...")
    xici_lower_ids = [
        "8ca55f0ea23d", "b5f6590e21c0", "bc6b5c8f44bf", "2b57bd06cc39",
        "c3ebf0a2c12f", "1f9ce4e8ad4f", "2d5b36f7c44c", "1cf6bf00af23",
        "5bfe82fcebbb", "15fe91d3c0f5", "1dd8a8f24f9e", "44cb4f3e4b1f"
    ]
    paragraphs = []
    for i, id in enumerate(xici_lower_ids, 1):
        print(f"  Chapter {i}/12...")
        text = extract_text_from_page(f"/guwen/bookv_{id}.aspx")
        if text:
            paragraphs.append(text)
        time.sleep(2)
    results['xici_lower'] = save_wing('xici_lower', '系辞下', 'Xi Ci Xia', paragraphs, output_dir)

    # 8. 说卦传 (Shuo Gua) - Chapters 1-11
    print("\nScraping 说卦传 (Shuo Gua Zhuan) - 11 chapters...")
    shuogua_ids = [
        "2345d6531ef4", "93abbfafe647", "d5a066ff47a7", "9e0a69b2c16f",
        "2f64b9ca5f09", "ea5f58419dd5", "1f5edba8e4f2", "be3c9086ffc8",
        "23a4c8c2cdb5", "82b9e1ad0e67", "c34c7f3ff85a"
    ]
    paragraphs = []
    for i, id in enumerate(shuogua_ids, 1):
        print(f"  Chapter {i}/11...")
        text = extract_text_from_page(f"/guwen/bookv_{id}.aspx")
        if text:
            paragraphs.append(text)
        time.sleep(2)
    results['shuogua'] = save_wing('shuogua', '说卦传', 'Shuo Gua Zhuan', paragraphs, output_dir)

    # 9. 序卦传 (Xu Gua) - Upper and Lower
    print("\nScraping 序卦传 (Xu Gua Zhuan) - 2 parts...")
    xugua_ids = ["5cd550a89e58", "ecc59b6622a5"]
    paragraphs = []
    for i, id in enumerate(xugua_ids, 1):
        print(f"  Part {i}/2...")
        text = extract_text_from_page(f"/guwen/bookv_{id}.aspx")
        if text:
            paragraphs.append(text)
        time.sleep(2)
    results['xugua'] = save_wing('xugua', '序卦传', 'Xu Gua Zhuan', paragraphs, output_dir)

    # 10. 杂卦传 (Za Gua) - Full text
    print("\nScraping 杂卦传 (Za Gua Zhuan)...")
    text = extract_text_from_page("/guwen/bookv_b64fdc9b38d6.aspx")
    if text:
        results['zagua'] = save_wing('zagua', '杂卦传', 'Za Gua Zhuan', [text], output_dir)

    # Save combined file
    print("\n" + "="*60)
    combined = {
        "title": "十翼",
        "title_en": "Ten Wings",
        "source": "gushiwen.cn",
        "wings": results,
        "total_wings": len(results),
        "total_characters": sum(len(r['content']) for r in results.values())
    }

    combined_path = output_dir / "yizhuan_complete.json"
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Complete! Saved yizhuan_complete.json")
    print(f"Total wings: {len(results)}/10")
    print(f"Total characters: {combined['total_characters']:,}")
    print("="*60)

    # Print summary
    print("\nSummary:")
    wing_names = {
        'tuan_upper': '彖传上', 'tuan_lower': '彖传下',
        'xiang_upper': '象传上', 'xiang_lower': '象传下',
        'xici_upper': '系辞上', 'xici_lower': '系辞下',
        'wenyan': '文言传', 'shuogua': '说卦传',
        'xugua': '序卦传', 'zagua': '杂卦传'
    }
    for key, name in wing_names.items():
        if key in results:
            chars = len(results[key]['content'])
            paras = len(results[key]['paragraphs'])
            print(f"  ✓ {name:8s} ({chars:,} chars, {paras} sections)")
        else:
            print(f"  ✗ {name}")


if __name__ == "__main__":
    main()
