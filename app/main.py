from fastapi import FastAPI
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_workspaces import router as workspaces_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(workspaces_router)
# @app.get("/health")
# async def health_check():
#     return {"status": "ok", "message": "TaskPilot API is running!"}
