"""
Dataset models for storing uploaded evaluation datasets
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..session import Base
import uuid


class Dataset(Base):
    """Dataset containing queries and ground truth for evaluation"""
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    total_items = Column(Integer, default=0)
    file_format = Column(String)  # csv, json, jsonl
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("DatasetItem", back_populates="dataset", cascade="all, delete-orphan")
    evaluation_runs = relationship("EvaluationRun", back_populates="dataset")


class DatasetItem(Base):
    """Individual item in a dataset (query + ground truth)"""
    __tablename__ = "dataset_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    
    # Core fields
    query = Column(Text, nullable=False)
    
    # Ground truth - stored as JSON for flexibility
    # Can contain: document_ids, text_spans, or full documents
    ground_truth_docs = Column(JSON, nullable=True)  # List of doc IDs or text
    ground_truth_answer = Column(Text, nullable=True)  # Optional expected answer
    
    # Optional metadata
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="items")
    results = relationship("EvaluationResult", back_populates="dataset_item")

