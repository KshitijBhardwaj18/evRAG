"""
Mean Reciprocal Rank (MRR): Average of reciprocal ranks of first relevant document

Formula: MRR = 1 / rank_of_first_relevant_doc
(For single query, mean is taken across multiple queries in practice)
"""
from typing import List, Any, Optional


def calculate_mrr(
    retrieved_docs: List[Any],
    ground_truth_docs: List[Any]
) -> float:
    """
    Calculate Mean Reciprocal Rank for a single query.
    
    Args:
        retrieved_docs: List of retrieved documents (in ranked order)
        ground_truth_docs: List of ground truth relevant documents
        
    Returns:
        Reciprocal rank (1/rank) of first relevant document, or 0 if none found
    """
    if not ground_truth_docs or not retrieved_docs:
        return 0.0
    
    # Normalize documents
    gt_set = _normalize_docs_set(ground_truth_docs)
    retrieved_list = _normalize_docs_list(retrieved_docs)
    
    # Find rank of first relevant document (1-indexed)
    for rank, doc in enumerate(retrieved_list, start=1):
        if doc in gt_set:
            return round(1.0 / rank, 4)
    
    return 0.0


def _normalize_docs_set(docs: List[Any]) -> set:
    """Normalize documents to set for comparison"""
    normalized = set()
    for doc in docs:
        if isinstance(doc, str):
            normalized.add(doc)
        elif isinstance(doc, dict):
            doc_id = doc.get('id') or doc.get('doc_id') or doc.get('document_id')
            if doc_id:
                normalized.add(str(doc_id))
            else:
                text = doc.get('text') or doc.get('content') or doc.get('page_content')
                if text:
                    normalized.add(str(text)[:200])
        else:
            normalized.add(str(doc))
    return normalized


def _normalize_docs_list(docs: List[Any]) -> list:
    """Normalize documents to list (preserving order)"""
    normalized = []
    for doc in docs:
        if isinstance(doc, str):
            normalized.append(doc)
        elif isinstance(doc, dict):
            doc_id = doc.get('id') or doc.get('doc_id') or doc.get('document_id')
            if doc_id:
                normalized.append(str(doc_id))
            else:
                text = doc.get('text') or doc.get('content') or doc.get('page_content')
                if text:
                    normalized.append(str(text)[:200])
        else:
            normalized.append(str(doc))
    return normalized

