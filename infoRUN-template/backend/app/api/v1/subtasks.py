from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ...services.task_service import TaskService
from ...schemas.task import (
    SubTaskResponse, SubTaskCreate, SubTaskUpdate
)
from ...core.responses import success_response
from ...core.exceptions import AppException
from ..deps import get_task_service, require_teacher, require_admin
from ...models.user import User

router = APIRouter()


@router.get("", response_model=List[SubTaskResponse])
async def get_subtasks(
    task_id: int = None,
    skip: int = 0,
    limit: int = 100,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_teacher)
):
    """Get all subtasks with optional task filtering."""
    try:
        if task_id:
            subtasks = task_service.get_subtasks(task_id, skip=skip, limit=limit)
        else:
            # This would need to be implemented in the service
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task ID is required"
            )
        
        return success_response(
            data=subtasks,
            message=f"Retrieved {len(subtasks)} subtasks"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subtasks: {str(e)}"
        )


@router.get("/{subtask_id}", response_model=SubTaskResponse)
async def get_subtask(
    subtask_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_teacher)
):
    """Get a specific subtask by ID."""
    try:
        subtask = task_service.get_subtask(subtask_id)
        return success_response(
            data=subtask,
            message="Subtask retrieved successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subtask: {str(e)}"
        )


@router.post("", response_model=SubTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    subtask_data: SubTaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_teacher)
):
    """Create a new subtask."""
    try:
        subtask = task_service.create_subtask(subtask_data)
        return success_response(
            data=subtask,
            message="Subtask created successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subtask: {str(e)}"
        )


@router.put("/{subtask_id}", response_model=SubTaskResponse)
async def update_subtask(
    subtask_id: int,
    subtask_data: SubTaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_teacher)
):
    """Update an existing subtask."""
    try:
        subtask = task_service.update_subtask(subtask_id, subtask_data)
        return success_response(
            data=subtask,
            message="Subtask updated successfully"
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subtask: {str(e)}"
        )


@router.delete("/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(require_admin)
):
    """Delete a subtask."""
    try:
        task_service.delete_subtask(subtask_id)
        return None
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subtask: {str(e)}"
        )
