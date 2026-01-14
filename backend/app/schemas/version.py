from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class DatasetVersionResponse(BaseModel):
    id: str
    dataset_id: str
    version_number: int
    changes_summary: Optional[str]
    item_count: int
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class DatasetVersionCreate(BaseModel):
    changes_summary: Optional[str] = Field(None, description="Description of changes")


class VersionComparison(BaseModel):
    version1: DatasetVersionResponse
    version2: DatasetVersionResponse
    items_added: int
    items_removed: int
    items_modified: int
    total_changes: int

