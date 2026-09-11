import logging

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.services.trace_service import (
    trace_log
)

from app.services.scheduler_service import (
    scheduler
)

from app.api.workflow import (
    router as workflow_router
)

from app.api.execution import (
    router as execution_router
)
from app.api.risk import (
    router as risk_router
)
from app.api.chat import (
    router as chat_router
)


# =========================================================
# LOGGING CONFIGURATION
# =========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)


logger = logging.getLogger(
    __name__
)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(

    title="CognitiveOps",

    description=(
        "AI Process Intelligence "
        "and Agentic Workflow Automation"
    ),

    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(

    workflow_router,

    prefix="/api"
)


app.include_router(

    execution_router,

    prefix="/api"
)
app.include_router(
    risk_router,
    prefix="/api"
)
app.include_router(
    chat_router,
    prefix="/api"
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {

        "message":
            "CognitiveOps API is running."

    }


# =========================================================
# STARTUP
# =========================================================

@app.on_event(
    "startup"
)
def startup_event():

    trace_log(
        "APPLICATION_START"
    )

    logger.info(
        "CognitiveOps application started."
    )

    if not scheduler.running:

        scheduler.start()

        trace_log(
            "SCHEDULER_STARTED"
        )

        logger.info(
            "Scheduler Started"
        )


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event(
    "shutdown"
)
def shutdown_event():

    if scheduler.running:

        scheduler.shutdown(
            wait=False
        )

        logger.info(
            "Scheduler Stopped"
        )

        trace_log(
            "SCHEDULER_STOPPED"
        )

    trace_log(
        "APPLICATION_STOP"
    )