# tests/test_password_validation_simple.py
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