from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..repositories.task_repo import TaskRepository, SubTaskRepository, VariantRepository, SubjectRepository
from ..schemas.task import (
    SubTaskCreate, SubTaskUpdate, TaskResponse, SubTaskResponse,
    SubjectResponse, VariantResponse, TaskListResponse, SubTaskListResponse
)
from ..core.exceptions import NotFoundError, ValidationError
from ..core.responses import paginated_response
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.subtask_repo = SubTaskRepository(db)
        self.variant_repo = VariantRepository(db)
        self.subject_repo = SubjectRepository(db)
    
    def get_subjects(self, skip: int = 0, limit: int = 100) -> List[SubjectResponse]:
        """Get all subjects with pagination."""
        subjects = self.subject_repo.get_all(skip=skip, limit=limit)
        return [SubjectResponse(
            id=subject.ID,
            name=subject.Name,
            description=subject.Description
        ) for subject in subjects]
    
    def get_subject(self, subject_id: int) -> SubjectResponse:
        """Get a specific subject."""
        subject = self.subject_repo.get_or_404(subject_id)
        return SubjectResponse(
            id=subject.ID,
            name=subject.Name,
            description=subject.Description
        )
    
    def get_tasks(self, subject_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        """Get tasks with optional subject filtering."""
        if subject_id:
            tasks = self.task_repo.get_tasks_by_subject(subject_id, skip=skip, limit=limit)
        else:
            tasks = self.task_repo.get_all(skip=skip, limit=limit)
        
        return [TaskResponse(
            task_id=task.TaskID,
            task_number=task.TaskNumber,
            task_title=task.TaskTitle,
            subject_id=task.SubjectID,
            subject=SubjectResponse(
                id=task.subject.ID,
                name=task.subject.Name,
                description=task.subject.Description
            ) if task.subject else None
        ) for task in tasks]
    
    def get_task(self, task_id: int) -> TaskResponse:
        """Get a specific task."""
        task = self.task_repo.get_or_404(task_id)
        return TaskResponse(
            task_id=task.TaskID,
            task_number=task.TaskNumber,
            task_title=task.TaskTitle,
            subject_id=task.SubjectID,
            subject=SubjectResponse(
                id=task.subject.ID,
                name=task.subject.Name,
                description=task.subject.Description
            ) if task.subject else None
        )
    
    def get_subtasks(self, task_id: int, skip: int = 0, limit: int = 100) -> List[SubTaskResponse]:
        """Get subtasks for a specific task."""
        # Verify task exists
        self.task_repo.get_or_404(task_id)
        
        subtasks = self.subtask_repo.get_subtasks_by_task(task_id, skip=skip, limit=limit)
        return [SubTaskResponse(
            subtask_id=subtask.SubTaskID,
            task_id=subtask.TaskID,
            subtask_number=subtask.SubTaskNumber,
            variant_id=subtask.VariantID,
            variant_name=subtask.variant.VariantName if subtask.variant else None,
            description=subtask.Description,
            answer=subtask.Answer,
            image_path=subtask.ImagePath,
            solution_path=subtask.SolutionPath
        ) for subtask in subtasks]
    
    def get_subtask(self, subtask_id: int) -> SubTaskResponse:
        """Get a specific subtask."""
        subtask = self.subtask_repo.get_or_404(subtask_id)
        return SubTaskResponse(
            subtask_id=subtask.SubTaskID,
            task_id=subtask.TaskID,
            subtask_number=subtask.SubTaskNumber,
            variant_id=subtask.VariantID,
            variant_name=subtask.variant.VariantName if subtask.variant else None,
            description=subtask.Description,
            answer=subtask.Answer,
            image_path=subtask.ImagePath,
            solution_path=subtask.SolutionPath
        )
    
    def create_subtask(self, subtask_data: SubTaskCreate) -> SubTaskResponse:
        """Create a new subtask."""
        # Verify task exists
        self.task_repo.get_or_404(subtask_data.task_id)
        
        # Handle variant
        variant_id = None
        if subtask_data.variant_id:
            variant = self.variant_repo.get_or_404(subtask_data.variant_id)
            variant_id = variant.VariantID
        
        # Create subtask
        subtask = self.subtask_repo.create_subtask(
            task_id=subtask_data.task_id,
            subtask_number=subtask_data.subtask_number,
            VariantID=variant_id,
            Description=subtask_data.description,
            Answer=subtask_data.answer
        )
        
        return SubTaskResponse(
            subtask_id=subtask.SubTaskID,
            task_id=subtask.TaskID,
            subtask_number=subtask.SubTaskNumber,
            variant_id=subtask.VariantID,
            variant_name=subtask.variant.VariantName if subtask.variant else None,
            description=subtask.Description,
            answer=subtask.Answer,
            image_path=subtask.ImagePath,
            solution_path=subtask.SolutionPath
        )
    
    def update_subtask(self, subtask_id: int, subtask_data: SubTaskUpdate) -> SubTaskResponse:
        """Update an existing subtask."""
        # Get existing subtask
        subtask = self.subtask_repo.get_or_404(subtask_id)
        
        # Prepare update data
        update_data = {}
        if subtask_data.subtask_number is not None:
            update_data["SubTaskNumber"] = subtask_data.subtask_number
        if subtask_data.variant_id is not None:
            # Verify variant exists
            self.variant_repo.get_or_404(subtask_data.variant_id)
            update_data["VariantID"] = subtask_data.variant_id
        if subtask_data.description is not None:
            update_data["Description"] = subtask_data.description
        if subtask_data.answer is not None:
            update_data["Answer"] = subtask_data.answer
        
        # Update subtask
        updated_subtask = self.subtask_repo.update_subtask(subtask_id, **update_data)
        
        return SubTaskResponse(
            subtask_id=updated_subtask.SubTaskID,
            task_id=updated_subtask.TaskID,
            subtask_number=updated_subtask.SubTaskNumber,
            variant_id=updated_subtask.VariantID,
            variant_name=updated_subtask.variant.VariantName if updated_subtask.variant else None,
            description=updated_subtask.Description,
            answer=updated_subtask.Answer,
            image_path=updated_subtask.ImagePath,
            solution_path=updated_subtask.SolutionPath
        )
    
    def delete_subtask(self, subtask_id: int) -> bool:
        """Delete a subtask."""
        return self.subtask_repo.delete(subtask_id)
    
    def get_variants(self) -> List[VariantResponse]:
        """Get all variants."""
        variants = self.variant_repo.get_all()
        return [VariantResponse(
            variant_id=variant.VariantID,
            variant_name=variant.VariantName,
            description=variant.Description
        ) for variant in variants]
    
    def get_variant(self, variant_id: int) -> VariantResponse:
        """Get a specific variant."""
        variant = self.variant_repo.get_or_404(variant_id)
        return VariantResponse(
            variant_id=variant.VariantID,
            variant_name=variant.VariantName,
            description=variant.Description
        )
    
    def get_subtasks_by_variant(self, variant_id: int) -> List[SubTaskResponse]:
        """Get all subtasks for a specific variant."""
        # Verify variant exists
        self.variant_repo.get_or_404(variant_id)
        
        subtasks = self.subtask_repo.get_subtasks_by_variant(variant_id)
        return [SubTaskResponse(
            subtask_id=subtask.SubTaskID,
            task_id=subtask.TaskID,
            subtask_number=subtask.SubTaskNumber,
            variant_id=subtask.VariantID,
            variant_name=subtask.variant.VariantName if subtask.variant else None,
            description=subtask.Description,
            answer=subtask.Answer,
            image_path=subtask.ImagePath,
            solution_path=subtask.SolutionPath
        ) for subtask in subtasks]
    
    def check_answer(self, subtask_id: int, student_answer: str) -> Dict[str, Any]:
        """Check if a student's answer is correct."""
        subtask = self.subtask_repo.get_or_404(subtask_id)
        
        if not subtask.Answer:
            raise ValidationError("This subtask does not have a correct answer configured")
        
        is_correct = student_answer.strip().lower() == subtask.Answer.strip().lower()
        
        return {
            "subtask_id": subtask_id,
            "student_answer": student_answer,
            "correct_answer": subtask.Answer,
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0
        }
