from typing import List, Optional
from pydantic import BaseModel
import logging

logging.getLogger("uvicorn").info(f"[schemas] LOADED FROM: {__file__}")

class ObjectInfo(BaseModel):
    label: str
    confidence: float
    area: float
    histogram: List[float]
    bbox: List[int]

class AnalyzeResponse(BaseModel):
    message: str
    objects: List[ObjectInfo]
    annotated_url: Optional[str] = None
    history_id: Optional[str] = None

class DebugVersion(BaseModel):
    python: str
    fastapi: Optional[str]
    uvicorn: Optional[str]
    numpy: Optional[str]
    opencv: Optional[str]
    torch: Optional[str]
    ultralytics: Optional[str]
    platform: str

class DebugConfig(BaseModel):
    detector: str
    model_weights: str
    upload_dir: str
    cors_origins: List[str]

class HistoryItem(BaseModel):
    id: str
    filename: str
    original_url: Optional[str] = None
    annotated_url: Optional[str] = None
    uploaded_at: str
    objects_count: int
    labels: List[str]

class HistoryList(BaseModel):
    items: List[HistoryItem]

class BulkDeleteResult(BaseModel):
    deleted: int
