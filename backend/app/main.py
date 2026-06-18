from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("MAIN FILE LOADED")

from app.api.workflow import (
    router as workflow_router
)

print("WORKFLOW IMPORTED")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    workflow_router,
    prefix="/api"
)

print("ROUTER INCLUDED")


@app.get("/")
def root():
    return {
        "message": "CognitiveOps Backend Running"
    }

from app.api import workflow

app.include_router(
    workflow.router,
    prefix="/api"
)