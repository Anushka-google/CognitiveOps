
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.api.upload import (
    router as upload_router
)

from app.api.query import (
    router as query_router
)

from app.api.analyze import (
    router as analyze_router
)

from app.api.workflow import (
    router as workflow_router
)

from app.api.risk import (
    router as risk_router
)



app = FastAPI()

from app.services.scheduler_service import (
    scheduler
)
scheduler.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    risk_router,
    prefix="/api"
)

app.include_router(
    upload_router,
    prefix="/api"
)

app.include_router(
    query_router,
    prefix="/api"
)

app.include_router(
    analyze_router,
    prefix="/api"
)

app.include_router(
    workflow_router,
    prefix="/api"
)


@app.get("/")
def root():
    return {
        "message":
        "CognitiveOps Backend Running"
    }

@app.get("/debug")
def debug():
    return {
        "message": "new code running"
    }

