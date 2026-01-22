#!/usr/bin/env python3
"""
Generate Text Embeddings for I Ching Hexagrams
===============================================
Creates vector embeddings for hexagram texts to enable:
- Semantic similarity search
- Clustering analysis
- ML model training

Uses character n-gram based embeddings (no external dependencies).
"""

import json
import sqlite3
import math
from pathlib import Path
from collections import Counter
from datetime import datetime


class SimpleEmbeddingGenerator:
    """Generate embeddings for I Ching texts using character n-grams."""

    def __init__(self, db_path: str = "data/iching.db", ngram_range: tuple = (1, 3)):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.ngram_range = ngram_range
        self.vocabulary = {}
        self.idf = {}

    def get_hexagram_texts(self) -> dict:
        """Get all hexagram texts from database."""
        cursor = self.conn.cursor()

        # Get hexagram info
        cursor.execute("""
            SELECT h.king_wen_number, h.name
            FROM hexagrams h
            ORDER BY h.king_wen_number
        """)
        hexagrams = {row['king_wen_number']: {'name': row['name']} for row in cursor.fetchall()}

        # Get hexagram texts (tuan, xiang)
        cursor.execute("""
            SELECT hexagram_id, text_type, content
            FROM hexagram_texts
        """)
        for row in cursor.fetchall():
            hex_id = row['hexagram_id']
            if hex_id in hexagrams:
                hexagrams[hex_id][row['text_type']] = row['content']

        # Get line texts
        cursor.execute("""
            SELECT hexagram_id, position, yaoci, xiaoxiang
            FROM lines
            ORDER BY hexagram_id, position
        """)
        for row in cursor.fetchall():
            hex_id = row['hexagram_id']
            if hex_id in hexagrams:
                if 'lines' not in hexagrams[hex_id]:
                    hexagrams[hex_id]['lines'] = []
                hexagrams[hex_id]['lines'].append({
                    'position': row['position'],
                    'yaoci': row['yaoci'],
                    'xiaoxiang': row['xiaoxiang']
                })

        return hexagrams

    def create_combined_text(self, hexagram: dict) -> str:
        """Combine all hexagram texts into single string for embedding."""
        parts = []

        if hexagram.get('name'):
            parts.append(hexagram['name'])
        if hexagram.get('guaci'):
            parts.append(hexagram['guaci'])
        if hexagram.get('tuan'):
            parts.append(hexagram['tuan'])
        if hexagram.get('daxiang'):
            parts.append(hexagram['daxiang'])
        if hexagram.get('lines'):
            for line in hexagram['lines']:
                if line.get('yaoci'):
                    parts.append(line['yaoci'])

        return ' '.join(parts)

    def extract_ngrams(self, text: str) -> list:
        """Extract character n-grams from text."""
        ngrams = []
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            for i in range(len(text) - n + 1):
                ngrams.append(text[i:i+n])
        return ngrams

    def build_vocabulary(self, texts: list):
        """Build vocabulary from all texts."""
        # Count document frequency
        doc_freq = Counter()
        for text in texts:
            ngrams = set(self.extract_ngrams(text))
            for ng in ngrams:
                doc_freq[ng] += 1

        # Filter by minimum document frequency and build vocabulary
        min_df = 2
        self.vocabulary = {}
        idx = 0
        for ng, freq in doc_freq.items():
            if freq >= min_df:
                self.vocabulary[ng] = idx
                # Calculate IDF
                self.idf[ng] = math.log(len(texts) / (1 + freq))
                idx += 1

        print(f"Vocabulary size: {len(self.vocabulary)} n-grams")

    def text_to_vector(self, text: str) -> list:
        """Convert text to TF-IDF vector."""
        ngrams = self.extract_ngrams(text)
        tf = Counter(ngrams)

        # Create vector
        vector = [0.0] * len(self.vocabulary)
        for ng, count in tf.items():
            if ng in self.vocabulary:
                idx = self.vocabulary[ng]
                # TF-IDF weighting
                vector[idx] = count * self.idf.get(ng, 0)

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def cosine_similarity(self, v1: list, v2: list) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        return dot  # Already normalized

    def generate_embeddings(self) -> dict:
        """Generate embeddings for all hexagrams."""
        hexagrams = self.get_hexagram_texts()

        # Create combined texts
        texts = []
        hex_ids = []
        for hex_id in sorted(hexagrams.keys()):
            combined = self.create_combined_text(hexagrams[hex_id])
            texts.append(combined)
            hex_ids.append(hex_id)

        print(f"Generating embeddings for {len(texts)} hexagrams...")

        # Build vocabulary
        self.build_vocabulary(texts)

        # Generate embeddings
        embeddings = [self.text_to_vector(text) for text in texts]

        # Create result dictionary
        result = {
            "method": "tfidf_ngram",
            "ngram_range": list(self.ngram_range),
            "dimension": len(self.vocabulary),
            "generated": datetime.now().isoformat(),
            "hexagrams": {}
        }

        for i, hex_id in enumerate(hex_ids):
            result["hexagrams"][hex_id] = {
                "name": hexagrams[hex_id].get('name', ''),
                "text_length": len(texts[i]),
                "embedding": embeddings[i]
            }

        return result

    def compute_all_similarities(self, embeddings: dict) -> dict:
        """Compute similarity between all hexagram pairs."""
        hex_ids = sorted(embeddings["hexagrams"].keys())

        pairs = []
        for i, id_a in enumerate(hex_ids):
            vec_a = embeddings["hexagrams"][id_a]["embedding"]
            for j, id_b in enumerate(hex_ids):
                if i < j:
                    vec_b = embeddings["hexagrams"][id_b]["embedding"]
                    sim = self.cosine_similarity(vec_a, vec_b)
                    pairs.append({
                        "hex_a": id_a,
                        "name_a": embeddings["hexagrams"][id_a]["name"],
                        "hex_b": id_b,
                        "name_b": embeddings["hexagrams"][id_b]["name"],
                        "similarity": round(sim, 6)
                    })

        # Sort by similarity
        pairs.sort(key=lambda x: x["similarity"], reverse=True)

        # Calculate statistics
        sims = [p["similarity"] for p in pairs]
        avg = sum(sims) / len(sims)
        variance = sum((s - avg) ** 2 for s in sims) / len(sims)
        std = math.sqrt(variance)

        return {
            "total_pairs": len(pairs),
            "most_similar": pairs[:10],
            "least_similar": pairs[-10:],
            "average_similarity": round(avg, 6),
            "std_similarity": round(std, 6),
            "max_similarity": round(max(sims), 6),
            "min_similarity": round(min(sims), 6)
        }

    def save_embeddings(self, embeddings: dict, output_path: str):
        """Save embeddings to JSON (compact format without full vectors)."""
        # Save compact version (without embedding vectors which are large)
        compact = {
            "method": embeddings["method"],
            "ngram_range": embeddings["ngram_range"],
            "dimension": embeddings["dimension"],
            "generated": embeddings["generated"],
            "hexagram_count": len(embeddings["hexagrams"]),
            "hexagrams": {}
        }

        for hex_id, data in embeddings["hexagrams"].items():
            compact["hexagrams"][str(hex_id)] = {
                "name": data["name"],
                "text_length": data["text_length"],
                "vector_norm": round(sum(v*v for v in data["embedding"]) ** 0.5, 6)
            }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(compact, f, ensure_ascii=False, indent=2)

        print(f"Saved embedding metadata to {output_path}")


def main():
    """Generate embeddings and analysis."""
    print("=" * 60)
    print("I Ching Text Embedding Generation")
    print("=" * 60)

    generator = SimpleEmbeddingGenerator()

    # Generate embeddings
    embeddings = generator.generate_embeddings()

    # Save embedding metadata
    output_dir = Path("data/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    generator.save_embeddings(embeddings, output_dir / "hexagram_embeddings.json")

    # Compute similarities
    print("\nComputing all pairwise similarities...")
    similarity_analysis = generator.compute_all_similarities(embeddings)

    # Save similarity analysis
    with open(output_dir / "embedding_similarity.json", 'w', encoding='utf-8') as f:
        json.dump(similarity_analysis, f, ensure_ascii=False, indent=2)

    # Print results
    print("\n" + "=" * 60)
    print("MOST SIMILAR HEXAGRAM PAIRS (by text embedding)")
    print("=" * 60)
    for pair in similarity_analysis["most_similar"][:5]:
        print(f"  {pair['name_a']} (#{pair['hex_a']}) <-> {pair['name_b']} (#{pair['hex_b']}): {pair['similarity']:.4f}")

    print("\n" + "=" * 60)
    print("LEAST SIMILAR HEXAGRAM PAIRS")
    print("=" * 60)
    for pair in similarity_analysis["least_similar"][:5]:
        print(f"  {pair['name_a']} (#{pair['hex_a']}) <-> {pair['name_b']} (#{pair['hex_b']}): {pair['similarity']:.4f}")

    print(f"\n{'='*60}")
    print("STATISTICS")
    print("=" * 60)
    print(f"  Total pairs analyzed: {similarity_analysis['total_pairs']}")
    print(f"  Average similarity: {similarity_analysis['average_similarity']:.4f}")
    print(f"  Std deviation: {similarity_analysis['std_similarity']:.4f}")
    print(f"  Max similarity: {similarity_analysis['max_similarity']:.4f}")
    print(f"  Min similarity: {similarity_analysis['min_similarity']:.4f}")

    print("\n" + "=" * 60)
    print("OUTPUT FILES")
    print("=" * 60)
    print(f"  Embeddings: data/analysis/hexagram_embeddings.json")
    print(f"  Similarity: data/analysis/embedding_similarity.json")

    # Close database
    generator.conn.close()

    print("\nEmbedding generation complete!")


if __name__ == "__main__":
    main()
