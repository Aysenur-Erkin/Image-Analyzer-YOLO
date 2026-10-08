from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from uuid import uuid4
from datetime import datetime
from typing import Optional, Literal
import os

from app.api.v1.schemas import (
    AnalyzeResponse, ObjectInfo,
    HistoryList, HistoryItem, BulkDeleteResult,
)
from app.services.inference import run_inference
from app.services.analytics import compute_statistics
from app.utils.storage import save_to_disk
from app.utils.visualize import draw_bboxes
from app.utils.history import (
    append_history, list_history, get_history_by_id,
    delete_history_item, clear_history,
)
from app.core.config import settings

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    conf: float = Query(0.25, ge=0.0, le=1.0),
    max_dets: int = Query(100, ge=1, le=3000),
    detector: Optional[Literal["auto", "yolo", "contour"]] = Query(None),
) -> AnalyzeResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    filename = f"{uuid4().hex}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, filename)
    save_to_disk(file, save_path)

    detections = run_inference(
        save_path, conf=conf, max_dets=max_dets, detector_override=detector
    )

    objects: list[ObjectInfo] = []
    for det in detections:
        stats = compute_statistics(save_path, det)
        objects.append(ObjectInfo(
            label=det.label,
            confidence=det.confidence,
            area=stats["area"],
            histogram=stats["histogram"],
            bbox=det.bbox,
        ))

    ann_name = f"annotated_{filename}"
    ann_path = os.path.join(settings.UPLOAD_DIR, "annotated", ann_name)
    draw_bboxes(save_path, detections, ann_path)

    hist_id = uuid4().hex
    entry = {
        "id": hist_id,
        "filename": filename,
        "original_url": f"/static/{filename}",
        "annotated_url": f"/static/annotated/{ann_name}",
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "objects_count": len(objects),
        "labels": sorted(list({o.label for o in objects})),
        "detector": (detector or settings.DETECTOR or "auto"),
    }
    append_history(entry)

    return AnalyzeResponse(
        message="analysis_complete",
        objects=objects,
        annotated_url=f"/static/annotated/{ann_name}",
        history_id=hist_id,
    )


@router.get("/history", response_model=HistoryList)
async def history_list(limit: int = Query(20, ge=1, le=200)) -> HistoryList:
    items = list_history(limit=limit)
    return HistoryList(items=[HistoryItem(**it) for it in items])

@router.get("/history/{hid}", response_model=HistoryItem)
async def history_detail(hid: str) -> HistoryItem:
    item = get_history_by_id(hid)
    if not item:
        raise HTTPException(status_code=404, detail="history item not found")
    return HistoryItem(**item)

@router.delete("/history/{hid}", response_model=HistoryItem)
async def history_delete_one(hid: str) -> HistoryItem:
    item = delete_history_item(hid)
    if not item:
        raise HTTPException(status_code=404, detail="history item not found")
    return HistoryItem(**item)

@router.delete("/history", response_model=BulkDeleteResult)
async def history_clear_all() -> BulkDeleteResult:
    n = clear_history()
    return BulkDeleteResult(deleted=n)
