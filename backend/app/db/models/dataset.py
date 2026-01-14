from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..session import Base
import uuid


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    current_version = Column(Integer, default=1)
    total_items = Column(Integer, default=0)
    file_format = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    items = relationship("DatasetItem", back_populates="dataset", cascade="all, delete-orphan")
    evaluation_runs = relationship("EvaluationRun", back_populates="dataset")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")


class DatasetItem(Base):
    __tablename__ = "dataset_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    query = Column(Text, nullable=False)
    ground_truth_docs = Column(JSON, nullable=True)
    ground_truth_answer = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    dataset = relationship("Dataset", back_populates="items")
    results = relationship("EvaluationResult", back_populates="dataset_item")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    changes_summary = Column(Text, nullable=True)
    item_count = Column(Integer, default=0)
    items_snapshot = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)
    
    dataset = relationship("Dataset", back_populates="versions")

