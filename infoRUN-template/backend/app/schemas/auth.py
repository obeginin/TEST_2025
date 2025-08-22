from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from .common import BaseSchema


class LoginRequest(BaseSchema):
    """Login request schema."""
    
    identifier: str = Field(..., description="Login, email, or phone number")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseSchema):
    """Login response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse" = Field(..., description="User information")


class RegisterRequest(BaseSchema):
    """User registration request schema."""
    
    login: str = Field(..., min_length=3, max_length=50, description="Unique login")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    middle_name: Optional[str] = Field(None, max_length=50, description="Middle name")
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ChangePasswordRequest(BaseSchema):
    """Change password request schema."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(BaseSchema):
    """User response schema."""
    
    id: int = Field(..., description="User ID")
    login: str = Field(..., description="User login")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    role_id: int = Field(..., description="User role ID")
    is_active: bool = Field(..., description="User active status")
    is_confirmed: bool = Field(..., description="Email confirmation status")
    full_name: str = Field(..., description="Full name")
    
    @field_validator("full_name", mode="before")
    @classmethod
    def generate_full_name(cls, v, info):
        if "first_name" in info.data and "last_name" in info.data:
            parts = [info.data["last_name"], info.data["first_name"]]
            if info.data.get("middle_name"):
                parts.append(info.data["middle_name"])
            return " ".join(parts)
        return v


class TokenData(BaseSchema):
    """Token data schema."""
    
    user_id: Optional[int] = Field(None, description="User ID from token")
    exp: Optional[int] = Field(None, description="Token expiration timestamp")
