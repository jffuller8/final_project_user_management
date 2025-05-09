#!/usr/bin/env python
from builtins import Exception, ValueError, bool, int, str
import os
import re
import bcrypt
from logging import getLogger

# Set up logging
logger = getLogger(__name__)

def hash_password(password: str, rounds: int = 12) -> str:
    """
    Hashes a password using bcrypt with a specified cost factor.
    
    Args:
        password (str): The plain text password to hash.
        rounds (int): The cost factor that determines the computational cost of hashing.
    
    Returns:
        str: The hashed password.
        
    Raises:
        ValueError: If hashing the password fails.
    """
    try:
        salt = bcrypt.gensalt(rounds=rounds)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to hash password: {e}")
        raise ValueError(f"Failed to hash password") from e

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    
    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The bcrypt hashed password.
    
    Returns:
        bool: True if the password is correct, False otherwise.
        
    Raises:
        ValueError: If the hashed password format is incorrect or the function fails to verify.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        raise ValueError("Authentication process encountered an unexpected error") from e

def generate_verification_token() -> str:
    """
    Generates a secure 16-byte URL-safe token.
    
    Returns:
        str: A random token suitable for email verification or password reset.
    """
    return os.urandom(16).hex()

def validate_password_strength(password: str) -> bool:
    """
    Validates that a password meets minimum security requirements.
    
    Args:
        password (str): The password to validate.
        
    Returns:
        bool: True if the password meets requirements, False otherwise.
    """
    # Minimum length
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
    if not any(c in special_chars for c in password):
        return False
    
    return True