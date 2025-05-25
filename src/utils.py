# src/utils.py

from typing import List, Tuple, Dict, Set
import networkx as nx
from nltk.corpus import wordnet as wn
from functools import lru_cache


def compute_expandability_score(
    node: str,
    deg_map: Dict[str, float],
    senses_map: Dict[str, int],
    lemma_freq: Dict[str, int]
) -> float:
    """
    Compute pivot expandability score based on precomputed maps:
      - normalized degree centrality (50%)
      - normalized WordNet synset count (30%)
      - normalized lemma frequency (20%)
    """
    # Normalize degree centrality
    max_deg = max(deg_map.values()) if deg_map else 1.0
    norm_deg = deg_map.get(node, 0.0) / max_deg

    # Normalize synset count
    max_syn = max(senses_map.values()) if senses_map else 1
    norm_syn = senses_map.get(node, 0) / max_syn

    # Normalize frequency
    max_freq = max(lemma_freq.values()) if lemma_freq else 1
    norm_freq = lemma_freq.get(node, 0) / max_freq

    return norm_deg * 0.5 + norm_syn * 0.3 + norm_freq * 0.2


def edge_weight(u: str, v: str, graph: nx.Graph) -> Tuple[float, str]:
    """
    Return (weight, kind) for edge (u,v): infinite if no edge.
    """
    if not graph.has_edge(u, v):
        return float('inf'), None
    data = graph.edges[u, v]
    w = data.get('w_composite', 1)
    kind = 'semantic' if data.get('source') == 'wordnet' else 'concept'
    return w, kind


def compute_semantic_score(chain: List[str], graph: nx.Graph) -> float:
    """
    Compute semantic cohesion score for a word chain.
    """
    total = 0.0
    kinds: Set[str] = set()
    for u, v in zip(chain, chain[1:]):
        w, kind = edge_weight(u, v, graph)
        if w == float('inf'):
            return 0.0
        mult = 1.0 if kind == 'semantic' else 0.7
        total += mult * (1.0 / (w or 1e-6))
        kinds.add(kind)
    if len(kinds) > 1:
        total += 0.1 * (len(kinds) - 1)
    return total


def get_two_hop_bridges(u: str, v: str, graph: nx.Graph) -> List[Tuple[str, float, str, bool]]:
    """
    Find two-hop bridge words between u and v (common neighbors).
    Returns list of (bridge, total_weight, kind, low_duplicate_flag).
    """
    neighbors_u = set(graph.neighbors(u))
    neighbors_v = set(graph.neighbors(v))
    common = neighbors_u & neighbors_v
    bridges = []
    for b in common:
        w1, kind1 = edge_weight(u, b, graph)
        w2, kind2 = edge_weight(b, v, graph)
        weight = w1 + w2
        kind = 'semantic' if kind1 == kind2 == 'semantic' else 'concept'
        low_dup = False
        bridges.append((b, weight, kind, low_dup))
    bridges.sort(key=lambda x: x[1])
    return bridges


def get_single_hops(u: str, v: str, graph: nx.Graph, familiar: Set[str]) -> List[Tuple[str, float]]:
    """
    Single-hop fallback: common neighbors of u and v filtered by familiar set.
    Returns list of (bridge, total_weight).
    """
    if u not in graph or v not in graph:
        return []
    neighbors_u = set(graph.neighbors(u))
    neighbors_v = set(graph.neighbors(v))
    common = neighbors_u & neighbors_v
    hops = []
    for b in common:
        if b not in familiar:
            continue
        w1, _ = edge_weight(u, b, graph)
        w2, _ = edge_weight(b, v, graph)
        hops.append((b, w1 + w2))
    hops.sort(key=lambda x: x[1])
    return hops
