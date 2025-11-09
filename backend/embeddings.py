"""
Embedding helper using sentence-transformers.
Normalizes vectors for cosine similarity with FAISS IndexFlatIP.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

# Model choice
MODEL_NAME = "all-mpnet-base-v2"

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    texts: list[str] -> returns normalized numpy array (n, dim) float32
    """
    model = get_model()
    embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    # normalize rows
    norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-9
    embs = embs / norms
    return embs.astype('float32')
