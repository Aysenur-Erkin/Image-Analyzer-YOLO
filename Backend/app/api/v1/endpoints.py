from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from uuid import uuid4
from datetime import datetime
from typing import Optional, Literal
import os, sys, platform, importlib, traceback, logging

from app.api.v1.schemas import (
    AnalyzeResponse, ObjectInfo,
    DebugVersion, DebugConfig,
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
logging.getLogger("uvicorn").info(f"[endpoints] LOADED FROM: {__file__}")


@router.post("/analyze", response_model=AnalyzeResponse, summary="Analyze an uploaded image")
async def analyze_image(
    file: UploadFile = File(...),
    conf: float = Query(0.25, ge=0.0, le=1.0, description="Minimum confidence"),
    max_dets: int = Query(100, ge=1, le=3000, description="Max detections"),
    detector: Optional[Literal["auto", "yolo", "contour"]] = Query(
        None, description="Detection engine override (auto|yolo|contour)"
    ),
) -> AnalyzeResponse:
    try:
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
        try:
            append_history(entry)
        except Exception as e:
            print(f"[history] skip: {e}")

        return AnalyzeResponse(
            message="analysis_complete",
            objects=objects,
            annotated_url=f"/static/annotated/{ann_name}",
            history_id=hist_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# debug
def _safe_version(mod_name: str) -> str | None:
    try:
        m = importlib.import_module(mod_name)
        return getattr(m, "__version__", "unknown")
    except Exception:
        return None

@router.get("/debug/version", response_model=DebugVersion, summary="Runtime & package versions")
async def debug_version() -> DebugVersion:
    try:
        import cv2
        opencv_ver = getattr(cv2, "__version__", "unknown")
    except Exception:
        opencv_ver = None
    return DebugVersion(
        python=sys.version.split()[0],
        fastapi=_safe_version("fastapi"),
        uvicorn=_safe_version("uvicorn"),
        numpy=_safe_version("numpy"),
        opencv=opencv_ver,
        torch=_safe_version("torch"),
        ultralytics=_safe_version("ultralytics"),
        platform=platform.platform(),
    )

@router.get("/debug/config", response_model=DebugConfig, summary="Safe configuration snapshot")
async def debug_config() -> DebugConfig:
    return DebugConfig(
        detector=(settings.DETECTOR or "auto"),
        model_weights=(settings.MODEL_WEIGHTS or "yolov8n.pt"),
        upload_dir=os.path.abspath(settings.UPLOAD_DIR),
        cors_origins=[o for o in settings.CORS_ORIGINS],
    )


@router.get("/history", response_model=HistoryList, summary="List recent uploads")
async def history_list(limit: int = Query(20, ge=1, le=200)) -> HistoryList:
    items = list_history(limit=limit)
    return HistoryList(items=[HistoryItem(**it) for it in items])

@router.get("/history/{hid}", response_model=HistoryItem, summary="Get a single upload by id")
async def history_detail(hid: str) -> HistoryItem:
    item = get_history_by_id(hid)
    if not item:
        raise HTTPException(status_code=404, detail="history item not found")
    return HistoryItem(**item)

@router.delete("/history/{hid}", response_model=HistoryItem, summary="Delete one history item & its files")
async def history_delete_one(hid: str) -> HistoryItem:
    item = delete_history_item(hid)
    if not item:
        raise HTTPException(status_code=404, detail="history item not found")
    return HistoryItem(**item)

@router.delete("/history", response_model=BulkDeleteResult, summary="Clear all history & files")
async def history_clear_all() -> BulkDeleteResult:
    n = clear_history()
    return BulkDeleteResult(deleted=n)


# smoke analyze
@router.post("/analyze_smoke")
async def analyze_smoke(file: UploadFile = File(...)):
    try:
        filename = f"smoke_{uuid4().hex}_{file.filename}"
        path = os.path.join(settings.UPLOAD_DIR, filename)
        save_to_disk(file, path)
        return {"ok": True, "original_url": f"/static/{filename}"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze_min")
async def analyze_min(file: UploadFile = File(...)):
    try:
        from app.models.detection import _detect_contour
        filename = f"min_{uuid4().hex}_{file.filename}"
        path = os.path.join(settings.UPLOAD_DIR, filename)
        save_to_disk(file, path)
        dets = _detect_contour(path)
        return {
            "ok": True,
            "count": len(dets),
            "first": dets[0].dict() if dets else None,
            "original_url": f"/static/{filename}",
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
