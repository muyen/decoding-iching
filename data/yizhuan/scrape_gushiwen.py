#!/usr/bin/env python3
"""
Scrape the Ten Wings (十翼) texts from gushiwen.cn using Playwright.
"""

import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Dict, List, Optional

# Ten Wings mapping for gushiwen.cn
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


async def scrape_gushiwen(output_dir: str):
    """Scrape Ten Wings from gushiwen.cn"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    base_url = "https://www.gushiwen.cn/guwen/book_adb08001c74f.aspx"
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"Navigating to {base_url}")
        await page.goto(base_url, wait_until='networkidle')
        await asyncio.sleep(2)

        # Get all chapter links
        chapter_links = await page.evaluate('''() => {
            const links = [];
            const items = document.querySelectorAll('.bookcont .sons a, .bookcont a[href*="guwen/bookv"]');
            items.forEach(a => {
                const href = a.getAttribute('href');
                const text = a.textContent.trim();
                if (href && text) {
                    links.push({
                        url: href.startsWith('http') ? href : 'https://www.gushiwen.cn' + href,
                        title: text
                    });
                }
            });
            return links;
        }''')

        print(f"Found {len(chapter_links)} chapter links")

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
                print(f"Could not find link for {title}")
                continue

            print(f"\nScraping {title} from {matching_link['url']}")

            try:
                await page.goto(matching_link['url'], wait_until='networkidle')
                await asyncio.sleep(2)

                # Extract content
                content_data = await page.evaluate('''() => {
                    const paragraphs = [];

                    // Try multiple selectors for content
                    const contentSelectors = [
                        '.contson',
                        '.sons',
                        '#contson',
                        '.contson p',
                        '.contson div',
                        '.bookMl .sons'
                    ];

                    for (const selector of contentSelectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            elements.forEach(el => {
                                const text = el.textContent.trim();
                                if (text && text.length > 10) {
                                    paragraphs.push(text);
                                }
                            });
                            if (paragraphs.length > 0) break;
                        }
                    }

                    // If still no paragraphs, try getting all text from main content
                    if (paragraphs.length === 0) {
                        const mainContent = document.querySelector('.main-content, .content, main');
                        if (mainContent) {
                            const text = mainContent.textContent.trim();
                            if (text) {
                                paragraphs.push(text);
                            }
                        }
                    }

                    return paragraphs;
                }''')

                if not content_data or len(content_data) == 0:
                    print(f"  Warning: No content found for {title}")
                    continue

                full_content = '\n\n'.join(content_data)

                result = {
                    "title": title,
                    "title_pinyin": info['title_pinyin'],
                    "content": full_content,
                    "paragraphs": content_data
                }

                # Save individual file
                filename = f"{key}.json"
                filepath = output_path / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                results[key] = result
                print(f"  Saved {filename} ({len(full_content)} chars, {len(content_data)} paragraphs)")

                # Rate limiting
                await asyncio.sleep(2)

            except Exception as e:
                print(f"  Error scraping {title}: {e}")

        await browser.close()

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
    asyncio.run(scrape_gushiwen(output_dir))
