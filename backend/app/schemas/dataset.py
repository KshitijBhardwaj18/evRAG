from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class DatasetItemCreate(BaseModel):
    query: str = Field(..., description="The query/question")
    ground_truth_docs: Optional[List[Any]] = Field(None, description="Ground truth documents")
    ground_truth_answer: Optional[str] = Field(None, description="Expected answer")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DatasetItemResponse(DatasetItemCreate):
    id: str
    dataset_id: str
    
    class Config:
        from_attributes = True


class DatasetCreate(BaseModel):
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    items: List[DatasetItemCreate] = Field(..., description="Dataset items")
    file_format: Optional[str] = Field("json", description="Original file format")


class DatasetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    current_version: int
    total_items: int
    file_format: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DatasetWithItems(DatasetResponse):
    items: List[DatasetItemResponse]

