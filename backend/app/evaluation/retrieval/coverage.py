"""
Coverage: Fraction of ground truth documents that were retrieved

Formula: Coverage = (# GT docs retrieved) / (total # GT docs)
This is essentially Recall without the @K constraint
"""
from typing import List, Any


def calculate_coverage(
    retrieved_docs: List[Any],
    ground_truth_docs: List[Any]
) -> float:
    """
    Calculate coverage: how much of the ground truth was retrieved?
    
    Args:
        retrieved_docs: List of retrieved documents (all of them)
        ground_truth_docs: List of ground truth relevant documents
        
    Returns:
        Coverage score between 0 and 1
    """
    if not ground_truth_docs:
        return 0.0
    
    if not retrieved_docs:
        return 0.0
    
    # Normalize documents
    gt_set = _normalize_docs_set(ground_truth_docs)
    retrieved_set = _normalize_docs_set(retrieved_docs)
    
    # Calculate overlap
    covered = len(gt_set & retrieved_set)
    coverage = covered / len(gt_set)
    
    return round(coverage, 4)


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

