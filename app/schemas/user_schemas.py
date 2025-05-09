from builtins import import ValueError, any, bool, str
import re
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID

from app.models.user_model import UserRole
from app.utils.nickname_gen import generate_nickname
from app.utils.security import validate_password_strength

def validate_url(url: Optional[str]) -> Optional[str]:
    """
    Validates if a URL is properly formatted.
    
    Args:
        url: URL to validate or None
        
    Returns:
        The validated URL or None
        
    Raises:
        ValueError: If URL format is invalid
    """
    if url is None:
        return None
        
    url_regex = r"^https?://[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_+.~#?&/=]*$"
    if not re.match(url_regex, url):
        raise ValueError("Invalid URL format")
        
    return url

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[str] = Field(None, min_length=3, pattern=r"[a-zA-Z0-9_-]+", example=generate_nickname())
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    role: UserRole
    
    # URL validation for all profile URLs
    validate_urls = validator("profile_picture_url", "linkedin_profile_url", "github_profile_url", pre=True, allow_reuse=True)(validate_url)

class UserCreate(UserBase):
    """Schema for user creation requests"""
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure@1234")
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength"""
        if not validate_password_strength(v):
            raise ValueError(
                "Password must be at least 8 characters and include uppercase letters, "
                "lowercase letters, numbers, and special characters"
            )
        return v

class UserUpdate(BaseModel):
    """Schema for user update requests"""
    nickname: Optional[str] = Field(None, min_length=3, pattern=r"[a-zA-Z0-9_-]+", example="john_doe123")
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    password: Optional[str] = Field(None, example="NewPassword@2023")

    # URL validation for all profile URLs
    validate_urls = validator("profile_picture_url", "linkedin_profile_url", "github_profile_url", pre=True, allow_reuse=True)(validate_url)
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength"""
        if v is not None and not validate_password_strength(v):
            raise ValueError(
                "Password must be at least 8 characters and include uppercase letters, "
                "lowercase letters, numbers, and special characters"
            )
        return v
    
    @root_validator(pre=True)
    def check_at_least_one_value(cls, values):
        """Ensure at least one field is provided for update"""
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

class LoginRequest(BaseModel):
    """Schema for login requests"""
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure@1234")

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., example="Not found")
    details: Optional[str] = Field(None, example="The requested resource was not found.")

class UserResponse(BaseModel):
    """Schema for user responses with navigation links"""
    id: UUID
    email: EmailStr
    nickname: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    profile_picture_url: Optional[str]
    github_profile_url: Optional[str]
    linkedin_profile_url: Optional[str]
    role: UserRole
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    links: dict

class UserListResponse(BaseModel):
    """Schema for paginated user list responses"""
    items: List[UserResponse]
    total: int
    page: int
    size: int
    links: dict