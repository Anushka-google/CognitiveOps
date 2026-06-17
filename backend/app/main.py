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