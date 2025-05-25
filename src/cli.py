# src/cli.py

import json
import pathlib
import argparse

from config import DRAFTS_DIR, MAX_ATTEMPTS
from .loader import get_graph, get_allowed_words, get_lemma_freq
from .generator import make_3x3_puzzle
from .preview import text_preview, html_preview


def write_puzzle_files(puzzle, date: str, index: int, out_dir: pathlib.Path):
    """
    Dump JSON, plain text, and HTML preview files for one puzzle.
    """
    base = out_dir / f"{date}_{index:02d}"
    # Prepare JSON data
    data = {
        "date": date,
        "grid": puzzle.grid,
        "anchors": puzzle.anchors,
        "bridges": puzzle.bridges,
        "scores": puzzle.scores,
        "review_status": "pending"
    }
    # Write JSON
    with open(f"{base}.json", "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=2)
    # Write plain-text preview
    with open(f"{base}.txt", "w", encoding="utf-8") as tf:
        tf.write(text_preview(puzzle))
    # Write HTML preview
    with open(f"{base}.html", "w", encoding="utf-8") as hf:
        hf.write(html_preview(puzzle))


def main():
    parser = argparse.ArgumentParser(description="Generate Linkidge puzzles")
    parser.add_argument("--date",    required=True, help="Puzzle date (YYYY-MM-DD)")
    parser.add_argument("--count",   type=int, default=1, help="Number of puzzles to generate")
    parser.add_argument("--out-dir", default=str(DRAFTS_DIR), help="Output directory for drafts")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    graph = get_graph(pruned=True)
    allowed_words = get_allowed_words()
    lemma_freq = get_lemma_freq()
    metadata = {
        "allowed_words": allowed_words,
        "lemma_freq": lemma_freq,
        "max_attempts": MAX_ATTEMPTS
    }

    # Generate puzzles
    for i in range(1, args.count + 1):
        puzzle = make_3x3_puzzle(graph, metadata)
        write_puzzle_files(puzzle, args.date, i, out_dir)
        print(f"→ Wrote draft #{i}")

if __name__ == "__main__":
    main()
