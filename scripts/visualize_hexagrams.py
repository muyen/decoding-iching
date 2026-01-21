#!/usr/bin/env python3
"""Visualization tools for I Ching hexagrams"""
import json
import sqlite3
from pathlib import Path

def create_hexagram_html():
    """Create an interactive HTML visualization of hexagrams"""

    base_dir = Path('/Users/arsenelee/github/iching')
    db_path = base_dir / 'data/iching.db'
    output_path = base_dir / 'data/hexagram_visualization.html'

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Get all hexagrams with trigram info
    cursor.execute('''
        SELECT h.*,
               ut.name as upper_trigram, ut.nature as upper_nature,
               lt.name as lower_trigram, lt.nature as lower_nature
        FROM hexagrams h
        JOIN trigrams ut ON h.upper_trigram_id = ut.id
        JOIN trigrams lt ON h.lower_trigram_id = lt.id
        ORDER BY h.king_wen_number
    ''')

    hexagrams = [dict(row) for row in cursor.fetchall()]

    # Create HTML
    html = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>I Ching 64 Hexagrams Visualization</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
        }
        h1 { text-align: center; margin-bottom: 20px; color: #ffd700; }
        .controls {
            text-align: center;
            margin-bottom: 20px;
        }
        .controls select, .controls input {
            padding: 8px 12px;
            margin: 5px;
            border-radius: 4px;
            border: none;
            background: #16213e;
            color: #eee;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 10px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .hexagram {
            background: #16213e;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .hexagram:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2);
        }
        .hexagram.selected {
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            border: 2px solid #ffd700;
        }
        .hex-number {
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }
        .hex-symbol {
            font-size: 24px;
            margin-bottom: 5px;
            line-height: 1;
        }
        .hex-line {
            width: 40px;
            height: 4px;
            margin: 3px auto;
            background: #ffd700;
        }
        .hex-line.yin {
            background: linear-gradient(90deg, #ffd700 35%, transparent 35%, transparent 65%, #ffd700 65%);
        }
        .hex-name {
            font-size: 18px;
            font-weight: bold;
            color: #ffd700;
            margin-top: 5px;
        }
        .hex-trigrams {
            font-size: 11px;
            color: #888;
            margin-top: 3px;
        }
        .detail-panel {
            position: fixed;
            right: 20px;
            top: 100px;
            width: 300px;
            background: #16213e;
            border-radius: 8px;
            padding: 20px;
            display: none;
        }
        .detail-panel.show { display: block; }
        .detail-panel h2 { color: #ffd700; margin-bottom: 15px; }
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }
        .yang-count {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            text-align: center;
            line-height: 20px;
            font-size: 11px;
            margin-left: 5px;
        }
        .yang-0 { background: #000; }
        .yang-1 { background: #1a1a1a; }
        .yang-2 { background: #333; }
        .yang-3 { background: #666; }
        .yang-4 { background: #999; }
        .yang-5 { background: #ccc; color: #000; }
        .yang-6 { background: #fff; color: #000; }
        .filter-info {
            text-align: center;
            margin: 10px 0;
            color: #888;
        }
    </style>
</head>
<body>
    <h1>周易六十四卦 · 64 Hexagrams</h1>

    <div class="controls">
        <select id="orderSelect" onchange="reorder()">
            <option value="kingwen">文王序 King Wen</option>
            <option value="fuxi">先天 Fu Xi (Binary)</option>
            <option value="mawangdui">馬王堆 Mawangdui</option>
        </select>
        <select id="filterTrigram" onchange="filterHexagrams()">
            <option value="">All Trigrams</option>
            <option value="乾">乾 (Heaven)</option>
            <option value="坤">坤 (Earth)</option>
            <option value="震">震 (Thunder)</option>
            <option value="巽">巽 (Wind)</option>
            <option value="坎">坎 (Water)</option>
            <option value="離">離 (Fire)</option>
            <option value="艮">艮 (Mountain)</option>
            <option value="兌">兌 (Lake)</option>
        </select>
        <select id="filterYang" onchange="filterHexagrams()">
            <option value="">All Yang Counts</option>
            <option value="0">0 Yang</option>
            <option value="1">1 Yang</option>
            <option value="2">2 Yang</option>
            <option value="3">3 Yang</option>
            <option value="4">4 Yang</option>
            <option value="5">5 Yang</option>
            <option value="6">6 Yang</option>
        </select>
    </div>

    <div class="filter-info" id="filterInfo"></div>

    <div class="grid" id="hexagramGrid"></div>

    <div class="detail-panel" id="detailPanel">
        <h2 id="detailName"></h2>
        <div id="detailContent"></div>
    </div>

    <script>
    const hexagrams = ''' + json.dumps(hexagrams, ensure_ascii=False) + ''';

    function drawHexagram(binary) {
        let html = '';
        for (let i = 5; i >= 0; i--) {
            const isYang = binary[i] === '1';
            html += `<div class="hex-line ${isYang ? 'yang' : 'yin'}"></div>`;
        }
        return html;
    }

    function renderGrid(order = 'kingwen') {
        const grid = document.getElementById('hexagramGrid');
        const filterTrigram = document.getElementById('filterTrigram').value;
        const filterYang = document.getElementById('filterYang').value;

        let sorted = [...hexagrams];

        if (order === 'fuxi') {
            sorted.sort((a, b) => a.fuxi_position - b.fuxi_position);
        } else if (order === 'mawangdui') {
            sorted.sort((a, b) => (a.mawangdui_position || 999) - (b.mawangdui_position || 999));
        }

        let filtered = sorted;
        if (filterTrigram) {
            filtered = filtered.filter(h =>
                h.upper_trigram === filterTrigram || h.lower_trigram === filterTrigram
            );
        }
        if (filterYang !== '') {
            filtered = filtered.filter(h => h.yang_count === parseInt(filterYang));
        }

        document.getElementById('filterInfo').textContent =
            `Showing ${filtered.length} of 64 hexagrams`;

        grid.innerHTML = filtered.map(h => `
            <div class="hexagram" data-kw="${h.king_wen_number}" onclick="showDetail(${h.king_wen_number})">
                <div class="hex-number">#${h.king_wen_number}
                    <span class="yang-count yang-${h.yang_count}">${h.yang_count}</span>
                </div>
                <div class="hex-symbol">${drawHexagram(h.binary_repr)}</div>
                <div class="hex-name">${h.name}</div>
                <div class="hex-trigrams">${h.upper_trigram}/${h.lower_trigram}</div>
            </div>
        `).join('');
    }

    function showDetail(kw) {
        const h = hexagrams.find(x => x.king_wen_number === kw);
        if (!h) return;

        document.querySelectorAll('.hexagram').forEach(el => el.classList.remove('selected'));
        document.querySelector(`.hexagram[data-kw="${kw}"]`)?.classList.add('selected');

        document.getElementById('detailName').textContent = `#${h.king_wen_number} ${h.name}`;
        document.getElementById('detailContent').innerHTML = `
            <div class="detail-row"><span>Binary:</span><span>${h.binary_repr}</span></div>
            <div class="detail-row"><span>Decimal:</span><span>${h.decimal_value}</span></div>
            <div class="detail-row"><span>Upper:</span><span>${h.upper_trigram} (${h.upper_nature})</span></div>
            <div class="detail-row"><span>Lower:</span><span>${h.lower_trigram} (${h.lower_nature})</span></div>
            <div class="detail-row"><span>Yang Lines:</span><span>${h.yang_count}</span></div>
            <div class="detail-row"><span>King Wen #:</span><span>${h.king_wen_number}</span></div>
            <div class="detail-row"><span>Fu Xi #:</span><span>${h.fuxi_position}</span></div>
            <div class="detail-row"><span>Mawangdui #:</span><span>${h.mawangdui_position || 'N/A'}</span></div>
            <div class="detail-row"><span>Canon:</span><span>${h.canon}</span></div>
            <div class="detail-row"><span>Pair:</span><span>${h.pair_number}</span></div>
            <div class="detail-row"><span>Symmetric:</span><span>${h.is_symmetric ? 'Yes' : 'No'}</span></div>
            <div class="detail-row"><span>Inverse →:</span><span>#${h.inverse_hexagram_id}</span></div>
            <div class="detail-row"><span>Complement →:</span><span>#${h.complement_hexagram_id}</span></div>
        `;
        document.getElementById('detailPanel').classList.add('show');
    }

    function reorder() {
        renderGrid(document.getElementById('orderSelect').value);
    }

    function filterHexagrams() {
        renderGrid(document.getElementById('orderSelect').value);
    }

    // Initial render
    renderGrid();
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    conn.close()
    print(f"Created visualization at {output_path}")


def create_trigram_matrix_html():
    """Create 8x8 trigram combination matrix"""
    base_dir = Path('/Users/arsenelee/github/iching')
    db_path = base_dir / 'data/iching.db'
    output_path = base_dir / 'data/trigram_matrix.html'

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Get trigram combinations
    cursor.execute('''
        SELECT ut.name as upper, lt.name as lower,
               h.name as hexagram, h.king_wen_number
        FROM hexagrams h
        JOIN trigrams ut ON h.upper_trigram_id = ut.id
        JOIN trigrams lt ON h.lower_trigram_id = lt.id
    ''')

    matrix = {}
    for row in cursor.fetchall():
        key = (row['upper'], row['lower'])
        matrix[key] = {'name': row['hexagram'], 'kw': row['king_wen_number']}

    trigram_order = ['乾', '兌', '離', '震', '巽', '坎', '艮', '坤']

    html = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Trigram Combination Matrix</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 40px;
        }
        h1 { text-align: center; color: #ffd700; margin-bottom: 30px; }
        table {
            border-collapse: collapse;
            margin: 0 auto;
        }
        th, td {
            width: 80px;
            height: 80px;
            text-align: center;
            border: 1px solid #333;
        }
        th {
            background: #0f3460;
            color: #ffd700;
        }
        td {
            background: #16213e;
            cursor: pointer;
            transition: background 0.2s;
        }
        td:hover {
            background: #0f3460;
        }
        .hex-name { font-size: 20px; font-weight: bold; color: #ffd700; }
        .hex-num { font-size: 11px; color: #888; }
        .header-cell { font-size: 24px; }
        .legend {
            text-align: center;
            margin-top: 20px;
            color: #888;
        }
    </style>
</head>
<body>
    <h1>八卦組合矩陣 · Trigram Combination Matrix</h1>
    <table>
        <tr>
            <th></th>
'''

    # Header row (lower trigrams)
    for tri in trigram_order:
        html += f'            <th class="header-cell">{tri}</th>\n'
    html += '        </tr>\n'

    # Data rows (upper trigrams)
    for upper in trigram_order:
        html += f'        <tr>\n            <th class="header-cell">{upper}</th>\n'
        for lower in trigram_order:
            data = matrix.get((upper, lower), {'name': '?', 'kw': '?'})
            html += f'''            <td onclick="alert('#{data['kw']} {data['name']}')">
                <div class="hex-name">{data['name']}</div>
                <div class="hex-num">#{data['kw']}</div>
            </td>
'''
        html += '        </tr>\n'

    html += '''    </table>
    <div class="legend">
        行 = 上卦 (Upper Trigram) · 列 = 下卦 (Lower Trigram)
    </div>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    conn.close()
    print(f"Created trigram matrix at {output_path}")


def create_network_json():
    """Export transformation network as JSON for D3.js visualization"""
    base_dir = Path('/Users/arsenelee/github/iching')
    db_path = base_dir / 'data/iching.db'
    output_path = base_dir / 'data/hexagram_network.json'

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Get nodes
    cursor.execute('''
        SELECT king_wen_number, name, binary_repr, yang_count
        FROM hexagrams
    ''')
    nodes = [{'id': row['king_wen_number'], 'name': row['name'],
              'binary': row['binary_repr'], 'yang_count': row['yang_count']}
             for row in cursor.fetchall()]

    # Get edges (only one direction to avoid duplicates)
    cursor.execute('''
        SELECT DISTINCT
            h1.king_wen_number as source,
            h2.king_wen_number as target,
            hr.changed_line
        FROM hexagram_relationships hr
        JOIN hexagrams h1 ON hr.from_hexagram_id = h1.id
        JOIN hexagrams h2 ON hr.to_hexagram_id = h2.id
        WHERE hr.relationship_type = 'single_line_change'
        AND h1.king_wen_number < h2.king_wen_number
    ''')
    links = [{'source': row['source'], 'target': row['target'],
              'changed_line': row['changed_line']}
             for row in cursor.fetchall()]

    network = {'nodes': nodes, 'links': links}

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(network, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"Created network JSON at {output_path}")
    print(f"  Nodes: {len(nodes)}, Links: {len(links)}")


if __name__ == '__main__':
    print("Creating visualizations...")
    create_hexagram_html()
    create_trigram_matrix_html()
    create_network_json()
    print("\nAll visualizations created!")
