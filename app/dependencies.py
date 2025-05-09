from builtins import Exception, dict, str
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Database
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService
from app.services.jwt_service import decode_token
from settings.config import Settings

def get_settings() -> Settings:
    """Return application settings."""
    return Settings()

def get_email_service() -> EmailService:
    """Create and return an email service."""
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

async def get_db() -> AsyncSession:
    """Dependency that provides a database session for each request."""
    async_session_factory = Database.get_session_factory()
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate and extract user information from the JWT token.
    
    Args:
        token (str): JWT token from the Authorization header
    
    Returns:
        dict: A dictionary containing user_id and role
    
    Raises:
        HTTPException: If token is invalid or missing required claims
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        
        if user_id is None or user_role is None:
            raise credentials_exception
        
        return {"user_id": user_id, "role": user_role}
    
    except Exception:
        raise credentials_exception

def require_role(role: str | list[str]):
    """
    Create a dependency to check user roles.
    
    Args:
        role (str | list[str]): Required role(s) to access the endpoint
    
    Returns:
        Callable: A dependency function that checks user roles
    
    Raises:
        HTTPException: If user does not have the required role
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        # Convert single role to list if needed
        required_roles = [role] if isinstance(role, str) else role
        
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        return current_user
    
    return role_checker