"""
Tests for account lockout and auto-unlock functionality.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.models.user_model import User

@pytest.mark.asyncio
async def test_account_locks_after_failed_attempts(async_client, verified_user, db_session):
    """Test that an account gets locked after multiple failed login attempts."""
    
    # Attempt multiple failed logins
    for _ in range(6):  # Assuming max_login_attempts is 5
        response = await async_client.post(
            "/login/",
            data={"username": verified_user.email, "password": "WrongPassword!123"}
        )
    
    # Check if user is locked in database
    await db_session.refresh(verified_user)
    assert verified_user.is_locked == True
    assert verified_user.locked_at is not None
    
    # Try to login with correct password
    response = await async_client.post(
        "/login/",
        data={"username": verified_user.email, "password": "MySuperPassword$1234"}
    )
    
    # Should fail because account is locked
    assert response.status_code == 400
    assert "locked" in response.text.lower()

@pytest.mark.asyncio
async def test_account_auto_unlocks_after_timeout(db_session, locked_user):
    """Test that a locked account automatically unlocks after the timeout period."""
    
    # Set the locked_at timestamp to over an hour ago
    locked_user.locked_at = datetime.now(timezone.utc) - timedelta(hours=2)
    db_session.add(locked_user)
    await db_session.commit()
    
    # Check if account is automatically unlocked when checking lock status
    from app.services.user_service import UserService
    is_locked = await UserService.is_account_locked(db_session, locked_user.email)
    
    # Should be automatically unlocked
    assert is_locked == False
    
    # Verify user state in database
    await db_session.refresh(locked_user)
    assert locked_user.is_locked == False
    assert locked_user.failed_login_attempts == 0