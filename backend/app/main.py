from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api.api import api_router
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for SAPDO AI platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to SAPDO API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
