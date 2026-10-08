from typing import List, Optional
from pydantic import BaseModel

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
