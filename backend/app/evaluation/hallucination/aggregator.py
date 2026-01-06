"""
Hallucination Score Aggregator

Combines multiple hallucination detection signals into a single score.
"""
from typing import Dict, Any, List


def aggregate_hallucination_score(
    llm_judge_result: Dict[str, Any],
    citation_result: Dict[str, Any],
    drift_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Aggregate multiple hallucination signals into final score.
    
    Args:
        llm_judge_result: Result from LLM judge
        citation_result: Result from citation check
        drift_result: Result from embedding drift
        
    Returns:
        Aggregated hallucination score and detailed breakdown
    """
    # Extract individual signals
    llm_confidence = llm_judge_result.get('confidence', 0.5)
    citation_coverage = citation_result.get('citation_coverage', 0.0)
    drift_score = drift_result.get('drift_score', 0.5)
    
    # Convert citation coverage to hallucination signal (inverse)
    citation_hallucination = 1.0 - citation_coverage
    
    # Weighted average (can be tuned)
    weights = {
        'llm_judge': 0.4,
        'citation': 0.35,
        'drift': 0.25
    }
    
    aggregated_score = (
        weights['llm_judge'] * llm_confidence +
        weights['citation'] * citation_hallucination +
        weights['drift'] * drift_score
    )
    
    # Collect all hallucinated spans
    hallucinated_spans = []
    
    # From LLM judge
    if llm_judge_result.get('hallucination_detected'):
        hallucinated_spans.extend(llm_judge_result.get('unsupported_claims', []))
    
    # From citation check
    hallucinated_spans.extend(citation_result.get('uncited_sentences', []))
    
    # Deduplicate
    hallucinated_spans = list(set(hallucinated_spans))
    
    return {
        "hallucination_score": round(aggregated_score, 4),
        "hallucinated_spans": hallucinated_spans,
        "breakdown": {
            "llm_judge": {
                "score": round(llm_confidence, 4),
                "weight": weights['llm_judge'],
                "detected": llm_judge_result.get('hallucination_detected', False)
            },
            "citation_check": {
                "score": round(citation_hallucination, 4),
                "weight": weights['citation'],
                "coverage": round(citation_coverage, 4)
            },
            "embedding_drift": {
                "score": round(drift_score, 4),
                "weight": weights['drift'],
                "avg_similarity": drift_result.get('avg_similarity', 0.0)
            }
        },
        "severity": _classify_severity(aggregated_score)
    }


def _classify_severity(score: float) -> str:
    """Classify hallucination severity"""
    if score < 0.2:
        return "none"
    elif score < 0.4:
        return "low"
    elif score < 0.6:
        return "medium"
    elif score < 0.8:
        return "high"
    else:
        return "critical"

