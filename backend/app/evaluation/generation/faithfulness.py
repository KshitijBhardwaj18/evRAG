"""
Faithfulness: Measures if the generated answer is grounded in the retrieved documents

Approach:
1. Break answer into claims/sentences
2. For each claim, check if it's supported by retrieved context
3. Score = (# supported claims) / (total # claims)

Uses embedding similarity to check if claims are supported
"""
from typing import List, Any, Dict, Optional
import re
from ...core.logging import log


def calculate_faithfulness(
    generated_answer: str,
    retrieved_docs: List[Any],
    embedding_model=None,
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Calculate faithfulness score: is answer grounded in context?
    
    Args:
        generated_answer: The generated answer text
        retrieved_docs: Retrieved documents that should support the answer
        embedding_model: Optional embedding model for semantic similarity
        threshold: Similarity threshold for claim support
        
    Returns:
        Dict with score and details about which claims are supported
    """
    if not generated_answer or not generated_answer.strip():
        return {"score": 0.0, "supported_claims": 0, "total_claims": 0, "details": []}
    
    if not retrieved_docs:
        return {"score": 0.0, "supported_claims": 0, "total_claims": 1, "details": []}
    
    # Extract context text from documents
    context_texts = _extract_texts(retrieved_docs)
    if not context_texts:
        return {"score": 0.0, "supported_claims": 0, "total_claims": 1, "details": []}
    
    # Break answer into claims (sentences)
    claims = _split_into_sentences(generated_answer)
    if not claims:
        return {"score": 1.0, "supported_claims": 0, "total_claims": 0, "details": []}
    
    # Check each claim
    supported = 0
    details = []
    
    for claim in claims:
        is_supported = _check_claim_support(claim, context_texts, embedding_model, threshold)
        if is_supported:
            supported += 1
        details.append({
            "claim": claim,
            "supported": is_supported
        })
    
    score = supported / len(claims) if claims else 0.0
    
    return {
        "score": round(score, 4),
        "supported_claims": supported,
        "total_claims": len(claims),
        "details": details
    }


def _extract_texts(docs: List[Any]) -> List[str]:
    """Extract text content from documents"""
    texts = []
    for doc in docs:
        if isinstance(doc, str):
            texts.append(doc)
        elif isinstance(doc, dict):
            text = doc.get('text') or doc.get('content') or doc.get('page_content')
            if text:
                texts.append(str(text))
    return texts


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences (claims)"""
    # Simple sentence splitting - can be improved with NLTK
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]


def _check_claim_support(
    claim: str,
    context_texts: List[str],
    embedding_model,
    threshold: float
) -> bool:
    """
    Check if a claim is supported by any context text.
    Uses string matching or embedding similarity if model provided.
    """
    # Simple substring matching as fallback
    claim_lower = claim.lower()
    for context in context_texts:
        context_lower = context.lower()
        
        # Check for substring match (strong signal)
        if claim_lower in context_lower or context_lower in claim_lower:
            return True
        
        # Check for significant word overlap
        claim_words = set(claim_lower.split())
        context_words = set(context_lower.split())
        overlap = len(claim_words & context_words)
        if overlap >= min(len(claim_words) * 0.6, 5):  # 60% overlap or 5+ words
            return True
    
    # If embedding model provided, use semantic similarity
    if embedding_model is not None:
        try:
            from sentence_transformers import util
            claim_emb = embedding_model.encode(claim, convert_to_tensor=True)
            context_embs = embedding_model.encode(context_texts, convert_to_tensor=True)
            
            similarities = util.cos_sim(claim_emb, context_embs)[0]
            max_sim = float(similarities.max())
            
            if max_sim >= threshold:
                return True
        except Exception as e:
            log.warning(f"Embedding similarity failed: {e}")
    
    return False

