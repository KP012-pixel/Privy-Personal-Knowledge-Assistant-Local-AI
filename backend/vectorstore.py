import faiss
import numpy as np
import os
import pickle

class FaissStore:
    def __init__(self, dim, persist_path=None):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # cosine when vectors normalized
        self.metadatas = []  # list of dicts aligned with vectors
        self.vectors = None
        self.persist_path = persist_path

        # load if exists
        if persist_path and os.path.exists(persist_path):
            try:
                data = pickle.load(open(persist_path, 'rb'))
                self.index = data['index']
                self.metadatas = data['metadatas']
            except Exception:
                pass

    def add(self, embeddings: np.ndarray, metadatas: list):
        """
        embeddings: (n, dim) float32
        metadatas: list of metadata dicts length n
        """
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        self.index.add(embeddings)
        self.metadatas.extend(metadatas)

    def search(self, query_emb: np.ndarray, k=6):
        if query_emb.ndim == 1:
            query_emb = query_emb.reshape(1, -1)
        D, I = self.index.search(query_emb, k)
        results = []
        for dist_row, idx_row in zip(D, I):
            row = []
            for score, idx in zip(dist_row, idx_row):
                if idx < 0 or idx >= len(self.metadatas):
                    continue
                md = dict(self.metadatas[idx])  # copy
                md['score'] = float(score)
                row.append(md)
            results.append(row)
        return results

    def save(self):
        if not self.persist_path:
            return
        try:
            pickle.dump({'index': self.index, 'metadatas': self.metadatas}, open(self.persist_path, 'wb'))
        except Exception:
            pass
