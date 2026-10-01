"""
A6 - Clean, dedupe, and merge into one final corpus file.

This script fixes two real problems:

1. DUPLICATES: every time you run src/main.py, it APPENDS to data/raw/*.jsonl
   instead of replacing it - so re-running the scraper on the same source
   creates duplicate entries. This script removes those duplicates by URL,
   keeping only the first copy of each.

2. INCONSISTENT CHINESE: some websites use Traditional Chinese characters
   (e.g. 臺灣), others use Simplified (e.g. 台湾) - same language, different
   character sets. Mixing both in one training dataset hurts a model's
   consistency. This script converts everything to Simplified Chinese.

Run this in two stages:
    python -m src.clean --dedupe-raw     (run this FIRST)
    python -m src.align                  (re-run alignment on the clean raw data)
    python -m src.clean --finalize       (dedupe + normalize the aligned pairs, merge into one file)
"""
import sys
import json
import opencc

from . import config

CORPUS_DIR = config.BASE_DIR / "data" / "corpus"
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

# t2s.json = Traditional-to-Simplified conversion config, built into opencc
converter = opencc.OpenCC("t2s")


def dedupe_raw():
    """
    Remove duplicate records from every file in data/raw/, keeping only the
    first occurrence of each URL. Overwrites each file with the clean version.
    """
    raw_files = list(config.RAW_DIR.glob("*.jsonl"))
    if not raw_files:
        print("No files found in data/raw/. Nothing to dedupe.")
        return

    for raw_file in raw_files:
        seen_urls = set()
        clean_records = []
        total = 0

        with open(raw_file, "r", encoding="utf-8") as f:
            for line in f:
                total += 1
                record = json.loads(line)
                if record["url"] not in seen_urls:
                    seen_urls.add(record["url"])
                    clean_records.append(record)

        removed = total - len(clean_records)
        with open(raw_file, "w", encoding="utf-8") as f:
            for record in clean_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"{raw_file.name}: {total} records -> {len(clean_records)} unique "
              f"({removed} duplicates removed)")


def finalize():
    """
    Take every file in data/aligned/, normalize Chinese text to Simplified,
    drop exact-duplicate pairs, and merge everything into one final corpus
    file: data/corpus/final_corpus.jsonl
    """
    aligned_dir = config.BASE_DIR / "data" / "aligned"
    aligned_files = list(aligned_dir.glob("*.jsonl"))
    if not aligned_files:
        print("No files found in data/aligned/. Run src/align.py first.")
        return

    seen_pairs = set()
    final_path = CORPUS_DIR / "final_corpus.jsonl"
    total_in, total_out = 0, 0

    with open(final_path, "w", encoding="utf-8") as f_out:
        for aligned_file in aligned_files:
            with open(aligned_file, "r", encoding="utf-8") as f_in:
                for line in f_in:
                    total_in += 1
                    record = json.loads(line)

                    # Normalize Traditional -> Simplified for consistency
                    record["zh_text"] = converter.convert(record["zh_text"])

                    # Dedupe on the actual text content, not just the URL -
                    # catches cases where two different pages produced the
                    # exact same sentence.
                    key = (record["zh_text"], record["en_text"])
                    if key in seen_pairs:
                        continue
                    seen_pairs.add(key)

                    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    total_out += 1

    print(f"Merged {len(aligned_files)} source file(s): "
          f"{total_in} pairs in -> {total_out} unique pairs out")
    print(f"Final corpus written to: {final_path}")


if __name__ == "__main__":
    if "--dedupe-raw" in sys.argv:
        dedupe_raw()
    elif "--finalize" in sys.argv:
        finalize()
    else:
        print("Usage:")
        print("  python -m src.clean --dedupe-raw   (run first, cleans data/raw/)")
        print("  python -m src.clean --finalize     (run after re-aligning, builds final corpus)")