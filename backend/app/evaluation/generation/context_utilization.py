"""
Context Utilization: Measures what percentage of the answer is backed by retrieved context

Formula: % of answer sentences that have support in retrieved docs
"""
from typing import List, Any, Dict
import re


def calculate_context_utilization(
    generated_answer: str,
    retrieved_docs: List[Any],
    embedding_model=None
) -> Dict[str, Any]:
    """
    Calculate context utilization: how much of answer uses retrieved context?
    
    Args:
        generated_answer: The generated answer
        retrieved_docs: Retrieved documents
        embedding_model: Optional embedding model
        
    Returns:
        Dict with utilization score and details
    """
    if not generated_answer or not generated_answer.strip():
        return {"score": 0.0, "utilized_sentences": 0, "total_sentences": 0}
    
    if not retrieved_docs:
        return {"score": 0.0, "utilized_sentences": 0, "total_sentences": 1}
    
    # Extract context text
    context_texts = _extract_texts(retrieved_docs)
    if not context_texts:
        return {"score": 0.0, "utilized_sentences": 0, "total_sentences": 1}
    
    # Split answer into sentences
    sentences = _split_into_sentences(generated_answer)
    if not sentences:
        return {"score": 1.0, "utilized_sentences": 0, "total_sentences": 0}
    
    # Check how many sentences have context support
    utilized = 0
    for sentence in sentences:
        if _has_context_support(sentence, context_texts):
            utilized += 1
    
    score = utilized / len(sentences) if sentences else 0.0
    
    return {
        "score": round(score, 4),
        "utilized_sentences": utilized,
        "total_sentences": len(sentences)
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


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]


def _has_context_support(sentence: str, context_texts: List[str]) -> bool:
    """Check if sentence has support in context"""
    sentence_lower = sentence.lower()
    
    for context in context_texts:
        context_lower = context.lower()
        
        # Check substring match
        if sentence_lower in context_lower:
            return True
        
        # Check word overlap
        sentence_words = set(sentence_lower.split())
        context_words = set(context_lower.split())
        overlap = len(sentence_words & context_words)
        
        # If >50% overlap, consider it supported
        if overlap >= len(sentence_words) * 0.5:
            return True
    
    return False

