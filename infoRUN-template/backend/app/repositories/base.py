from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from ..models.base import Base
from ..core.exceptions import NotFoundError, DatabaseError
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common crud operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        try:
            return self.db.get(self.model, id)
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to retrieve {self.model.__name__}")
    
    def get_or_404(self, id: int) -> ModelType:
        """Get a single record by ID or raise 404."""
        obj = self.get(id)
        if obj is None:
            raise NotFoundError(self.model.__name__, str(id))
        return obj
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        try:
            stmt = select(self.model).offset(skip).limit(limit)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to retrieve {self.model.__name__} list")
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        try:
            obj = self.model(**kwargs)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create {self.model.__name__}")
    
    def update(self, id: int, **kwargs) -> ModelType:
        """Update an existing record."""
        try:
            obj = self.get_or_404(id)
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to update {self.model.__name__}")
    
    def delete(self, id: int) -> bool:
        """Delete a record."""
        try:
            obj = self.get_or_404(id)
            self.db.delete(obj)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to delete {self.model.__name__}")
    
    def count(self) -> int:
        """Count total records."""
        try:
            stmt = select(self.model)
            return self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to count {self.model.__name__}")
    
    def exists(self, id: int) -> bool:
        """Check if record exists."""
        try:
            return self.db.get(self.model, id) is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {e}")
            return False
    
    def filter_by(self, **kwargs) -> List[ModelType]:
        """Filter records by given criteria."""
        try:
            stmt = select(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            logger.error(f"Error filtering {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to filter {self.model.__name__}")
    
    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get a single record by field value."""
        try:
            if not hasattr(self.model, field):
                raise ValueError(f"Field {field} does not exist in {self.model.__name__}")
            
            stmt = select(self.model).where(getattr(self.model, field) == value)
            return self.db.scalar(stmt)
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field}={value}: {e}")
            raise DatabaseError(f"Failed to retrieve {self.model.__name__}")
    
    def get_by_field_or_404(self, field: str, value: Any) -> ModelType:
        """Get a single record by field value or raise 404."""
        obj = self.get_by_field(field, value)
        if obj is None:
            raise NotFoundError(self.model.__name__, f"{field}={value}")
        return obj
