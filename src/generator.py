# src/generator.py

import random
from typing import List, Dict, Tuple
import networkx as nx
from nltk.corpus import wordnet as wn
from itertools import combinations
from functools import lru_cache

from config import (
    SEMANTIC_THRESHOLD,
    MAX_ATTEMPTS,
    FREQ_PERCENTILE,
    LENGTH_MAX,
    ALLOWED_POS
)
from .utils import (
    compute_expandability_score,
    compute_semantic_score,
    get_two_hop_bridges,
    get_single_hops,
)


class Puzzle:
    """
    Container for a 3×3 Linkidge puzzle.

    Attributes:
      grid: List[List[str]]      # The 3×3 word grid
      anchors: List[str]         # Four corner anchors [A, C, G, I]
      bridges: List[str]         # Five connectors [B, D, E, F, H]
      scores: Dict[str, float]   # row1, row2, row3, col1, col2, col3
    """
    def __init__(self, grid: List[List[str]], anchors: List[str], bridges: List[str], scores: Dict[str, float]):
        self.grid = grid
        self.anchors = anchors
        self.bridges = bridges
        self.scores = scores


def make_3x3_puzzle(graph: nx.Graph, metadata: dict) -> Puzzle:
    """
    Generate a 3×3 Linkidge puzzle with performance optimizations and quality checks.
    """
    # 1. Initial data and metadata
    allowed = set(metadata.get('allowed_words', graph.nodes()))
    lemma_freq = metadata.get('lemma_freq', {})

    # 2. Cache WordNet synsets for allowed words
    synsets_map: Dict[str, List] = {w: wn.synsets(w) for w in allowed}

    @lru_cache(maxsize=None)
    def primary_pos(word: str) -> Tuple[str, ...]:
        return tuple({s.pos() for s in synsets_map.get(word, [])})

    @lru_cache(maxsize=None)
    def is_near_synonym(u: str, v: str) -> bool:
        for su in synsets_map.get(u, []):
            for sv in synsets_map.get(v, []):
                if (su.wup_similarity(sv) or 0.0) >= 0.95:
                    return True
        return False

    # 3. Precompute centrality and synset counts
    deg_map = nx.degree_centrality(graph)
    senses_map = {w: len(synsets_map.get(w, [])) for w in allowed}

    # 4. Frequency cutoff
    freqs = sorted(lemma_freq.get(w, 0) for w in allowed)
    cutoff_idx = int(len(freqs) * FREQ_PERCENTILE)
    freq_min_val = freqs[cutoff_idx] if freqs else 0

    # 5. Valid connectors
    good_connectors = {
        w for w in allowed
        if lemma_freq.get(w, 0) >= freq_min_val
        and (not LENGTH_MAX or len(w) <= LENGTH_MAX)
        and any(pos in ALLOWED_POS for pos in primary_pos(w))
    }

    # 6. Score and select anchors
    scored = [
        (n, compute_expandability_score(n, deg_map, senses_map, lemma_freq))
        for n in allowed
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top_k = min(100, len(scored))
    top_nodes = [n for n, _ in scored[:top_k]]
    score_map = {n: sc for n, sc in scored}

    # 7. Precompute connector pools
    connector_pool: Dict[Tuple[str, str], List[str]] = {}
    for u, v in combinations(top_nodes, 2):
        two = [b for b, _, _, _ in get_two_hop_bridges(u, v, graph) if not _ and b in good_connectors]
        one = [b for b, _ in get_single_hops(u, v, graph, allowed) if b in good_connectors]
        direct = [b for b in set(graph.neighbors(u)).intersection(graph.neighbors(v)) if b in good_connectors]
        connector_pool[(u, v)] = two or one or direct

    # 8. Attempt loop
    for attempt in range(MAX_ATTEMPTS):
        relax_syn = attempt >= MAX_ATTEMPTS * 0.8
        relax_th = attempt >= MAX_ATTEMPTS * 0.9

        # a. Pick corner anchors
        anchors = random.sample(top_nodes, 4)
        anchors.sort(key=lambda x: score_map.get(x, 0), reverse=True)
        A, C, G, I = anchors

        # b. Side connectors
        B_choices = connector_pool.get((A, C), [])
        D_choices = connector_pool.get((A, G), [])
        F_choices = connector_pool.get((C, I), [])
        H_choices = connector_pool.get((G, I), [])
        if not all((B_choices, D_choices, F_choices, H_choices)):
            continue
        B = random.choice(B_choices)
        D = random.choice(D_choices)
        F = random.choice(F_choices)
        H = random.choice(H_choices)

        # c. Center connector
        E_choices = connector_pool.get((D, F)) or connector_pool.get((F, D))
        if not E_choices:
            two = [b for b, _, _, _ in get_two_hop_bridges(D, F, graph) if b in good_connectors]
            one = [b for b, _ in get_single_hops(D, F, graph, allowed) if b in good_connectors]
            direct = [b for b in set(graph.neighbors(D)).intersection(graph.neighbors(F)) if b in good_connectors]
            E_choices = two or one or direct
        if not E_choices:
            continue
        E = random.choice(E_choices)

        # d. Build grid & uniqueness
        grid = [[A, B, C], [D, E, F], [G, H, I]]
        flat = [A, B, C, D, E, F, G, H, I]
        if len(set(flat)) < 9:
            continue

        # e. Synonym ban
        adjacent_pairs = [
            (A, B), (B, C), (D, E), (E, F), (G, H), (H, I),
            (A, D), (D, G), (B, E), (E, H), (C, F), (F, I)
        ]
        if not relax_syn and any(is_near_synonym(x, y) for x, y in adjacent_pairs):
            continue

        # f. Score rows & cols
        chains = {
            'row1': [A, B, C], 'row2': [D, E, F], 'row3': [G, H, I],
            'col1': [A, D, G], 'col2': [B, E, H], 'col3': [C, F, I]
        }
        scores = {k: compute_semantic_score(v, graph) for k, v in chains.items()}

        # g. Threshold
        current_thr = SEMANTIC_THRESHOLD * (0.9 if relax_th else 1.0)
        if all(val >= current_thr for val in scores.values()):
            return Puzzle(grid, anchors, [B, D, E, F, H], scores)

        # 9. Deterministic fallback
    from itertools import combinations as _comb
    for A, C, G, I in _comb(top_nodes, 4):
        if not all(connector_pool.get(p) for p in [(A,C),(A,G),(C,I),(G,I)]):
            continue
        B = connector_pool[(A, C)][0]
        D = connector_pool[(A, G)][0]
        F = connector_pool[(C, I)][0]
        H = connector_pool[(G, I)][0]
        two = [b for b, _, _, _ in get_two_hop_bridges(D, F, graph)]
        one = [b for b, _ in get_single_hops(D, F, graph, allowed)]
        direct = list(set(graph.neighbors(D)).intersection(graph.neighbors(F)))
        E_choices = two or one or direct
        if not E_choices:
            continue
        E = E_choices[0]
        grid = [[A, B, C], [D, E, F], [G, H, I]]
        if len(set([A, B, C, D, E, F, G, H, I])) < 9:
            continue
                # Recompute scores for fallback grid
        chains_fb = {
            'row1': [A, B, C], 'row2': [D, E, F], 'row3': [G, H, I],
            'col1': [A, D, G], 'col2': [B, E, H], 'col3': [C, F, I]
        }
        scores_fb = {k: compute_semantic_score(v, graph) for k, v in chains_fb.items()}
        # Ensure no zero-score chains in fallback
        if any(val == 0.0 for val in scores_fb.values()):
            continue
        return Puzzle(grid, [A, C, G, I], [B, D, E, F, H], scores_fb)

    raise ValueError(f"Could not generate puzzle after {MAX_ATTEMPTS} attempts and fallback")(f"Could not generate puzzle after {MAX_ATTEMPTS} attempts and fallback")
