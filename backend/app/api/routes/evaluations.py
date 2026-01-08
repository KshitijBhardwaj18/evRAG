"""
Evaluation API routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...db.session import get_db
from ...schemas.evaluation import EvaluationRunCreate, EvaluationRunResponse, EvaluationResultResponse, RunComparison
from ...services import evaluation_service
from ...core.logging import log

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("", response_model=EvaluationRunResponse, status_code=201)
async def create_evaluation_run(
    run_data: EvaluationRunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create and start an evaluation run.
    The evaluation runs in the background.
    """
    try:
        # Create run
        run = await evaluation_service.create_evaluation_run(db, run_data)
        
        # Execute in background
        background_tasks.add_task(
            _execute_run_background,
            run.id
        )
        
        return run
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Error creating evaluation run: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[EvaluationRunResponse])
async def list_evaluation_runs(
    dataset_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List evaluation runs"""
    runs = await evaluation_service.list_evaluation_runs(db, dataset_id, skip, limit)
    return runs


@router.get("/{run_id}", response_model=EvaluationRunResponse)
async def get_evaluation_run(
    run_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get an evaluation run"""
    run = await evaluation_service.get_evaluation_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/results", response_model=List[EvaluationResultResponse])
async def get_run_results(
    run_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all results for an evaluation run"""
    run = await evaluation_service.get_run_with_results(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.results


@router.get("/compare/{run_id_1}/{run_id_2}")
async def compare_runs(
    run_id_1: str,
    run_id_2: str,
    db: AsyncSession = Depends(get_db)
):
    """Compare two evaluation runs"""
    try:
        comparison = await evaluation_service.compare_runs(db, run_id_1, run_id_2)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error(f"Error comparing runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_run_background(run_id: str):
    """Execute evaluation run in background"""
    from ...db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            await evaluation_service.execute_evaluation_run(db, run_id)
        except Exception as e:
            log.error(f"Background execution failed for run {run_id}: {e}")

