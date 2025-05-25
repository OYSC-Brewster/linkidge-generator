# tests/test_preview.py
from src.preview import text_preview

def test_text_preview_contains_status_and_grid():
    class DummyPuzzle:
        grid = [['a','b','c'],['d','e','f'],['g','h','i']]
        scores = {k:1.0 for k in ['row1','row2','row3','col1','col2','col3']}
    txt = text_preview(DummyPuzzle)
    assert 'Puzzle Grid:' in txt
    assert 'Status:' in txt
    # Check all rows appear
    assert 'a | b | c' in txt
    assert 'd | e | f' in txt
    assert 'g | h | i' in txt
