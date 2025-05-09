# User Management System

A comprehensive user management backend system built with FastAPI, PostgreSQL, and Docker.

## Features

- **User Registration and Authentication**: Secure user registration with email verification
- **JWT Authentication**: Secure token-based authentication
- **Email Service**: Email notifications for account verification and password reset
- **Database Management**: PostgreSQL with Alembic migrations
- **Containerization**: Docker and Docker Compose setup for development and deployment
- **Testing**: Comprehensive testing suite with pytest

## Project Setup

### Prerequisites

- Docker and Docker Compose
- Git
- MailTrap account (for email testing)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/jffuller8/final_project_user_management.git
   cd final_project_user_management

Create a .env file in the project root with your MailTrap credentials:
MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_FROM=from@example.com
MAIL_PORT=2525
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_TLS=True
MAIL_SSL=False

Build and start the Docker containers:
bashdocker compose up --build

Run the Alembic migrations to set up the database:
bashdocker compose exec fastapi alembic upgrade head


Database Management
The project uses PostgreSQL as the database and Alembic for migrations.
PGAdmin Setup

Access PGAdmin at http://localhost:5050
Login with credentials (from docker-compose.yml):

Email: admin@example.com (or as configured)
Password: adminpassword (or as configured)


Add a new server with these connection details:

Host: postgres
Port: 5432
Database: myappdb
Username: user
Password: password



Alembic Commands

Create a new migration:
bashdocker compose exec fastapi alembic revision --autogenerate -m "description"

Apply migrations:
bashdocker compose exec fastapi alembic upgrade head


API Documentation
Once the application is running, you can access the API documentation at:

Swagger UI: http://localhost/docs
ReDoc: http://localhost/redoc

Testing
Run the tests using pytest:
bashdocker compose exec fastapi pytest
For specific test files:
bashdocker compose exec fastapi pytest tests/test_specific_file.py
Troubleshooting
Docker and Database Issues
If you encounter Alembic synchronization issues:

Drop the Alembic version table in the database
Run the migration again:
bashdocker compose exec fastapi alembic upgrade head


If you change the database schema:

Delete the Alembic migration
Delete the Alembic version table
Delete the users table
Regenerate the migration:
bashdocker compose exec fastapi alembic revision --autogenerate -m "initial migration"


Deployment
The project is configured for CI/CD with GitHub Actions and DockerHub.
Production Environment Setup

Enable GitHub Issues in the repository settings
Create a production environment in GitHub
Add DockerHub credentials as environment secrets:

DOCKER_USERNAME: Your DockerHub username
DOCKER_TOKEN: Your DockerHub access token