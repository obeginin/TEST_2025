from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator, Optional
from ..core.database import get_db
from ..core.security import get_current_user, get_current_active_user, require_admin
from ..models.user import User
from ..services.task_service import TaskService
from ..repositories.task_repo import TaskRepository, SubTaskRepository, VariantRepository, SubjectRepository

# Database dependency
def get_database() -> Generator[Session, None, None]:
    """Get database session."""
    return get_db()

# Service dependencies
def get_task_service(db: Session = Depends(get_database)) -> TaskService:
    """Get task service instance."""
    return TaskService(db)

def get_task_repository(db: Session = Depends(get_database)) -> TaskRepository:
    """Get task repository instance."""
    return TaskRepository(db)

def get_subtask_repository(db: Session = Depends(get_database)) -> SubTaskRepository:
    """Get subtask repository instance."""
    return SubTaskRepository(db)

def get_variant_repository(db: Session = Depends(get_database)) -> VariantRepository:
    """Get variant repository instance."""
    return VariantRepository(db)

def get_subject_repository(db: Session = Depends(get_database)) -> SubjectRepository:
    """Get subject repository instance."""
    return SubjectRepository(db)

# Authentication dependencies
def get_current_user_dep() -> User:
    """Get current authenticated user."""
    return get_current_user()

def get_current_active_user_dep() -> User:
    """Get current active user."""
    return get_current_active_user()

def get_admin_user() -> User:
    """Get current admin user."""
    return require_admin()

# Optional authentication for public endpoints
def get_optional_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    return current_user

# Role-based access control
def require_teacher(current_user: User = Depends(get_current_active_user_dep)) -> User:
    """Require teacher role."""
    if current_user.RoleID != 2:  # Assuming 2 is teacher role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user

def require_student(current_user: User = Depends(get_current_active_user_dep)) -> User:
    """Require student role."""
    if current_user.RoleID != 3:  # Assuming 3 is student role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user
