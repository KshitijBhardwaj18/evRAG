"""
Citation Check: Verify that each sentence in the answer can be mapped to retrieved chunks

Each answer sentence should have a "citation" (supporting evidence) in the context.
If a sentence lacks citation, it's potentially hallucinated.
"""
from typing import List, Any, Dict
import re


def check_citations(
    generated_answer: str,
    retrieved_docs: List[Any],
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Check citation coverage: can each answer sentence be cited to context?
    
    Args:
        generated_answer: The generated answer
        retrieved_docs: Retrieved documents (potential citations)
        threshold: Minimum word overlap to consider a citation valid
        
    Returns:
        Dict with citation coverage and uncited sentences
    """
    if not generated_answer or not generated_answer.strip():
        return {
            "citation_coverage": 0.0,
            "cited_sentences": 0,
            "total_sentences": 0,
            "uncited_sentences": []
        }
    
    if not retrieved_docs:
        sentences = _split_into_sentences(generated_answer)
        return {
            "citation_coverage": 0.0,
            "cited_sentences": 0,
            "total_sentences": len(sentences),
            "uncited_sentences": sentences
        }
    
    # Extract context
    context_texts = _extract_texts(retrieved_docs)
    
    # Split answer into sentences
    sentences = _split_into_sentences(generated_answer)
    
    if not sentences:
        return {
            "citation_coverage": 1.0,
            "cited_sentences": 0,
            "total_sentences": 0,
            "uncited_sentences": []
        }
    
    # Check each sentence for citation
    cited = 0
    uncited = []
    
    for sentence in sentences:
        has_citation = _find_citation(sentence, context_texts, threshold)
        if has_citation:
            cited += 1
        else:
            uncited.append(sentence)
    
    coverage = cited / len(sentences) if sentences else 0.0
    
    return {
        "citation_coverage": round(coverage, 4),
        "cited_sentences": cited,
        "total_sentences": len(sentences),
        "uncited_sentences": uncited
    }


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]


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


def _find_citation(sentence: str, context_texts: List[str], threshold: float) -> bool:
    """
    Find if sentence has a citation (support) in context.
    Uses word overlap as proxy for citation.
    """
    sentence_lower = sentence.lower()
    sentence_words = set(sentence_lower.split())
    
    if not sentence_words:
        return False
    
    for context in context_texts:
        context_lower = context.lower()
        
        # Check for substring match (strong citation)
        if sentence_lower in context_lower:
            return True
        
        # Check for word overlap (weaker citation)
        context_words = set(context_lower.split())
        overlap = len(sentence_words & context_words)
        overlap_ratio = overlap / len(sentence_words)
        
        if overlap_ratio >= threshold:
            return True
    
    return False

