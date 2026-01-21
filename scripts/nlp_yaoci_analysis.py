#!/usr/bin/env python3
"""
爻辭語義NLP分析

分析爻辭文本的語義特徵，尋找與吉凶預測相關的語言模式
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 吉凶關鍵詞及其權重
JI_KEYWORDS = {
    '元吉': 2, '大吉': 2, '吉': 1, '利': 0.5, '亨': 0.5,
    '無咎': 0.3, '无咎': 0.3, '貞吉': 1.5, '終吉': 1,
    '有慶': 0.5, '光明': 0.5, '正': 0.3, '善': 0.5,
    '有喜': 0.5, '得': 0.3, '昌': 0.5, '泰': 0.5,
    '孚': 0.3, '順': 0.3, '和': 0.3
}

XIONG_KEYWORDS = {
    '大凶': -2, '凶': -1, '咎': -0.5, '厲': -0.5, '悔': -0.5,
    '吝': -0.3, '憂': -0.5, '難': -0.5, '險': -0.5,
    '損': -0.5, '敗': -0.5, '亡': -0.5, '失': -0.3,
    '困': -0.5, '否': -0.5, '災': -0.5, '殃': -0.5,
    '危': -0.5, '窮': -0.5, '終': -0.3, '血': -0.3,
    '傷': -0.5, '戰': -0.3, '死': -0.5
}

# 中性/條件詞
NEUTRAL_KEYWORDS = {
    '或': 0, '可': 0, '宜': 0, '時': 0, '待': 0,
    '小': 0, '若': 0, '如': 0, '不': 0
}

# 象徵詞彙
SYMBOL_CATEGORIES = {
    '天象': ['天', '日', '月', '星', '雲', '雨', '雷', '風', '霜', '雪'],
    '地象': ['地', '山', '川', '水', '海', '田', '野', '谷', '淵', '泉'],
    '人事': ['君', '臣', '人', '民', '夫', '婦', '子', '父', '母', '友'],
    '動物': ['龍', '虎', '馬', '牛', '羊', '豕', '雉', '魚', '鳥', '狐'],
    '植物': ['木', '草', '花', '果', '禾', '麥', '桑', '楊', '柳'],
    '器物': ['車', '舟', '輪', '劍', '弓', '矢', '鼎', '鉞', '圭', '璋'],
    '方位': ['東', '西', '南', '北', '上', '下', '中', '左', '右'],
    '數字': ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '萬'],
    '時間': ['朝', '夕', '日', '月', '歲', '年', '時', '旦', '暮', '終', '始'],
    '動作': ['往', '來', '行', '止', '進', '退', '升', '降', '入', '出', '見', '遇']
}

def load_hexagram_data():
    """載入64卦數據"""
    with open('data/zhouyi-64gua/zhouyi_64gua.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['hexagrams']

def extract_yaoci_features(hexagrams):
    """提取爻辭特徵"""
    all_yaoci = []

    for gua in hexagrams:
        gua_name = gua['name']
        gua_number = gua['number']
        upper = gua.get('trigrams', {}).get('upper', '')
        lower = gua.get('trigrams', {}).get('lower', '')

        for i, yao in enumerate(gua.get('yaoci', [])[:6]):  # 只取前6爻
            text = yao.get('text', '')
            position = yao.get('position', '')

            # 計算吉凶分數
            ji_score = sum(weight for kw, weight in JI_KEYWORDS.items() if kw in text)
            xiong_score = sum(weight for kw, weight in XIONG_KEYWORDS.items() if kw in text)

            # 提取符號類別
            symbols = {}
            for category, words in SYMBOL_CATEGORIES.items():
                count = sum(1 for w in words if w in text)
                if count > 0:
                    symbols[category] = count

            # 文本長度
            text_length = len(text)

            # 提取數字
            numbers = re.findall(r'[一二三四五六七八九十百千萬]', text)

            all_yaoci.append({
                'gua_name': gua_name,
                'gua_number': gua_number,
                'position': i + 1,
                'position_name': position,
                'text': text,
                'text_length': text_length,
                'ji_score': ji_score,
                'xiong_score': xiong_score,
                'net_score': ji_score + xiong_score,
                'symbols': symbols,
                'numbers': numbers,
                'upper_trigram': upper,
                'lower_trigram': lower
            })

    return all_yaoci

def analyze_keyword_distribution(yaoci_data):
    """分析關鍵詞分布"""
    print("\n" + "=" * 70)
    print(" 關鍵詞分布分析")
    print("=" * 70)

    # 統計各關鍵詞出現次數
    ji_counts = Counter()
    xiong_counts = Counter()

    for yao in yaoci_data:
        text = yao['text']
        for kw in JI_KEYWORDS:
            if kw in text:
                ji_counts[kw] += 1
        for kw in XIONG_KEYWORDS:
            if kw in text:
                xiong_counts[kw] += 1

    print("\n【吉類關鍵詞統計 Top 15】")
    for kw, count in ji_counts.most_common(15):
        print(f"  {kw}: {count}次 (權重: {JI_KEYWORDS[kw]})")

    print("\n【凶類關鍵詞統計 Top 15】")
    for kw, count in xiong_counts.most_common(15):
        print(f"  {kw}: {count}次 (權重: {XIONG_KEYWORDS[kw]})")

    return ji_counts, xiong_counts

def analyze_symbol_patterns(yaoci_data):
    """分析象徵符號模式"""
    print("\n" + "=" * 70)
    print(" 象徵符號分析")
    print("=" * 70)

    # 按吉凶分類統計符號
    ji_yaos = [y for y in yaoci_data if y['net_score'] >= 0.5]
    xiong_yaos = [y for y in yaoci_data if y['net_score'] <= -0.3]
    zhong_yaos = [y for y in yaoci_data if -0.3 < y['net_score'] < 0.5]

    print(f"\n分類: 吉={len(ji_yaos)}, 凶={len(xiong_yaos)}, 中={len(zhong_yaos)}")

    # 各類別的符號分布
    for name, group in [('吉', ji_yaos), ('凶', xiong_yaos), ('中', zhong_yaos)]:
        print(f"\n【{name}類爻辭符號統計】")
        symbol_totals = Counter()
        for yao in group:
            for cat, count in yao['symbols'].items():
                symbol_totals[cat] += count

        for cat, count in symbol_totals.most_common():
            avg = count / len(group) if group else 0
            print(f"  {cat}: {count}次 (平均 {avg:.2f}/爻)")

    return ji_yaos, xiong_yaos, zhong_yaos

def analyze_text_length_correlation(yaoci_data):
    """分析文本長度與吉凶的關係"""
    print("\n" + "=" * 70)
    print(" 文本長度與吉凶關係")
    print("=" * 70)

    # 按淨分數分組
    ji_lengths = [y['text_length'] for y in yaoci_data if y['net_score'] >= 0.5]
    xiong_lengths = [y['text_length'] for y in yaoci_data if y['net_score'] <= -0.3]
    zhong_lengths = [y['text_length'] for y in yaoci_data if -0.3 < y['net_score'] < 0.5]

    print(f"\n吉爻平均長度: {np.mean(ji_lengths):.1f} (n={len(ji_lengths)})")
    print(f"凶爻平均長度: {np.mean(xiong_lengths):.1f} (n={len(xiong_lengths)})")
    print(f"中爻平均長度: {np.mean(zhong_lengths):.1f} (n={len(zhong_lengths)})")

    # 繪製分布圖
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 箱線圖
    ax = axes[0]
    data_to_plot = [ji_lengths, zhong_lengths, xiong_lengths]
    bp = ax.boxplot(data_to_plot, labels=['吉', '中', '凶'], patch_artist=True)
    colors = ['#4CAF50', '#FFC107', '#F44336']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel('爻辭長度（字數）')
    ax.set_title('吉凶類別的爻辭長度分布')

    # 散點圖
    ax2 = axes[1]
    scores = [y['net_score'] for y in yaoci_data]
    lengths = [y['text_length'] for y in yaoci_data]
    colors = ['#4CAF50' if s >= 0.5 else '#F44336' if s <= -0.3 else '#FFC107' for s in scores]
    ax2.scatter(lengths, scores, c=colors, alpha=0.5, s=30)
    ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.5)
    ax2.axhline(y=-0.3, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('爻辭長度')
    ax2.set_ylabel('淨吉凶分數')
    ax2.set_title('爻辭長度 vs 吉凶分數')

    plt.tight_layout()
    plt.savefig('docs/figures/nlp_text_length.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n已保存: docs/figures/nlp_text_length.png")

def analyze_position_keywords(yaoci_data):
    """分析各爻位的關鍵詞特徵"""
    print("\n" + "=" * 70)
    print(" 爻位關鍵詞特徵分析")
    print("=" * 70)

    position_keywords = defaultdict(lambda: {'ji': Counter(), 'xiong': Counter()})

    for yao in yaoci_data:
        pos = yao['position']
        text = yao['text']

        for kw in JI_KEYWORDS:
            if kw in text:
                position_keywords[pos]['ji'][kw] += 1
        for kw in XIONG_KEYWORDS:
            if kw in text:
                position_keywords[pos]['xiong'][kw] += 1

    print("\n【各爻位特徵關鍵詞】")
    for pos in range(1, 7):
        print(f"\n第{pos}爻:")
        ji_top = position_keywords[pos]['ji'].most_common(5)
        xiong_top = position_keywords[pos]['xiong'].most_common(5)
        print(f"  吉詞: {', '.join(f'{kw}({c})' for kw, c in ji_top)}")
        print(f"  凶詞: {', '.join(f'{kw}({c})' for kw, c in xiong_top)}")

def build_prediction_features(yaoci_data):
    """構建預測特徵矩陣"""
    print("\n" + "=" * 70)
    print(" 預測特徵矩陣構建")
    print("=" * 70)

    features = []
    labels = []

    for yao in yaoci_data:
        # 特徵向量
        feature = {
            'position': yao['position'],
            'text_length': yao['text_length'],
            'ji_score': yao['ji_score'],
            'xiong_score': abs(yao['xiong_score']),
            'has_dragon': 1 if '龍' in yao['text'] else 0,
            'has_king': 1 if '王' in yao['text'] else 0,
            'has_heaven': 1 if '天' in yao['text'] else 0,
            'has_earth': 1 if '地' in yao['text'] else 0,
            'has_danger': 1 if any(d in yao['text'] for d in ['險', '危', '難', '厲']) else 0,
            'num_symbols': sum(yao['symbols'].values()),
        }
        features.append(feature)

        # 標籤
        if yao['net_score'] >= 0.5:
            labels.append(1)  # 吉
        elif yao['net_score'] <= -0.3:
            labels.append(-1)  # 凶
        else:
            labels.append(0)  # 中

    # 特徵重要性分析
    print("\n【特徵與吉凶的相關性】")
    for feature_name in ['position', 'text_length', 'ji_score', 'xiong_score',
                         'has_dragon', 'has_danger', 'num_symbols']:
        values = [f[feature_name] for f in features]
        correlation = np.corrcoef(values, labels)[0, 1]
        print(f"  {feature_name}: r = {correlation:.3f}")

    return features, labels

def ngram_analysis(yaoci_data):
    """N-gram分析"""
    print("\n" + "=" * 70)
    print(" N-gram 分析")
    print("=" * 70)

    # 提取所有爻辭文本
    ji_texts = [y['text'] for y in yaoci_data if y['net_score'] >= 0.5]
    xiong_texts = [y['text'] for y in yaoci_data if y['net_score'] <= -0.3]

    def get_bigrams(texts):
        bigrams = Counter()
        for text in texts:
            # 移除標點
            clean = re.sub(r'[，。：；、？！「」『』]', '', text)
            for i in range(len(clean) - 1):
                bigrams[clean[i:i+2]] += 1
        return bigrams

    ji_bigrams = get_bigrams(ji_texts)
    xiong_bigrams = get_bigrams(xiong_texts)

    print("\n【吉爻特有二字組合 Top 20】")
    ji_specific = {bg: c for bg, c in ji_bigrams.items()
                   if c >= 3 and xiong_bigrams.get(bg, 0) == 0}
    for bg, c in sorted(ji_specific.items(), key=lambda x: -x[1])[:20]:
        print(f"  {bg}: {c}次")

    print("\n【凶爻特有二字組合 Top 20】")
    xiong_specific = {bg: c for bg, c in xiong_bigrams.items()
                      if c >= 3 and ji_bigrams.get(bg, 0) == 0}
    for bg, c in sorted(xiong_specific.items(), key=lambda x: -x[1])[:20]:
        print(f"  {bg}: {c}次")

def create_summary_visualization(yaoci_data):
    """創建總結可視化"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. 各爻位的吉凶分數分布
    ax = axes[0, 0]
    positions = list(range(1, 7))
    ji_rates = []
    xiong_rates = []
    for pos in positions:
        pos_yaos = [y for y in yaoci_data if y['position'] == pos]
        ji_count = sum(1 for y in pos_yaos if y['net_score'] >= 0.5)
        xiong_count = sum(1 for y in pos_yaos if y['net_score'] <= -0.3)
        total = len(pos_yaos)
        ji_rates.append(ji_count / total * 100)
        xiong_rates.append(xiong_count / total * 100)

    x = np.arange(6)
    width = 0.35
    ax.bar(x - width/2, ji_rates, width, label='吉', color='#4CAF50', alpha=0.8)
    ax.bar(x + width/2, xiong_rates, width, label='凶', color='#F44336', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f'第{p}爻' for p in positions])
    ax.set_ylabel('比率 (%)')
    ax.set_title('各爻位NLP分析吉凶率')
    ax.legend()

    # 2. 關鍵詞詞雲效果（柱狀圖模擬）
    ax = axes[0, 1]
    ji_counts = Counter()
    for yao in yaoci_data:
        for kw in JI_KEYWORDS:
            if kw in yao['text']:
                ji_counts[kw] += 1
    top_ji = ji_counts.most_common(10)
    words, counts = zip(*top_ji) if top_ji else ([], [])
    ax.barh(words, counts, color='#4CAF50', alpha=0.8)
    ax.set_xlabel('出現次數')
    ax.set_title('吉類關鍵詞頻率 Top 10')
    ax.invert_yaxis()

    # 3. 符號類別分布
    ax = axes[1, 0]
    symbol_totals = Counter()
    for yao in yaoci_data:
        for cat, count in yao['symbols'].items():
            symbol_totals[cat] += count

    categories = list(symbol_totals.keys())
    counts = list(symbol_totals.values())
    ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.set_title('象徵符號類別分布')

    # 4. 文本長度分布
    ax = axes[1, 1]
    lengths = [y['text_length'] for y in yaoci_data]
    scores = [y['net_score'] for y in yaoci_data]
    colors = ['#4CAF50' if s >= 0.5 else '#F44336' if s <= -0.3 else '#FFC107' for s in scores]
    ax.scatter(range(len(lengths)), lengths, c=colors, alpha=0.5, s=20)
    ax.set_xlabel('爻序號')
    ax.set_ylabel('爻辭長度')
    ax.set_title('384爻爻辭長度分布（綠=吉，紅=凶，黃=中）')

    plt.tight_layout()
    plt.savefig('docs/figures/nlp_summary.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n已保存: docs/figures/nlp_summary.png")

def main():
    """主函數"""
    print("=" * 70)
    print(" 爻辭NLP語義分析")
    print("=" * 70)

    # 確保目錄存在
    Path('docs/figures').mkdir(parents=True, exist_ok=True)

    # 載入數據
    hexagrams = load_hexagram_data()

    # 提取特徵
    yaoci_data = extract_yaoci_features(hexagrams)
    print(f"\n已提取 {len(yaoci_data)} 爻的特徵")

    # 執行各類分析
    ji_counts, xiong_counts = analyze_keyword_distribution(yaoci_data)
    ji_yaos, xiong_yaos, zhong_yaos = analyze_symbol_patterns(yaoci_data)
    analyze_text_length_correlation(yaoci_data)
    analyze_position_keywords(yaoci_data)
    features, labels = build_prediction_features(yaoci_data)
    ngram_analysis(yaoci_data)
    create_summary_visualization(yaoci_data)

    # 導出數據
    export_data = {
        'total_yaoci': len(yaoci_data),
        'ji_count': len(ji_yaos),
        'xiong_count': len(xiong_yaos),
        'zhong_count': len(zhong_yaos),
        'ji_keywords': dict(ji_counts.most_common(20)),
        'xiong_keywords': dict(xiong_counts.most_common(20)),
        'features': features[:10],  # 樣本
        'labels_distribution': {
            '吉': labels.count(1),
            '中': labels.count(0),
            '凶': labels.count(-1)
        }
    }

    with open('data/analysis/nlp_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print("\n數據已導出至: data/analysis/nlp_analysis.json")

    print("\n" + "=" * 70)
    print(" NLP分析完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
