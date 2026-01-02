"""
Mean Average Precision (MAP): Average of precision values at each relevant document position

Formula: MAP = (1 / # relevant docs) * Σ(Precision@k * relevance@k)
where k is the rank and relevance@k is 1 if doc at k is relevant, 0 otherwise
"""
from typing import List, Any


def calculate_map(
    retrieved_docs: List[Any],
    ground_truth_docs: List[Any]
) -> float:
    """
    Calculate Mean Average Precision for a single query.
    
    Args:
        retrieved_docs: List of retrieved documents (in ranked order)
        ground_truth_docs: List of ground truth relevant documents
        
    Returns:
        MAP score between 0 and 1
    """
    if not ground_truth_docs or not retrieved_docs:
        return 0.0
    
    # Normalize documents
    gt_set = _normalize_docs_set(ground_truth_docs)
    retrieved_list = _normalize_docs_list(retrieved_docs)
    
    # Calculate average precision
    precision_sum = 0.0
    num_relevant_found = 0
    
    for rank, doc in enumerate(retrieved_list, start=1):
        if doc in gt_set:
            num_relevant_found += 1
            precision_at_k = num_relevant_found / rank
            precision_sum += precision_at_k
    
    if num_relevant_found == 0:
        return 0.0
    
    # Average over all relevant documents (not just found ones)
    average_precision = precision_sum / len(gt_set)
    return round(average_precision, 4)


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

