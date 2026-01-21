#!/usr/bin/env python3
"""Extract structured trigram-to-symbol mappings from 說卦傳 (Shuo Gua Zhuan)"""
import json
from pathlib import Path

def create_trigram_mappings():
    """Create comprehensive trigram mappings from 說卦傳"""

    # Binary representations (bottom to top)
    trigram_binary = {
        '乾': '111',  # ☰ Heaven
        '坤': '000',  # ☷ Earth
        '震': '100',  # ☳ Thunder (yang at bottom)
        '巽': '011',  # ☴ Wind (yin at bottom)
        '坎': '010',  # ☵ Water (yang in middle)
        '離': '101',  # ☲ Fire (yin in middle)
        '艮': '001',  # ☶ Mountain (yang at top)
        '兌': '110',  # ☱ Lake (yin at top)
    }

    mappings = {
        '乾': {
            'name': '乾',
            'pinyin': 'qián',
            'english': 'Heaven/Creative',
            'binary': '111',
            'unicode_symbol': '☰',

            # Chapter 7: Core attribute
            'attribute': '健',
            'attribute_meaning': 'strength, vigor, creativity',

            # Chapter 4: Function
            'function': '君之',
            'function_meaning': 'to rule, to lead',

            # Chapter 5: Direction & Season (後天八卦)
            'direction': '西北',
            'direction_english': 'Northwest',
            'season_action': '戰',
            'season_meaning': 'conflict, yin-yang clash',

            # Chapter 8: Primary animal
            'animal': '馬',
            'animal_english': 'horse',

            # Chapter 9: Body part
            'body_part': '首',
            'body_part_english': 'head',

            # Chapter 10: Family role
            'family_role': '父',
            'family_role_english': 'father',

            # Chapter 11: Extended symbols
            'extended_symbols': {
                'nature': ['天', '圜'],
                'social': ['君', '父'],
                'materials': ['玉', '金'],
                'qualities': ['寒', '冰', '大赤'],
                'horses': ['良馬', '老馬', '瘠馬', '駁馬'],
                'plants': ['木果'],
            },
            'all_symbols': ['天', '圜', '君', '父', '玉', '金', '寒', '冰', '大赤', '良馬', '老馬', '瘠馬', '駁馬', '木果'],
        },

        '坤': {
            'name': '坤',
            'pinyin': 'kūn',
            'english': 'Earth/Receptive',
            'binary': '000',
            'unicode_symbol': '☷',

            'attribute': '順',
            'attribute_meaning': 'yielding, compliance, receptivity',

            'function': '藏之',
            'function_meaning': 'to store, to nurture',

            'direction': '西南',
            'direction_english': 'Southwest',
            'season_action': '致役',
            'season_meaning': 'nurturing service',

            'animal': '牛',
            'animal_english': 'ox, cow',

            'body_part': '腹',
            'body_part_english': 'belly, abdomen',

            'family_role': '母',
            'family_role_english': 'mother',

            'extended_symbols': {
                'nature': ['地'],
                'social': ['母', '眾'],
                'materials': ['布', '釜'],
                'qualities': ['吝嗇', '均', '文', '黑'],
                'animals': ['子母牛'],
                'objects': ['大輿', '柄'],
            },
            'all_symbols': ['地', '母', '布', '釜', '吝嗇', '均', '子母牛', '大輿', '文', '眾', '柄', '黑'],
        },

        '震': {
            'name': '震',
            'pinyin': 'zhèn',
            'english': 'Thunder/Arousing',
            'binary': '100',
            'unicode_symbol': '☳',

            'attribute': '動',
            'attribute_meaning': 'movement, action, arousal',

            'function': '動之',
            'function_meaning': 'to move, to activate',

            'direction': '東',
            'direction_english': 'East',
            'season_action': '出',
            'season_meaning': 'emergence, beginning',

            'animal': '龍',
            'animal_english': 'dragon',

            'body_part': '足',
            'body_part_english': 'foot',

            'family_role': '長男',
            'family_role_english': 'eldest son',

            'extended_symbols': {
                'nature': ['雷'],
                'colors': ['玄黃'],
                'qualities': ['敷', '決躁', '蕃鮮'],
                'plants': ['蒼筤竹', '萑葦'],
                'paths': ['大塗'],
                'horse_qualities': ['善鳴', '馵足', '作足', '的顙'],
                'crops': ['反生'],
            },
            'all_symbols': ['雷', '龍', '玄黃', '敷', '大塗', '長子', '決躁', '蒼筤竹', '萑葦', '善鳴', '馵足', '作足', '的顙', '反生', '健', '蕃鮮'],
        },

        '巽': {
            'name': '巽',
            'pinyin': 'xùn',
            'english': 'Wind/Gentle',
            'binary': '011',
            'unicode_symbol': '☴',

            'attribute': '入',
            'attribute_meaning': 'penetrating, entering, gentle influence',

            'function': '散之',
            'function_meaning': 'to scatter, to disperse',

            'direction': '東南',
            'direction_english': 'Southeast',
            'season_action': '齊',
            'season_meaning': 'alignment, purification',

            'animal': '雞',
            'animal_english': 'chicken, rooster',

            'body_part': '股',
            'body_part_english': 'thigh',

            'family_role': '長女',
            'family_role_english': 'eldest daughter',

            'extended_symbols': {
                'nature': ['木', '風'],
                'qualities': ['繩直', '白', '長', '高', '進退', '不果', '臭'],
                'occupations': ['工'],
                'person_features': ['寡髮', '廣顙', '多白眼'],
                'commerce': ['近利市三倍'],
            },
            'all_symbols': ['木', '風', '長女', '繩直', '工', '白', '長', '高', '進退', '不果', '臭', '寡髮', '廣顙', '多白眼', '近利市三倍', '躁卦'],
        },

        '坎': {
            'name': '坎',
            'pinyin': 'kǎn',
            'english': 'Water/Abysmal',
            'binary': '010',
            'unicode_symbol': '☵',

            'attribute': '陷',
            'attribute_meaning': 'danger, pitfall, depth',

            'function': '潤之',
            'function_meaning': 'to moisten, to nourish (as rain)',

            'direction': '北',
            'direction_english': 'North',
            'season_action': '勞',
            'season_meaning': 'toil, where things return',

            'animal': '豕',
            'animal_english': 'pig',

            'body_part': '耳',
            'body_part_english': 'ear',

            'family_role': '中男',
            'family_role_english': 'middle son',

            'extended_symbols': {
                'nature': ['水', '月'],
                'places': ['溝瀆'],
                'qualities': ['隱伏', '矯輮', '通', '堅多心'],
                'objects': ['弓輪'],
                'afflictions': ['加憂', '心病', '耳痛', '血卦', '赤'],
                'horse_qualities': ['美脊', '亟心', '下首', '薄蹄', '曳'],
                'vehicle': ['多眚'],
                'negative': ['盜'],
            },
            'all_symbols': ['水', '溝瀆', '隱伏', '矯輮', '弓輪', '加憂', '心病', '耳痛', '血卦', '赤', '美脊', '亟心', '下首', '薄蹄', '曳', '多眚', '通', '月', '盜', '堅多心'],
        },

        '離': {
            'name': '離',
            'pinyin': 'lí',
            'english': 'Fire/Clinging',
            'binary': '101',
            'unicode_symbol': '☲',

            'attribute': '麗',
            'attribute_meaning': 'clinging, brightness, beauty',

            'function': '烜之',
            'function_meaning': 'to dry, to illuminate (as sun)',

            'direction': '南',
            'direction_english': 'South',
            'season_action': '相見',
            'season_meaning': 'visibility, manifestation',

            'animal': '雉',
            'animal_english': 'pheasant',

            'body_part': '目',
            'body_part_english': 'eye',

            'family_role': '中女',
            'family_role_english': 'middle daughter',

            'extended_symbols': {
                'nature': ['火', '日', '電'],
                'military': ['甲冑', '戈兵'],
                'body': ['大腹'],
                'shell_creatures': ['鱉', '蟹', '蠃', '蚌', '龜'],
                'wood': ['科上槁'],
            },
            'all_symbols': ['火', '日', '電', '中女', '甲冑', '戈兵', '大腹', '乾卦', '鱉', '蟹', '蠃', '蚌', '龜', '科上槁'],
        },

        '艮': {
            'name': '艮',
            'pinyin': 'gèn',
            'english': 'Mountain/Keeping Still',
            'binary': '001',
            'unicode_symbol': '☶',

            'attribute': '止',
            'attribute_meaning': 'stopping, stillness, rest',

            'function': '止之',
            'function_meaning': 'to stop, to stabilize',

            'direction': '東北',
            'direction_english': 'Northeast',
            'season_action': '成言',
            'season_meaning': 'completion, where things end and begin',

            'animal': '狗',
            'animal_english': 'dog',

            'body_part': '手',
            'body_part_english': 'hand',

            'family_role': '少男',
            'family_role_english': 'youngest son',

            'extended_symbols': {
                'nature': ['山'],
                'places': ['徑路', '門闕'],
                'objects': ['小石', '果苽'],
                'roles': ['閽寺'],
                'body': ['指'],
                'animals': ['狗', '鼠', '黔喙之屬'],
                'wood': ['堅多節'],
            },
            'all_symbols': ['山', '徑路', '小石', '門闕', '果苽', '閽寺', '指', '狗', '鼠', '黔喙之屬', '堅多節'],
        },

        '兌': {
            'name': '兌',
            'pinyin': 'duì',
            'english': 'Lake/Joyous',
            'binary': '110',
            'unicode_symbol': '☱',

            'attribute': '說',
            'attribute_meaning': 'joy, pleasure, expression',

            'function': '說之',
            'function_meaning': 'to please, to bring joy',

            'direction': '西',
            'direction_english': 'West',
            'season_action': '說言',
            'season_meaning': 'joyful expression, autumn harvest',

            'animal': '羊',
            'animal_english': 'sheep, goat',

            'body_part': '口',
            'body_part_english': 'mouth',

            'family_role': '少女',
            'family_role_english': 'youngest daughter',

            'extended_symbols': {
                'nature': ['澤'],
                'roles': ['少女', '巫', '妾'],
                'speech': ['口舌'],
                'actions': ['毀折', '附決'],
                'terrain': ['剛鹵'],
                'animals': ['羊'],
            },
            'all_symbols': ['澤', '少女', '巫', '口舌', '毀折', '附決', '剛鹵', '妾', '羊'],
        },
    }

    return mappings

def create_relationship_matrix():
    """Create relationships between trigrams from 說卦傳 Chapter 3"""
    # 天地定位，山泽通气，雷风相薄，水火不相射
    relationships = {
        'complementary_pairs': [
            {'pair': ['乾', '坤'], 'relationship': '定位', 'meaning': 'establish position (heaven-earth axis)'},
            {'pair': ['艮', '兌'], 'relationship': '通氣', 'meaning': 'exchange energy (mountain-lake)'},
            {'pair': ['震', '巽'], 'relationship': '相薄', 'meaning': 'interact closely (thunder-wind)'},
            {'pair': ['坎', '離'], 'relationship': '不相射', 'meaning': 'do not oppose (water-fire balance)'},
        ],
        'fuxi_sequence': {
            'description': '先天八卦 (Fu Xi / Before Heaven arrangement)',
            'arrangement': [
                {'position': 'South', 'trigram': '乾', 'binary': '111'},
                {'position': 'North', 'trigram': '坤', 'binary': '000'},
                {'position': 'East', 'trigram': '離', 'binary': '101'},
                {'position': 'West', 'trigram': '坎', 'binary': '010'},
                {'position': 'Northeast', 'trigram': '震', 'binary': '100'},
                {'position': 'Southwest', 'trigram': '巽', 'binary': '011'},
                {'position': 'Southeast', 'trigram': '兌', 'binary': '110'},
                {'position': 'Northwest', 'trigram': '艮', 'binary': '001'},
            ]
        },
        'king_wen_sequence': {
            'description': '後天八卦 (King Wen / After Heaven arrangement)',
            'arrangement': [
                {'position': 'South', 'trigram': '離', 'binary': '101'},
                {'position': 'North', 'trigram': '坎', 'binary': '010'},
                {'position': 'East', 'trigram': '震', 'binary': '100'},
                {'position': 'West', 'trigram': '兌', 'binary': '110'},
                {'position': 'Northeast', 'trigram': '艮', 'binary': '001'},
                {'position': 'Southwest', 'trigram': '坤', 'binary': '000'},
                {'position': 'Southeast', 'trigram': '巽', 'binary': '011'},
                {'position': 'Northwest', 'trigram': '乾', 'binary': '111'},
            ]
        }
    }
    return relationships

def create_analysis_categories():
    """Create categories for analysis"""
    categories = {
        'nature_elements': {
            'description': 'Natural phenomena associated with each trigram',
            'mapping': {
                '乾': '天 (Heaven)',
                '坤': '地 (Earth)',
                '震': '雷 (Thunder)',
                '巽': '風 (Wind)',
                '坎': '水 (Water)',
                '離': '火 (Fire)',
                '艮': '山 (Mountain)',
                '兌': '澤 (Lake/Marsh)',
            }
        },
        'family_structure': {
            'description': 'Family roles - reveals generative principle',
            'mapping': {
                '乾': {'role': '父', 'generation': 'parent', 'gender': 'male'},
                '坤': {'role': '母', 'generation': 'parent', 'gender': 'female'},
                '震': {'role': '長男', 'generation': 'child', 'gender': 'male', 'birth_order': 1},
                '巽': {'role': '長女', 'generation': 'child', 'gender': 'female', 'birth_order': 1},
                '坎': {'role': '中男', 'generation': 'child', 'gender': 'male', 'birth_order': 2},
                '離': {'role': '中女', 'generation': 'child', 'gender': 'female', 'birth_order': 2},
                '艮': {'role': '少男', 'generation': 'child', 'gender': 'male', 'birth_order': 3},
                '兌': {'role': '少女', 'generation': 'child', 'gender': 'female', 'birth_order': 3},
            },
            'generative_principle': 'Children are formed by one parent line entering the other: 震 = yang entering yin at bottom (first attempt), etc.'
        },
        'attributes': {
            'description': 'Core qualities/actions',
            'mapping': {
                '乾': {'attribute': '健', 'meaning': 'creative strength'},
                '坤': {'attribute': '順', 'meaning': 'receptive yielding'},
                '震': {'attribute': '動', 'meaning': 'movement, action'},
                '巽': {'attribute': '入', 'meaning': 'penetration, gentle influence'},
                '坎': {'attribute': '陷', 'meaning': 'danger, depth'},
                '離': {'attribute': '麗', 'meaning': 'clarity, attachment'},
                '艮': {'attribute': '止', 'meaning': 'stillness, stopping'},
                '兌': {'attribute': '說', 'meaning': 'joy, expression'},
            }
        },
        'body_parts': {
            'description': 'Somatic correspondences',
            'mapping': {
                '乾': '首 (head)',
                '坤': '腹 (belly)',
                '震': '足 (foot)',
                '巽': '股 (thigh)',
                '坎': '耳 (ear)',
                '離': '目 (eye)',
                '艮': '手 (hand)',
                '兌': '口 (mouth)',
            }
        },
        'animals': {
            'description': 'Primary animal associations',
            'mapping': {
                '乾': '馬 (horse)',
                '坤': '牛 (ox)',
                '震': '龍 (dragon)',
                '巽': '雞 (chicken)',
                '坎': '豕 (pig)',
                '離': '雉 (pheasant)',
                '艮': '狗 (dog)',
                '兌': '羊 (sheep)',
            }
        },
        'directions_kingwen': {
            'description': '後天八卦方位 (King Wen directions)',
            'mapping': {
                '震': '東 (East)',
                '巽': '東南 (Southeast)',
                '離': '南 (South)',
                '坤': '西南 (Southwest)',
                '兌': '西 (West)',
                '乾': '西北 (Northwest)',
                '坎': '北 (North)',
                '艮': '東北 (Northeast)',
            }
        }
    }
    return categories

def main():
    base_dir = Path('/Users/arsenelee/github/iching')
    output_dir = base_dir / 'data/structure'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate mappings
    print("Extracting 說卦傳 trigram mappings...")

    trigram_mappings = create_trigram_mappings()
    relationships = create_relationship_matrix()
    categories = create_analysis_categories()

    # Save comprehensive trigram data
    trigram_file = output_dir / 'shuogua_trigram_mappings.json'
    with open(trigram_file, 'w', encoding='utf-8') as f:
        json.dump({
            'title': '說卦傳八卦象徵對照表',
            'english_title': 'Shuo Gua Zhuan Trigram Symbol Mappings',
            'source': '說卦傳 (Discussion of Trigrams)',
            'description': 'Comprehensive trigram-to-symbol mappings extracted from the Shuo Gua appendix of the I Ching',
            'trigrams': trigram_mappings,
            'total_trigrams': len(trigram_mappings),
        }, f, ensure_ascii=False, indent=2)
    print(f"  Saved trigram mappings to {trigram_file}")

    # Save relationships
    relationship_file = output_dir / 'trigram_relationships.json'
    with open(relationship_file, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, ensure_ascii=False, indent=2)
    print(f"  Saved trigram relationships to {relationship_file}")

    # Save analysis categories
    categories_file = output_dir / 'analysis_categories.json'
    with open(categories_file, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print(f"  Saved analysis categories to {categories_file}")

    # Statistics
    total_symbols = sum(len(t['all_symbols']) for t in trigram_mappings.values())
    print(f"\n=== Statistics ===")
    print(f"Total trigrams: {len(trigram_mappings)}")
    print(f"Total symbol associations: {total_symbols}")
    print(f"Symbols per trigram:")
    for name, data in trigram_mappings.items():
        print(f"  {name} ({data['english']}): {len(data['all_symbols'])} symbols")

if __name__ == '__main__':
    main()
