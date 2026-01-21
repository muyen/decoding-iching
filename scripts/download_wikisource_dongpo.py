#!/usr/bin/env python3
"""Download 東坡易傳 (Su Shi's I Ching Commentary) from Wikisource"""
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
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    output_dir = base_dir / 'data/commentaries/dongpo_yizhuan'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Available pages (1-35 and 繫辭傳)
    pages = []
    for i in range(1, 36):
        pages.append(f"{i:02d}")

    # Add 繫辭傳
    pages.append("繫辭傳上")
    pages.append("繫辭傳下")

    all_content = []

    print("Downloading 東坡易傳 from Wikisource...")

    for page in pages:
        title = f"東坡易傳/{page}"
        print(f"  Downloading {title}...")

        content = get_wikisource_content(title)

        if content:
            cleaned = clean_wiki_markup(content)
            all_content.append(f"\n\n{'='*60}\n東坡易傳 {page}\n{'='*60}\n\n{cleaned}")
            print(f"    Got {len(cleaned)} chars")
        else:
            print(f"    Not available")

        time.sleep(0.5)

    # Save complete collection
    complete_file = output_dir / 'dongpo_yizhuan.txt'
    with open(complete_file, 'w', encoding='utf-8') as f:
        f.write("東坡易傳 (北宋 蘇軾 撰)\n")
        f.write("Dongpo Yi Zhuan - Su Shi's Commentary on the I Ching\n")
        f.write("Source: Wikisource (zh.wikisource.org)\n")
        f.write("Note: Hexagrams 36-64 not yet transcribed on Wikisource\n")
        f.write("=" * 60 + "\n")
        f.write(''.join(all_content))

    total_chars = sum(len(c) for c in all_content)
    print(f"\nSaved to {complete_file}")
    print(f"Total: {len([c for c in all_content if c])} sections, {total_chars} characters")

if __name__ == '__main__':
    main()
