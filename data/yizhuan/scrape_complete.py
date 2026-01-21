#!/usr/bin/env python3
"""
Scrape the complete Ten Wings texts from gushiwen.cn
The commentaries are embedded within hexagram pages.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
})

# Hexagram URLs from the main page
HEXAGRAM_URLS = [
    # Upper Canon (上经) - Hexagrams 1-30
    "/guwen/bookv_5f3454cfdbc9.aspx",  # 1. Qian
    "/guwen/bookv_4dafb366ae4b.aspx",  # 2. Kun
    "/guwen/bookv_f3e0217a213e.aspx",  # 3. Zhun
    "/guwen/bookv_e18f6303d14d.aspx",  # 4. Meng
    "/guwen/bookv_9bdab6b9d7e1.aspx",  # 5. Xu
    "/guwen/bookv_8dd1491506ef.aspx",  # 6. Song
    "/guwen/bookv_c93215f5528e.aspx",  # 7. Shi
    "/guwen/bookv_476a23ccebc8.aspx",  # 8. Bi
    "/guwen/bookv_e5e791e97369.aspx",  # 9. Xiao Xu
    "/guwen/bookv_bac028a07779.aspx",  # 10. Lv
    "/guwen/bookv_fb4f1df4b64b.aspx",  # 11. Tai
    "/guwen/bookv_0ea2c2b8d709.aspx",  # 12. Pi
    "/guwen/bookv_8e39036d4982.aspx",  # 13. Tong Ren
    "/guwen/bookv_07df8e4f9377.aspx",  # 14. Da You
    "/guwen/bookv_3c34e814ea2e.aspx",  # 15. Qian
    "/guwen/bookv_5464aef56fd0.aspx",  # 16. Yu
    "/guwen/bookv_d5d2a92596ee.aspx",  # 17. Sui
    "/guwen/bookv_14a4760263f1.aspx",  # 18. Gu
    "/guwen/bookv_141d4b00e731.aspx",  # 19. Lin
    "/guwen/bookv_27284aff311c.aspx",  # 20. Guan
    "/guwen/bookv_7217cfdf4e29.aspx",  # 21. Shi He
    "/guwen/bookv_47a21079ff1f.aspx",  # 22. Bi
    "/guwen/bookv_c951bb9c0f75.aspx",  # 23. Bo
    "/guwen/bookv_86c4e9155ed8.aspx",  # 24. Fu
    "/guwen/bookv_37b6eed182cc.aspx",  # 25. Wu Wang
    "/guwen/bookv_02e4473eeb3d.aspx",  # 26. Da Xu
    "/guwen/bookv_ba0790256dfd.aspx",  # 27. Yi
    "/guwen/bookv_47e22c224e96.aspx",  # 28. Da Guo
    "/guwen/bookv_19bde5773772.aspx",  # 29. Kan
    "/guwen/bookv_2a43661a83dd.aspx",  # 30. Li
]

# Lower Canon (下经) hexagrams 31-64 for 象传下
HEXAGRAM_URLS_LOWER = [
    "/guwen/bookv_53d12a100fe1.aspx",  # 31. Xian
    "/guwen/bookv_25717a825930.aspx",  # 32. Heng
    "/guwen/bookv_98ea7c1242e0.aspx",  # 33. Dun
    "/guwen/bookv_b9ecf83d95d5.aspx",  # 34. Da Zhuang
    "/guwen/bookv_d2ec150c6d5e.aspx",  # 35. Jin
    "/guwen/bookv_1ca694222e0e.aspx",  # 36. Ming Yi
    "/guwen/bookv_40db6c7edbf7.aspx",  # 37. Jia Ren
    "/guwen/bookv_6ecf3912d4ed.aspx",  # 38. Kui
    "/guwen/bookv_b40919a45c42.aspx",  # 39. Jian
    "/guwen/bookv_27b9a60c4d7c.aspx",  # 40. Jie
    "/guwen/bookv_784b739ab52d.aspx",  # 41. Sun
    "/guwen/bookv_0c560288b9f7.aspx",  # 42. Yi
    "/guwen/bookv_92a00b39f6e3.aspx",  # 43. Guai
    "/guwen/bookv_9b487a987862.aspx",  # 44. Gou
    "/guwen/bookv_25d1f974679a.aspx",  # 45. Cui
    "/guwen/bookv_f49ef6ca5f4c.aspx",  # 46. Sheng
    "/guwen/bookv_b970c3af86f7.aspx",  # 47. Kun
    "/guwen/bookv_a0a32f044e1b.aspx",  # 48. Jing
    "/guwen/bookv_3808c7a46ab1.aspx",  # 49. Ge
    "/guwen/bookv_9dce24c077d5.aspx",  # 50. Ding
    "/guwen/bookv_618281df810f.aspx",  # 51. Zhen
    "/guwen/bookv_ac0b361955a2.aspx",  # 52. Gen
    "/guwen/bookv_c8d7bd2b9158.aspx",  # 53. Jian
    "/guwen/bookv_69e33a90bd75.aspx",  # 54. Gui Mei
    "/guwen/bookv_7f6fb8ee6527.aspx",  # 55. Feng
    "/guwen/bookv_366512e6074d.aspx",  # 56. Lv
    "/guwen/bookv_c2d3f5548776.aspx",  # 57. Xun
    "/guwen/bookv_156b55aedcf2.aspx",  # 58. Dui
    "/guwen/bookv_5b858106654f.aspx",  # 59. Huan
    "/guwen/bookv_0a8ff823fd4a.aspx",  # 60. Jie
    "/guwen/bookv_3f2841826113.aspx",  # 61. Zhong Fu
    "/guwen/bookv_f075bd586a3e.aspx",  # 62. Xiao Guo
    "/guwen/bookv_a1db98007e2f.aspx",  # 63. Ji Ji
    "/guwen/bookv_a6294a2cceed.aspx",  # 64. Wei Ji
]

# For 象传下, need hexagrams starting from 65 (which are duplicates for lower canon)
XIANG_LOWER_URLS = [
    "/guwen/bookv_8c2d6cf852bb.aspx",  # 65. Qian (start of 象传下)
    "/guwen/bookv_ec9c1576e342.aspx",  # 66. Kun
    "/guwen/bookv_935c7368e950.aspx",  # 67. Zhun
    "/guwen/bookv_9df98b2b71d7.aspx",  # 68. Meng
    "/guwen/bookv_3886e30eab24.aspx",  # 69. Xu
    "/guwen/bookv_76f1b3cd1336.aspx",  # 70. Song
    "/guwen/bookv_aeadc14c8195.aspx",  # 71. Shi
    "/guwen/bookv_5f5bb1c05577.aspx",  # 72. Bi
    "/guwen/bookv_b1489292e5e5.aspx",  # 73. Xiao Xu
    "/guwen/bookv_c78e73a84ed5.aspx",  # 74. Lv
    "/guwen/bookv_19ce5dd980d4.aspx",  # 75. Tai
    "/guwen/bookv_c673bf0f2eb0.aspx",  # 76. Pi
    "/guwen/bookv_9ab07af0f625.aspx",  # 77. Tong Ren
    "/guwen/bookv_8cd5a91ad4fd.aspx",  # 78. Da You
    "/guwen/bookv_c2a78759ae5d.aspx",  # 79. Qian
    "/guwen/bookv_f37d18e8288c.aspx",  # 80. Yu
    "/guwen/bookv_0c39461359a6.aspx",  # 81. Sui
    "/guwen/bookv_6903e6f6b706.aspx",  # 82. Gu
    "/guwen/bookv_0a0a43466bb4.aspx",  # 83. Lin
    "/guwen/bookv_7928e1ca4c60.aspx",  # 84. Guan
    "/guwen/bookv_d327e6f6be10.aspx",  # 85. Shi He
    "/guwen/bookv_c0c55c99f90a.aspx",  # 86. Bi
    "/guwen/bookv_23d3fd6afe63.aspx",  # 87. Bo
    "/guwen/bookv_8280e855e3af.aspx",  # 88. Fu
    "/guwen/bookv_f683c3cf2368.aspx",  # 89. Wu Wang
    "/guwen/bookv_78b831d9fe1e.aspx",  # 90. Da Xu
    "/guwen/bookv_34e3344c052a.aspx",  # 91. Yi
    "/guwen/bookv_7634b2ee7b44.aspx",  # 92. Da Guo
    "/guwen/bookv_70e7ee3e7622.aspx",  # 93. Kan
    "/guwen/bookv_0f34e24123f0.aspx",  # 94. Li
    "/guwen/bookv_b9d6eca27621.aspx",  # 95. Xian
    "/guwen/bookv_eb0e2e19dc97.aspx",  # 96. Heng
    "/guwen/bookv_e6f54a4c52de.aspx",  # 97. Dun
    "/guwen/bookv_07fa3e5d0d1a.aspx",  # 98. Da Zhuang
]


def extract_text_from_page(url: str) -> str:
    """Extract text content from a gushiwen page"""
    full_url = f"https://www.gushiwen.cn{url}"

    try:
        response = session.get(full_url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find content
        text = ""
        for div in soup.select('.contson, .sons'):
            content = div.get_text(separator='\n', strip=True)
            # Clean up - remove audio player text
            lines = [line.strip() for line in content.split('\n')
                     if line.strip() and not any(skip in line for skip in
                                                  ['播放', '列表', '循环', '您的浏览器', '0.25x', '0:00'])]
            if lines:
                text = '\n'.join(lines)
                break

        return text.strip()

    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""


def scrape_tuan_shang(output_dir: Path):
    """Scrape 彖传上 (Tuan Zhuan Upper)"""
    print("\nScraping 彖传上 (Tuan Zhuan Upper)...")
    paragraphs = []

    for i, url in enumerate(HEXAGRAM_URLS[:30], 1):  # First 30 hexagrams
        print(f"  [{i}/30] Hexagram {i}...")
        text = extract_text_from_page(url)
        if text:
            paragraphs.append(text)
        time.sleep(2)

    result = {
        "title": "彖传上",
        "title_pinyin": "Tuan Zhuan Shang",
        "content": '\n\n'.join(paragraphs),
        "paragraphs": paragraphs
    }

    with open(output_dir / "tuan_upper.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Saved tuan_upper.json ({len(result['content'])} chars)")
    return result


def scrape_tuan_xia(output_dir: Path):
    """Scrape 彖传下 (Tuan Zhuan Lower)"""
    print("\nScraping 彖传下 (Tuan Zhuan Lower)...")
    paragraphs = []

    for i, url in enumerate(HEXAGRAM_URLS_LOWER, 31):  # Hexagrams 31-64
        print(f"  [{i-30}/34] Hexagram {i}...")
        text = extract_text_from_page(url)
        if text:
            paragraphs.append(text)
        time.sleep(2)

    result = {
        "title": "彖传下",
        "title_pinyin": "Tuan Zhuan Xia",
        "content": '\n\n'.join(paragraphs),
        "paragraphs": paragraphs
    }

    with open(output_dir / "tuan_lower.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Saved tuan_lower.json ({len(result['content'])} chars)")
    return result


def scrape_xiang_shang(output_dir: Path):
    """Scrape 象传上 (Xiang Zhuan Upper)"""
    print("\nScraping 象传上 (Xiang Zhuan Upper)...")
    paragraphs = []

    # Use the second set of URLs (65-94) for Xiang commentary
    for i, url in enumerate(XIANG_LOWER_URLS[:30], 1):  # First 30 hexagrams
        print(f"  [{i}/30] Hexagram {i}...")
        text = extract_text_from_page(url)
        if text:
            paragraphs.append(text)
        time.sleep(2)

    result = {
        "title": "象传上",
        "title_pinyin": "Xiang Zhuan Shang",
        "content": '\n\n'.join(paragraphs),
        "paragraphs": paragraphs
    }

    with open(output_dir / "xiang_upper.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Saved xiang_upper.json ({len(result['content'])} chars)")
    return result


def main():
    output_dir = Path("/Users/arsenelee/github/iching/data/yizhuan")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("Ten Wings Scraper - gushiwen.cn")
    print("="*60)

    results = {}

    # Start with Tuan Zhuan Upper
    results['tuan_upper'] = scrape_tuan_shang(output_dir)

    print("\n" + "="*60)
    print(f"Phase 1 complete. Collected {len(results)} sections.")
    print("="*60)


if __name__ == "__main__":
    main()
