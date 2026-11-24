import json
import logging
from typing import List, Union
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer ({e}). Using deterministic offline vectorizer.")
            self._model = None

    def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * settings.EMBEDDING_DIM

        if self._model is not None:
            try:
                embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return embedding.tolist()
            except Exception as e:
                logger.warning(f"Inference error with SentenceTransformer: {e}")

        # Deterministic offline fallback projection (384-dimensional normalized vector)
        return self._offline_fallback_embedding(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self._model is not None:
            try:
                embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"Batch inference error with SentenceTransformer: {e}")

        return [self._offline_fallback_embedding(t) for t in texts]

    def _offline_fallback_embedding(self, text: str) -> List[float]:
        """Deterministic 384-dim semantic hash projection for offline environments."""
        import hashlib
        vec = np.zeros(settings.EMBEDDING_DIM, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % settings.EMBEDDING_DIM
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign * (1.0 / (1.0 + np.log1p(i)))
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def cosine_similarity(vec_a: Union[List[float], np.ndarray], vec_b: Union[List[float], np.ndarray]) -> float:
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-6 or norm_b < 1e-6:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

embedding_service = EmbeddingService.get_instance()
