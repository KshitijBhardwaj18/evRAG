"""
Semantic Similarity: Measures similarity between generated answer and ground truth answer

Uses embeddings to compare semantic meaning
"""
from typing import Optional, Dict, Any


def calculate_semantic_similarity(
    generated_answer: str,
    ground_truth_answer: Optional[str],
    embedding_model=None
) -> Dict[str, Any]:
    """
    Calculate semantic similarity between generated and ground truth answers.
    
    Args:
        generated_answer: The generated answer
        ground_truth_answer: The expected answer (optional)
        embedding_model: Embedding model for similarity computation
        
    Returns:
        Dict with similarity score
    """
    if not ground_truth_answer or not generated_answer:
        return {"score": None, "method": "not_available", "reason": "missing_ground_truth"}
    
    # Method 1: Simple text overlap (baseline)
    text_overlap = _calculate_text_overlap(generated_answer, ground_truth_answer)
    
    # Method 2: Embedding similarity (preferred)
    embedding_score = None
    if embedding_model is not None:
        try:
            from sentence_transformers import util
            
            gen_emb = embedding_model.encode(generated_answer, convert_to_tensor=True)
            gt_emb = embedding_model.encode(ground_truth_answer, convert_to_tensor=True)
            
            similarity = util.cos_sim(gen_emb, gt_emb)[0][0]
            embedding_score = float(similarity)
        except Exception:
            embedding_score = None
    
    # Use embedding score if available, otherwise text overlap
    final_score = embedding_score if embedding_score is not None else text_overlap
    
    return {
        "score": round(final_score, 4) if final_score is not None else None,
        "text_overlap": round(text_overlap, 4),
        "embedding_similarity": round(embedding_score, 4) if embedding_score else None,
        "method": "embedding" if embedding_score is not None else "text_overlap"
    }


def _calculate_text_overlap(text1: str, text2: str) -> float:
    """Calculate simple word overlap between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    # Jaccard similarity
    return intersection / union if union > 0 else 0.0

