from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_workspaces import router as workspaces_router
from app.api.v1.routes_projects import router as projects_router
from app.api.v1.routes_tasks import router as tasks_router
from app.api.v1.routes_comments import router as comments_router
from app.api.v1.routes_workspace_members import router as workspace_members_router  
from app.api.v1.routes_activity_logs import router as activity_logs_router
from app.api.v1.routes_ai import router as ai_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]

# added some middlewares

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(workspace_members_router)
app.include_router(activity_logs_router)
app.include_router(ai_router)