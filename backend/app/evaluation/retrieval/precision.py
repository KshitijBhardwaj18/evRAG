"""
Precision@K: Fraction of retrieved documents that are relevant

Formula: Precision@K = (# relevant docs in top K) / K
"""
from typing import List, Dict, Any


def calculate_precision_at_k(
    retrieved_docs: List[Any],
    ground_truth_docs: List[Any],
    k_values: List[int] = [1, 3, 5, 10]
) -> Dict[int, float]:
    """
    Calculate Precision@K for multiple K values.
    
    Args:
        retrieved_docs: List of retrieved documents (in ranked order)
        ground_truth_docs: List of ground truth relevant documents
        k_values: List of K values to compute precision for
        
    Returns:
        Dictionary mapping K to Precision@K score
    """
    if not ground_truth_docs:
        return {k: 0.0 for k in k_values}
    
    if not retrieved_docs:
        return {k: 0.0 for k in k_values}
    
    # Normalize documents for comparison
    gt_set = _normalize_docs(ground_truth_docs)
    retrieved_list = _normalize_docs(retrieved_docs)
    
    results = {}
    for k in k_values:
        top_k = retrieved_list[:k]
        if not top_k:
            results[k] = 0.0
            continue
            
        relevant_retrieved = len(set(top_k) & gt_set)
        precision = relevant_retrieved / len(top_k)
        results[k] = round(precision, 4)
    
    return results


def _normalize_docs(docs: List[Any]) -> list:
    """
    Normalize documents to comparable format (preserving order for retrieved).
    """
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

