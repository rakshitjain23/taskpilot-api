from fastapi import FastAPI
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_workspaces import router as workspaces_router
from app.api.v1.routes_projects import router as projects_router
from app.api.v1.routes_tasks import router as tasks_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)