# tests/test_loader.py
import pytest
from src.loader import get_graph, get_allowed_words, get_lemma_freq

def test_loader_bundle():
    graph = get_graph(pruned=True)
    assert hasattr(graph, 'nodes') and hasattr(graph, 'edges')
    aw = get_allowed_words()
    assert isinstance(aw, set) and len(aw) > 0
    lf = get_lemma_freq()
    assert isinstance(lf, dict) and all(isinstance(v, int) for v in lf.values())


# tests/test_utils.py
import networkx as nx
import pytest
from src.utils import compute_semantic_score

def test_compute_semantic_score_simple_chain():
    # Build a tiny graph: a-b-c chain
    G = nx.Graph()
    G.add_edge('a', 'b', w_composite=1, source='wordnet')
    G.add_edge('b', 'c', w_composite=1, source='wordnet')
    score = compute_semantic_score(['a', 'b', 'c'], G)
    # Each edge contributes 1.0; two edges + no mix penalty = 2.0
    assert pytest.approx(score, rel=1e-3) == 2.0