from typing import List
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploads"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    DETECTOR: str = "auto"
    MODEL_WEIGHTS: str = "yolov8n.pt"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("CORS_ORIGINS", pre=True)
    def split_origins(cls, v):
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        return v

settings = Settings()
