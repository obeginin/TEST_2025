from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from ...services.task_service import TaskService
from ...schemas.task import (
    TaskResponse, SubTaskResponse, SubjectResponse, VariantResponse,
    SubTaskCreate, SubTaskUpdate, AnswerCheckRequest, AnswerCheckResponse
)
from ...core.responses import success_response, paginated_response
from ...core.exceptions import AppException
from ..deps import get_task_service, get_current_active_user_dep, require_teacher, require_admin
from ...models.user import User

router = APIRouter()


@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get all subjects with pagination."""
    try:
        subjects = task_service.get_subjects(skip=skip, limit=limit)
        return success_response(
            data=subjects,
            message=f"Retrieved {len(subjects)} subjects"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subjects: {str(e)}"
        )


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get a specific subject by ID."""
    try:
        subject = task_service.get_subject(subject_id)
        return success_response(
            data=subject,
            message="Subject retrieved successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subject: {str(e)}"
        )


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get tasks with optional subject filtering."""
    try:
        tasks = task_service.get_tasks(subject_id=subject_id, skip=skip, limit=limit)
        return success_response(
            data=tasks,
            message=f"Retrieved {len(tasks)} tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get a specific task by ID."""
    try:
        task = task_service.get_task(task_id)
        return success_response(
            data=task,
            message="Task retrieved successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task: {str(e)}"
        )


@router.get("/{task_id}/subtasks", response_model=List[SubTaskResponse])
async def get_task_subtasks(
    task_id: int,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get all subtasks for a specific task."""
    try:
        subtasks = task_service.get_subtasks(task_id, skip=skip, limit=limit)
        return success_response(
            data=subtasks,
            message=f"Retrieved {len(subtasks)} subtasks for task {task_id}"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subtasks: {str(e)}"
        )


@router.get("/variants", response_model=List[VariantResponse])
async def get_variants(
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get all variants."""
    try:
        variants = task_service.get_variants()
        return success_response(
            data=variants,
            message=f"Retrieved {len(variants)} variants"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve variants: {str(e)}"
        )


@router.get("/variants/{variant_id}", response_model=VariantResponse)
async def get_variant(
    variant_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get a specific variant by ID."""
    try:
        variant = task_service.get_variant(variant_id)
        return success_response(
            data=variant,
            message="Variant retrieved successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve variant: {str(e)}"
        )


@router.get("/variants/{variant_id}/subtasks", response_model=List[SubTaskResponse])
async def get_variant_subtasks(
    variant_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Get all subtasks for a specific variant."""
    try:
        subtasks = task_service.get_subtasks_by_variant(variant_id)
        return success_response(
            data=subtasks,
            message=f"Retrieved {len(subtasks)} subtasks for variant {variant_id}"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve variant subtasks: {str(e)}"
        )


@router.post("/check-answer", response_model=AnswerCheckResponse)
async def check_answer(
    request: AnswerCheckRequest,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_active_user_dep)
):
    """Check if a student's answer is correct."""
    try:
        result = task_service.check_answer(request.subtask_id, request.student_answer)
        return success_response(
            data=result,
            message="Answer checked successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check answer: {str(e)}"
        )
