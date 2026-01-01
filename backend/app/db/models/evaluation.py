"""
Evaluation run and result models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..session import Base
import uuid
import enum


class RunStatus(str, enum.Enum):
    """Status of an evaluation run"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRun(Base):
    """An evaluation run on a dataset with a RAG pipeline"""
    __tablename__ = "evaluation_runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    
    # Run metadata
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)
    
    # RAG pipeline configuration
    rag_endpoint = Column(String, nullable=True)  # API endpoint if remote
    rag_config = Column(JSON, nullable=True)  # Configuration parameters
    
    # Aggregate metrics (computed after all items evaluated)
    metrics = Column(JSON, nullable=True)
    
    # Progress tracking
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="evaluation_runs")
    results = relationship("EvaluationResult", back_populates="run", cascade="all, delete-orphan")


class EvaluationResult(Base):
    """Result of evaluating a single query in a run"""
    __tablename__ = "evaluation_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("evaluation_runs.id"), nullable=False)
    dataset_item_id = Column(String, ForeignKey("dataset_items.id"), nullable=False)
    
    # RAG pipeline outputs
    retrieved_docs = Column(JSON, nullable=True)  # List of retrieved documents
    generated_answer = Column(Text, nullable=True)
    
    # Retrieval metrics
    recall_at_k = Column(JSON, nullable=True)  # {1: 0.5, 3: 0.8, 5: 1.0}
    precision_at_k = Column(JSON, nullable=True)
    mrr = Column(Float, nullable=True)
    map_score = Column(Float, nullable=True)
    hit_rate = Column(Float, nullable=True)
    coverage = Column(Float, nullable=True)
    
    # Generation metrics
    faithfulness = Column(Float, nullable=True)
    answer_relevance = Column(Float, nullable=True)
    context_utilization = Column(Float, nullable=True)
    semantic_similarity = Column(Float, nullable=True)
    rouge_l = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Hallucination detection
    hallucination_score = Column(Float, nullable=True)  # 0 = no hallucination, 1 = full hallucination
    hallucinated_spans = Column(JSON, nullable=True)  # List of hallucinated text spans
    citation_coverage = Column(Float, nullable=True)  # % of answer covered by citations
    
    # Detailed breakdowns
    metrics_detail = Column(JSON, nullable=True)  # Additional metric details
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    run = relationship("EvaluationRun", back_populates="results")
    dataset_item = relationship("DatasetItem", back_populates="results")

