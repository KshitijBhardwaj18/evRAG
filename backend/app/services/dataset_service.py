from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import Dataset, DatasetItem
from ..schemas.dataset import DatasetCreate, DatasetResponse, DatasetWithItems
from ..core.logging import log
from . import version_service


async def create_dataset(db: AsyncSession, dataset_data: DatasetCreate) -> Dataset:
    log.info(f"Creating dataset: {dataset_data.name}")
    
    dataset = Dataset(
        name=dataset_data.name,
        description=dataset_data.description,
        total_items=len(dataset_data.items),
        file_format=dataset_data.file_format,
        current_version=1
    )
    
    db.add(dataset)
    await db.flush()
    
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
    
    await version_service.create_version(db, dataset.id, "Initial version")
    
    log.info(f"Dataset created with ID: {dataset.id}")
    return dataset


async def get_dataset(db: AsyncSession, dataset_id: str) -> Optional[Dataset]:
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    return result.scalar_one_or_none()


async def get_dataset_with_items(db: AsyncSession, dataset_id: str) -> Optional[Dataset]:
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.items))
        .where(Dataset.id == dataset_id)
    )
    return result.scalar_one_or_none()


async def list_datasets(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dataset]:
    result = await db.execute(
        select(Dataset).offset(skip).limit(limit).order_by(Dataset.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_dataset(db: AsyncSession, dataset_id: str) -> bool:
    dataset = await get_dataset(db, dataset_id)
    if not dataset:
        return False
    
    await db.delete(dataset)
    await db.commit()
    
    log.info(f"Dataset deleted: {dataset_id}")
    return True

