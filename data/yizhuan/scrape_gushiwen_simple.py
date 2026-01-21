#!/usr/bin/env python3
"""
Scrape the Ten Wings (十翼) texts from gushiwen.cn
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ten Wings mapping
TEN_WINGS = {
    "tuan_upper": {
        "title": "彖传上",
        "title_pinyin": "Tuan Zhuan Shang",
    },
    "tuan_lower": {
        "title": "彖传下",
        "title_pinyin": "Tuan Zhuan Xia",
    },
    "xiang_upper": {
        "title": "象传上",
        "title_pinyin": "Xiang Zhuan Shang",
    },
    "xiang_lower": {
        "title": "象传下",
        "title_pinyin": "Xiang Zhuan Xia",
    },
    "xici_upper": {
        "title": "系辞上",
        "title_pinyin": "Xi Ci Shang",
    },
    "xici_lower": {
        "title": "系辞下",
        "title_pinyin": "Xi Ci Xia",
    },
    "wenyan": {
        "title": "文言传",
        "title_pinyin": "Wen Yan Zhuan",
    },
    "shuogua": {
        "title": "说卦传",
        "title_pinyin": "Shuo Gua Zhuan",
    },
    "xugua": {
        "title": "序卦传",
        "title_pinyin": "Xu Gua Zhuan",
    },
    "zagua": {
        "title": "杂卦传",
        "title_pinyin": "Za Gua Zhuan",
    }
}


def scrape_gushiwen(output_dir: str):
    """Scrape Ten Wings from gushiwen.cn"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
    })

    base_url = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"
    results = {}

    print(f"Fetching main page: {base_url}")
    try:
        response = session.get(base_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all chapter links
        chapter_links = []
        for a in soup.select('.bookcont a, .sons a, a[href*="bookv"]'):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if href and text:
                if not href.startswith('http'):
                    href = 'https://www.gushiwen.cn' + href
                chapter_links.append({'url': href, 'title': text})

        print(f"Found {len(chapter_links)} potential chapter links")

        # Process each Ten Wings text
        for key, info in TEN_WINGS.items():
            title = info['title']

            # Find matching link
            matching_link = None
            for link in chapter_links:
                if title in link['title']:
                    matching_link = link
                    break

            if not matching_link:
                print(f"\nCould not find link for {title}, trying direct search...")
                # Try searching directly
                continue

            print(f"\nScraping {title} from {matching_link['url']}")

            try:
                time.sleep(2)  # Rate limiting
                response = session.get(matching_link['url'], timeout=10)
                response.encoding = 'utf-8'
                page_soup = BeautifulSoup(response.text, 'html.parser')

                # Extract content - try multiple selectors
                paragraphs = []

                # Method 1: Look for content div/contson
                content_divs = page_soup.select('.contson, .sons, #contson')
                for div in content_divs:
                    # Get all text, split by double newlines
                    text = div.get_text(separator='\n', strip=True)
                    if text and len(text) > 20:
                        # Split into paragraphs by blank lines
                        paras = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 10]
                        paragraphs.extend(paras)

                # Method 2: If no content, look for paragraphs
                if not paragraphs:
                    for p in page_soup.select('.contson p, .sons p'):
                        text = p.get_text(strip=True)
                        if text and len(text) > 10:
                            paragraphs.append(text)

                # Method 3: Look for divs with class containing 'cont'
                if not paragraphs:
                    for div in page_soup.select('div[class*="cont"]'):
                        text = div.get_text(strip=True)
                        if text and len(text) > 20:
                            paragraphs.append(text)

                if not paragraphs:
                    print(f"  Warning: No content found for {title}")
                    continue

                # Clean up paragraphs - remove duplicates and navigation text
                cleaned_paragraphs = []
                seen = set()
                for para in paragraphs:
                    # Skip navigation/header text
                    if any(skip in para for skip in ['首页', '推荐', '搜索', '登录', '注册', '诗文', '名句', '作者', '古籍']):
                        continue
                    if para not in seen and len(para) > 10:
                        cleaned_paragraphs.append(para)
                        seen.add(para)

                paragraphs = cleaned_paragraphs
                full_content = '\n\n'.join(paragraphs)

                result = {
                    "title": title,
                    "title_pinyin": info['title_pinyin'],
                    "content": full_content,
                    "paragraphs": paragraphs
                }

                # Save individual file
                filename = f"{key}.json"
                filepath = output_path / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                results[key] = result
                print(f"  Saved {filename} ({len(full_content)} chars, {len(paragraphs)} paragraphs)")

            except Exception as e:
                print(f"  Error scraping {title}: {e}")

    except Exception as e:
        print(f"Error fetching main page: {e}")
        return results

    # Save combined file
    if results:
        combined = {
            "title": "十翼",
            "title_en": "Ten Wings",
            "wings": results,
            "total_wings": len(results),
            "total_characters": sum(len(r['content']) for r in results.values())
        }

        combined_path = output_path / "yizhuan_complete.json"
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"Scraping complete!")
        print(f"Total wings collected: {len(results)}/10")
        print(f"Total characters: {combined['total_characters']:,}")
        print(f"{'='*60}")

    return results


if __name__ == "__main__":
    output_dir = "/Users/arsenelee/github/iching/data/yizhuan"
    scrape_gushiwen(output_dir)
