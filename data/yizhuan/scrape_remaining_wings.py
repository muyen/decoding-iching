#!/usr/bin/env python3
"""
Scrape the remaining Ten Wings: 系辞, 文言, 说卦, 序卦, 杂卦
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
    text = re.sub(r'\n\s*\n', '\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text.strip()


def extract_text_from_page(url: str) -> str:
    """Extract text content from a page"""
    full_url = f"https://www.gushiwen.cn{url}"

    try:
        response = session.get(full_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        for div in soup.select('.contson, .sons'):
            content = div.get_text(separator='\n', strip=True)
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
        time.sleep(2)

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
    print("Remaining Ten Wings Scraper")
    print("="*60)

    results = {}

    # 5. 系辞传上 (Xi Ci Upper) - Chapters 1-12
    xici_upper_urls = [f"/guwen/bookv_{id}.aspx" for id in [
        "bb689e6439c3", "ee671638f6bb", "e89a903b3cc8", "fdf70db3c61c",
        "75ec81a11dd8", "6cf95dec7d91", "69fe1f3e2c35", "b12ca8e9c65e",
        "34bda38889d2", "a6e5a79e1343", "e7cfef03de05", "a88e0ec5d75b"
    ]]
    results['xici_upper'] = scrape_wing(
        'xici_upper', '系辞上', 'Xi Ci Shang', xici_upper_urls, output_dir)

    # 6. 系辞传下 (Xi Ci Lower) - Chapters 1-12
    xici_lower_urls = [f"/guwen/bookv_{id}.aspx" for id in [
        "8ca55f0ea23d", "b5f6590e21c0", "bc6b5c8f44bf", "2b57bd06cc39",
        "c3ebf0a2c12f", "1f9ce4e8ad4f", "2d5b36f7c44c", "1cf6bf00af23",
        "5bfe82fcebbb", "15fe91d3c0f5", "1dd8a8f24f9e", "44cb4f3e4b1f"
    ]]
    results['xici_lower'] = scrape_wing(
        'xici_lower', '系辞下', 'Xi Ci Xia', xici_lower_urls, output_dir)

    # 7. 文言传 (Wen Yan) - 2 sections
    wenyan_urls = [
        "/guwen/bookv_0919dbb2c038.aspx",  # Qian
        "/guwen/bookv_e7df59ae6733.aspx"   # Kun
    ]
    results['wenyan'] = scrape_wing(
        'wenyan', '文言传', 'Wen Yan Zhuan', wenyan_urls, output_dir)

    # 8. 说卦传 (Shuo Gua) - Chapters 1-11
    shuogua_urls = [f"/guwen/bookv_{id}.aspx" for id in [
        "2345d6531ef4", "93abbfafe647", "d5a066ff47a7", "9e0a69b2c16f",
        "2f64b9ca5f09", "ea5f58419dd5", "1f5edba8e4f2", "be3c9086ffc8",
        "23a4c8c2cdb5", "82b9e1ad0e67", "c34c7f3ff85a"
    ]]
    results['shuogua'] = scrape_wing(
        'shuogua', '说卦传', 'Shuo Gua Zhuan', shuogua_urls, output_dir)

    # 9. 序卦传 (Xu Gua) - Upper and Lower
    xugua_urls = [
        "/guwen/bookv_5cd550a89e58.aspx",  # Upper
        "/guwen/bookv_ecc59b6622a5.aspx"   # Lower
    ]
    results['xugua'] = scrape_wing(
        'xugua', '序卦传', 'Xu Gua Zhuan', xugua_urls, output_dir)

    # 10. 杂卦传 (Za Gua) - Full text
    zagua_urls = ["/guwen/bookv_b64fdc9b38d6.aspx"]
    results['zagua'] = scrape_wing(
        'zagua', '杂卦传', 'Za Gua Zhuan', zagua_urls, output_dir)

    print("\n" + "="*60)
    print(f"Complete! Collected {len(results)} remaining wings")
    print("="*60)

    return results


if __name__ == "__main__":
    main()
