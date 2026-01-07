"""
Evaluation service for managing evaluation runs
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from ..db.models import EvaluationRun, EvaluationResult, DatasetItem, RunStatus
from ..schemas.evaluation import EvaluationRunCreate
from ..evaluation.runner import EvaluationRunner, load_embedding_model
from ..rag.pipelines import create_rag_pipeline
from ..core.logging import log
from ..core.config import settings


async def create_evaluation_run(
    db: AsyncSession,
    run_data: EvaluationRunCreate
) -> EvaluationRun:
    """
    Create a new evaluation run.
    
    Args:
        db: Database session
        run_data: Run creation data
        
    Returns:
        Created evaluation run
    """
    log.info(f"Creating evaluation run: {run_data.name}")
    
    # Get dataset to count items
    from .dataset_service import get_dataset
    dataset = await get_dataset(db, run_data.dataset_id)
    if not dataset:
        raise ValueError(f"Dataset not found: {run_data.dataset_id}")
    
    # Create run
    run = EvaluationRun(
        dataset_id=run_data.dataset_id,
        name=run_data.name,
        description=run_data.description,
        status=RunStatus.PENDING,
        rag_endpoint=run_data.rag_endpoint,
        rag_config=run_data.rag_config,
        total_items=dataset.total_items
    )
    
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    log.info(f"Evaluation run created with ID: {run.id}")
    return run


async def execute_evaluation_run(
    db: AsyncSession,
    run_id: str
) -> EvaluationRun:
    """
    Execute an evaluation run.
    This runs all evaluations for the dataset.
    
    Args:
        db: Database session
        run_id: Run ID
        
    Returns:
        Updated evaluation run
    """
    log.info(f"Executing evaluation run: {run_id}")
    
    # Get run with dataset items
    result = await db.execute(
        select(EvaluationRun)
        .options(selectinload(EvaluationRun.dataset).selectinload('items'))
        .where(EvaluationRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise ValueError(f"Run not found: {run_id}")
    
    if run.status == RunStatus.RUNNING:
        raise ValueError("Run is already running")
    
    # Update status
    run.status = RunStatus.RUNNING
    run.started_at = datetime.utcnow()
    await db.commit()
    
    try:
        # Initialize evaluation components
        embedding_model = load_embedding_model()
        evaluator = EvaluationRunner(
            embedding_model=embedding_model,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Create RAG pipeline
        if run.rag_endpoint:
            rag_pipeline = create_rag_pipeline(run.rag_endpoint, "api")
        else:
            log.warning("No RAG endpoint provided, using mock pipeline")
            rag_pipeline = create_rag_pipeline(pipeline_type="mock")
        
        # Process each dataset item
        all_results = []
        
        for item in run.dataset.items:
            log.info(f"Evaluating item {run.completed_items + 1}/{run.total_items}")
            
            try:
                # Query RAG pipeline
                rag_response = await rag_pipeline.query(
                    item.query,
                    run.rag_config
                )
                
                # Evaluate
                eval_result = evaluator.evaluate_single(
                    query=item.query,
                    retrieved_docs=rag_response["retrieved_docs"],
                    generated_answer=rag_response["generated_answer"],
                    ground_truth_docs=item.ground_truth_docs,
                    ground_truth_answer=item.ground_truth_answer
                )
                
                # Store result
                result_record = EvaluationResult(
                    run_id=run.id,
                    dataset_item_id=item.id,
                    retrieved_docs=rag_response["retrieved_docs"],
                    generated_answer=rag_response["generated_answer"],
                    recall_at_k=eval_result.get("recall_at_k"),
                    precision_at_k=eval_result.get("precision_at_k"),
                    mrr=eval_result.get("mrr"),
                    map_score=eval_result.get("map_score"),
                    hit_rate=eval_result.get("hit_rate"),
                    coverage=eval_result.get("coverage"),
                    faithfulness=eval_result.get("faithfulness"),
                    answer_relevance=eval_result.get("answer_relevance"),
                    context_utilization=eval_result.get("context_utilization"),
                    semantic_similarity=eval_result.get("semantic_similarity"),
                    rouge_l=eval_result.get("rouge_l"),
                    f1_score=eval_result.get("f1_score"),
                    hallucination_score=eval_result.get("hallucination_score"),
                    hallucinated_spans=eval_result.get("hallucinated_spans"),
                    citation_coverage=eval_result.get("citation_coverage"),
                    metrics_detail=eval_result
                )
                
                db.add(result_record)
                all_results.append(eval_result)
                
                # Update progress
                run.completed_items += 1
                await db.commit()
                
            except Exception as e:
                log.error(f"Error evaluating item {item.id}: {e}")
                # Continue with next item
                continue
        
        # Calculate aggregate metrics
        aggregate_metrics = evaluator.calculate_aggregate_metrics(all_results)
        run.metrics = aggregate_metrics
        
        # Mark as completed
        run.status = RunStatus.COMPLETED
        run.completed_at = datetime.utcnow()
        await db.commit()
        
        log.info(f"Evaluation run completed: {run_id}")
        
    except Exception as e:
        log.error(f"Error executing evaluation run: {e}")
        run.status = RunStatus.FAILED
        run.error_message = str(e)
        await db.commit()
        raise
    
    await db.refresh(run)
    return run


async def get_evaluation_run(db: AsyncSession, run_id: str) -> Optional[EvaluationRun]:
    """Get an evaluation run by ID"""
    result = await db.execute(
        select(EvaluationRun).where(EvaluationRun.id == run_id)
    )
    return result.scalar_one_or_none()


async def get_run_with_results(db: AsyncSession, run_id: str) -> Optional[EvaluationRun]:
    """Get evaluation run with all results"""
    result = await db.execute(
        select(EvaluationRun)
        .options(selectinload(EvaluationRun.results))
        .where(EvaluationRun.id == run_id)
    )
    return result.scalar_one_or_none()


async def list_evaluation_runs(
    db: AsyncSession,
    dataset_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[EvaluationRun]:
    """List evaluation runs"""
    query = select(EvaluationRun).offset(skip).limit(limit).order_by(EvaluationRun.created_at.desc())
    
    if dataset_id:
        query = query.where(EvaluationRun.dataset_id == dataset_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def compare_runs(
    db: AsyncSession,
    run_id_1: str,
    run_id_2: str
) -> Dict[str, Any]:
    """
    Compare two evaluation runs.
    
    Args:
        db: Database session
        run_id_1: First run ID
        run_id_2: Second run ID
        
    Returns:
        Comparison data
    """
    run1 = await get_evaluation_run(db, run_id_1)
    run2 = await get_evaluation_run(db, run_id_2)
    
    if not run1 or not run2:
        raise ValueError("One or both runs not found")
    
    if run1.dataset_id != run2.dataset_id:
        log.warning("Comparing runs from different datasets")
    
    # Calculate deltas
    metrics1 = run1.metrics or {}
    metrics2 = run2.metrics or {}
    
    deltas = {}
    improvements = {}
    
    for key in metrics1.keys():
        if key in metrics2 and isinstance(metrics1[key], (int, float)):
            delta = metrics2[key] - metrics1[key]
            deltas[key] = round(delta, 4)
            
            if metrics1[key] != 0:
                improvement_pct = (delta / abs(metrics1[key])) * 100
                improvements[key] = round(improvement_pct, 2)
    
    return {
        "run1": run1,
        "run2": run2,
        "metric_deltas": deltas,
        "improvement_pct": improvements
    }

