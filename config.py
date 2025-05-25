# config.py

from pathlib import Path

# --- Data paths ---
BASE_DIR     = Path(__file__).parent
DATA_DIR     = BASE_DIR.parent / "data"
GRAPH_FILE   = DATA_DIR / "graph_pruned_norm.gpickle"
FULL_GRAPH   = DATA_DIR / "graph_full_norm.gpickle"
ALLOWED_FILE = DATA_DIR / "allowed_words.txt"
FREQ_FILE    = DATA_DIR / "lemma_freq.json"
BUNDLE_FILE  = DATA_DIR / "linkidge_bundle.pkl"

# --- Generation parameters ---
SEMANTIC_THRESHOLD = 1.5   # min score for rows/cols
GRID_SIZE          = 3     # 3×3 puzzle
MAX_ATTEMPTS       = 1000  # max retries before failing

# --- Connector filtering ---
FREQ_PERCENTILE = 0.10          # exclude bottom 10% by frequency
LENGTH_MAX      = 12            # maximum word length for connectors
ALLOWED_POS     = {"n", "v", "a", "s"}  # noun, verb, adj, sat.adj

# --- Output directories ---
PUZZLE_DIR    = BASE_DIR / "puzzles"
DRAFTS_DIR    = PUZZLE_DIR / "drafts"
PUBLISHED_DIR = PUZZLE_DIR / "published"
