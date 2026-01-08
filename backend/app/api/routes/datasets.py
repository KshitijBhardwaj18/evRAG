"""
Dataset API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import csv
import io

from ...db.session import get_db
from ...schemas.dataset import DatasetCreate, DatasetResponse, DatasetWithItems, DatasetItemCreate
from ...services import dataset_service
from ...core.logging import log

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse, status_code=201)
async def create_dataset(
    dataset: DatasetCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new dataset"""
    try:
        created = await dataset_service.create_dataset(db, dataset)
        return created
    except Exception as e:
        log.error(f"Error creating dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=DatasetResponse, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a dataset from file (CSV, JSON, or JSONL).
    
    Expected formats:
    - CSV: columns: query, ground_truth_docs, ground_truth_answer (optional)
    - JSON: {"items": [{query, ground_truth_docs, ground_truth_answer}, ...]}
    - JSONL: one item per line
    """
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Determine format from filename
        filename = file.filename.lower()
        
        if filename.endswith('.json'):
            items = _parse_json(content_str)
            file_format = "json"
        elif filename.endswith('.jsonl'):
            items = _parse_jsonl(content_str)
            file_format = "jsonl"
        elif filename.endswith('.csv'):
            items = _parse_csv(content_str)
            file_format = "csv"
        else:
            raise ValueError("Unsupported file format. Use .json, .jsonl, or .csv")
        
        # Create dataset
        dataset_data = DatasetCreate(
            name=name or file.filename,
            description=description,
            items=items,
            file_format=file_format
        )
        
        created = await dataset_service.create_dataset(db, dataset_data)
        return created
        
    except Exception as e:
        log.error(f"Error uploading dataset: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all datasets"""
    datasets = await dataset_service.list_datasets(db, skip, limit)
    return datasets


@router.get("/{dataset_id}", response_model=DatasetWithItems)
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a dataset with all items"""
    dataset = await dataset_service.get_dataset_with_items(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a dataset"""
    deleted = await dataset_service.delete_dataset(db, dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return None


def _parse_json(content: str) -> List[DatasetItemCreate]:
    """Parse JSON format"""
    data = json.loads(content)
    
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Invalid JSON format")
    
    return [DatasetItemCreate(**item) for item in items]


def _parse_jsonl(content: str) -> List[DatasetItemCreate]:
    """Parse JSONL format"""
    items = []
    for line in content.strip().split('\n'):
        if line.strip():
            item = json.loads(line)
            items.append(DatasetItemCreate(**item))
    return items


def _parse_csv(content: str) -> List[DatasetItemCreate]:
    """Parse CSV format"""
    items = []
    reader = csv.DictReader(io.StringIO(content))
    
    for row in reader:
        # Parse ground_truth_docs (could be JSON array or comma-separated)
        gt_docs_str = row.get('ground_truth_docs', '[]')
        try:
            gt_docs = json.loads(gt_docs_str)
        except:
            # Fallback: split by comma
            gt_docs = [d.strip() for d in gt_docs_str.split(',') if d.strip()]
        
        item = DatasetItemCreate(
            query=row['query'],
            ground_truth_docs=gt_docs if gt_docs else None,
            ground_truth_answer=row.get('ground_truth_answer')
        )
        items.append(item)
    
    return items

