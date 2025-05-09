"""
File: conftest.py

Overview:
This Python test file utilizes pytest to manage database states and HTTP clients for testing a web application built with FastAPI and SQLAlchemy. It includes detailed fixtures to mock the testing environment, ensuring each test is run in isolation with a consistent setup.
"""

# Standard library imports
from builtins import Exception, range, str
from datetime import timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

# Third-party imports
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from faker import Faker

# Application-specific imports
from app.main import app
from app.database import Base
from app.models.user_model import User, UserRole
from app.utils.security import hash_password
from app.services.jwt_service import create_access_token

# Import mocks first to avoid circular dependencies
from tests.mocks.settings import get_mock_settings

# Mock implementation for settings
class MockSettings:
    max_login_attempts = 5
    access_token_expire_minutes = 30
    database_url = "sqlite+aiosqlite:///:memory:"
    server_base_url = "http://localhost"
    send_real_mail = False
    smtp_server = "mock-smtp-server"
    smtp_port = 587
    smtp_username = "mock-username"
    smtp_password = "mock-password"

def get_mock_settings():
    return MockSettings()

# Mock implementation for template manager and email service
class MockTemplateManager:
    def render_template(self, template_name, context):
        return f"Rendered template {template_name} with context {context}"

class MockEmailService:
    def __init__(self, template_manager=None):
        self.template_manager = template_manager or MockTemplateManager()
        
    async def send_verification_email(self, user):
        # Mock implementation
        return True
        
    async def send_user_email(self, user_data, email_type):
        # Mock implementation
        return True

# Set up Faker for generating test data
fake = Faker()

# Database setup for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)

# Override dependencies to avoid circular imports
@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # Patch the get_settings function to return our mock
    monkeypatch.setattr("app.dependencies.get_settings", get_mock_settings)
    
    # If you need to patch other dependencies, add them here
    mock_email_service = MockEmailService(MockTemplateManager())
    monkeypatch.setattr("app.dependencies.get_email_service", lambda: mock_email_service)

@pytest.fixture
def email_service():
    return MockEmailService(MockTemplateManager())

@pytest.fixture(scope="function")
async def async_client(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Override the get_db dependency to use our test session
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()

# Patch the get_db function to avoid circular imports
def get_db():
    pass

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # you can comment out this line during development if you are debugging a single test
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture(scope="function")
async def locked_user(db_session):
    unique_email = fake.email()
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "username": unique_email,  # Added to match User model requirements
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": True,
        "failed_login_attempts": 5,  # Using mock_settings.max_login_attempts
        "locked_at": fake.date_time_this_year(),  # Add locked_at timestamp
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def user(db_session):
    unique_email = fake.email()
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "username": unique_email,  # Added to match User model requirements
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def verified_user(db_session):
    unique_email = fake.email()
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "username": unique_email,  # Added to match User model requirements
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def unverified_user(db_session):
    unique_email = fake.email()
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "username": unique_email,  # Added to match User model requirements
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    users = []
    for _ in range(50):
        unique_email = fake.email()
        user_data = {
            "nickname": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": unique_email,
            "username": unique_email,  # Added to match User model requirements
            "hashed_password": fake.password(),
            "role": UserRole.AUTHENTICATED,
            "email_verified": False,
            "is_locked": False,
        }
        user = User(**user_data)
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    return users

@pytest.fixture
async def admin_user(db_session: AsyncSession):
    unique_email = fake.email()
    user = User(
        nickname="admin_user",
        email=unique_email,
        username=unique_email,  # Added to match User model requirements
        first_name="Admin",
        last_name="User",
        hashed_password=hash_password("SecureAdmin$1234"),
        role=UserRole.ADMIN,
        is_locked=False,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
async def manager_user(db_session: AsyncSession):
    unique_email = fake.email()
    user = User(
        nickname="manager_john",
        first_name="Manager",
        last_name="User",
        email=unique_email,
        username=unique_email,  # Added to match User model requirements
        hashed_password=hash_password("SecureManager$1234"),
        role=UserRole.MANAGER,
        is_locked=False,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user

# Configure a fixture for each type of user role you want to test
@pytest.fixture(scope="function")
def admin_token(admin_user):
    # Assuming admin_user has an 'id' and 'role' attribute
    token_data = {"sub": admin_user.email, "role": admin_user.role.name}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))

@pytest.fixture(scope="function")
def manager_token(manager_user):
    token_data = {"sub": manager_user.email, "role": manager_user.role.name}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))

@pytest.fixture(scope="function")
def user_token(user):
    token_data = {"sub": user.email, "role": user.role.name}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))