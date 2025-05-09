# tests/mocks/settings.py
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