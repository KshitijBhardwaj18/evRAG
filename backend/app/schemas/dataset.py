"""
Pydantic schemas for datasets
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class DatasetItemCreate(BaseModel):
    """Schema for creating a dataset item"""
    query: str = Field(..., description="The query/question")
    ground_truth_docs: Optional[List[Any]] = Field(None, description="Ground truth documents (IDs or text)")
    ground_truth_answer: Optional[str] = Field(None, description="Expected answer (optional)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DatasetItemResponse(DatasetItemCreate):
    """Schema for dataset item response"""
    id: str
    dataset_id: str
    
    class Config:
        from_attributes = True


class DatasetCreate(BaseModel):
    """Schema for creating a dataset"""
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    items: List[DatasetItemCreate] = Field(..., description="Dataset items")
    file_format: Optional[str] = Field("json", description="Original file format")


class DatasetResponse(BaseModel):
    """Schema for dataset response"""
    id: str
    name: str
    description: Optional[str]
    total_items: int
    file_format: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DatasetWithItems(DatasetResponse):
    """Dataset response with items included"""
    items: List[DatasetItemResponse]

