from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from .common import BaseSchema, PaginationParams


class SubjectResponse(BaseSchema):
    """Subject response schema."""
    
    id: int = Field(..., description="Subject ID")
    name: str = Field(..., description="Subject name")
    description: Optional[str] = Field(None, description="Subject description")


class TaskResponse(BaseSchema):
    """Task response schema."""
    
    task_id: int = Field(..., description="Task ID")
    task_number: int = Field(..., description="Task number")
    task_title: str = Field(..., description="Task title")
    subject_id: int = Field(..., description="Subject ID")
    subject: Optional[SubjectResponse] = Field(None, description="Subject information")


class SubTaskResponse(BaseSchema):
    """SubTask response schema."""
    
    subtask_id: int = Field(..., description="SubTask ID")
    task_id: int = Field(..., description="Task ID")
    subtask_number: int = Field(..., description="SubTask number")
    variant_id: Optional[int] = Field(None, description="Variant ID")
    variant_name: Optional[str] = Field(None, description="Variant name")
    description: Optional[str] = Field(None, description="Task description")
    answer: Optional[str] = Field(None, description="Correct answer")
    image_path: Optional[str] = Field(None, description="Image file path")
    solution_path: Optional[str] = Field(None, description="Solution file path")


class SubTaskCreate(BaseSchema):
    """SubTask creation request schema."""
    
    task_id: int = Field(..., gt=0, description="Task ID")
    subtask_number: int = Field(..., gt=0, description="SubTask number")
    variant_id: Optional[int] = Field(None, gt=0, description="Variant ID")
    description: Optional[str] = Field(None, description="Task description")
    answer: Optional[str] = Field(None, max_length=32, description="Correct answer")
    
    @field_validator("subtask_number")
    @classmethod
    def validate_subtask_number(cls, v):
        if v <= 0:
            raise ValueError("SubTask number must be positive")
        return v


class SubTaskUpdate(BaseSchema):
    """SubTask update request schema."""
    
    subtask_number: Optional[int] = Field(None, gt=0, description="SubTask number")
    variant_id: Optional[int] = Field(None, gt=0, description="Variant ID")
    description: Optional[str] = Field(None, description="Task description")
    answer: Optional[str] = Field(None, max_length=32, description="Correct answer")
    
    @field_validator("subtask_number")
    @classmethod
    def validate_subtask_number(cls, v):
        if v is not None and v <= 0:
            raise ValueError("SubTask number must be positive")
        return v


class VariantResponse(BaseSchema):
    """Variant response schema."""
    
    variant_id: int = Field(..., description="Variant ID")
    variant_name: str = Field(..., description="Variant name")
    description: Optional[str] = Field(None, description="Variant description")


class VariantCreate(BaseSchema):
    """Variant creation request schema."""
    
    variant_name: str = Field(..., min_length=1, max_length=100, description="Variant name")
    description: Optional[str] = Field(None, description="Variant description")


class FileResponse(BaseSchema):
    """File response schema."""
    
    id: int = Field(..., description="File ID")
    filename: str = Field(..., description="File name")
    file_path: str = Field(..., description="File path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="File content type")
    upload_date: datetime = Field(..., description="Upload timestamp")


class StudentTaskResponse(BaseSchema):
    """Student task response schema."""
    
    student_task_id: int = Field(..., description="Student task ID")
    student_id: int = Field(..., description="Student ID")
    subtask_id: int = Field(..., description="SubTask ID")
    student_answer: Optional[str] = Field(None, description="Student's answer")
    completion_status: str = Field(..., description="Completion status")
    score: Optional[float] = Field(None, description="Task score")
    completion_date: Optional[datetime] = Field(None, description="Completion timestamp")
    solution_student_path: Optional[str] = Field(None, description="Student solution file path")


class AnswerCheckRequest(BaseSchema):
    """Answer check request schema."""
    
    subtask_id: int = Field(..., gt=0, description="SubTask ID")
    student_answer: str = Field(..., description="Student's answer")


class AnswerCheckResponse(BaseSchema):
    """Answer check response schema."""
    
    subtask_id: int = Field(..., description="SubTask ID")
    student_answer: str = Field(..., description="Student's answer")
    correct_answer: str = Field(..., description="Correct answer")
    is_correct: bool = Field(..., description="Answer correctness")
    score: Optional[float] = Field(None, description="Earned score")


class TaskListResponse(BaseSchema):
    """Task list response schema."""
    
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class SubTaskListResponse(BaseSchema):
    """SubTask list response schema."""
    
    subtasks: List[SubTaskResponse] = Field(..., description="List of subtasks")
    total: int = Field(..., description="Total number of subtasks")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class SubjectListResponse(BaseSchema):
    """Subject list response schema."""
    
    subjects: List[SubjectResponse] = Field(..., description="List of subjects")
    total: int = Field(..., description="Total number of subjects")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
