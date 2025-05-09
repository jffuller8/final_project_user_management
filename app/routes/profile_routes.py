from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user_model import User, UserRole
from app.schemas.profile_schemas import ProfileUpdate, ProfileResponse, ProfessionalStatusUpdate
from app.services.profile_service import get_user_profile, update_user_profile, update_professional_status
from app.services.notification_service import NotificationService
from app.dependencies import get_current_user, get_current_admin

router = APIRouter(tags=["profile"])

@router.get("/profile", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current user's profile"""
    return current_user

@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update the current user's profile"""
    updated_user = await update_user_profile(db, str(current_user.id), profile_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.put("/users/{user_id}/professional-status", response_model=ProfileResponse)
async def update_user_professional_status(
    user_id: str,
    status_data: ProfessionalStatusUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's professional status.
    Only administrators can perform this action.
    """
    # Verify the user_id in the path matches the one in the request body
    if user_id != status_data.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    # Update the professional status
    updated_user = await update_professional_status(db, status_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Send notification to the user
    await NotificationService.send_status_upgrade_notification(updated_user)
    
    return updated_user

@router.get("/users/{user_id}/profile", response_model=ProfileResponse)
async def get_user_profile_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a user's profile by ID.
    Regular users can only view their own profile.
    Admins can view any profile.
    """
    # Check if the user is requesting their own profile or is an admin
    if str(current_user.id) != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )
    
    user = await get_user_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user