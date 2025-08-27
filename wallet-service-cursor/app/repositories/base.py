from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from typing import TypeVar, Generic, Type, List, Optional, Any
from ..core.exceptions import NotFoundError
import logging
from sqlalchemy import func

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository with common crud operations."""
    
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        return self.db.get(self.model, id)
    
    def get_or_404(self, id: int) -> T:
        """Get entity by ID or raise 404 error."""
        entity = self.get(id)
        if not entity:
            raise NotFoundError(self.model.__name__, str(id))
        return entity
    
    def get_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Get entity by field value."""
        stmt = select(self.model).where(getattr(self.model, field_name) == value)
        return self.db.scalar(stmt)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())
    
    def create(self, **kwargs) -> T:
        """Create new entity."""
        entity = self.model(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, id: int, **kwargs) -> T:
        """Update entity by ID."""
        entity = self.get_or_404(id)
        for key, value in kwargs.items():
            setattr(entity, key, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        entity = self.get_or_404(id)
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def count(self) -> int:
        """Count total entities."""
        stmt = select(self.model)
        return self.db.scalar(select(func.count()).select_from(stmt.subquery()))
