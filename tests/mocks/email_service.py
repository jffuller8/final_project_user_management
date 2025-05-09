# tests/mocks/email_service.py
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