from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..db.models import Dataset, DatasetItem, DatasetVersion
from ..schemas.version import DatasetVersionCreate
from ..core.logging import log
import json


async def create_version(
    db: AsyncSession,
    dataset_id: str,
    changes_summary: Optional[str] = None
) -> DatasetVersion:
    log.info(f"Creating version for dataset: {dataset_id}")
    
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.items))
        .where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise ValueError(f"Dataset not found: {dataset_id}")
    
    items_snapshot = [
        {
            "id": item.id,
            "query": item.query,
            "ground_truth_docs": item.ground_truth_docs,
            "ground_truth_answer": item.ground_truth_answer,
            "metadata": item.metadata
        }
        for item in dataset.items
    ]
    
    version = DatasetVersion(
        dataset_id=dataset_id,
        version_number=dataset.current_version,
        changes_summary=changes_summary,
        item_count=len(dataset.items),
        items_snapshot=items_snapshot
    )
    
    db.add(version)
    await db.commit()
    await db.refresh(version)
    
    log.info(f"Version {version.version_number} created for dataset {dataset_id}")
    return version


async def list_versions(
    db: AsyncSession,
    dataset_id: str
) -> List[DatasetVersion]:
    result = await db.execute(
        select(DatasetVersion)
        .where(DatasetVersion.dataset_id == dataset_id)
        .order_by(DatasetVersion.version_number.desc())
    )
    return list(result.scalars().all())


async def get_version(
    db: AsyncSession,
    dataset_id: str,
    version_number: int
) -> Optional[DatasetVersion]:
    result = await db.execute(
        select(DatasetVersion)
        .where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version_number == version_number
        )
    )
    return result.scalar_one_or_none()


async def rollback_to_version(
    db: AsyncSession,
    dataset_id: str,
    version_number: int
) -> Dataset:
    log.info(f"Rolling back dataset {dataset_id} to version {version_number}")
    
    version = await get_version(db, dataset_id, version_number)
    if not version:
        raise ValueError(f"Version {version_number} not found")
    
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.items))
        .where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise ValueError(f"Dataset not found: {dataset_id}")
    
    for item in dataset.items:
        await db.delete(item)
    
    for item_data in version.items_snapshot:
        new_item = DatasetItem(
            dataset_id=dataset_id,
            query=item_data["query"],
            ground_truth_docs=item_data.get("ground_truth_docs"),
            ground_truth_answer=item_data.get("ground_truth_answer"),
            metadata=item_data.get("metadata")
        )
        db.add(new_item)
    
    dataset.current_version += 1
    dataset.total_items = len(version.items_snapshot)
    
    await create_version(
        db,
        dataset_id,
        f"Rolled back to version {version_number}"
    )
    
    await db.commit()
    await db.refresh(dataset)
    
    log.info(f"Rollback completed for dataset {dataset_id}")
    return dataset


async def compare_versions(
    db: AsyncSession,
    dataset_id: str,
    version1: int,
    version2: int
) -> Dict[str, Any]:
    v1 = await get_version(db, dataset_id, version1)
    v2 = await get_version(db, dataset_id, version2)
    
    if not v1 or not v2:
        raise ValueError("One or both versions not found")
    
    items1 = {item["id"]: item for item in v1.items_snapshot}
    items2 = {item["id"]: item for item in v2.items_snapshot}
    
    added = len(set(items2.keys()) - set(items1.keys()))
    removed = len(set(items1.keys()) - set(items2.keys()))
    
    modified = 0
    for item_id in set(items1.keys()) & set(items2.keys()):
        if items1[item_id] != items2[item_id]:
            modified += 1
    
    return {
        "version1": v1,
        "version2": v2,
        "items_added": added,
        "items_removed": removed,
        "items_modified": modified,
        "total_changes": added + removed + modified
    }

