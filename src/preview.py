# src/preview.py

import html as _html
from typing import List
from config import SEMANTIC_THRESHOLD
from .generator import Puzzle


def preview_status(puzzle: Puzzle) -> str:
    """
    Return 'normal' if all chains meet the threshold, otherwise list below-threshold chains.
    """
    low = [k for k, v in puzzle.scores.items() if v < SEMANTIC_THRESHOLD]
    return "normal" if not low else f"below-threshold: {low}"


def text_preview(puzzle: Puzzle) -> str:
    """
    Return a plain-text representation of the puzzle grid and its scores.
    """
    lines: List[str] = []
    lines.append("Puzzle Grid:")
    for row in puzzle.grid:
        lines.append(" | ".join(row))
    lines.append("")
    lines.append("Scores:")
    for key, score in puzzle.scores.items():
        lines.append(f"{key}: {score:.2f}")
    lines.append("")
    lines.append(f"Status: {preview_status(puzzle)}")
    return "\n".join(lines)


def html_preview(puzzle: Puzzle) -> str:
    """
    Return a minimal HTML snippet (table plus scores) for quick inspection.
    """
    rows_html = []
    for row in puzzle.grid:
        cells = "".join(f"<td>{_html.escape(cell)}</td>" for cell in row)
        rows_html.append(f"<tr>{cells}</tr>")
    table_html = (
        '<table border="1" cellpadding="5" cellspacing="0">'
        + ''.join(rows_html)
        + '</table>'
    )
    scores_items = ''.join(f"<li>{_html.escape(k)}: {v:.2f}</li>" for k, v in puzzle.scores.items())
    scores_html = f"<h3>Scores</h3><ul>{scores_items}</ul>"
    status_html = f"<p>Status: {preview_status(puzzle)}</p>"
    return table_html + scores_html + status_html