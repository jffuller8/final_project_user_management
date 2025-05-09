"""
Tests for the login route functionality.
"""
import pytest

@pytest.mark.asyncio
async def test_login_route(async_client, verified_user):
    """Test that the login route works correctly."""
    
    # Successful login
    response = await async_client.post(
        "/login/",
        data={"username": verified_user.email, "password": "MySuperPassword$1234"}
    )
    
    # Should succeed
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_with_incorrect_credentials(async_client, verified_user):
    """Test login with incorrect credentials."""
    
    # Incorrect password
    response = await async_client.post(
        "/login/",
        data={"username": verified_user.email, "password": "WrongPassword123!"}
    )
    
    # Should fail
    assert response.status_code == 401
    assert "incorrect" in response.text.lower()

@pytest.mark.asyncio
async def test_login_with_unverified_email(async_client, unverified_user):
    """Test login with unverified email."""
    
    # Login with unverified email
    response = await async_client.post(
        "/login/",
        data={"username": unverified_user.email, "password": "MySuperPassword$1234"}
    )
    
    # Should fail
    assert response.status_code == 401