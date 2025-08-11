import os
from typing import List, Union
from pydantic import BaseSettings, Field, validator

class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploads"
    SECRET_KEY: str = "change-me"

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    DETECTOR: str = "auto"
    MODEL_WEIGHTS: str = "yolov8n.pt"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json
                try:
                    return json.loads(s)
                except Exception:
                    pass
            return [p.strip() for p in s.split(",") if p.strip()]
        return ["*"]

settings = Settings()
