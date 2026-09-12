"""Pydantic schemas for request/response validation"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.VOLUNTEER


class UserCreate(UserBase):
    """User registration schema"""
    password: str = Field(..., min_length=12)
    confirm_password: str = Field(..., min_length=12)

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v: str, values: dict) -> str:
        """Ensure passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema (without password)"""
    id: int
    is_active: bool
    is_verified: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    password: str = Field(..., min_length=12)
    confirm_password: str = Field(..., min_length=12)

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = False
    error: dict = Field(
        ...,
        example={
            "code": "INVALID_CREDENTIALS",
            "message": "Email or password is incorrect",
            "field": "password"
        }
    )


class SuccessResponse(BaseModel):
    """Standardized success response"""
    success: bool = True
    data: Optional[dict] = None
    message: Optional[str] = None
