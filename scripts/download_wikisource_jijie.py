#!/usr/bin/env python3
"""Download all 17 volumes of 周易集解 from Wikisource"""
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
                revisions = page.get('revisions', [])
                if revisions:
                    content = revisions[0].get('slots', {}).get('main', {}).get('content', '')
                    return content
    except Exception as e:
        print(f"Error fetching {title}: {e}")

    return None

def clean_wiki_markup(text):
    """Remove wiki markup and clean text"""
    # Remove templates like {{header}}
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
    output_dir = base_dir / 'data/commentaries/zhouyi_jijie'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Volume names in Chinese
    volumes = [
        '卷一', '卷二', '卷三', '卷四', '卷五', '卷六', '卷七', '卷八',
        '卷九', '卷十', '卷十一', '卷十二', '卷十三', '卷十四', '卷十五',
        '卷十六', '卷十七'
    ]

    all_content = []

    print("Downloading 周易集解 from Wikisource...")

    for i, vol in enumerate(volumes, 1):
        title = f"周易集解/{vol}"
        print(f"  [{i}/{len(volumes)}] Downloading {title}...")

        content = get_wikisource_content(title)

        if content:
            cleaned = clean_wiki_markup(content)

            # Save individual volume
            vol_file = output_dir / f"{vol.replace('卷', 'vol')}.txt"
            with open(vol_file, 'w', encoding='utf-8') as f:
                f.write(f"周易集解 {vol}\n")
                f.write("=" * 40 + "\n\n")
                f.write(cleaned)

            all_content.append(f"\n\n{'='*60}\n周易集解 {vol}\n{'='*60}\n\n{cleaned}")
            print(f"    Saved {vol_file.name} ({len(cleaned)} chars)")
        else:
            print(f"    Failed to download {title}")

        time.sleep(1)  # Be nice to the server

    # Save complete collection
    complete_file = output_dir / 'zhouyi_jijie_complete.txt'
    with open(complete_file, 'w', encoding='utf-8') as f:
        f.write("周易集解 (唐 李鼎祚 撰)\n")
        f.write("Zhou Yi Ji Jie - Collection of I Ching Commentaries\n")
        f.write("Source: Wikisource (zh.wikisource.org)\n")
        f.write("=" * 60 + "\n")
        f.write(''.join(all_content))

    total_chars = sum(len(c) for c in all_content)
    print(f"\nComplete collection saved to {complete_file}")
    print(f"Total: {len(volumes)} volumes, {total_chars} characters")

if __name__ == '__main__':
    main()
