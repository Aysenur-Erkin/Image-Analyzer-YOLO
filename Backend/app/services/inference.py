import os
from typing import List, Optional
from app.models.detection import Detection, _detect_contour
from app.core.config import settings

def _detect_yolo(image_path: str, conf: float, max_dets: int) -> List[Detection]:
    from ultralytics import YOLO
    model = YOLO(settings.MODEL_WEIGHTS)
    results = model.predict(image_path, conf=conf, max_det=max_dets, verbose=False)
    dets: List[Detection] = []
    for r in results:
        if r.boxes is None:
            continue
        names = r.names if hasattr(r, "names") else {}
        for b in r.boxes:
            xyxy = b.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, xyxy)
            confv = float(b.conf[0]) if hasattr(b, "conf") else 1.0
            cls_id = int(b.cls[0]) if hasattr(b, "cls") else 0
            label = names.get(cls_id, f"id_{cls_id}")
            dets.append(Detection(label=label, confidence=confv, bbox=[x1, y1, x2, y2]))
    return dets

def run_inference(
    image_path: str,
    conf: float = 0.25,
    max_dets: int = 100,
    detector_override: Optional[str] = None,
) -> List[Detection]:
    mode = (detector_override or settings.DETECTOR or "auto").lower()

    if mode == "contour":
        return _detect_contour(image_path)

    if mode == "yolo":
        return _detect_yolo(image_path, conf=conf, max_dets=max_dets)

    try:
        return _detect_yolo(image_path, conf=conf, max_dets=max_dets)
    except Exception as e:
        print(f"[inference] YOLO failed -> fallback to contour: {e}")
        return _detect_contour(image_path)
