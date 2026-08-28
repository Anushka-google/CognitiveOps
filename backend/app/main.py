import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.intent import (
    router as intent_router
)
from app.services.scheduler_service import (
    scheduler
)

from app.api.risk import (
    router as risk_router
)

from app.api.workflow import (
    router as workflow_router
)

from app.api.execution import (
    router as execution_router
)


# ==========================================
# Logging Configuration
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


# ==========================================
# Application
# ==========================================

logger.info(
    "MAIN FILE LOADED"
)

app = FastAPI()


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Routers
# ==========================================

app.include_router(
    workflow_router,
    prefix="/api"
)
app.include_router(
    intent_router,
    prefix="/api"
)

app.include_router(
    risk_router,
    prefix="/api"
)

app.include_router(
    execution_router,
    prefix="/api"
)

logger.info(
    "ROUTERS INCLUDED"
)


# ==========================================
# Scheduler Startup
# ==========================================

@app.on_event("startup")
def start_scheduler():

    scheduler.start()

    logger.info(
        "SCHEDULER STARTED"
    )


# ==========================================
# Root Endpoint
# ==========================================

@app.get("/")
def root():

    return {
        "message":
        "CognitiveOps Backend Running"
    }