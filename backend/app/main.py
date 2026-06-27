from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.scheduler_service import (
    scheduler
)
from app.api.risk import (
    router as risk_router
)


print("MAIN FILE LOADED")

from app.api.workflow import (
    router as workflow_router
)

print("WORKFLOW IMPORTED")

app = FastAPI()

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    print(
        "Scheduler Started"
    )

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

app.include_router(
    risk_router,
    prefix="/api"
)

print("ROUTER INCLUDED")


@app.get("/")
def root():
    return {
        "message": "CognitiveOps Backend Running"
    }

