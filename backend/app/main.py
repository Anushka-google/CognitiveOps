from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Backend Running"
    }

@app.get("/debug")
def debug():
    return {
        "message": "new code running"
    }


from app.api.workflow import (
    router as workflow_router
)

app.include_router(
    workflow_router,
    prefix="/api"
)