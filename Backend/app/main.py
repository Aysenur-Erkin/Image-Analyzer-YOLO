import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.endpoints import router as api_router

app = FastAPI(title="ImageAnalyzer API", description="API for uploading and analyzing images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

@app.get("/health", tags=["Health"], summary="Health Check", description="Basit bir sağlık kontrolü endpoint'i.")
async def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")
