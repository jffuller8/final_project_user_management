from app.models.user_model import User
from app.dependencies import get_settings

class NotificationService:
    """Service for sending notifications to users"""
    
    @staticmethod
    async def send_status_upgrade_notification(user: User) -> bool:
        """
        Send notification to user about professional status upgrade.
        
        In a real application, this would send an actual email.
        For this implementation, we'll just log the notification.
        """
        status = "upgraded to" if user.is_professional else "removed from"
        message = f"Your professional status has been {status} professional."
        
        # For demo purposes, just print to console
        # In a real app, this would send an email or other notification
        print(f"[NOTIFICATION] To: {user.email} - {message}")
        
        # Log the notification (in a real app, this would be more robust)
        print(f"[LOG] Professional status notification sent to {user.email}")
        
        return True