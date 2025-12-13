from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import api

app = FastAPI(
    title="YouCam Skin Analysis API",
    description="Backend API for YouCam Skin Analysis integration",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "YouCam Skin Analysis API", "docs": "/docs", "health": "/api/health"}
