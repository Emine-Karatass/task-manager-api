# Task Manager API

A RESTful Task Manager API built with **FastAPI**, featuring JWT-based authentication, PostgreSQL persistence, and full CRUD functionality with filtering, pagination, and automated testing.

## Features

- **User Authentication** — Register and login with JWT-based token authentication and secure password hashing
- **Task Management** — Full CRUD operations (Create, Read, Update, Delete) for tasks
- **Ownership & Authorization** — Each user can only access and manage their own tasks
- **Categories & Priority** — Organize tasks by category and priority level
- **Filtering & Pagination** — Filter tasks by completion status, priority, or category, with skip/limit pagination
- **Input Validation** — Request validation using Pydantic models
- **Automated Testing** — Test suite covering authentication, CRUD operations, and edge cases using pytest
- **Containerized** — Fully dockerized with a PostgreSQL database via Docker Compose

## Tech Stack

| Layer          | Technology              |
|----------------|--------------------------|
| Framework      | FastAPI                 |
| Database       | PostgreSQL (SQLAlchemy ORM) |
| Authentication | JWT (OAuth2 Password Flow) |
| Testing        | pytest, httpx            |
| Containerization | Docker, Docker Compose |

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed on your machine

### Run with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/Emine-Karatass/task-manager-api.git
   cd task-manager-api
   ```

2. Start the application:
   ```bash
   docker-compose up --build
   ```

3. The API will be available at `http://localhost:8000`, and the interactive Swagger documentation at:
   ```
   http://localhost:8000/docs
   ```

### Environment Variables

The application reads its database connection string from the `DATABASE_URL` environment variable. See `.env.example` for the expected format. If not set, the app falls back to a local SQLite database for development.

## API Overview

### Authentication

| Method | Endpoint     | Description                |
|--------|--------------|-----------------------------|
| POST   | `/register`  | Create a new user account   |
| POST   | `/login`     | Authenticate and receive a JWT access token |

### Tasks

| Method | Endpoint         | Description                              |
|--------|------------------|-------------------------------------------|
| GET    | `/tasks`         | List the authenticated user's tasks (supports filtering by `completed`, `priority`, `category`, and pagination via `skip`/`limit`) |
| GET    | `/tasks/{id}`    | Retrieve a single task by ID              |
| POST   | `/tasks`         | Create a new task                         |
| PUT    | `/tasks/{id}`    | Update an existing task                   |
| DELETE | `/tasks/{id}`    | Delete a task                             |

All task endpoints require a valid JWT token (obtained via `/login`) passed in the `Authorization` header, and enforce that users can only access their own tasks.

## Running Tests

The project includes a pytest test suite covering registration, login, and full task CRUD flows, including authorization edge cases.

```bash
pip install -r requirements.txt
pytest
```

## Project Structure

```
task-manager-api/
├── task_manager_api.py   # Main application: models, routes, auth logic
├── test_main.py          # Automated test suite (pytest)
├── requirements.txt      # Python dependencies
├── Dockerfile             # Application container definition
├── docker-compose.yml     # API + PostgreSQL orchestration
└── README.md
```

## Author

Built by Emine as a backend development portfolio project.
