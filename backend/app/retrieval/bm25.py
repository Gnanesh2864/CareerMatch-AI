import math
import re
from typing import List, Dict, Any, Tuple
from collections import Counter

class BM25Retriever:
    """
    In-memory BM25 Okapi retrieval engine for high-performance keyword search.
    Implements standard Lucene/Okapi BM25 scoring with tokenization and length normalization.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[Dict[str, Any]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.num_docs: int = 0
        self.doc_token_counts: List[Counter] = []

    @staticmethod
    def tokenize(text: str) -> List[str]:
        if not text:
            return []
        tokens = re.findall(r'[a-zA-Z0-9_\+#]+', text.lower())
        # Filter 1-letter stop tokens (except c)
        return [t for t in tokens if len(t) > 1 or t in ['c', 'r']]

    def index_documents(self, documents: List[Dict[str, Any]], text_fields: List[str] = ["title", "description", "skills"]):
        self.corpus = documents
        self.num_docs = len(documents)
        self.doc_lengths = []
        self.doc_token_counts = []
        self.doc_freqs = Counter()

        total_tokens = 0
        for doc in documents:
            combined_text = " ".join([str(doc.get(f, "")) for f in text_fields])
            tokens = self.tokenize(combined_text)
            self.doc_lengths.append(len(tokens))
            total_tokens += len(tokens)

            token_counter = Counter(tokens)
            self.doc_token_counts.append(token_counter)

            for token in token_counter:
                self.doc_freqs[token] += 1

        self.avg_doc_len = total_tokens / max(1, self.num_docs)

        # Precompute IDF
        self.idf = {}
        for token, freq in self.doc_freqs.items():
            # Standard BM25 IDF formulation
            self.idf[token] = math.log(1.0 + (self.num_docs - freq + 0.5) / (freq + 0.5))

    def score(self, query: str) -> List[Tuple[int, float]]:
        """Scores all indexed documents against the query string. Returns (doc_idx, bm25_score)."""
        query_tokens = self.tokenize(query)
        if not query_tokens or self.num_docs == 0:
            return [(i, 0.0) for i in range(self.num_docs)]

        scores = [0.0] * self.num_docs

        for q_token in query_tokens:
            if q_token not in self.idf:
                continue
            idf_val = self.idf[q_token]

            for i in range(self.num_docs):
                tf = self.doc_token_counts[i].get(q_token, 0)
                if tf > 0:
                    doc_len = self.doc_lengths[i]
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                    term_score = idf_val * (tf * (self.k1 + 1.0)) / denom
                    scores[i] += term_score

        # Pair with indices
        scored_docs = list(enumerate(scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs
