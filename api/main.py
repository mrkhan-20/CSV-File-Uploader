"""Main FastAPI application"""
from fastapi import FastAPI
from routers import upload, operations, tasks, files

app = FastAPI(title="CSV Processing API", version="1.0.0")

# Include routers
app.include_router(upload.router)
app.include_router(operations.router)
app.include_router(tasks.router)
app.include_router(files.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
