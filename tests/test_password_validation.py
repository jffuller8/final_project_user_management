"""
Tests for password strength validation functionality.
"""
import pytest
from app.utils.security import validate_password_strength

def test_password_strength_validation():
    """Test that password strength validation works correctly."""
    
    # Should pass - good password
    assert validate_password_strength("StrongP@ss123") == True
    
    # Should fail - too short
    assert validate_password_strength("Short1!") == False
    
    # Should fail - no uppercase
    assert validate_password_strength("password123!") == False
    
    # Should fail - no lowercase
    assert validate_password_strength("PASSWORD123!") == False
    
    # Should fail - no digits
    assert validate_password_strength("Password!") == False
    
    # Should fail - no special characters
    assert validate_password_strength("Password123") == False

@pytest.mark.asyncio
async def test_user_creation_with_weak_password(async_client, email_service):
    """Test that user creation fails with a weak password."""
    
    # Try to create a user with a weak password
    response = await async_client.post(
        "/register/",
        json={
            "email": "newuser@example.com",
            "password": "weak",  # Missing uppercase, digits, special chars
            "nickname": "weakuser",
            "role": "AUTHENTICATED"
        }
    )
    
    # Should fail
    assert response.status_code == 400
    assert "password" in response.text.lower()

@pytest.mark.asyncio
async def test_user_creation_with_strong_password(async_client, email_service):
    """Test that user creation succeeds with a strong password."""
    
    # Create a user with a strong password
    response = await async_client.post(
        "/register/",
        json={
            "email": "stronguser@example.com",
            "password": "StrongP@ss123",
            "nickname": "stronguser",
            "role": "AUTHENTICATED"
        }
    )
    
    # Should succeed
    assert response.status_code == 201, f"Response: {response.text}"