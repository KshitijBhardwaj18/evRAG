"""
ROUGE-L and F1 Score: Standard NLP metrics for comparing generated vs ground truth text

ROUGE-L: Longest common subsequence based metric
F1: Harmonic mean of precision and recall at token level
"""
from typing import Optional, Dict, Any


def calculate_rouge_l(
    generated_answer: str,
    ground_truth_answer: Optional[str]
) -> Optional[float]:
    """
    Calculate ROUGE-L score between generated and ground truth answers.
    
    Args:
        generated_answer: The generated answer
        ground_truth_answer: The expected answer
        
    Returns:
        ROUGE-L F1 score or None if no ground truth
    """
    if not ground_truth_answer or not generated_answer:
        return None
    
    try:
        from rouge_score import rouge_scorer
        scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
        scores = scorer.score(ground_truth_answer, generated_answer)
        return round(scores['rougeL'].fmeasure, 4)
    except Exception:
        # Fallback to simple LCS-based metric
        return _simple_rouge_l(generated_answer, ground_truth_answer)


def calculate_f1_score(
    generated_answer: str,
    ground_truth_answer: Optional[str]
) -> Optional[float]:
    """
    Calculate token-level F1 score between generated and ground truth answers.
    
    Args:
        generated_answer: The generated answer
        ground_truth_answer: The expected answer
        
    Returns:
        F1 score or None if no ground truth
    """
    if not ground_truth_answer or not generated_answer:
        return None
    
    # Tokenize
    gen_tokens = set(generated_answer.lower().split())
    gt_tokens = set(ground_truth_answer.lower().split())
    
    if not gen_tokens or not gt_tokens:
        return 0.0
    
    # Calculate precision and recall
    tp = len(gen_tokens & gt_tokens)
    precision = tp / len(gen_tokens) if gen_tokens else 0.0
    recall = tp / len(gt_tokens) if gt_tokens else 0.0
    
    # F1 = harmonic mean
    if precision + recall == 0:
        return 0.0
    
    f1 = 2 * (precision * recall) / (precision + recall)
    return round(f1, 4)


def _simple_rouge_l(text1: str, text2: str) -> float:
    """
    Simple ROUGE-L implementation using longest common subsequence.
    Fallback when rouge_score package not available.
    """
    tokens1 = text1.lower().split()
    tokens2 = text2.lower().split()
    
    lcs_length = _lcs_length(tokens1, tokens2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    # ROUGE-L = F-measure based on LCS
    r_lcs = lcs_length / len(tokens2) if tokens2 else 0.0
    p_lcs = lcs_length / len(tokens1) if tokens1 else 0.0
    
    if r_lcs + p_lcs == 0:
        return 0.0
    
    f_lcs = 2 * r_lcs * p_lcs / (r_lcs + p_lcs)
    return round(f_lcs, 4)


def _lcs_length(seq1: list, seq2: list) -> int:
    """Calculate longest common subsequence length"""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

