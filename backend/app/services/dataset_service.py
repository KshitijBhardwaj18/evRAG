"""
Dataset service for managing datasets
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import Dataset, DatasetItem
from ..schemas.dataset import DatasetCreate, DatasetResponse, DatasetWithItems
from ..core.logging import log


async def create_dataset(db: AsyncSession, dataset_data: DatasetCreate) -> Dataset:
    """
    Create a new dataset with items.
    
    Args:
        db: Database session
        dataset_data: Dataset creation data
        
    Returns:
        Created dataset
    """
    log.info(f"Creating dataset: {dataset_data.name}")
    
    # Create dataset
    dataset = Dataset(
        name=dataset_data.name,
        description=dataset_data.description,
        total_items=len(dataset_data.items),
        file_format=dataset_data.file_format
    )
    
    db.add(dataset)
    await db.flush()  # Get dataset ID
    
    # Create items
    for item_data in dataset_data.items:
        item = DatasetItem(
            dataset_id=dataset.id,
            query=item_data.query,
            ground_truth_docs=item_data.ground_truth_docs,
            ground_truth_answer=item_data.ground_truth_answer,
            metadata=item_data.metadata
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(dataset)
    
    log.info(f"Dataset created with ID: {dataset.id}")
    return dataset


async def get_dataset(db: AsyncSession, dataset_id: str) -> Optional[Dataset]:
    """
    Get a dataset by ID.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        Dataset or None
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    return result.scalar_one_or_none()


async def get_dataset_with_items(db: AsyncSession, dataset_id: str) -> Optional[Dataset]:
    """
    Get a dataset with all items loaded.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        Dataset with items or None
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.items))
        .where(Dataset.id == dataset_id)
    )
    return result.scalar_one_or_none()


async def list_datasets(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dataset]:
    """
    List all datasets.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of datasets
    """
    result = await db.execute(
        select(Dataset).offset(skip).limit(limit).order_by(Dataset.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_dataset(db: AsyncSession, dataset_id: str) -> bool:
    """
    Delete a dataset and all its items.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        
    Returns:
        True if deleted, False if not found
    """
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        return False
    
    await db.delete(dataset)
    await db.commit()
    
    log.info(f"Dataset deleted: {dataset_id}")
    return True

