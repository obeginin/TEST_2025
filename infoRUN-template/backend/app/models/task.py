from sqlalchemy import Integer, String, Text, ForeignKey, DECIMAL, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from .base import Base


class Task(Base):
    """Task model representing task categories."""
    
    __tablename__ = "Tasks"
    
    TaskID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    TaskNumber: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    TaskTitle: Mapped[str] = mapped_column(String(255), nullable=False)
    SubjectID: Mapped[int] = mapped_column(Integer, ForeignKey("Subjects.ID"), nullable=False)
    
    # Relationships
    subject = relationship("Subject", back_populates="tasks")
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.TaskID}, number={self.TaskNumber}, title='{self.TaskTitle}')>"


class SubTask(Base):
    """SubTask model representing individual tasks."""
    
    __tablename__ = "SubTasks"
    
    SubTaskID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    TaskID: Mapped[int] = mapped_column(Integer, ForeignKey("Tasks.TaskID"), nullable=False)
    SubTaskNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    VariantID: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Variants.VariantID"), nullable=True)
    
    # Content fields
    Description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    Answer: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    # File paths
    ImagePath: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    SolutionPath: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="subtasks")
    variant = relationship("Variant", back_populates="subtasks")
    files = relationship("SubTaskFile", back_populates="subtask", cascade="all, delete-orphan")
    student_tasks = relationship("StudentTask", back_populates="subtask")
    
    def __repr__(self):
        return f"<SubTask(id={self.SubTaskID}, task_id={self.TaskID}, number={self.SubTaskNumber})>"


class Variant(Base):
    """Variant model for task variants."""
    
    __tablename__ = "Variants"
    
    VariantID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    VariantName: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    Description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    subtasks = relationship("SubTask", back_populates="variant")
    
    def __repr__(self):
        return f"<Variant(id={self.VariantID}, name='{self.VariantName}')>"


class SubTaskFile(Base):
    """File attachments for subtasks."""
    
    __tablename__ = "SubTaskFiles"
    
    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    SubTaskID: Mapped[int] = mapped_column(Integer, ForeignKey("SubTasks.SubTaskID"), nullable=False)
    FileName: Mapped[str] = mapped_column(String(255), nullable=False)
    FilePath: Mapped[str] = mapped_column(String(500), nullable=False)
    FileSize: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ContentType: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    UploadDate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    subtask = relationship("SubTask", back_populates="files")
    
    def __repr__(self):
        return f"<SubTaskFile(id={self.ID}, filename='{self.FileName}')>"


class StudentTask(Base):
    """Student task completion tracking."""
    
    __tablename__ = "StudentTasks"
    
    StudentTaskID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    StudentID: Mapped[int] = mapped_column(Integer, ForeignKey("Users.ID"), nullable=False)
    SubTaskID: Mapped[int] = mapped_column(Integer, ForeignKey("SubTasks.SubTaskID"), nullable=False)
    
    # Completion data
    StudentAnswer: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    CompletionStatus: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")
    Score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    CompletionDate: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    SolutionStudentPath: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    student = relationship("User", back_populates="student_tasks")
    subtask = relationship("SubTask", back_populates="student_tasks")
    
    def __repr__(self):
        return f"<StudentTask(id={self.StudentTaskID}, student_id={self.StudentID}, subtask_id={self.SubTaskID})>"
