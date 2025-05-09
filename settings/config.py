from builtins import bool, int, str
from pathlib import Path
from pydantic import Field, AnyUrl, DirectoryPath
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # App configuration
    max_login_attempts: int = Field(default=5, description="Background color of QR codes")
    server_base_url: AnyUrl = Field(default="http://localhost", description="Base URL of the server")
    # Change DirectoryPath to str or provide a default that exists
    server_download_folder: str = Field(default="downloads", description="Folder for storing downloaded files")
    
    # Security and authentication configuration
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for encryption")
    algorithm: str = Field(default="HS256", description="Algorithm used for encryption")
    access_token_expire_minutes: int = Field(default=30, description="Expiration time for access tokens in minutes")
    admin_username: str = Field(default="admin@example.com", description="Default admin username")
    admin_password: str = Field(default="secret", description="Default admin password")
    debug_mode: bool = Field(default=True, description="Debug mode outputs errors and sqlalchemy queries")
    jwt_secret_key: str = "a_very_secret_key"
    hash_algorithm: str = "bcrypt"
    jwt_algorithm: str = "HS256"
    refresh_token_expire_minutes: int = 1440  # 24 hours for refresh token
    
    # Database configuration
    database_url: str = Field(default="postgresql+asyncpg://user:password@postgres/myappdb", description="URL for connecting to the database")
    
    # Optional: If necessary, add connection URL from components
    postgres_driver: str = Field(default="postgresql+asyncpg")
    postgres_user: str = Field(default="user", description="PostgreSQL username")
    postgres_password: str = Field(default="password", description="PostgreSQL password")
    postgres_server: str = Field(default="localhost", description="PostgreSQL server address")
    postgres_port: str = Field(default="5432", description="PostgreSQL port")
    postgres_db: str = Field(default="myappdb", description="PostgreSQL database name")
    
    # Discord configuration
    discord_bot_token: str = Field(default="NONE", description="Discord bot token")
    discord_channel_id: int = Field(default=123456789, description="Default Discord channel ID for the bot to interact")
    
    # Email/SMTP configuration
    openai_api_key: str = Field(default="none", description="Open AI API Key")
    send_real_mail: bool = Field(default=False, description="Use mock")
    
    # Add the missing email configuration fields that were causing validation errors
    mail_username: str = Field(default="", description="Username for SMTP server")
    mail_password: str = Field(default="", description="Password for SMTP server")
    mail_from: str = Field(default="noreply@example.com", description="Email address to send from")
    mail_port: int = Field(default=587, description="SMTP port for sending emails")
    mail_server: str = Field(default="smtp.example.com", description="SMTP server for sending emails")
    mail_tls: bool = Field(default=True, description="Use TLS for SMTP connection")
    mail_ssl: bool = Field(default=False, description="Use SSL for SMTP connection")
    
    smtp_server: str = Field(default="smtp.mailtrip.username", description="Username for SMTP server")
    smtp_port: int = Field(default=2525, description="SMTP port for sending emails")
    smtp_username: str = Field(default="your-mailtrip-username", description="Username for SMTP server")
    smtp_password: str = Field(default="your-mailtrip-password", description="Password for SMTP server")
    
    class Config:
        # If your .env file is not in the root directory, adjust the path accordingly.
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    # Instantiate settings to be imported in your application
settings = Settings()