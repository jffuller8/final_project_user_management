from datetime import datetime, timedelta
from enum import Enum
import uuid
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, func, Time as SQLAlchemyTime
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class UserRole(Enum):
    """Enumeration of user roles within the application, stored as ENUM in the database."""
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"

class User(Base):
    """Represents a user within the application, corresponding to the 'users' table in the database.
    This class uses SQLAlchemy ORM for mapping attributes to database columns efficiently.
    """
    __tablename__ = "users"
    # Remove the defaults keyword which is causing the error
    # __mapper_args__ = {"defaults": True}
    
    # Primary attributes
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Personal information
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    bio: Mapped[str] = mapped_column(String(255), nullable=True)
    profile_picture_url: Mapped[str] = mapped_column(String(255), nullable=True)
    linkedin_profile_url: Mapped[str] = mapped_column(String(255), nullable=True)
    github_profile_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # User status
    role: Mapped[UserRole] = mapped_column(SQLAlchemyTime(UserRole), name="UserRole", create_constraint=True, nullable=False)
    is_professional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    professional_status_updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    
    # Authentication and security
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    locked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # New field for account lockout
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    verification_token: Mapped[str] = mapped_column(String, nullable=True)
    verification_token_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # New field for token expiration
    
    def __repr__(self) -> str:
        """Provides a readable representation of a user object."""
        return f"User({self.nickname}, Role: {self.role.name})"
    
    def lock_account(self):
        """Locks the user account."""
        self.is_locked = True
        self.locked_at = datetime.now()
    
    def unlock_account(self):
        """Unlocks the user account."""
        self.is_locked = False
        self.failed_login_attempts = 0
        self.locked_at = None
        
    def verify_email(self):
        """Marks the email as verified."""
        self.email_verified = True
        self.verification_token = None
        self.verification_token_created_at = None
        
    def has_role(self, role_name: UserRole) -> bool:
        """Checks if the user has a specified role."""
        return self.role == role_name
    
    def update_professional_status(self, status: bool):
        """Updates the professional status and logs the update time."""
        self.is_professional = status
        self.professional_status_updated_at = datetime.now()
        
    def is_verification_token_expired(self) -> bool:
        """Check if the verification token has expired (48 hours)."""
        if not self.verification_token_created_at:
            return True
        return (datetime.now() - self.verification_token_created_at) > timedelta(hours=48)
        
    def should_auto_unlock(self) -> bool:
        """Check if account should be automatically unlocked (1 hour lockout)."""
        if not self.locked_at:
            return False
        return (datetime.now() - self.locked_at) > timedelta(hours=1)