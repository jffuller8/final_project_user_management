from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone, timedelta
import secrets
from typing import Optional, Dict, List
from pydantic import ValidationError
from sqlalchemy import func, null, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_email_service, get_settings
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password, validate_password_strength
from uuid import UUID
from app.services.email_service import EmailService
from app.models.user_model import UserRole
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class UserService:
    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            raise

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        try:
            query = select(User).filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user: {e}")
            return None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str) -> Optional[User]:
        return await cls._fetch_user(session, username=username)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        try:
            # Validate password strength first
            if not validate_password_strength(user_data.get('password', '')):
                logger.warning("User creation failed: Password does not meet strength requirements")
                return None
                
            # Validate incoming data
            validated_data = UserCreate(**user_data).model_dump()
            
            # Check for existing email
            existing_user = await cls.get_by_email(session, validated_data['email'])
            if existing_user:
                logger.warning(f"User with email {validated_data['email']} already exists")
                return None
                
            # Hash password
            validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            
            # Create user object
            new_user = User(**validated_data)
            
            # Generate unique nickname
            new_nickname = generate_nickname()
            while await cls.get_by_nickname(session, new_nickname):
                new_nickname = generate_nickname()
            new_user.nickname = new_nickname
            
            # Set appropriate role
            user_count = await cls.count(session)
            new_user.role = UserRole.ADMIN if user_count == 0 else UserRole.ANONYMOUS
            logger.info(f"Creating user with role: {new_user.role}")
            
            # Handle email verification
            if new_user.role == UserRole.ADMIN:
                new_user.email_verified = True
                new_user.verification_token = None
            else:
                new_user.email_verified = False
                new_user.verification_token = generate_verification_token()
                new_user.verification_token_created_at = datetime.now(timezone.utc)
                try:
                    await email_service.send_verification_email(new_user)
                except Exception as e:
                    logger.error(f"Failed to send verification email: {e}")
                    # Continue with user creation even if email fails

            # Save user to database
            session.add(new_user)
            await session.commit()
            logger.info(f"User created successfully: {new_user.id}")
            return new_user
            
        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error during user creation: {e}")
            await session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            await session.rollback()
            return None

    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            # Check if user exists
            user = await cls.get_by_id(session, user_id)
            if not user:
                logger.warning(f"Cannot update non-existent user: {user_id}")
                return None
            
            # Validate password strength if provided
            if 'password' in update_data and not validate_password_strength(update_data['password']):
                logger.warning(f"Password update failed: Does not meet strength requirements")
                return None
                
            # Validate update data
            validated_data = UserUpdate(**update_data).model_dump(exclude_unset=True)
            
            # Handle password updates
            if 'password' in validated_data:
                validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
                
            # Perform update
            query = (
                update(User)
                .where(User.id == user_id)
                .values(**validated_data)
                .execution_options(synchronize_session="fetch")
            )
            
            await session.execute(query)
            await session.commit()
            
            # Refresh and return updated user
            updated_user = await cls.get_by_id(session, user_id)
            if updated_user:
                await session.refresh(updated_user)
                logger.info(f"User {user_id} updated successfully")
                return updated_user
            else:
                logger.error(f"User {user_id} not found after update")
                return None
                
        except ValidationError as e:
            logger.error(f"Validation error during user update: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error during user update: {e}")
            await session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error during user update: {e}")
            await session.rollback()
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found.")
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str]) -> Optional[User]:
        email_service = get_email_service()
        return await cls.create(session, user_data, email_service)
    
    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
        """
        Check if a user account is locked and handle automatic unlocking.
        """
        try:
            user = await cls.get_by_email(session, email)
            if not user or not user.is_locked:
                return False
                
            # Check if account should be automatically unlocked (1 hour lockout)
            if user.locked_at and (datetime.now(timezone.utc) - user.locked_at > timedelta(hours=1)):
                # Auto-unlock the account
                user.is_locked = False
                user.failed_login_attempts = 0
                user.locked_at = None
                session.add(user)
                await session.commit()
                logger.info(f"Account {email} automatically unlocked after timeout period")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error checking account lock status: {e}")
            return False

    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        try:
            user = await cls.get_by_email(session, email)
            if not user:
                return None
                
            # Check account status
            if await cls.is_account_locked(session, email):  # Use the updated method
                return None
                
            if not user.email_verified:
                return None
                
            # Verify password
            if verify_password(password, user.hashed_password):
                # Successful login
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                return user
            else:
                # Failed login
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.is_locked = True
                    user.locked_at = datetime.now(timezone.utc)  # Record lock time
                    logger.warning(f"Account {email} locked after {user.failed_login_attempts} failed attempts")
                
                session.add(user)
                await session.commit()
                return None
        except Exception as e:
            logger.error(f"Error during login: {e}")
            await session.rollback()
            return None

    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        # Validate password strength
        if not validate_password_strength(new_password):
            logger.warning(f"Password reset failed: New password does not meet strength requirements")
            return False
            
        hashed_password = hash_password(new_password)
        user = await cls.get_by_id(session, user_id)
        if user:
            user.hashed_password = hashed_password
            user.failed_login_attempts = 0  # Resetting failed login attempts
            user.is_locked = False  # Unlocking the user account, if locked
            user.locked_at = None  # Clear the locked timestamp
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user or not user.verification_token or user.verification_token != token:
            return False
            
        # Check if token is expired (48 hours)
        if not user.verification_token_created_at or (
            datetime.now(timezone.utc) - user.verification_token_created_at > timedelta(hours=48)
        ):
            logger.warning(f"Expired verification token used for user {user_id}")
            return False
            
        # Valid token
        user.email_verified = True
        user.verification_token = None
        user.verification_token_created_at = None
        user.role = UserRole.AUTHENTICATED
        
        session.add(user)
        await session.commit()
        logger.info(f"Email verified successfully for user {user_id}")
        return True

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        """
        Count the number of users in the database.

        :param session: The AsyncSession instance for database access.
        :return: The count of users.
        """
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        count = result.scalar()
        return count
    
    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0  # Reset failed login attempts
            user.locked_at = None  # Clear the locked timestamp
            session.add(user)
            await session.commit()
            return True
        return False
        
    @classmethod
    async def generate_new_verification_token(cls, session: AsyncSession, email: str) -> bool:
        """Generate a new verification token for a user."""
        try:
            user = await cls.get_by_email(session, email)
            if not user or user.email_verified:
                # Don't reveal if user exists for security
                return False
                
            user.verification_token = generate_verification_token()
            user.verification_token_created_at = datetime.now(timezone.utc)
            
            session.add(user)
            await session.commit()
            
            # Return true to indicate token was generated
            return True
            
        except Exception as e:
            logger.error(f"Error generating new verification token: {e}")
            await session.rollback()
            return False