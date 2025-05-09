#!/usr/bin/env python
from builtins import import ValueError, dict, str
from typing import Optional, Dict
from smtplib import SMTP, SMTPException
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User
from app.dependencies import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class EmailService:
    """
    Service for sending various types of emails to users
    """
    
    def __init__(self, template_manager: TemplateManager):
        """
        Initialize the email service with required dependencies
        
        Args:
            template_manager: Manager for rendering email templates
        """
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager
    
    async def send_user_email(self, user_data: dict, email_type: str):
        """
        Sends an email to a user based on the specified type
        
        Args:
            user_data: Dictionary containing user information
            email_type: Type of email to send (verification, password_reset, etc.)
            
        Raises:
            ValueError: If the email type is invalid
        """
        subject_map = {
            "email_verification": "Verify Your Account",
            "password_reset": "Password Reset Instructions",
            "account_locked": "Account Locked Notification"
        }
        
        if email_type not in subject_map:
            raise ValueError(f"Invalid email type")
        
        html_content = self.template_manager.render_template(email_type, user_data)
        
        try:
            await self.smtp_client.send_email(
                subject=subject_map[email_type],
                html_content=html_content,
                user_data=user_data
            )
            logger.info(f"Sent {email_type} email to {user_data.get('email')}")
            return True
        except SMTPException as e:
            # Log the error and consider a retry mechanism
            logger.error(f"Failed to send {email_type} email: {str(e)}")
            return False
    
    async def send_verification_email(self, user: User):
        """
        Sends a verification email to a newly registered user
        
        Args:
            user: User object containing email and verification token
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        verification_url = f"{settings.server_base_url}/verify-email/{user.id}/{user.verification_token}"
        
        user_data = {
            "name": user.first_name or user.nickname or "User",
            "verification_url": verification_url,
            "email": user.email,
            "expiry_hours": 48  # Token expires after 48 hours
        }
        
        return await self.send_user_email(
            user_data=user_data,
            email_type="email_verification"
        )