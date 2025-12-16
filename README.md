# TaskPilot API

TaskPilot API is the backend service for the TaskPilot project management application. It provides a robust set of features for managing workspaces, projects, tasks, comments, and team collaboration, built with modern Python technologies.

## 🚀 Key Features

*   **Authentication**: Secure JWT-based authentication and user management.
*   **Workspaces**: Create and manage isolated workspaces for different teams or organizations.
*   **Projects & Tasks**: Comprehensive project management with task tracking, status updates, and assignment.
*   **Collaboration**: Real-time commenting on tasks and projects.
*   **Activity Logging**: detailed audit logs for user actions.
*   **AI Integration**: Features powered by DeepSeek AI (configured via `routes_ai`).
*   **Role-Based Access**: Granular permissions for workspace members.

## 🛠️ Tech Stack

*   **Language**: Python 3
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast (high-performance) web framework.
*   **Database**: PostgreSQL - Robust relational database.
*   **ORM**: SQLAlchemy (Async) - Database abstraction.
*   **Migrations**: Alembic - Database schema migrations.
*   **Caching**: Redis - In-memory data structure store.
*   **Task Queue**: Celery - Distributed task queue (background processing).
*   **Containerization**: Docker & Docker Compose.

## 📂 File Structure

```
taskpilot-api/
├── app/
│   ├── api/            # API Route definitions (endpoints)
│   │   └── v1/         # Version 1 API routes
│   ├── core/           # Core configuration, security, and logging
│   ├── db/             # Database connection and session management
│   ├── models/         # SQLAlchemy Database Models
│   ├── schemas/        # Pydantic Schemas (Request/Response DTOs)
│   ├── services/       # Business logic layer
│   └── tasks/          # Celery background tasks
├── alembic/            # Database migration scripts
├── alembic.ini         # Alembic configuration
├── docker-compose.yml  # Docker Compose service definition
├── Dockerfile          # Docker image definition
└── requirements.txt    # Python dependencies
```

## ⚡ Getting Started

### Prerequisites

*   **Docker** and **Docker Compose** installed.
*   (Optional) **Python 3.10+** for local development without Docker.

### 🐳 Running with Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd taskpilot-api
    ```

2.  **Environment Setup:**
    Create a `.env` file in the root directory (see [Configuration](#configuration) below).

3.  **Start Services:**
    ```bash
    docker-compose up --build
    ```
    This will start the Backend API, PostgreSQL database, and Redis.

4.  **Access the API:**
    The API will be available at `http://localhost:8000`.
    Interactive API docs (Swagger UI) are at `http://localhost:8000/docs`.

### 💻 Local Development Setup

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start backing services (PostgreSQL & Redis):**
    You can use Docker for just the dependencies:
    ```bash
    docker-compose up db redis -d
    ```

4.  **Run Migrations:**
    Apply database schema changes:
    ```bash
    alembic upgrade head
    ```

5.  **Run the Application:**
    ```bash
    uvicorn app.main:app --reload
    ```

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Security
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/taskpilot
# Note: If running via Docker Compose, use 'db' as login host:
# DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/taskpilot

# Redis
REDIS_URL=redis://localhost:6379/0
# Note: If running via Docker Compose, use 'redis':
# REDIS_URL=redis://redis:6379/0

# AI Configuration (Optional)
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 🚀 API Documentation

Once the application is running, navigate to `/docs` (Swagger UI) or `/redoc` for interactive API documentation. This provides a complete list of all available endpoints and allows you to test them directly from browser.

## 🤝 Contributing

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
