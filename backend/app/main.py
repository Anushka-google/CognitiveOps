from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.query import router as query_router
from app.api.analyze import router as analyze_router

app = FastAPI()
app.include_router(upload_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(analyze_router,
    prefix="/api")

@app.get("/")
def root():
    return {"message": "CognitiveOps Backend Running"}



#tum sara kaam khud se hi kr rhe ho copilot k use nhi kr rhe?khi bhi bhai use kr use bhi worth it rhe thoda