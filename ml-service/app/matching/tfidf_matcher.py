"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: TF-IDF Matcher (Stage 2)
Description: Word and Character N-Gram TF-IDF lexical similarity with persistence.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pickle
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from app.normalization.text_normalizer import normalize_text
except ImportError:
    from backend.app.ml.text_normalizer import normalize_text


class TFIDFMatcher:
    """
    Computes lexical similarity using a combination of:
    - Word N-grams (1-2) to capture distinct material terms
    - Character N-grams (3-5) to capture alphanumeric codes (e.g. M10, SS304, 50MM)
    """

    def __init__(
        self,
        word_ngram_range: Tuple[int, int] = (1, 2),
        char_ngram_range: Tuple[int, int] = (3, 5),
        word_weight: float = 0.55,
        char_weight: float = 0.45,
    ):
        self.word_weight = word_weight
        self.char_weight = char_weight

        self.word_vectorizer = TfidfVectorizer(
            ngram_range=word_ngram_range,
            min_df=1,
            token_pattern=r"(?u)\b[a-zA-Z0-9_\-\.\/]+\b",
            lowercase=False,  # text is pre-normalized
        )

        self.char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=char_ngram_range,
            min_df=1,
            lowercase=False,
        )

        self.is_fitted = False

    def fit(self, texts: List[str]) -> "TFIDFMatcher":
        """
        Fits both word and character vectorizers on corpus.
        """
        normalized_texts = [normalize_text(t) for t in texts]
        self.word_vectorizer.fit(normalized_texts)
        self.char_vectorizer.fit(normalized_texts)
        self.is_fitted = True
        return self

    def compute_similarity(
        self, text_a: str, text_b: str
    ) -> Dict[str, float]:
        """
        Computes cosine similarity between two texts.
        If not fitted on corpus, fits temporarily on the pair.
        """
        norm_a = normalize_text(text_a)
        norm_b = normalize_text(text_b)

        if not norm_a or not norm_b:
            return {"word_sim": 0.0, "char_sim": 0.0, "lexical_score": 0.0}

        if not self.is_fitted:
            # Local fit on the pair if no global corpus is loaded
            local_word = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"(?u)\b\S+\b")
            local_char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
            try:
                w_mat = local_word.fit_transform([norm_a, norm_b])
                sim_word = float(cosine_similarity(w_mat[0:1], w_mat[1:2])[0][0])
            except Exception:
                sim_word = 0.0

            try:
                c_mat = local_char.fit_transform([norm_a, norm_b])
                sim_char = float(cosine_similarity(c_mat[0:1], c_mat[1:2])[0][0])
            except Exception:
                sim_char = 0.0
        else:
            w_a = self.word_vectorizer.transform([norm_a])
            w_b = self.word_vectorizer.transform([norm_b])
            sim_word = float(cosine_similarity(w_a, w_b)[0][0])

            c_a = self.char_vectorizer.transform([norm_a])
            c_b = self.char_vectorizer.transform([norm_b])
            sim_char = float(cosine_similarity(c_a, c_b)[0][0])

        combined = (self.word_weight * sim_word) + (self.char_weight * sim_char)
        # Clamp to [0.0, 1.0]
        combined = max(0.0, min(1.0, combined))

        return {
            "word_sim": round(sim_word, 4),
            "char_sim": round(sim_char, 4),
            "lexical_score": round(combined, 4),
        }

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(
                {
                    "word_vectorizer": self.word_vectorizer,
                    "char_vectorizer": self.char_vectorizer,
                    "is_fitted": self.is_fitted,
                    "word_weight": self.word_weight,
                    "char_weight": self.char_weight,
                },
                f,
            )

    @classmethod
    def load(cls, filepath: Path) -> "TFIDFMatcher":
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        matcher = cls(word_weight=data["word_weight"], char_weight=data["char_weight"])
        matcher.word_vectorizer = data["word_vectorizer"]
        matcher.char_vectorizer = data["char_vectorizer"]
        matcher.is_fitted = data["is_fitted"]
        return matcher


# Singleton instance
_tfidf_instance: Optional[TFIDFMatcher] = None


def get_tfidf_matcher() -> TFIDFMatcher:
    global _tfidf_instance
    if _tfidf_instance is None:
        _tfidf_instance = TFIDFMatcher()
    return _tfidf_instance
