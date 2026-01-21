#!/usr/bin/env python3
"""
Scraper with CORRECTED chapter IDs
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

        # Find ALL content divs
        all_text = []
        for div in soup.select('.contson, .sons'):
            content = div.get_text(separator='\n', strip=True)
            if '播放列表' in content or '循环' in content or len(content) < 20:
                continue
            content = clean_text(content)
            if content:
                all_text.append(content)

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
    print("Corrected Ten Wings Scraper")
    print("="*60)

    results = {}

    # Load existing good files
    existing = ['tuan_upper', 'tuan_lower', 'xiang_upper', 'xiang_lower', 'wenyan']
    for key in existing:
        filepath = output_dir / f"{key}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if len(data.get('content', '')) > 1000:
                    results[key] = data
                    print(f"Using existing {key}.json ({len(data['content'])} chars)")

    # 5. 系辞上 (Xi Ci Upper) - Chapters 1-12 with CORRECT IDs
    print("\nScraping 系辞上 (Xi Ci Shang) - 12 chapters...")
    xici_upper_ids = [
        "bb689e6439c3", "ee671638f6bb", "b3877e3d11ea", "2609fad629d1",
        "39373e2c179d", "ecf30ca2254e", "31b4d3191af6", "f0d597fa5039",
        "1ca83cdce872", "8d70fae1ca1d", "b685c6df3b74", "c407096a9760"
    ]
    paragraphs = []
    for i, id in enumerate(xici_upper_ids, 1):
        print(f"  Chapter {i}/12...")
        text = extract_text_from_page(f"/guwen/bookv_{id}.aspx")
        if text:
            paragraphs.append(text)
        time.sleep(2)
    results['xici_upper'] = save_wing('xici_upper', '系辞上', 'Xi Ci Shang', paragraphs, output_dir)

    # 6. 系辞下 (Xi Ci Lower) - Chapters 1-12 with CORRECT IDs
    print("\nScraping 系辞下 (Xi Ci Xia) - 12 chapters...")
    xici_lower_ids = [
        "8ca55f0ea23d", "b5f6590e21c0", "334184de9714", "3f62482e18de",
        "e805a4a67035", "499415055f7a", "a6d210a6844c", "ffaa165c0ea1",
        "d02a57f2d772", "978c2063e4a5", "acf5cb0c6a2b", "9f7bbd36ca78"
    ]
    paragraphs = []
    for i, id in enumerate(xici_lower_ids, 1):
        print(f"  Chapter {i}/12...")
        text = extract_text_from_page(f"/guwen/bookv_{id}.aspx")
        if text:
            paragraphs.append(text)
        time.sleep(2)
    results['xici_lower'] = save_wing('xici_lower', '系辞下', 'Xi Ci Xia', paragraphs, output_dir)

    # 8. 说卦传 (Shuo Gua) - Chapters 1-11 with CORRECT IDs
    print("\nScraping 说卦传 (Shuo Gua Zhuan) - 11 chapters...")
    shuogua_ids = [
        "2345d6531ef4", "93abbfafe647", "453af28b69c5", "2dd46cd40579",
        "720da4487131", "613addc0345e", "a6f92252c875", "3929b92c79de",
        "31a53a0dfb70", "1209fa67db6d", "2066d5e2cf33"
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
