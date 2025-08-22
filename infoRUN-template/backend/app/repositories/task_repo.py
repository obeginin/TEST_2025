from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from .base import BaseRepository
from ..models.task import Task, SubTask, Variant, Subject
from ..models.user import User
from ..core.exceptions import NotFoundError, ConflictError
import logging

logger = logging.getLogger(__name__)


class TaskRepository(BaseRepository[Task]):
    """Repository for Task operations."""
    
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    def get_tasks_by_subject(self, subject_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by subject ID."""
        try:
            stmt = (
                select(Task)
                .where(Task.SubjectID == subject_id)
                .order_by(Task.TaskNumber)
                .offset(skip)
                .limit(limit)
            )
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            logger.error(f"Error getting tasks by subject {subject_id}: {e}")
            raise
    
    def get_task_with_subtasks(self, task_id: int) -> Optional[Task]:
        """Get task with all its subtasks."""
        try:
            stmt = (
                select(Task)
                .where(Task.TaskID == task_id)
                .options(selectinload(Task.subtasks))
            )
            return self.db.scalar(stmt)
        except Exception as e:
            logger.error(f"Error getting task with subtasks {task_id}: {e}")
            raise
    
    def get_task_by_number(self, task_number: int) -> Optional[Task]:
        """Get task by task number."""
        return self.get_by_field("TaskNumber", task_number)
    
    def create_task(self, task_number: int, task_title: str, subject_id: int) -> Task:
        """Create a new task."""
        # Check if task number already exists
        existing_task = self.get_task_by_number(task_number)
        if existing_task:
            raise ConflictError(f"Task with number {task_number} already exists")
        
        return self.create(
            TaskNumber=task_number,
            TaskTitle=task_title,
            SubjectID=subject_id
        )


class SubTaskRepository(BaseRepository[SubTask]):
    """Repository for SubTask operations."""
    
    def __init__(self, db: Session):
        super().__init__(SubTask, db)
    
    def get_subtasks_by_task(self, task_id: int, skip: int = 0, limit: int = 100) -> List[SubTask]:
        """Get subtasks by task ID."""
        try:
            stmt = (
                select(SubTask)
                .where(SubTask.TaskID == task_id)
                .order_by(SubTask.SubTaskNumber)
                .offset(skip)
                .limit(limit)
            )
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            logger.error(f"Error getting subtasks by task {task_id}: {e}")
            raise
    
    def get_subtasks_by_variant(self, variant_id: int) -> List[SubTask]:
        """Get subtasks by variant ID."""
        try:
            stmt = (
                select(SubTask)
                .where(SubTask.VariantID == variant_id)
                .order_by(SubTask.SubTaskNumber)
            )
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            logger.error(f"Error getting subtasks by variant {variant_id}: {e}")
            raise
    
    def get_subtask_with_files(self, subtask_id: int) -> Optional[SubTask]:
        """Get subtask with all its files."""
        try:
            stmt = (
                select(SubTask)
                .where(SubTask.SubTaskID == subtask_id)
                .options(selectinload(SubTask.files))
            )
            return self.db.scalar(stmt)
        except Exception as e:
            logger.error(f"Error getting subtask with files {subtask_id}: {e}")
            raise
    
    def get_next_subtask_number(self, task_id: int) -> int:
        """Get the next available subtask number for a task."""
        try:
            stmt = (
                select(func.coalesce(func.max(SubTask.SubTaskNumber), 0))
                .where(SubTask.TaskID == task_id)
            )
            max_number = self.db.scalar(stmt) or 0
            return max_number + 1
        except Exception as e:
            logger.error(f"Error getting next subtask number for task {task_id}: {e}")
            raise
    
    def create_subtask(self, task_id: int, subtask_number: int, **kwargs) -> SubTask:
        """Create a new subtask."""
        # Check if subtask number already exists for this task
        existing_subtask = self.db.scalar(
            select(SubTask)
            .where(SubTask.TaskID == task_id, SubTask.SubTaskNumber == subtask_number)
        )
        if existing_subtask:
            raise ConflictError(f"Subtask with number {subtask_number} already exists for task {task_id}")
        
        return self.create(TaskID=task_id, SubTaskNumber=subtask_number, **kwargs)
    
    def update_subtask(self, subtask_id: int, **kwargs) -> SubTask:
        """Update a subtask."""
        subtask = self.get_or_404(subtask_id)
        
        # If updating subtask number, check for conflicts
        if "SubTaskNumber" in kwargs:
            existing_subtask = self.db.scalar(
                select(SubTask)
                .where(
                    SubTask.TaskID == subtask.TaskID,
                    SubTask.SubTaskNumber == kwargs["SubTaskNumber"],
                    SubTask.SubTaskID != subtask_id
                )
            )
            if existing_subtask:
                raise ConflictError(f"Subtask with number {kwargs['SubTaskNumber']} already exists for task {subtask.TaskID}")
        
        return self.update(subtask_id, **kwargs)


class VariantRepository(BaseRepository[Variant]):
    """Repository for Variant operations."""
    
    def __init__(self, db: Session):
        super().__init__(Variant, db)
    
    def get_variant_by_name(self, variant_name: str) -> Optional[Variant]:
        """Get variant by name."""
        return self.get_by_field("VariantName", variant_name)
    
    def get_or_create_variant(self, variant_name: str, description: Optional[str] = None) -> Variant:
        """Get existing variant or create new one."""
        variant = self.get_variant_by_name(variant_name)
        if variant:
            return variant
        
        return self.create(VariantName=variant_name, Description=description)


class SubjectRepository(BaseRepository[Subject]):
    """Repository for Subject operations."""
    
    def __init__(self, db: Session):
        super().__init__(Subject, db)
    
    def get_subject_by_name(self, name: str) -> Optional[Subject]:
        """Get subject by name."""
        return self.get_by_field("Name", name)
    
    def get_subjects_with_task_count(self) -> List[Dict[str, Any]]:
        """Get subjects with their task counts."""
        try:
            stmt = (
                select(
                    Subject.ID,
                    Subject.Name,
                    Subject.Description,
                    func.count(Task.TaskID).label("task_count")
                )
                .outerjoin(Task, Subject.ID == Task.SubjectID)
                .group_by(Subject.ID, Subject.Name, Subject.Description)
                .order_by(Subject.Name)
            )
            result = self.db.execute(stmt)
            return [
                {
                    "id": row.ID,
                    "name": row.Name,
                    "description": row.Description,
                    "task_count": row.task_count or 0
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting subjects with task count: {e}")
            raise
