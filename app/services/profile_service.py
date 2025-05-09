from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user_model import User
from app.schemas.profile_schemas import ProfileUpdate, ProfessionalStatusUpdate
from datetime import datetime

async def get_user_profile(db: AsyncSession, user_id: str) -> User:
    """Get user profile by user ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def update_user_profile(db: AsyncSession, user_id: str, profile_data: ProfileUpdate) -> User:
    """Update user profile information"""
    user = await get_user_profile(db, user_id)
    if not user:
        return None
        
    # Update only fields that are provided
    update_data = profile_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
        
    # Update the updated_at timestamp
    user.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(user)
    return user

async def update_professional_status(db: AsyncSession, status_data: ProfessionalStatusUpdate) -> User:
    """Update user's professional status"""
    user = await get_user_profile(db, status_data.user_id)
    if not user:
        return None
        
    user.is_professional = status_data.is_professional
    user.professional_status_updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(user)
    return user