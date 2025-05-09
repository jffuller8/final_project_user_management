"""
This Python file is part of a FastAPI application, demonstrating user management functionalities including creating, reading,
updating, and deleting (CRUD) user information. It uses OAuth2 with Password Flow for security, ensuring that only authenticated
users can perform certain operations.
"""

from builtins import dict, int, len, str
from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db, get_email_service, require_role
from app.schemas.pagination_schema import EnhancedPagination
from app.schemas.token_schema import TokenResponse
from app.schemas.user_schemas import LoginRequest, UserBase, UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.services.jwt_service import create_access_token
from app.utils.link_generation import create_user_links, generate_pagination_links
from app.dependencies import get_settings
from app.services.email_service import EmailService
import time
import asyncio
from typing import Dict, List
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
settings = get_settings()
logger = logging.getLogger(__name__)

# Rate limiting for authentication endpoints
auth_request_timestamps: Dict[str, List[float]] = {}
MAX_REQUESTS_PER_MINUTE = 5
RATE_LIMIT_WINDOW = 60  # seconds

async def check_rate_limit(client_ip: str) -> float:
    """Check rate limit for an IP and return delay time in seconds"""
    now = time.time()
    
    if client_ip not in auth_request_timestamps:
        auth_request_timestamps[client_ip] = []
    
    # Clean old timestamps
    auth_request_timestamps[client_ip] = [
        t for t in auth_request_timestamps[client_ip] 
        if now - t < RATE_LIMIT_WINDOW
    ]
    
    # Calculate requests in the time window
    request_count = len(auth_request_timestamps[client_ip])
    
    # Record this request timestamp
    auth_request_timestamps[client_ip].append(now)
    
    # If too many requests, implement exponential backoff
    if request_count >= MAX_REQUESTS_PER_MINUTE:
        delay = min(2 ** (request_count - MAX_REQUESTS_PER_MINUTE), 30)
        logger.warning(f"Rate limiting applied to {client_ip}: {delay}s delay")
        return delay
    
    return 0

@router.get("/users/{user_id}", response_model=UserResponse, name="get_user", tags=["User Management Requires (Admin or Manager Roles)"])
async def get_user(user_id: UUID, request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Endpoint to fetch a user by their unique identifier (UUID).
    """
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_construct(
        id=user.id,
        nickname=user.nickname,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        profile_picture_url=user.profile_picture_url,
        github_profile_url=user.github_profile_url,
        linkedin_profile_url=user.linkedin_profile_url,
        role=user.role,
        email=user.email,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        links=create_user_links(user.id, request)  
    )

@router.put("/users/{user_id}", response_model=UserResponse, name="update_user", tags=["User Management Requires (Admin or Manager Roles)"])
async def update_user(user_id: UUID, user_update: UserUpdate, request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Update user information.
    """
    user_data = user_update.model_dump(exclude_unset=True)
    updated_user = await UserService.update(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_construct(
        id=updated_user.id,
        bio=updated_user.bio,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        nickname=updated_user.nickname,
        email=updated_user.email,
        role=updated_user.role,
        last_login_at=updated_user.last_login_at,
        profile_picture_url=updated_user.profile_picture_url,
        github_profile_url=updated_user.github_profile_url,
        linkedin_profile_url=updated_user.linkedin_profile_url,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        links=create_user_links(updated_user.id, request)
    )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_user", tags=["User Management Requires (Admin or Manager Roles)"])
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Delete a user by their ID.
    """
    success = await UserService.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["User Management Requires (Admin or Manager Roles)"], name="create_user")
async def create_user(user: UserCreate, request: Request, db: AsyncSession = Depends(get_db), email_service: EmailService = Depends(get_email_service), token: str = Depends(oauth2_scheme), current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))):
    """
    Create a new user.
    """
    existing_user = await UserService.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    created_user = await UserService.create(db, user.model_dump(), email_service)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user - password may be too weak")
    
    return UserResponse.model_construct(
        id=created_user.id,
        bio=created_user.bio,
        first_name=created_user.first_name,
        last_name=created_user.last_name,
        profile_picture_url=created_user.profile_picture_url,
        nickname=created_user.nickname,
        email=created_user.email,
        role=created_user.role,
        last_login_at=created_user.last_login_at,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at,
        links=create_user_links(created_user.id, request)
    )

@router.get("/users/", response_model=UserListResponse, tags=["User Management Requires (Admin or Manager Roles)"])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role(["ADMIN", "MANAGER"]))
):
    total_users = await UserService.count(db)
    users = await UserService.list_users(db, skip, limit)

    user_responses = [
        UserResponse.model_validate(user) for user in users
    ]
    
    pagination_links = generate_pagination_links(request, skip, limit, total_users)
    
    # Construct the final response with pagination details
    return UserListResponse(
        items=user_responses,
        total=total_users,
        page=skip // limit + 1 if limit > 0 else 1,
        size=len(user_responses),
        links=pagination_links
    )

@router.post("/register/", response_model=UserResponse, tags=["Login and Registration"])
async def register(
    user_data: UserCreate, 
    request: Request, 
    session: AsyncSession = Depends(get_db), 
    email_service: EmailService = Depends(get_email_service)
):
    # Apply rate limiting
    client_ip = request.client.host if request.client else "unknown"
    delay = await check_rate_limit(client_ip)
    if delay > 0:
        await asyncio.sleep(delay)
        
    user = await UserService.register_user(session, user_data.model_dump())
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="Registration failed - email may already exist or password is too weak"
        )
        
    return UserResponse.model_construct(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        profile_picture_url=user.profile_picture_url,
        github_profile_url=user.github_profile_url,
        linkedin_profile_url=user.linkedin_profile_url,
        role=user.role,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        links=create_user_links(user.id, request)
    )

@router.post("/login/", response_model=TokenResponse, tags=["Login and Registration"])
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_db)
):
    # Apply rate limiting
    client_ip = request.client.host if request.client else "unknown"
    delay = await check_rate_limit(client_ip)
    if delay > 0:
        await asyncio.sleep(delay)
        
    if await UserService.is_account_locked(session, form_data.username):
        raise HTTPException(
            status_code=400, 
            detail="Account locked due to too many failed login attempts. Try again later or request account unlock."
        )

    user = await UserService.login_user(session, form_data.username, form_data.password)
    if user:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

        access_token = create_access_token(
            data={"sub": user.email, "role": str(user.role.name)},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect email or password.")

@router.get("/verify-email/{user_id}/{token}", status_code=status.HTTP_200_OK, name="verify_email", tags=["Login and Registration"])
async def verify_email(
    user_id: UUID, 
    token: str, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user's email with a provided token.
    """
    # Apply rate limiting
    client_ip = request.client.host if request.client else "unknown"
    delay = await check_rate_limit(client_ip)
    if delay > 0:
        await asyncio.sleep(delay)
        
    if await UserService.verify_email_with_token(db, user_id, token):
        return {"message": "Email verified successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Invalid or expired verification token"
    )

@router.post("/request-verification-email/", status_code=status.HTTP_200_OK, tags=["Login and Registration"])
async def request_verification_email(
    request: Request,
    email: str,
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Request a new verification email if the current one expired.
    """
    # Apply rate limiting
    client_ip = request.client.host if request.client else "unknown"
    delay = await check_rate_limit(client_ip)
    if delay > 0:
        await asyncio.sleep(delay)
        
    user = await UserService.get_by_email(db, email)
    
    # Don't reveal if email exists for security reasons
    if not user or user.email_verified:
        return {"message": "If your email exists and is not verified, a new verification email has been sent"}
    
    # Generate new verification token
    if await UserService.generate_new_verification_token(db, email):
        # Refresh user data with new token
        user = await UserService.get_by_email(db, email)
        await email_service.send_verification_email(user)
    
    return {"message": "If your email exists and is not verified, a new verification email has been sent"}