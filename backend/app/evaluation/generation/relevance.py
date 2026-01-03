"""
Answer Relevance: Measures if the answer addresses the question

Uses semantic similarity between question and answer
"""
from typing import Optional, Dict, Any


def calculate_answer_relevance(
    query: str,
    generated_answer: str,
    embedding_model=None
) -> Dict[str, Any]:
    """
    Calculate answer relevance: does answer address the question?
    
    Args:
        query: The original query/question
        generated_answer: The generated answer
        embedding_model: Optional embedding model for semantic similarity
        
    Returns:
        Dict with relevance score and details
    """
    if not query or not generated_answer:
        return {"score": 0.0, "method": "empty"}
    
    # Method 1: Keyword overlap (simple baseline)
    keyword_score = _keyword_relevance(query, generated_answer)
    
    # Method 2: Embedding similarity (if model provided)
    embedding_score = None
    if embedding_model is not None:
        try:
            from sentence_transformers import util
            query_emb = embedding_model.encode(query, convert_to_tensor=True)
            answer_emb = embedding_model.encode(generated_answer, convert_to_tensor=True)
            
            similarity = util.cos_sim(query_emb, answer_emb)[0][0]
            embedding_score = float(similarity)
        except Exception:
            embedding_score = None
    
    # Use embedding score if available, otherwise keyword score
    final_score = embedding_score if embedding_score is not None else keyword_score
    
    return {
        "score": round(final_score, 4),
        "keyword_overlap": round(keyword_score, 4),
        "semantic_similarity": round(embedding_score, 4) if embedding_score else None,
        "method": "semantic" if embedding_score is not None else "keyword"
    }


def _keyword_relevance(query: str, answer: str) -> float:
    """
    Calculate relevance based on keyword overlap.
    Simple but effective baseline.
    """
    # Extract meaningful words (remove stopwords)
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'do', 'does'}
    
    query_words = set(query.lower().split()) - stopwords
    answer_words = set(answer.lower().split()) - stopwords
    
    if not query_words:
        return 0.0
    
    overlap = len(query_words & answer_words)
    relevance = overlap / len(query_words)
    
    return min(relevance, 1.0)  # Cap at 1.0

