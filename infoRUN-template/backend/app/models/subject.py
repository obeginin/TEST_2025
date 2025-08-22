from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base


class Subject(Base):
    """Subject model for educational subjects."""
    
    __tablename__ = "Subjects"
    
    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    Description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="subject")
    
    def __repr__(self):
        return f"<Subject(id={self.ID}, name='{self.Name}')>"
