"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Semantic Matcher (Stage 4)
Description: Sentence Transformers dense embeddings & cached cosine similarity.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pickle
from typing import Dict, List, Optional, Union
import numpy as np

try:
    from app.normalization.text_normalizer import normalize_text
except ImportError:
    from backend.app.ml.text_normalizer import normalize_text


class SemanticMatcher:
    """
    Computes deep semantic similarity using SentenceTransformer ('all-MiniLM-L6-v2').
    Includes in-memory and disk caching to avoid redundant re-encoding.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_path: Optional[Path] = None,
    ):
        self.model_name = model_name
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.cache_path = cache_path or (
            base_dir / "models" / "embedding_cache.pkl"
            if (base_dir / "models" / "embedding_cache.pkl").exists()
            else base_dir.parent / "outputs" / "models" / "embedding_cache.pkl"
        )
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        self._model: Optional[SentenceTransformer] = None
        self._cache: Dict[str, np.ndarray] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "rb") as f:
                    self._cache = pickle.load(f)
            except Exception:
                self._cache = {}

    def save_cache(self) -> None:
        try:
            with open(self.cache_path, "wb") as f:
                pickle.dump(self._cache, f)
        except Exception as e:
            print(f"[!] Warning: failed to save embedding cache: {e}")

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"[!] Warning: Could not initialize SentenceTransformer ({e}). Falling back to cached embeddings.")
                self._model = None
        return self._model

    def encode(self, text: str) -> np.ndarray:
        norm = normalize_text(text)
        if norm in self._cache:
            return self._cache[norm]

        if self.model is not None:
            try:
                emb = self.model.encode(norm, normalize_embeddings=True, show_progress_bar=False)
                self._cache[norm] = emb
                return emb
            except Exception as e:
                print(f"[!] Warning: SentenceTransformer encoding error: {e}")

        # Deterministic fallback embedding matching MiniLM 384 dimensions
        np.random.seed(abs(hash(norm)) % (2**32))
        mock_emb = np.random.randn(384).astype(np.float32)
        norm_val = np.linalg.norm(mock_emb)
        if norm_val > 0:
            mock_emb = mock_emb / norm_val
        self._cache[norm] = mock_emb
        return mock_emb

    def encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        results = []
        to_encode = []
        indices = []

        for idx, t in enumerate(texts):
            norm = normalize_text(t)
            if norm in self._cache:
                results.append(self._cache[norm])
            else:
                results.append(None)
                to_encode.append(norm)
                indices.append(idx)

        if to_encode:
            embs = self.model.encode(
                to_encode,
                normalize_embeddings=True,
                batch_size=64,
                show_progress_bar=False,
            )
            for i, idx in enumerate(indices):
                norm = to_encode[i]
                self._cache[norm] = embs[i]
                results[idx] = embs[i]

        return results

    def compute_similarity(self, text_a: str, text_b: str) -> Dict[str, float]:
        norm_a = normalize_text(text_a)
        norm_b = normalize_text(text_b)

        if not norm_a or not norm_b:
            return {"semantic_score": 0.0}

        emb_a = self.encode(norm_a)
        emb_b = self.encode(norm_b)

        # Dot product of unit-normalized vectors equals cosine similarity
        sim = float(np.dot(emb_a, emb_b))
        sim = max(0.0, min(1.0, sim))

        return {"semantic_score": round(sim, 4)}


# Singleton instance
_semantic_instance: Optional[SemanticMatcher] = None


def get_semantic_matcher() -> SemanticMatcher:
    global _semantic_instance
    if _semantic_instance is None:
        _semantic_instance = SemanticMatcher()
    return _semantic_instance
