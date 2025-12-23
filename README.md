# TaskPilot API

TaskPilot API is the robust backend service for the TaskPilot project management application. Built with modern Python technologies, it provides a scalable foundation for managing workspaces, projects, tasks, and real-time team collaboration.

## 🚀 Key Features

*   **🔐 Secure Authentication**: Full JWT-based generic authentication system with secure password hashing.
*   **🏢 Workspace Management**: Multi-tenant architecture allowing users to create and manage isolated workspaces.
*   **📊 Project & Task Tracking**: Comprehensive project lifecycles with granular task management (status updates, priorities, assignments).
*   **💬 Collaboration Tools**: Real-time commenting system on tasks to facilitate team communication.
*   **🤖 Context-Aware AI**: Integrated **DeepSeek AI** assistant that understands your project context (tasks, deadlines, members) to provide intelligent suggestions.
*   **📜 Activity Logging**: Detailed audit trails for all user actions within workspaces and projects.
*   **🛡️ Role-Based Access Control**: Granular permission systems for workspace members (Admins, Members, etc.).

## 🛠️ Tech Stack

*   **Language**: Python 3.10+
*   **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance, easy-to-learn, fast-to-code, ready-for-production.
*   **Database**: PostgreSQL - The world's most advanced open source relational database.
*   **ORM**: SQLAlchemy (Async) - The Python SQL Toolkit and Object Relational Mapper.
*   **Migrations**: Alembic - A lightweight database migration tool for usage with SQLAlchemy.
*   **Caching**: Redis - In-memory data store for caching and message brokerage.
*   **Async Tasks**: Celery - Distributed task queue for handling background jobs (emails, AI processing).
*   **Containerization**: Docker & Docker Compose - For consistent development and deployment environments.

## 📂 Detailed File Structure

```text
taskpilot-api/
├── alembic/                # Database migration scripts and revisions
├── app/
│   ├── api/
│   │   └── v1/             # API Version 1 endpoints
│   │       ├── routes_auth.py          # Login, Register, Refresh Token
│   │       ├── routes_users.py         # User profile management
│   │       ├── routes_workspaces.py    # Workspace CRUD & settings
│   │       ├── routes_workspace_members.py # Member management
│   │       ├── routes_projects.py      # Project creation & tracking
│   │       ├── routes_tasks.py         # Task assignment & status
│   │       ├── routes_comments.py      # Task comments
│   │       ├── routes_activity_logs.py # User activity history
│   │       └── routes_ai.py            # AI assistant endpoints
│   ├── core/               # Application capability configuration
│   │   ├── config.py           # Environment variables (Pydantic BaseSettings)
│   │   ├── security.py         # JWT handling & Password hashing
│   │   └── logging_config.py   # Structured logging setup
│   ├── db/                 # Database layer
│   │   ├── session.py          # Async session factory
│   │   ├── base.py             # SQLAlchemy Declarative Base
│   │   └── init_db.py          # Initial data seeding script
│   ├── models/             # SQLAlchemy Database Tables
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── comment.py
│   │   ├── activity_log.py
│   │   └── ai_request.py
│   ├── schemas/            # Pydantic Models (Data Transfer Objects)
│   │   ├── user_schema.py
│   │   ├── task_schema.py
│   │   ├── project_schema.py
│   │   └── ...
│   ├── services/           # Business Logic Layer
│   │   ├── ai_service.py       # AI Context & DeepSeek integration
│   │   ├── project_service.py  # Project-related logic
│   │   ├── task_service.py     # Complex task operations
│   │   └── deepseek_client.py  # External AI API client
│   ├── tasks/              # Celery Background Tasks
│   │   ├── ai_tasks.py         # Async AI processing
│   │   └── email_tasks.py      # Async email notifications
│   ├── utils/              # Shared Utilities
│   ├── celery_app.py       # Celery application configuration
│   └── main.py             # Application entrypoint & middleware
├── docker-compose.yml      # Orchestration for API, DB, and Redis
├── Dockerfile              # Production-ready Docker image
└── requirements.txt        # Python dependencies
```

## ⚡ Getting Started

### Prerequisites

*   **Docker** and **Docker Compose** installed (recommended).
*   (Optional) **Python 3.10+** and **PostgreSQL** for local setup.

### 🐳 Running with Docker (Quickstart)

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd taskpilot-api
    ```

2.  **Environment Setup:**
    Create a `.env` file in the root directory (copy the example structure below).

3.  **Start the Stack:**
    ```bash
    docker-compose up --build
    ```
    This spins up:
    *   **API Service**: `http://localhost:8000`
    *   **PostgreSQL**: Port `5432`
    *   **Redis**: Port `6379`

4.  **Explore the API:**
    Open your browser to **`http://localhost:8000/docs`** for the interactive Swagger UI.

### 💻 Local Development (Manual)

1.  **Set up Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start Logic Dependencies:**
    Use Docker to run just the DB and Cache:
    ```bash
    docker-compose up db redis -d
    ```

4.  **Apply Migrations:**
    ```bash
    alembic upgrade head
    ```

5.  **Run API:**
    ```bash
    uvicorn app.main:app --reload
    ```

## ⚙️ Configuration

Create a `.env` file in the root directory.

```env
# --- Security ---
SECRET_KEY=change_this_to_a_secure_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- Database ---
# Local execution:
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/taskpilot
# Docker execution (service name 'db'):
# DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/taskpilot

# --- Redis ---
# Local execution:
REDIS_URL=redis://localhost:6379/0
# Docker execution (service name 'redis'):
# REDIS_URL=redis://redis:6379/0

# --- AI Integration (DeepSeek) ---
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## 🤝 Contributing

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the feature branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
