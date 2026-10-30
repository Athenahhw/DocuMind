
from fastapi import FastAPI

app = FastAPI(
    title="DocuMind API",
    description="AI-powered document management system",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to DocuMind!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
