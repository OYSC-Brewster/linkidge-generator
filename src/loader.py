# src/loader.py

import pickle
from pathlib import Path

# Path to the bundled data pickle
BUNDLE_PATH = Path(__file__).parent.parent / "data" / "linkidge_bundle.pkl"


def load_bundle(path: Path = BUNDLE_PATH) -> tuple:
    """
    Load and return the bundled data:
      - graph (NetworkX)
      - allowed_words (set)
      - lemma_freq (dict)
    """
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["graph"], data["allowed_words"], data["lemma_freq"]


def get_graph(pruned: bool = True) -> "nx.Graph":
    """
    Return the semantic graph (pruned) from the bundle.
    The 'pruned' flag is kept for compatibility but ignored, as we bundle only the pruned graph.
    """
    graph, _, _ = load_bundle()
    return graph


def get_allowed_words() -> set:
    """
    Return the set of allowed words from the bundle.
    """
    _, allowed_words, _ = load_bundle()
    return allowed_words


def get_lemma_freq() -> dict:
    """
    Return the lemma frequency mapping from the bundle.
    """
    _, _, lemma_freq = load_bundle()
    return lemma_freq
