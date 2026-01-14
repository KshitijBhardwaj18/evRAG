from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...db.session import get_db
from ...schemas.version import DatasetVersionResponse, DatasetVersionCreate, VersionComparison
from ...services import version_service
from ...core.logging import log

router = APIRouter(prefix="/datasets/{dataset_id}/versions", tags=["versions"])


@router.get("", response_model=List[DatasetVersionResponse])
async def list_versions(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        versions = await version_service.list_versions(db, dataset_id)
        return versions
    except Exception as e:
        log.error(f"Error listing versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{version_number}", response_model=DatasetVersionResponse)
async def get_version(
    dataset_id: str,
    version_number: int,
    db: AsyncSession = Depends(get_db)
):
    version = await version_service.get_version(db, dataset_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.post("", response_model=DatasetVersionResponse, status_code=201)
async def create_version(
    dataset_id: str,
    version_data: DatasetVersionCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        version = await version_service.create_version(
            db,
            dataset_id,
            version_data.changes_summary
        )
        return version
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error(f"Error creating version: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{version_number}/rollback")
async def rollback_version(
    dataset_id: str,
    version_number: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        dataset = await version_service.rollback_to_version(db, dataset_id, version_number)
        return {"message": f"Rolled back to version {version_number}", "dataset_id": dataset.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error(f"Error rolling back version: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{version1}/{version2}", response_model=VersionComparison)
async def compare_versions(
    dataset_id: str,
    version1: int,
    version2: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        comparison = await version_service.compare_versions(db, dataset_id, version1, version2)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error(f"Error comparing versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

