from sqlalchemy import BigInteger, String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from .base import Base


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "Users"
    
    ID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    Login: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    Email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    Password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Personal information
    First_Name: Mapped[str] = mapped_column(String(50), nullable=False)
    Last_Name: Mapped[str] = mapped_column(String(50), nullable=False)
    Middle_Name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Additional fields
    RoleID: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1=Admin, 2=Teacher, 3=Student
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    IsConfirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    IsDeleted: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student_tasks = relationship("StudentTask", back_populates="student")
    
    def __repr__(self):
        return f"<User(id={self.ID}, login='{self.Login}', email='{self.Email}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = [self.Last_Name, self.First_Name]
        if self.Middle_Name:
            parts.append(self.Middle_Name)
        return " ".join(parts)
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.RoleID == 1
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is teacher."""
        return self.RoleID == 2
    
    @property
    def is_student(self) -> bool:
        """Check if user is student."""
        return self.RoleID == 3
