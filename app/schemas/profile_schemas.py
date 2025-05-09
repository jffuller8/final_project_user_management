from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ProfileUpdate(BaseModel):
    """Schema for updating user profile information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=255)
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None

class ProfessionalStatusUpdate(BaseModel):
    """Schema for updating a user's professional status"""
    user_id: str
    is_professional: bool = False
    reason: Optional[str] = None
    
class ProfileResponse(BaseModel):
    """Response schema for profile information"""
    id: str
    email: str
    nickname: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None
    is_professional: bool
    
    class Config:
        orm_mode = True