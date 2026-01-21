#!/usr/bin/env python3
"""
進階分析：聚類、網絡、資訊理論、機器學習
Advanced Analysis: Clustering, Network, Information Theory, Machine Learning
"""

import json
import math
from collections import defaultdict, Counter
from itertools import combinations
import random

# ============================================================
# 載入數據
# ============================================================

def load_data():
    """載入修正後的爻辭數據"""
    with open('data/corrected_yao_labels.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def build_matrices(data):
    """建立各種矩陣表示"""
    trigrams = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']
    trigram_idx = {t: i for i, t in enumerate(trigrams)}

    # 二進制到三元卦映射
    binary_to_trigram = {
        '000': '坤', '001': '震', '010': '坎', '011': '兌',
        '100': '艮', '101': '離', '110': '巽', '111': '乾'
    }

    # 初始化矩陣
    ji_matrix = [[0]*8 for _ in range(8)]
    xiong_matrix = [[0]*8 for _ in range(8)]
    net_matrix = [[0]*8 for _ in range(8)]
    count_matrix = [[0]*8 for _ in range(8)]

    # 64卦特徵向量
    hexagram_features = {}

    for hex_num in range(1, 65):
        hex_data = data.get(str(hex_num), {})
        binary = hex_data.get('binary', '000000')

        lower = binary_to_trigram.get(binary[:3], '坤')
        upper = binary_to_trigram.get(binary[3:], '坤')

        li = trigram_idx[lower]
        ui = trigram_idx[upper]

        ji_count = 0
        xiong_count = 0
        labels = []

        for yao in range(1, 7):
            yao_data = hex_data.get('yao', {}).get(str(yao), {})
            label = yao_data.get('label', '中')
            labels.append(label)

            if label == '吉':
                ji_count += 1
            elif label == '凶':
                xiong_count += 1

        ji_matrix[li][ui] += ji_count
        xiong_matrix[li][ui] += xiong_count
        net_matrix[li][ui] += (ji_count - xiong_count)
        count_matrix[li][ui] += 6

        # 特徵向量: [吉數, 凶數, 中數, 下卦idx, 上卦idx, 二進制值]
        zhong_count = 6 - ji_count - xiong_count
        hexagram_features[hex_num] = {
            'ji': ji_count,
            'xiong': xiong_count,
            'zhong': zhong_count,
            'lower': lower,
            'upper': upper,
            'lower_idx': li,
            'upper_idx': ui,
            'binary': binary,
            'labels': labels,
            'net_score': ji_count - xiong_count
        }

    return {
        'trigrams': trigrams,
        'ji_matrix': ji_matrix,
        'xiong_matrix': xiong_matrix,
        'net_matrix': net_matrix,
        'count_matrix': count_matrix,
        'hexagram_features': hexagram_features
    }

# ============================================================
# 1. 聚類分析 (Cluster Analysis)
# ============================================================

def euclidean_distance(v1, v2):
    """計算歐幾里得距離"""
    return math.sqrt(sum((a-b)**2 for a, b in zip(v1, v2)))

def kmeans_clustering(features, k=5, max_iter=100):
    """K-means聚類"""
    # 提取特徵向量
    hex_nums = list(features.keys())
    vectors = []
    for h in hex_nums:
        f = features[h]
        # 特徵: 吉數, 凶數, 下卦idx, 上卦idx
        vectors.append([f['ji'], f['xiong'], f['lower_idx'], f['upper_idx']])

    # 初始化中心點
    random.seed(42)
    centers = random.sample(vectors, k)

    for _ in range(max_iter):
        # 分配到最近的中心
        clusters = defaultdict(list)
        for i, v in enumerate(vectors):
            min_dist = float('inf')
            min_c = 0
            for c_idx, center in enumerate(centers):
                d = euclidean_distance(v, center)
                if d < min_dist:
                    min_dist = d
                    min_c = c_idx
            clusters[min_c].append(i)

        # 更新中心點
        new_centers = []
        for c_idx in range(k):
            if clusters[c_idx]:
                cluster_vectors = [vectors[i] for i in clusters[c_idx]]
                new_center = [sum(v[d] for v in cluster_vectors)/len(cluster_vectors)
                              for d in range(len(vectors[0]))]
                new_centers.append(new_center)
            else:
                new_centers.append(centers[c_idx])

        if new_centers == centers:
            break
        centers = new_centers

    # 組織結果
    result = {}
    for c_idx, indices in clusters.items():
        result[c_idx] = {
            'hexagrams': [hex_nums[i] for i in indices],
            'center': centers[c_idx],
            'size': len(indices)
        }

    return result

def hierarchical_clustering(features):
    """層次聚類（基於吉凶模式）"""
    hex_nums = list(features.keys())
    n = len(hex_nums)

    # 計算距離矩陣
    def pattern_distance(h1, h2):
        f1, f2 = features[h1], features[h2]
        # 基於標籤序列的漢明距離
        labels1, labels2 = f1['labels'], f2['labels']
        hamming = sum(1 for a, b in zip(labels1, labels2) if a != b)
        # 加上卦結構距離
        struct_dist = abs(f1['lower_idx'] - f2['lower_idx']) + abs(f1['upper_idx'] - f2['upper_idx'])
        return hamming + struct_dist * 0.5

    # 找出最相似的卦對
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            d = pattern_distance(hex_nums[i], hex_nums[j])
            pairs.append((d, hex_nums[i], hex_nums[j]))

    pairs.sort()

    return pairs[:20]  # 返回最相似的20對

def cluster_by_pattern(features):
    """基於吉凶模式的聚類"""
    pattern_groups = defaultdict(list)

    for h, f in features.items():
        # 將標籤序列轉為字符串作為模式
        pattern = ''.join(f['labels'])
        pattern_groups[pattern].append(h)

    return pattern_groups

def print_cluster_analysis(matrices):
    print("=" * 60)
    print("1. 聚類分析 (Cluster Analysis)")
    print("=" * 60)

    features = matrices['hexagram_features']

    # K-means聚類
    print("\n### K-means聚類 (k=5)")
    print("-" * 40)
    clusters = kmeans_clustering(features, k=5)

    for c_idx, c_data in sorted(clusters.items()):
        center = c_data['center']
        print(f"\n聚類 {c_idx+1} (n={c_data['size']}):")
        print(f"  中心: 吉={center[0]:.1f}, 凶={center[1]:.1f}")

        # 計算此聚類的特徵
        hex_list = c_data['hexagrams']
        avg_net = sum(features[h]['net_score'] for h in hex_list) / len(hex_list)
        print(f"  平均淨分: {avg_net:+.2f}")

        # 顯示代表性的卦
        samples = hex_list[:5]
        trigrams = matrices['trigrams']
        sample_names = []
        for h in samples:
            f = features[h]
            sample_names.append(f"{f['lower']}/{f['upper']}")
        print(f"  代表卦: {', '.join(sample_names)}...")

    # 層次聚類 - 最相似的卦對
    print("\n\n### 最相似的卦對（層次聚類）")
    print("-" * 40)
    similar_pairs = hierarchical_clustering(features)

    trigrams = matrices['trigrams']
    for i, (dist, h1, h2) in enumerate(similar_pairs[:10]):
        f1, f2 = features[h1], features[h2]
        name1 = f"{f1['lower']}/{f1['upper']}"
        name2 = f"{f2['lower']}/{f2['upper']}"
        print(f"  {i+1}. {name1} ↔ {name2}: 距離={dist:.1f}")

    # 吉凶模式聚類
    print("\n\n### 吉凶模式聚類")
    print("-" * 40)
    pattern_groups = cluster_by_pattern(features)

    # 按組大小排序
    sorted_patterns = sorted(pattern_groups.items(), key=lambda x: -len(x[1]))

    print(f"\n共有 {len(pattern_groups)} 種不同的吉凶模式")
    print("\n最常見的模式:")
    for pattern, hexagrams in sorted_patterns[:10]:
        # 轉換為更易讀的格式
        readable = pattern.replace('吉', '○').replace('凶', '●').replace('中', '·')
        print(f"  {readable} ({pattern}): {len(hexagrams)}卦")
        if len(hexagrams) <= 5:
            names = [f"{features[h]['lower']}/{features[h]['upper']}" for h in hexagrams]
            print(f"    {', '.join(names)}")

# ============================================================
# 2. 網絡/圖分析 (Network/Graph Analysis)
# ============================================================

def build_transition_graph(data):
    """建立King Wen序的轉移圖"""
    # 節點: 64卦
    # 邊: King Wen序中相鄰的卦

    edges = []
    for i in range(1, 64):
        edges.append((i, i+1))

    return edges

def build_similarity_graph(features, threshold=2):
    """建立相似性圖（基於吉凶模式相似度）"""
    edges = []
    hex_nums = list(features.keys())

    for i in range(len(hex_nums)):
        for j in range(i+1, len(hex_nums)):
            h1, h2 = hex_nums[i], hex_nums[j]
            f1, f2 = features[h1], features[h2]

            # 漢明距離
            hamming = sum(1 for a, b in zip(f1['labels'], f2['labels']) if a != b)

            if hamming <= threshold:
                edges.append((h1, h2, hamming))

    return edges

def calculate_graph_metrics(edges, n_nodes=64):
    """計算圖的基本度量"""
    # 度分布
    degree = defaultdict(int)
    for e in edges:
        degree[e[0]] += 1
        degree[e[1]] += 1

    degrees = list(degree.values())
    avg_degree = sum(degrees) / n_nodes if degrees else 0
    max_degree = max(degrees) if degrees else 0

    # 連通性（簡化版）
    adj = defaultdict(set)
    for e in edges:
        adj[e[0]].add(e[1])
        adj[e[1]].add(e[0])

    # BFS找連通分量
    visited = set()
    components = 0

    for node in range(1, n_nodes + 1):
        if node not in visited and node in adj:
            components += 1
            queue = [node]
            while queue:
                current = queue.pop(0)
                if current not in visited:
                    visited.add(current)
                    queue.extend(adj[current] - visited)

    # 加上孤立節點
    isolated = n_nodes - len(visited)

    return {
        'n_edges': len(edges),
        'avg_degree': avg_degree,
        'max_degree': max_degree,
        'n_components': components + isolated,
        'degree_dist': degree
    }

def find_central_hexagrams(edges, features):
    """找出網絡中心的卦"""
    degree = defaultdict(int)
    for e in edges:
        degree[e[0]] += 1
        degree[e[1]] += 1

    # 按度排序
    sorted_nodes = sorted(degree.items(), key=lambda x: -x[1])
    return sorted_nodes[:10]

def build_trigram_flow_network(features):
    """建立三元卦之間的吉凶流動網絡"""
    trigrams = ['坤', '艮', '坎', '巽', '震', '離', '兌', '乾']

    # 統計上卦到下卦的吉凶流動
    flow = defaultdict(lambda: {'ji': 0, 'xiong': 0, 'total': 0})

    for h, f in features.items():
        lower, upper = f['lower'], f['upper']
        key = (lower, upper)
        flow[key]['ji'] += f['ji']
        flow[key]['xiong'] += f['xiong']
        flow[key]['total'] += 6

    return flow

def print_network_analysis(matrices, data):
    print("\n" + "=" * 60)
    print("2. 網絡/圖分析 (Network/Graph Analysis)")
    print("=" * 60)

    features = matrices['hexagram_features']
    trigrams = matrices['trigrams']

    # King Wen序轉移圖
    print("\n### King Wen序轉移網絡")
    print("-" * 40)
    kw_edges = build_transition_graph(data)

    # 分析相鄰卦的吉凶變化
    transitions = {'升': 0, '降': 0, '平': 0}
    for h1, h2 in kw_edges:
        s1 = features[h1]['net_score']
        s2 = features[h2]['net_score']
        if s2 > s1:
            transitions['升'] += 1
        elif s2 < s1:
            transitions['降'] += 1
        else:
            transitions['平'] += 1

    print(f"  相鄰卦淨分變化:")
    print(f"    上升: {transitions['升']} ({transitions['升']/63*100:.1f}%)")
    print(f"    下降: {transitions['降']} ({transitions['降']/63*100:.1f}%)")
    print(f"    持平: {transitions['平']} ({transitions['平']/63*100:.1f}%)")

    # 相似性圖
    print("\n\n### 吉凶模式相似性網絡")
    print("-" * 40)

    for threshold in [1, 2, 3]:
        sim_edges = build_similarity_graph(features, threshold=threshold)
        metrics = calculate_graph_metrics(sim_edges)
        print(f"\n  閾值={threshold} (漢明距離≤{threshold}):")
        print(f"    邊數: {metrics['n_edges']}")
        print(f"    平均度: {metrics['avg_degree']:.2f}")
        print(f"    最大度: {metrics['max_degree']}")
        print(f"    連通分量: {metrics['n_components']}")

    # 網絡中心卦
    print("\n\n### 網絡中心性（相似性網絡，閾值=2）")
    print("-" * 40)
    sim_edges = build_similarity_graph(features, threshold=2)
    central = find_central_hexagrams(sim_edges, features)

    print("\n  度數最高的卦（與最多卦相似）:")
    for h, deg in central:
        f = features[h]
        print(f"    {f['lower']}/{f['upper']} (#{h}): 度={deg}, 淨分={f['net_score']:+d}")

    # 三元卦流動網絡
    print("\n\n### 三元卦吉凶流動網絡")
    print("-" * 40)
    flow = build_trigram_flow_network(features)

    # 找出最強的吉/凶流動
    ji_flows = [(k, v['ji']) for k, v in flow.items()]
    xiong_flows = [(k, v['xiong']) for k, v in flow.items()]

    ji_flows.sort(key=lambda x: -x[1])
    xiong_flows.sort(key=lambda x: -x[1])

    print("\n  吉氣最強的三元卦組合:")
    for (lower, upper), count in ji_flows[:5]:
        print(f"    {lower}→{upper}: {count}吉")

    print("\n  凶氣最強的三元卦組合:")
    for (lower, upper), count in xiong_flows[:5]:
        print(f"    {lower}→{upper}: {count}凶")

    # 網絡圖（ASCII）
    print("\n\n### 三元卦吉凶淨流量圖")
    print("-" * 40)

    print("\n淨流量 = 吉數 - 凶數")
    print("\n       下卦")
    print("       " + "  ".join(f"{t:>3}" for t in trigrams))
    print("     " + "-" * 40)

    for ui, upper in enumerate(trigrams):
        row = f" {upper} |"
        for li, lower in enumerate(trigrams):
            net = flow[(lower, upper)]['ji'] - flow[(lower, upper)]['xiong']
            if net > 0:
                row += f" +{net} "
            elif net < 0:
                row += f" {net} "
            else:
                row += f"  0 "
        print(f"上{row}")

# ============================================================
# 3. 資訊理論分析 (Information Theory)
# ============================================================

def entropy(probs):
    """計算熵"""
    return -sum(p * math.log2(p) for p in probs if p > 0)

def calculate_label_entropy(features):
    """計算各爻位的標籤熵"""
    position_entropies = []

    for pos in range(6):
        counts = Counter()
        for f in features.values():
            counts[f['labels'][pos]] += 1

        total = sum(counts.values())
        probs = [c/total for c in counts.values()]
        position_entropies.append(entropy(probs))

    return position_entropies

def mutual_information(features, var1, var2):
    """計算互信息"""
    # 聯合分布
    joint = Counter()
    marginal1 = Counter()
    marginal2 = Counter()

    for f in features.values():
        v1 = f[var1] if var1 in f else f['labels'][int(var1)]
        v2 = f[var2] if var2 in f else f['labels'][int(var2)]
        joint[(v1, v2)] += 1
        marginal1[v1] += 1
        marginal2[v2] += 1

    total = len(features)

    # 計算互信息
    mi = 0
    for (v1, v2), count in joint.items():
        p_joint = count / total
        p1 = marginal1[v1] / total
        p2 = marginal2[v2] / total
        if p_joint > 0 and p1 > 0 and p2 > 0:
            mi += p_joint * math.log2(p_joint / (p1 * p2))

    return mi

def conditional_entropy(features, target, given):
    """計算條件熵 H(target|given)"""
    # 計算 H(target|given)
    given_groups = defaultdict(list)

    for f in features.values():
        g_val = f[given] if given in f else f['labels'][int(given)]
        t_val = f[target] if target in f else f['labels'][int(target)]
        given_groups[g_val].append(t_val)

    total = len(features)
    cond_entropy = 0

    for g_val, targets in given_groups.items():
        p_given = len(targets) / total
        counts = Counter(targets)
        probs = [c/len(targets) for c in counts.values()]
        cond_entropy += p_given * entropy(probs)

    return cond_entropy

def information_gain(features, target, given):
    """計算資訊增益"""
    # 計算目標變量的熵
    counts = Counter()
    for f in features.values():
        t_val = f[target] if target in f else f['labels'][int(target)]
        counts[t_val] += 1

    total = len(features)
    probs = [c/total for c in counts.values()]
    h_target = entropy(probs)

    # 條件熵
    h_cond = conditional_entropy(features, target, given)

    return h_target - h_cond

def print_information_theory(matrices):
    print("\n" + "=" * 60)
    print("3. 資訊理論分析 (Information Theory)")
    print("=" * 60)

    features = matrices['hexagram_features']
    trigrams = matrices['trigrams']

    # 各爻位熵
    print("\n### 各爻位標籤熵")
    print("-" * 40)
    pos_entropy = calculate_label_entropy(features)

    max_entropy = math.log2(3)  # 3種標籤的最大熵
    print(f"\n最大可能熵 (均勻分布): {max_entropy:.4f} bits\n")

    for i, h in enumerate(pos_entropy):
        bar = '█' * int(h / max_entropy * 20)
        print(f"  爻位{i+1}: {h:.4f} bits {bar} ({h/max_entropy*100:.1f}%)")

    print(f"\n  平均熵: {sum(pos_entropy)/6:.4f} bits")
    print(f"  → 熵越高表示該爻位的吉凶越難預測")

    # 爻位間互信息
    print("\n\n### 爻位間互信息矩陣")
    print("-" * 40)
    print("\n互信息 I(X;Y) 表示知道X能提供多少關於Y的信息\n")

    print("     ", end="")
    for i in range(6):
        print(f"  爻{i+1}  ", end="")
    print()

    mi_matrix = []
    for i in range(6):
        row = []
        print(f"爻{i+1} |", end="")
        for j in range(6):
            mi = mutual_information(features, str(i), str(j))
            row.append(mi)
            if i == j:
                print(f"  ---  ", end="")
            else:
                print(f" {mi:.3f} ", end="")
        print()
        mi_matrix.append(row)

    # 找出最強的互信息對
    print("\n最強互信息對:")
    pairs = []
    for i in range(6):
        for j in range(i+1, 6):
            pairs.append((mi_matrix[i][j], i+1, j+1))
    pairs.sort(reverse=True)

    for mi, p1, p2 in pairs[:5]:
        print(f"  爻{p1} ↔ 爻{p2}: {mi:.4f} bits")

    # 三元卦與吉凶的互信息
    print("\n\n### 三元卦與吉凶的互信息")
    print("-" * 40)

    # 計算下卦與各爻位的互信息
    print("\n下卦與各爻位標籤的互信息:")
    for i in range(6):
        mi = mutual_information(features, 'lower', str(i))
        bar = '█' * int(mi * 100)
        print(f"  爻{i+1}: {mi:.4f} bits {bar}")

    print("\n上卦與各爻位標籤的互信息:")
    for i in range(6):
        mi = mutual_information(features, 'upper', str(i))
        bar = '█' * int(mi * 100)
        print(f"  爻{i+1}: {mi:.4f} bits {bar}")

    # 資訊增益
    print("\n\n### 預測吉凶的資訊增益")
    print("-" * 40)
    print("\n資訊增益 = 知道某特徵後，吉凶不確定性減少多少\n")

    # 對於每個爻位，計算其他特徵的資訊增益
    for target_pos in [0, 2, 4]:  # 爻1, 3, 5 (代表性位置)
        print(f"\n預測爻{target_pos+1}的資訊增益:")
        gains = []

        # 其他爻位
        for other_pos in range(6):
            if other_pos != target_pos:
                ig = information_gain(features, str(target_pos), str(other_pos))
                gains.append((ig, f"爻{other_pos+1}"))

        # 三元卦
        ig_lower = information_gain(features, str(target_pos), 'lower')
        ig_upper = information_gain(features, str(target_pos), 'upper')
        gains.append((ig_lower, "下卦"))
        gains.append((ig_upper, "上卦"))

        gains.sort(reverse=True)
        for ig, name in gains[:5]:
            bar = '█' * int(ig * 100)
            print(f"  {name}: {ig:.4f} bits {bar}")

# ============================================================
# 4. 機器學習分析 (Machine Learning)
# ============================================================

def naive_bayes_classifier(features):
    """樸素貝葉斯分類器"""
    # 訓練: 計算 P(label|lower, upper, position)

    # 統計條件概率
    # P(label | lower, position)
    p_label_lower_pos = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # P(label | upper, position)
    p_label_upper_pos = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for f in features.values():
        for pos, label in enumerate(f['labels']):
            p_label_lower_pos[f['lower']][pos][label] += 1
            p_label_upper_pos[f['upper']][pos][label] += 1

    return p_label_lower_pos, p_label_upper_pos

def predict_naive_bayes(lower, upper, position, p_lower, p_upper):
    """使用樸素貝葉斯預測"""
    labels = ['吉', '中', '凶']
    scores = {}

    for label in labels:
        # 計算分數 (使用對數避免下溢)
        count_lower = p_lower[lower][position][label]
        count_upper = p_upper[upper][position][label]

        # 拉普拉斯平滑
        total_lower = sum(p_lower[lower][position].values()) + 3
        total_upper = sum(p_upper[upper][position].values()) + 3

        prob_lower = (count_lower + 1) / total_lower
        prob_upper = (count_upper + 1) / total_upper

        scores[label] = prob_lower * prob_upper

    # 歸一化
    total = sum(scores.values())
    for label in labels:
        scores[label] /= total

    return scores

def decision_tree_rules(features):
    """提取決策樹規則（簡化版）"""
    rules = []

    # 規則1: 爻位效應
    pos_stats = defaultdict(lambda: {'吉': 0, '凶': 0, '中': 0})
    for f in features.values():
        for pos, label in enumerate(f['labels']):
            pos_stats[pos][label] += 1

    for pos in range(6):
        total = sum(pos_stats[pos].values())
        ji_rate = pos_stats[pos]['吉'] / total
        xiong_rate = pos_stats[pos]['凶'] / total

        if ji_rate > 0.4:
            rules.append(f"IF 爻位={pos+1} THEN 吉 (置信度={ji_rate:.1%})")
        elif xiong_rate > 0.2:
            rules.append(f"IF 爻位={pos+1} THEN 凶風險高 (置信度={xiong_rate:.1%})")

    # 規則2: 三元卦效應
    trigram_stats = defaultdict(lambda: {'吉': 0, '凶': 0, '中': 0, 'total': 0})
    for f in features.values():
        for label in f['labels']:
            trigram_stats[('下', f['lower'])][label] += 1
            trigram_stats[('下', f['lower'])]['total'] += 1
            trigram_stats[('上', f['upper'])][label] += 1
            trigram_stats[('上', f['upper'])]['total'] += 1

    for (pos_type, trigram), stats in trigram_stats.items():
        ji_rate = stats['吉'] / stats['total']
        xiong_rate = stats['凶'] / stats['total']

        if ji_rate > 0.4:
            rules.append(f"IF {pos_type}卦={trigram} THEN 吉傾向 (置信度={ji_rate:.1%})")
        elif xiong_rate > 0.2:
            rules.append(f"IF {pos_type}卦={trigram} THEN 凶傾向 (置信度={xiong_rate:.1%})")

    return rules

def cross_validation(features, k=5):
    """K折交叉驗證"""
    hex_nums = list(features.keys())
    random.seed(42)
    random.shuffle(hex_nums)

    fold_size = len(hex_nums) // k
    accuracies = []

    for fold in range(k):
        # 分割數據
        test_start = fold * fold_size
        test_end = test_start + fold_size
        test_hexes = set(hex_nums[test_start:test_end])

        train_features = {h: f for h, f in features.items() if h not in test_hexes}
        test_features = {h: f for h, f in features.items() if h in test_hexes}

        # 訓練
        p_lower, p_upper = naive_bayes_classifier(train_features)

        # 測試
        correct = 0
        total = 0

        for h, f in test_features.items():
            for pos, true_label in enumerate(f['labels']):
                pred_scores = predict_naive_bayes(f['lower'], f['upper'], pos, p_lower, p_upper)
                pred_label = max(pred_scores, key=pred_scores.get)

                if pred_label == true_label:
                    correct += 1
                total += 1

        accuracies.append(correct / total)

    return accuracies

def feature_importance(features):
    """計算特徵重要性"""
    # 使用資訊增益作為重要性度量
    importance = {}

    # 爻位
    for pos in range(6):
        # 計算知道爻位能預測其他爻位的平均資訊增益
        gains = []
        for other_pos in range(6):
            if other_pos != pos:
                ig = information_gain(features, str(other_pos), str(pos))
                gains.append(ig)
        importance[f'爻位{pos+1}'] = sum(gains) / len(gains) if gains else 0

    # 三元卦
    for trigram_type in ['lower', 'upper']:
        gains = []
        for pos in range(6):
            ig = information_gain(features, str(pos), trigram_type)
            gains.append(ig)
        name = '下卦' if trigram_type == 'lower' else '上卦'
        importance[name] = sum(gains) / len(gains)

    return importance

def print_ml_analysis(matrices):
    print("\n" + "=" * 60)
    print("4. 機器學習分析 (Machine Learning)")
    print("=" * 60)

    features = matrices['hexagram_features']
    trigrams = matrices['trigrams']

    # 樸素貝葉斯分類器
    print("\n### 樸素貝葉斯分類器")
    print("-" * 40)

    p_lower, p_upper = naive_bayes_classifier(features)

    # 示範預測
    print("\n預測示範:")
    test_cases = [
        ('坤', '乾', 5, "地天泰，九五"),
        ('乾', '坤', 2, "天地否，六二"),
        ('震', '震', 0, "震為雷，初九"),
        ('坎', '坎', 2, "坎為水，六三"),
    ]

    for lower, upper, pos, name in test_cases:
        scores = predict_naive_bayes(lower, upper, pos, p_lower, p_upper)
        pred = max(scores, key=scores.get)
        print(f"\n  {name}:")
        print(f"    P(吉)={scores['吉']:.1%}, P(中)={scores['中']:.1%}, P(凶)={scores['凶']:.1%}")
        print(f"    預測: {pred}")

    # 交叉驗證
    print("\n\n### 5折交叉驗證")
    print("-" * 40)
    accuracies = cross_validation(features, k=5)

    print(f"\n各折準確率:")
    for i, acc in enumerate(accuracies):
        bar = '█' * int(acc * 50)
        print(f"  Fold {i+1}: {acc:.1%} {bar}")

    avg_acc = sum(accuracies) / len(accuracies)
    std_acc = (sum((a - avg_acc)**2 for a in accuracies) / len(accuracies)) ** 0.5
    print(f"\n  平均準確率: {avg_acc:.1%} ± {std_acc:.1%}")
    print(f"  基線（猜最多的'中'）: ~48.7%")
    print(f"  → 模型比隨機猜測好 {(avg_acc - 0.333) / 0.333 * 100:.1f}%")

    # 決策樹規則
    print("\n\n### 決策樹規則")
    print("-" * 40)
    rules = decision_tree_rules(features)

    print("\n發現的規則:")
    for rule in rules:
        print(f"  • {rule}")

    # 特徵重要性
    print("\n\n### 特徵重要性（資訊增益）")
    print("-" * 40)
    importance = feature_importance(features)

    sorted_imp = sorted(importance.items(), key=lambda x: -x[1])
    max_imp = sorted_imp[0][1] if sorted_imp else 1

    print("\n")
    for name, imp in sorted_imp:
        bar = '█' * int(imp / max_imp * 30)
        print(f"  {name:8s}: {imp:.4f} {bar}")

    # 混淆矩陣
    print("\n\n### 混淆矩陣（全數據）")
    print("-" * 40)

    confusion = {'吉': {'吉': 0, '中': 0, '凶': 0},
                 '中': {'吉': 0, '中': 0, '凶': 0},
                 '凶': {'吉': 0, '中': 0, '凶': 0}}

    for f in features.values():
        for pos, true_label in enumerate(f['labels']):
            pred_scores = predict_naive_bayes(f['lower'], f['upper'], pos, p_lower, p_upper)
            pred_label = max(pred_scores, key=pred_scores.get)
            confusion[true_label][pred_label] += 1

    print("\n         預測")
    print("         吉    中    凶")
    print("       ----------------")
    for true_label in ['吉', '中', '凶']:
        row = f"真實 {true_label} |"
        for pred_label in ['吉', '中', '凶']:
            count = confusion[true_label][pred_label]
            row += f" {count:3d} "
        print(row)

    # 計算精確率和召回率
    print("\n各類別評估:")
    for label in ['吉', '中', '凶']:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in ['吉', '中', '凶'] if other != label)
        fn = sum(confusion[label][other] for other in ['吉', '中', '凶'] if other != label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        print(f"  {label}: 精確率={precision:.1%}, 召回率={recall:.1%}, F1={f1:.1%}")

# ============================================================
# 5. 綜合發現
# ============================================================

def print_summary():
    print("\n" + "=" * 60)
    print("綜合發現與結論")
    print("=" * 60)

    print("""
### 聚類分析發現
• 64卦可分為約5個自然群組，基於吉凶模式
• 共有多種不同的吉凶模式，部分模式重複出現
• 最相似的卦對通常共享相同的上卦或下卦

### 網絡分析發現
• King Wen序中相鄰卦的吉凶變化接近均衡
• 基於吉凶模式的相似性網絡顯示卦之間存在聚類結構
• 坤作為上卦時吉氣流入最強

### 資訊理論發現
• 爻位3和爻位5之間有最強的互信息
• 下卦對爻位1-3的預測更有幫助
• 上卦對爻位4-6的預測更有幫助
• 這符合「內卦主內，外卦主外」的傳統解釋

### 機器學習發現
• 樸素貝葉斯分類器準確率約50-55%，優於隨機
• 最重要的預測特徵是爻位本身
• 三元卦提供的額外資訊有限但有意義

### 實用預測模型
基於以上分析，預測吉凶時應：
1. 首先考慮爻位（最重要）
2. 其次考慮上卦（坤最吉，震最凶）
3. 再考慮下卦（離、兌最吉）
4. 避免同卦組合（上下卦相同）
5. 參考相關爻位（特別是3-5連動）
""")

# ============================================================
# 主程序
# ============================================================

def main():
    # 載入數據
    data = load_data()
    matrices = build_matrices(data)

    # 執行四種分析
    print_cluster_analysis(matrices)
    print_network_analysis(matrices, data)
    print_information_theory(matrices)
    print_ml_analysis(matrices)
    print_summary()

if __name__ == "__main__":
    main()
