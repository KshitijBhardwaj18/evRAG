"""
Embedding Drift: Measure semantic distance between answer and retrieved documents

If answer embedding drifts too far from context embeddings, it may be hallucinated.
"""
from typing import List, Any, Dict, Optional


def calculate_embedding_drift(
    generated_answer: str,
    retrieved_docs: List[Any],
    embedding_model=None
) -> Dict[str, Any]:
    """
    Calculate embedding drift between answer and context.
    
    Args:
        generated_answer: The generated answer
        retrieved_docs: Retrieved documents
        embedding_model: Embedding model for computing similarity
        
    Returns:
        Dict with drift score (0 = no drift, 1 = high drift)
    """
    if not generated_answer or not retrieved_docs:
        return {
            "drift_score": 1.0,
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "max_similarity": 0.0,
            "method": "missing_data"
        }
    
    # Extract context texts
    context_texts = _extract_texts(retrieved_docs)
    
    if not context_texts:
        return {
            "drift_score": 1.0,
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "max_similarity": 0.0,
            "method": "no_context"
        }
    
    # If no embedding model, use text overlap
    if embedding_model is None:
        return _text_based_drift(generated_answer, context_texts)
    
    # Compute embedding similarities
    try:
        from sentence_transformers import util
        
        answer_emb = embedding_model.encode(generated_answer, convert_to_tensor=True)
        context_embs = embedding_model.encode(context_texts, convert_to_tensor=True)
        
        similarities = util.cos_sim(answer_emb, context_embs)[0]
        similarities = [float(s) for s in similarities]
        
        avg_sim = sum(similarities) / len(similarities)
        max_sim = max(similarities)
        min_sim = min(similarities)
        
        # Drift = inverse of similarity (1 - similarity)
        drift = 1.0 - avg_sim
        
        return {
            "drift_score": round(drift, 4),
            "avg_similarity": round(avg_sim, 4),
            "min_similarity": round(min_sim, 4),
            "max_similarity": round(max_sim, 4),
            "method": "embedding"
        }
        
    except Exception:
        return _text_based_drift(generated_answer, context_texts)


def _text_based_drift(answer: str, context_texts: List[str]) -> Dict[str, Any]:
    """
    Calculate drift using text overlap (fallback method).
    """
    answer_words = set(answer.lower().split())
    
    similarities = []
    for context in context_texts:
        context_words = set(context.lower().split())
        
        if not answer_words or not context_words:
            similarities.append(0.0)
            continue
        
        # Jaccard similarity
        intersection = len(answer_words & context_words)
        union = len(answer_words | context_words)
        sim = intersection / union if union > 0 else 0.0
        similarities.append(sim)
    
    if not similarities:
        return {
            "drift_score": 1.0,
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "max_similarity": 0.0,
            "method": "text_overlap"
        }
    
    avg_sim = sum(similarities) / len(similarities)
    drift = 1.0 - avg_sim
    
    return {
        "drift_score": round(drift, 4),
        "avg_similarity": round(avg_sim, 4),
        "min_similarity": round(min(similarities), 4),
        "max_similarity": round(max(similarities), 4),
        "method": "text_overlap"
    }


def _extract_texts(docs: List[Any]) -> List[str]:
    """Extract text from documents"""
    texts = []
    for doc in docs:
        if isinstance(doc, str):
            texts.append(doc)
        elif isinstance(doc, dict):
            text = doc.get('text') or doc.get('content') or doc.get('page_content')
            if text:
                texts.append(str(text))
    return texts

