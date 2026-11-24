import math
from typing import List, Set

def precision_at_k(retrieved_ids: List[int], relevant_ids: Set[int], k: int) -> float:
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return float(hits / k)

def recall_at_k(retrieved_ids: List[int], relevant_ids: Set[int], k: int) -> float:
    if not relevant_ids:
        return 1.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return float(hits / len(relevant_ids))

def mean_reciprocal_rank(retrieved_ids: List[int], relevant_ids: Set[int]) -> float:
    for rank, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0

def ndcg_at_k(retrieved_ids: List[int], relevant_relevance: dict, k: int) -> float:
    """
    Computes Normalized Discounted Cumulative Gain at rank K.
    relevant_relevance maps doc_id to graded relevance (e.g. 1 to 3).
    """
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    
    # Calculate DCG
    dcg = 0.0
    for rank, doc_id in enumerate(top_k, 1):
        rel = relevant_relevance.get(doc_id, 0)
        dcg += (2**rel - 1) / math.log2(rank + 1)

    # Calculate Ideal DCG (IDCG)
    ideal_rels = sorted(relevant_relevance.values(), reverse=True)[:k]
    idcg = sum((2**rel - 1) / math.log2(rank + 1) for rank, rel in enumerate(ideal_rels, 1))

    if idcg <= 0.0:
        return 0.0
    return float(dcg / idcg)
