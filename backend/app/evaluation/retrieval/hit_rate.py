"""
Hit Rate: Binary metric indicating if at least one relevant document was retrieved

Formula: Hit Rate = 1 if any relevant doc in results, else 0
"""
from typing import List, Any


def calculate_hit_rate(
    retrieved_docs: List[Any],
    ground_truth_docs: List[Any]
) -> float:
    """
    Calculate Hit Rate (binary: did we retrieve at least one relevant doc?)
    
    Args:
        retrieved_docs: List of retrieved documents
        ground_truth_docs: List of ground truth relevant documents
        
    Returns:
        1.0 if at least one relevant document retrieved, 0.0 otherwise
    """
    if not ground_truth_docs or not retrieved_docs:
        return 0.0
    
    # Normalize documents
    gt_set = _normalize_docs_set(ground_truth_docs)
    retrieved_set = _normalize_docs_set(retrieved_docs)
    
    # Check if any overlap exists
    has_hit = len(gt_set & retrieved_set) > 0
    return 1.0 if has_hit else 0.0


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

