#!/usr/bin/env python3
"""Download 周易本義 (Zhu Xi's I Ching Commentary) from Wikisource"""
import json
import time
import urllib.request
import urllib.parse
import re
from pathlib import Path

def get_wikisource_content(title):
    """Fetch content from Wikisource using API"""
    base_url = "https://zh.wikisource.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "formatversion": "2"
    }

    url = base_url + "?" + urllib.parse.urlencode(params)

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; IChing-TextAnalysis/1.0)'
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))

            pages = data.get('query', {}).get('pages', [])
            if pages:
                page = pages[0]
                if page.get('missing'):
                    return None
                revisions = page.get('revisions', [])
                if revisions:
                    content = revisions[0].get('slots', {}).get('main', {}).get('content', '')
                    return content
    except Exception as e:
        print(f"Error fetching {title}: {e}")

    return None

def clean_wiki_markup(text):
    """Remove wiki markup and clean text"""
    # Remove templates
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    # Remove [[ ]] links but keep text
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove category links
    text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    output_dir = base_dir / 'data/commentaries/zhouyi_benyi'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 周易本義 individual volumes
    # 原本周易本義 has 12 volumes
    pages = [
        "原本周易本義_(四庫全書本)/卷一",
        "原本周易本義_(四庫全書本)/卷二",
        "原本周易本義_(四庫全書本)/卷三",
        "原本周易本義_(四庫全書本)/卷四",
        "原本周易本義_(四庫全書本)/卷五",
        "原本周易本義_(四庫全書本)/卷六",
        "原本周易本義_(四庫全書本)/卷七",
        "原本周易本義_(四庫全書本)/卷八",
        "原本周易本義_(四庫全書本)/卷九",
        "原本周易本義_(四庫全書本)/卷十",
        "原本周易本義_(四庫全書本)/卷十一",
        "原本周易本義_(四庫全書本)/卷十二",
        "原本周易本義_(四庫全書本)/卷末上",
        "原本周易本義_(四庫全書本)/卷末下",
    ]

    print("Downloading 原本周易本義 from Wikisource...")

    all_content = []
    total_chars = 0

    for title in pages:
        vol_name = title.split('/')[-1]
        print(f"  [{pages.index(title)+1}/{len(pages)}] Downloading {vol_name}...")

        content = get_wikisource_content(title)

        if content and len(content) > 100:
            cleaned = clean_wiki_markup(content)
            if len(cleaned) > 50:
                all_content.append(f"\n\n{'='*60}\n{vol_name}\n{'='*60}\n\n{cleaned}")
                total_chars += len(cleaned)
                print(f"      Got {len(cleaned)} chars")
            else:
                print(f"      Content too short after cleaning")
        else:
            print(f"      Not available or empty")

        time.sleep(0.5)

    if total_chars > 1000:
        # Save complete collection
        complete_file = output_dir / 'zhouyi_benyi_complete.txt'

        with open(complete_file, 'w', encoding='utf-8') as f:
            f.write("原本周易本義 (宋 朱熹 撰)\n")
            f.write("Yuan Ben Zhou Yi Ben Yi - Zhu Xi's Original Meaning of the Book of Changes\n")
            f.write("Source: Wikisource (zh.wikisource.org) - 四庫全書本\n")
            f.write("=" * 60 + "\n")
            f.write(''.join(all_content))

        print(f"\nSaved to {complete_file}")
        print(f"Total: {len(all_content)} volumes, {total_chars} characters")
    else:
        print(f"\nInsufficient content downloaded ({total_chars} chars)")
        print("The text may not be fully transcribed on Wikisource.")

if __name__ == '__main__':
    main()
