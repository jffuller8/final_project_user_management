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
   ```

2. Create a `.env` file in the project root with your MailTrap credentials:
   ```
   MAIL_USERNAME=your_mailtrap_username
   MAIL_PASSWORD=your_mailtrap_password
   MAIL_FROM=from@example.com
   MAIL_PORT=2525
   MAIL_SERVER=sandbox.smtp.mailtrap.io
   MAIL_TLS=True
   MAIL_SSL=False
   ```

3. Build and start the Docker containers:
   ```bash
   docker compose up --build
   ```

4. Run the Alembic migrations to set up the database:
   ```bash
   docker compose exec fastapi alembic upgrade head
   ```

## Database Management

The project uses PostgreSQL as the database and Alembic for migrations.

### PGAdmin Setup

1. Access PGAdmin at http://localhost:5050
2. Login with credentials (from docker-compose.yml):
   - Email: admin@example.com (or as configured)
   - Password: adminpassword (or as configured)
3. Add a new server with these connection details:
   - Host: postgres
   - Port: 5432
   - Database: myappdb
   - Username: user
   - Password: password

### Alembic Commands

- Create a new migration:
  ```bash
  docker compose exec fastapi alembic revision --autogenerate -m "description"
  ```
- Apply migrations:
  ```bash
  docker compose exec fastapi alembic upgrade head
  ```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## Testing

Run the tests using pytest:
```bash
docker compose exec fastapi pytest
```

For specific test files:
```bash
docker compose exec fastapi pytest tests/test_specific_file.py
```

## Troubleshooting

### Docker and Database Issues

If you encounter Alembic synchronization issues:
1. Drop the Alembic version table in the database
2. Run the migration again:
   ```bash
   docker compose exec fastapi alembic upgrade head
   ```

If you change the database schema:
1. Delete the Alembic migration
2. Delete the Alembic version table
3. Delete the users table
4. Regenerate the migration:
   ```bash
   docker compose exec fastapi alembic revision --autogenerate -m "initial migration"
   ```

## Deployment

The project is configured for CI/CD with GitHub Actions and DockerHub.

### Production Environment Setup

1. Enable GitHub Issues in the repository settings
2. Create a production environment in GitHub
3. Add DockerHub credentials as environment secrets:
   - DOCKER_USERNAME: Your DockerHub username
   - DOCKER_TOKEN: Your DockerHub access token

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details.
