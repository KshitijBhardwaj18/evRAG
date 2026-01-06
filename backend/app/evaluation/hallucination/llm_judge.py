"""
LLM-as-Judge Hallucination Detection

Uses an LLM to evaluate if claims in the answer are supported by context.
Prompts the LLM to identify unsupported or contradictory statements.
"""
from typing import List, Any, Dict, Optional
import re
from ...core.logging import log


def detect_hallucination_llm(
    generated_answer: str,
    retrieved_docs: List[Any],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use LLM to judge if answer contains hallucinations.
    
    Args:
        generated_answer: The generated answer to evaluate
        retrieved_docs: Retrieved documents (context)
        api_key: OpenAI API key (optional)
        
    Returns:
        Dict with hallucination assessment and identified spans
    """
    if not generated_answer or not generated_answer.strip():
        return {
            "hallucination_detected": False,
            "confidence": 0.0,
            "unsupported_claims": [],
            "method": "empty_answer"
        }
    
    if not retrieved_docs:
        # No context = everything is potentially hallucinated
        return {
            "hallucination_detected": True,
            "confidence": 1.0,
            "unsupported_claims": [generated_answer],
            "method": "no_context"
        }
    
    # Extract context text
    context_texts = _extract_texts(retrieved_docs)
    context_str = "\n\n".join(context_texts[:3])  # Use top 3 docs
    
    # Try OpenAI if API key provided
    if api_key:
        try:
            result = _llm_judge_openai(generated_answer, context_str, api_key)
            if result:
                return result
        except Exception as e:
            log.warning(f"OpenAI LLM judge failed: {e}")
    
    # Fallback to rule-based detection
    return _rule_based_detection(generated_answer, context_texts)


def _llm_judge_openai(answer: str, context: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Use OpenAI to judge hallucinations.
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""You are an AI evaluator. Your task is to determine if the ANSWER contains any hallucinations (unsupported or contradictory claims) when compared to the CONTEXT.

CONTEXT:
{context}

ANSWER:
{answer}

Evaluate the answer and identify any claims that are:
1. Not supported by the context
2. Contradict the context
3. Add information not present in the context

Respond in this exact format:
HALLUCINATION: [YES/NO]
CONFIDENCE: [0.0-1.0]
UNSUPPORTED_CLAIMS:
- [claim 1 if any]
- [claim 2 if any]

Be strict in your evaluation."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content
        return _parse_llm_response(result_text)
        
    except Exception as e:
        log.error(f"OpenAI LLM judge error: {e}")
        return None


def _parse_llm_response(response: str) -> Dict[str, Any]:
    """Parse LLM response into structured format"""
    lines = response.strip().split('\n')
    
    hallucination_detected = False
    confidence = 0.5
    unsupported_claims = []
    
    for line in lines:
        if line.startswith("HALLUCINATION:"):
            hallucination_detected = "YES" in line.upper()
        elif line.startswith("CONFIDENCE:"):
            try:
                confidence = float(re.search(r'[\d.]+', line).group())
            except:
                confidence = 0.5
        elif line.startswith("- "):
            claim = line[2:].strip()
            if claim:
                unsupported_claims.append(claim)
    
    return {
        "hallucination_detected": hallucination_detected,
        "confidence": confidence,
        "unsupported_claims": unsupported_claims,
        "method": "llm_judge"
    }


def _rule_based_detection(answer: str, context_texts: List[str]) -> Dict[str, Any]:
    """
    Rule-based hallucination detection (fallback).
    Checks if answer claims are in context.
    """
    # Split answer into sentences
    sentences = re.split(r'[.!?]+', answer)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    unsupported = []
    
    for sentence in sentences:
        if not _has_support(sentence, context_texts):
            unsupported.append(sentence)
    
    total = len(sentences)
    hallucination_ratio = len(unsupported) / total if total > 0 else 0.0
    
    return {
        "hallucination_detected": hallucination_ratio > 0.3,  # >30% unsupported
        "confidence": hallucination_ratio,
        "unsupported_claims": unsupported,
        "method": "rule_based"
    }


def _has_support(sentence: str, context_texts: List[str]) -> bool:
    """Check if sentence has support in context"""
    sentence_lower = sentence.lower()
    sentence_words = set(sentence_lower.split())
    
    for context in context_texts:
        context_lower = context.lower()
        
        # Substring match
        if sentence_lower in context_lower:
            return True
        
        # Word overlap
        context_words = set(context_lower.split())
        overlap = len(sentence_words & context_words)
        
        # If >60% overlap, consider supported
        if overlap >= len(sentence_words) * 0.6:
            return True
    
    return False


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

