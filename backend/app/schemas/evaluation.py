"""
Pydantic schemas for evaluation runs and results
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from ..db.models.evaluation import RunStatus


class RAGConfig(BaseModel):
    """Configuration for RAG pipeline"""
    endpoint: Optional[str] = Field(None, description="RAG API endpoint")
    top_k: int = Field(5, description="Number of documents to retrieve")
    model: Optional[str] = Field(None, description="Generation model to use")
    temperature: float = Field(0.7, description="Generation temperature")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class EvaluationRunCreate(BaseModel):
    """Schema for creating an evaluation run"""
    dataset_id: str = Field(..., description="Dataset to evaluate on")
    name: str = Field(..., description="Run name")
    description: Optional[str] = Field(None, description="Run description")
    rag_endpoint: Optional[str] = Field(None, description="RAG pipeline endpoint")
    rag_config: Optional[Dict[str, Any]] = Field(None, description="RAG configuration")


class EvaluationRunResponse(BaseModel):
    """Schema for evaluation run response"""
    id: str
    dataset_id: str
    name: str
    description: Optional[str]
    status: RunStatus
    rag_endpoint: Optional[str]
    rag_config: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    total_items: int
    completed_items: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EvaluationResultResponse(BaseModel):
    """Schema for evaluation result response"""
    id: str
    run_id: str
    dataset_item_id: str
    
    # RAG outputs
    retrieved_docs: Optional[List[Any]]
    generated_answer: Optional[str]
    
    # Retrieval metrics
    recall_at_k: Optional[Dict[int, float]]
    precision_at_k: Optional[Dict[int, float]]
    mrr: Optional[float]
    map_score: Optional[float]
    hit_rate: Optional[float]
    coverage: Optional[float]
    
    # Generation metrics
    faithfulness: Optional[float]
    answer_relevance: Optional[float]
    context_utilization: Optional[float]
    semantic_similarity: Optional[float]
    rouge_l: Optional[float]
    f1_score: Optional[float]
    
    # Hallucination detection
    hallucination_score: Optional[float]
    hallucinated_spans: Optional[List[str]]
    citation_coverage: Optional[float]
    
    # Details
    metrics_detail: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RunComparison(BaseModel):
    """Schema for comparing two runs"""
    run1: EvaluationRunResponse
    run2: EvaluationRunResponse
    metric_deltas: Dict[str, float]  # Difference in metrics
    improvement_pct: Dict[str, float]  # Percentage improvement

