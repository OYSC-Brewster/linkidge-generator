# tests/test_generator.py
import pytest
import config
import networkx as nx
from src.generator import make_3x3_puzzle, Puzzle

def test_generator_raises_on_zero_attempts(monkeypatch):
    # Force MAX_ATTEMPTS to 0
    import config
    monkeypatch.setattr(config, 'MAX_ATTEMPTS', 0)
    G = nx.Graph()
    metadata = {'allowed_words': set(), 'lemma_freq': {}, 'max_attempts': 0}
    with pytest.raises(ValueError):
        make_3x3_puzzle(G, metadata)


def test_generator_returns_puzzle(monkeypatch):
    # Use a trivial graph where every node is connected
    G = nx.complete_graph(['x','y','z','u','v','w','p','q','r'])
    # Add w_composite and source attributes
    for u,v in G.edges():
        G.edges[u,v]['w_composite'] = 1
        G.edges[u,v]['source'] = 'wordnet'
    allowed = set(G.nodes())
    lemma_freq = {n:1 for n in allowed}
    monkeypatch.setattr(config, 'MAX_ATTEMPTS', 1)
    puzzle = make_3x3_puzzle(G, {'allowed_words':allowed, 'lemma_freq':lemma_freq})
    assert isinstance(puzzle, Puzzle)
    assert len(puzzle.grid) == 3 and len(puzzle.grid[0]) == 3