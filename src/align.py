"""
A5 - Align Chinese and English paragraphs using LaBSE embeddings.

Why this file exists: the scraper saves a WHOLE article's Chinese text and
a whole article's English text as two separate blobs. They're not lined up
sentence-by-sentence or paragraph-by-paragraph yet - paragraph 3 in Chinese
might correspond to paragraph 5 in English, or not exist in English at all.

This script splits both sides into paragraphs, turns each paragraph into a
vector (an "embedding") using a model called LaBSE that understands meaning
across languages, then matches each Chinese paragraph to whichever English
paragraph is closest in meaning. Each match gets a similarity score from 0
to 1 - higher means more confident the pairing is correct.

Run this AFTER you've scraped data with src/main.py, not instead of it.
Run with:  python -m src.align
"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"

import json
import numpy as np
from sentence_transformers import SentenceTransformer

from . import config

ALIGNED_DIR = config.BASE_DIR / "data" / "aligned"
ALIGNED_DIR.mkdir(parents=True, exist_ok=True)

# Only keep matches at or above this similarity score. Pairs scoring below
# this are likely bad matches (unrelated paragraphs) and get dropped rather
# than polluting your dataset with garbage.
MIN_QUALITY_SCORE = 0.5


def split_paragraphs(text):
    """Split a blob of text into paragraphs, dropping empty/tiny fragments."""
    parts = [p.strip() for p in text.split("\n")]
    return [p for p in parts if len(p) > 10]


def cosine_similarity_matrix(a, b):
    """
    Compute cosine similarity between every row in a and every row in b.
    Returns a matrix where result[i][j] = similarity between a[i] and b[j].
    """
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return a_norm @ b_norm.T


def align_record(model, record):
    """
    Given one scraped record (one article's full zh_text and en_text),
    return a list of aligned paragraph pairs with quality scores.
    """
    zh_paragraphs = split_paragraphs(record["zh_text"])
    en_paragraphs = split_paragraphs(record["en_text"])

    if not zh_paragraphs or not en_paragraphs:
        return []

    zh_embeddings = model.encode(zh_paragraphs)
    en_embeddings = model.encode(en_paragraphs)
    sim_matrix = cosine_similarity_matrix(zh_embeddings, en_embeddings)

    aligned = []
    for i, zh_para in enumerate(zh_paragraphs):
        best_j = int(np.argmax(sim_matrix[i]))
        score = float(sim_matrix[i][best_j])
        if score >= MIN_QUALITY_SCORE:
            aligned.append({
                "zh_text": zh_para,
                "en_text": en_paragraphs[best_j],
                "quality_score": round(score, 4),
                "source": record["source"],
                "url": record["url"],
            })
    return aligned


def main():
    print("Loading LaBSE model (first run downloads it, may take a few minutes)...")
    model = SentenceTransformer("sentence-transformers/LaBSE")

    raw_files = list(config.RAW_DIR.glob("*.jsonl"))
    if not raw_files:
        print("No scraped data found in data/raw/. Run 'python -m src.main' first.")
        return

    total_aligned = 0

    for raw_file in raw_files:
        source_name = raw_file.stem
        out_path = ALIGNED_DIR / f"{source_name}.jsonl"
        source_aligned = 0

        with open(raw_file, "r", encoding="utf-8") as f_in, \
             open(out_path, "w", encoding="utf-8") as f_out:
            for line in f_in:
                record = json.loads(line)
                pairs = align_record(model, record)
                for pair in pairs:
                    f_out.write(json.dumps(pair, ensure_ascii=False) + "\n")
                source_aligned += len(pairs)

        print(f"{source_name}: {source_aligned} aligned paragraph pairs -> {out_path}")
        total_aligned += source_aligned

    print(f"\nTotal aligned pairs across all sources: {total_aligned}")


if __name__ == "__main__":
    main()