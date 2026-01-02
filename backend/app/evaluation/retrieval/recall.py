"""
Recall@K: Fraction of relevant documents retrieved in top K results

Formula: Recall@K = (# relevant docs in top K) / (total # relevant docs)
"""
from typing import List, Dict, Any


def calculate_recall_at_k(
    retrieved_docs: List[Any],
    ground_truth_docs: List[Any],
    k_values: List[int] = [1, 3, 5, 10]
) -> Dict[int, float]:
    """
    Calculate Recall@K for multiple K values.
    
    Args:
        retrieved_docs: List of retrieved documents (in ranked order)
        ground_truth_docs: List of ground truth relevant documents
        k_values: List of K values to compute recall for
        
    Returns:
        Dictionary mapping K to Recall@K score
        
    Note:
        Documents can be compared by:
        - Exact match (if both are strings/IDs)
        - Dict comparison (if 'id' or 'doc_id' field exists)
        - Text similarity (handled by match_doc helper)
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
        relevant_retrieved = len(set(top_k) & gt_set)
        recall = relevant_retrieved / len(gt_set)
        results[k] = round(recall, 4)
    
    return results


def _normalize_docs(docs: List[Any]) -> set:
    """
    Normalize documents to comparable format.
    Handles strings, dicts with 'id'/'doc_id', or full documents.
    """
    normalized = set()
    for doc in docs:
        if isinstance(doc, str):
            normalized.add(doc)
        elif isinstance(doc, dict):
            # Try to extract ID
            doc_id = doc.get('id') or doc.get('doc_id') or doc.get('document_id')
            if doc_id:
                normalized.add(str(doc_id))
            else:
                # Use text content as fallback
                text = doc.get('text') or doc.get('content') or doc.get('page_content')
                if text:
                    normalized.add(str(text)[:200])  # Use first 200 chars as ID
        else:
            # Fallback: convert to string
            normalized.add(str(doc))
    
    return normalized

