#!/usr/bin/env python3
"""Create SQLite database and import all I Ching data"""
import sqlite3
import json
from pathlib import Path

def create_schema(conn):
    """Create database tables"""
    cursor = conn.cursor()

    # Trigrams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trigrams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            pinyin TEXT,
            english TEXT,
            binary_repr TEXT NOT NULL,
            unicode_symbol TEXT,
            nature TEXT,
            attribute TEXT,
            attribute_meaning TEXT,
            family_role TEXT,
            body_part TEXT,
            animal TEXT,
            direction TEXT,
            element TEXT
        )
    ''')

    # Hexagrams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hexagrams (
            id INTEGER PRIMARY KEY,
            king_wen_number INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            pinyin TEXT,
            english TEXT,
            binary_repr TEXT NOT NULL,
            decimal_value INTEGER,
            fuxi_position INTEGER,
            mawangdui_position INTEGER,
            upper_trigram_id INTEGER REFERENCES trigrams(id),
            lower_trigram_id INTEGER REFERENCES trigrams(id),
            nuclear_upper_id INTEGER REFERENCES trigrams(id),
            nuclear_lower_id INTEGER REFERENCES trigrams(id),
            inverse_hexagram_id INTEGER,
            complement_hexagram_id INTEGER,
            is_symmetric BOOLEAN,
            yang_count INTEGER,
            yin_count INTEGER,
            canon TEXT,
            pair_number INTEGER
        )
    ''')

    # Lines (爻) table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lines (
            id INTEGER PRIMARY KEY,
            hexagram_id INTEGER REFERENCES hexagrams(id),
            position INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            yaoci TEXT,
            xiaoxiang TEXT
        )
    ''')

    # Hexagram texts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hexagram_texts (
            id INTEGER PRIMARY KEY,
            hexagram_id INTEGER REFERENCES hexagrams(id),
            text_type TEXT NOT NULL,
            content TEXT,
            source TEXT
        )
    ''')

    # Commentaries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commentaries (
            id INTEGER PRIMARY KEY,
            hexagram_id INTEGER REFERENCES hexagrams(id),
            source TEXT NOT NULL,
            author TEXT,
            era TEXT,
            content TEXT
        )
    ''')

    # Trigram symbols table (from 說卦傳)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trigram_symbols (
            id INTEGER PRIMARY KEY,
            trigram_id INTEGER REFERENCES trigrams(id),
            category TEXT,
            symbol TEXT,
            english TEXT
        )
    ''')

    # Hexagram relationships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hexagram_relationships (
            id INTEGER PRIMARY KEY,
            from_hexagram_id INTEGER REFERENCES hexagrams(id),
            to_hexagram_id INTEGER REFERENCES hexagrams(id),
            relationship_type TEXT NOT NULL,
            changed_line INTEGER
        )
    ''')

    # Sequences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sequences (
            id INTEGER PRIMARY KEY,
            hexagram_id INTEGER REFERENCES hexagrams(id),
            sequence_name TEXT NOT NULL,
            position INTEGER NOT NULL
        )
    ''')

    # Ten Wings texts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ten_wings (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            pinyin TEXT,
            english_name TEXT,
            content TEXT,
            char_count INTEGER
        )
    ''')

    conn.commit()
    print("Schema created successfully")

def import_trigrams(conn, base_dir):
    """Import trigram data"""
    cursor = conn.cursor()

    # Load shuogua mappings
    shuogua_file = base_dir / 'data/structure/shuogua_trigram_mappings.json'
    with open(shuogua_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    trigrams = data['trigrams']
    trigram_id_map = {}

    for name, tri in trigrams.items():
        cursor.execute('''
            INSERT INTO trigrams (name, pinyin, english, binary_repr, unicode_symbol,
                                 nature, attribute, attribute_meaning, family_role,
                                 body_part, animal, direction, element)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tri['name'],
            tri['pinyin'],
            tri['english'],
            tri['binary'],
            tri['unicode_symbol'],
            tri.get('lower_trigram', {}).get('nature') or tri.get('upper_trigram', {}).get('nature'),
            tri['attribute'],
            tri['attribute_meaning'],
            tri['family_role'],
            tri['body_part'],
            tri['animal'],
            tri['direction'],
            None  # element
        ))
        trigram_id_map[name] = cursor.lastrowid

        # Insert symbols
        for symbol in tri.get('all_symbols', []):
            cursor.execute('''
                INSERT INTO trigram_symbols (trigram_id, category, symbol)
                VALUES (?, ?, ?)
            ''', (trigram_id_map[name], 'all', symbol))

    conn.commit()
    print(f"Imported {len(trigram_id_map)} trigrams with symbols")
    return trigram_id_map

def import_hexagrams(conn, base_dir, trigram_id_map):
    """Import hexagram data"""
    cursor = conn.cursor()

    # Load hexagram structure
    hex_file = base_dir / 'data/structure/hexagrams_structure.json'
    with open(hex_file, 'r', encoding='utf-8') as f:
        hexagrams = json.load(f)

    # Load Mawangdui positions
    mw_file = base_dir / 'data/structure/mawangdui_sequence.json'
    mw_positions = {}
    if mw_file.exists():
        with open(mw_file, 'r', encoding='utf-8') as f:
            mw_data = json.load(f)
            for item in mw_data.get('sequence', []):
                mw_positions[item['binary']] = item['mawangdui_position']

    hexagram_id_map = {}

    for kw_num, hex_data in hexagrams.items():
        # Get trigram IDs
        upper_tri_name = hex_data['upper_trigram']['name']
        lower_tri_name = hex_data['lower_trigram']['name']
        nuclear_upper_name = hex_data['nuclear_upper_trigram']['name']
        nuclear_lower_name = hex_data['nuclear_lower_trigram']['name']

        cursor.execute('''
            INSERT INTO hexagrams (king_wen_number, name, binary_repr, decimal_value,
                                  fuxi_position, mawangdui_position,
                                  upper_trigram_id, lower_trigram_id,
                                  nuclear_upper_id, nuclear_lower_id,
                                  inverse_hexagram_id, complement_hexagram_id,
                                  is_symmetric, yang_count, yin_count, canon, pair_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(kw_num),
            hex_data['name'],
            hex_data['binary'],
            hex_data['decimal'],
            hex_data['fuxi_position'],
            mw_positions.get(hex_data['binary']),
            trigram_id_map.get(upper_tri_name),
            trigram_id_map.get(lower_tri_name),
            trigram_id_map.get(nuclear_upper_name),
            trigram_id_map.get(nuclear_lower_name),
            hex_data['inverse_hexagram'],
            hex_data['complement_hexagram'],
            hex_data['is_symmetric'],
            hex_data['yang_count'],
            hex_data['yin_count'],
            hex_data['canon'],
            hex_data['pair']
        ))
        hexagram_id_map[int(kw_num)] = cursor.lastrowid

        # Insert lines
        for line in hex_data['lines']:
            cursor.execute('''
                INSERT INTO lines (hexagram_id, position, line_type)
                VALUES (?, ?, ?)
            ''', (hexagram_id_map[int(kw_num)], line['position'], line['type']))

    conn.commit()
    print(f"Imported {len(hexagram_id_map)} hexagrams")
    return hexagram_id_map

def import_transformations(conn, base_dir, hexagram_id_map):
    """Import hexagram transformation relationships"""
    cursor = conn.cursor()

    trans_file = base_dir / 'data/structure/transformations.json'
    with open(trans_file, 'r', encoding='utf-8') as f:
        transformations = json.load(f)

    count = 0
    for trans in transformations:
        from_id = hexagram_id_map.get(trans['from_hexagram'])
        to_id = hexagram_id_map.get(trans['to_hexagram'])
        if from_id and to_id:
            cursor.execute('''
                INSERT INTO hexagram_relationships (from_hexagram_id, to_hexagram_id,
                                                   relationship_type, changed_line)
                VALUES (?, ?, ?, ?)
            ''', (from_id, to_id, 'single_line_change', trans['changed_line']))
            count += 1

    conn.commit()
    print(f"Imported {count} transformation relationships")

def import_sequences(conn, base_dir, hexagram_id_map):
    """Import sequence data"""
    cursor = conn.cursor()

    # King Wen sequence
    for kw_num, hex_id in hexagram_id_map.items():
        cursor.execute('''
            INSERT INTO sequences (hexagram_id, sequence_name, position)
            VALUES (?, ?, ?)
        ''', (hex_id, 'king_wen', kw_num))

    # Fu Xi sequence (from hexagram data)
    hex_file = base_dir / 'data/structure/hexagrams_structure.json'
    with open(hex_file, 'r', encoding='utf-8') as f:
        hexagrams = json.load(f)

    for kw_num, hex_data in hexagrams.items():
        hex_id = hexagram_id_map.get(int(kw_num))
        if hex_id:
            cursor.execute('''
                INSERT INTO sequences (hexagram_id, sequence_name, position)
                VALUES (?, ?, ?)
            ''', (hex_id, 'fuxi', hex_data['fuxi_position']))

    # Mawangdui sequence
    mw_file = base_dir / 'data/structure/mawangdui_sequence.json'
    if mw_file.exists():
        with open(mw_file, 'r', encoding='utf-8') as f:
            mw_data = json.load(f)

        # Build binary to kw_num lookup
        binary_to_kw = {}
        for kw_num, hex_data in hexagrams.items():
            binary_to_kw[hex_data['binary']] = int(kw_num)

        for item in mw_data.get('sequence', []):
            kw_num = binary_to_kw.get(item['binary'])
            if kw_num:
                hex_id = hexagram_id_map.get(kw_num)
                if hex_id:
                    cursor.execute('''
                        INSERT INTO sequences (hexagram_id, sequence_name, position)
                        VALUES (?, ?, ?)
                    ''', (hex_id, 'mawangdui', item['mawangdui_position']))

    conn.commit()
    print("Imported sequence data")

def import_ten_wings(conn, base_dir):
    """Import Ten Wings texts"""
    cursor = conn.cursor()

    yizhuan_dir = base_dir / 'data/yizhuan'

    wings = [
        ('xici_shang.json', '繫辭上傳', 'xici_shang', 'Xi Ci Shang (Great Commentary I)'),
        ('xici_xia.json', '繫辭下傳', 'xici_xia', 'Xi Ci Xia (Great Commentary II)'),
        ('shuogua.json', '說卦傳', 'shuogua', 'Shuo Gua (Discussion of Trigrams)'),
        ('xugua.json', '序卦傳', 'xugua', 'Xu Gua (Sequence of Hexagrams)'),
        ('zagua.json', '雜卦傳', 'zagua', 'Za Gua (Miscellaneous Notes)'),
    ]

    for filename, name, pinyin, english in wings:
        filepath = yizhuan_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            content = data.get('content', '')
            cursor.execute('''
                INSERT INTO ten_wings (name, pinyin, english_name, content, char_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, pinyin, english, content, len(content)))

    conn.commit()
    print("Imported Ten Wings texts")

def import_hexagram_texts(conn, base_dir, hexagram_id_map):
    """Import hexagram texts from zhouyi_64gua.json"""
    cursor = conn.cursor()

    gua_file = base_dir / 'data/zhouyi-64gua/zhouyi_64gua.json'
    if not gua_file.exists():
        print("zhouyi_64gua.json not found, skipping hexagram texts")
        return

    with open(gua_file, 'r', encoding='utf-8') as f:
        gua_data = json.load(f)

    # The data is nested under 'hexagrams' key
    hexagrams_list = gua_data.get('hexagrams', [])

    count = 0
    for hex_info in hexagrams_list:
        kw_num = hex_info.get('number')
        if not kw_num:
            continue

        hex_id = hexagram_id_map.get(kw_num)
        if not hex_id:
            continue

        # Guaci (卦辭)
        if hex_info.get('guaci'):
            cursor.execute('''
                INSERT INTO hexagram_texts (hexagram_id, text_type, content, source)
                VALUES (?, ?, ?, ?)
            ''', (hex_id, 'guaci', hex_info['guaci'], 'ZHOUYI'))
            count += 1

        # Tuanzhuan (彖傳)
        if hex_info.get('tuan'):
            cursor.execute('''
                INSERT INTO hexagram_texts (hexagram_id, text_type, content, source)
                VALUES (?, ?, ?, ?)
            ''', (hex_id, 'tuanzhuan', hex_info['tuan'], 'ZHOUYI'))
            count += 1

        # Xiang (象傳) - first element is daxiang
        xiang_list = hex_info.get('xiang', [])
        if xiang_list and len(xiang_list) > 0:
            cursor.execute('''
                INSERT INTO hexagram_texts (hexagram_id, text_type, content, source)
                VALUES (?, ?, ?, ?)
            ''', (hex_id, 'daxiang', xiang_list[0], 'ZHOUYI'))
            count += 1

        # Yaoci (爻辭) - update lines table
        yaoci_list = hex_info.get('yaoci', [])
        for i, yao in enumerate(yaoci_list):
            if yao and i < 6:
                yao_text = yao.get('text', '') if isinstance(yao, dict) else str(yao)
                cursor.execute('''
                    UPDATE lines SET yaoci = ?
                    WHERE hexagram_id = ? AND position = ?
                ''', (yao_text, hex_id, i + 1))

        # Xiaoxiang (小象) - remaining elements in xiang list
        if len(xiang_list) > 1:
            for i, xx in enumerate(xiang_list[1:7]):  # Skip daxiang, get up to 6 xiaoxiang
                if xx:
                    cursor.execute('''
                        UPDATE lines SET xiaoxiang = ?
                        WHERE hexagram_id = ? AND position = ?
                    ''', (xx, hex_id, i + 1))

    conn.commit()
    print(f"Imported {count} hexagram texts")

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    db_file = base_dir / 'data/iching.db'

    # Remove existing database
    if db_file.exists():
        db_file.unlink()

    # Create connection
    conn = sqlite3.connect(db_file)

    try:
        # Create schema
        create_schema(conn)

        # Import data
        trigram_id_map = import_trigrams(conn, base_dir)
        hexagram_id_map = import_hexagrams(conn, base_dir, trigram_id_map)
        import_transformations(conn, base_dir, hexagram_id_map)
        import_sequences(conn, base_dir, hexagram_id_map)
        import_ten_wings(conn, base_dir)
        import_hexagram_texts(conn, base_dir, hexagram_id_map)

        print(f"\nDatabase created at {db_file}")

        # Print statistics
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trigrams")
        print(f"  Trigrams: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM hexagrams")
        print(f"  Hexagrams: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM lines")
        print(f"  Lines: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM hexagram_relationships")
        print(f"  Relationships: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM trigram_symbols")
        print(f"  Trigram symbols: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM ten_wings")
        print(f"  Ten Wings texts: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM hexagram_texts")
        print(f"  Hexagram texts: {cursor.fetchone()[0]}")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
