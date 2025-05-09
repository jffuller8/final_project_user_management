"""
Tests for email verification token expiration.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.utils.security import generate_verification_token

@pytest.mark.asyncio
async def test_verification_token_expires(async_client, db_session, unverified_user):
    """Test that verification tokens expire after the specified time."""
    
    # Set a verification token and expired creation timestamp
    unverified_user.verification_token = generate_verification_token()
    unverified_user.verification_token_created_at = datetime.now(timezone.utc) - timedelta(hours=49)  # Older than 48 hours
    db_session.add(unverified_user)
    await db_session.commit()
    
    # Try to verify with the expired token
    response = await async_client.get(
        f"/verify-email/{unverified_user.id}/{unverified_user.verification_token}"
    )
    
    # Should fail with expired token message
    assert response.status_code == 400
    assert "expired" in response.text.lower() or "invalid" in response.text.lower()
    
    # Verify user is still unverified in database
    await db_session.refresh(unverified_user)
    assert unverified_user.email_verified == False

@pytest.mark.asyncio
async def test_verification_token_valid(async_client, db_session, unverified_user):
    """Test that verification tokens work when they're not expired."""
    
    # Set a verification token with recent timestamp
    unverified_user.verification_token = generate_verification_token()
    unverified_user.verification_token_created_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.add(unverified_user)
    await db_session.commit()
    
    # Try to verify with the valid token
    response = await async_client.get(
        f"/verify-email/{unverified_user.id}/{unverified_user.verification_token}"
    )
    
    # Should succeed
    assert response.status_code == 200
    
    # Verify user is now verified in database
    await db_session.refresh(unverified_user)
    assert unverified_user.email_verified == True