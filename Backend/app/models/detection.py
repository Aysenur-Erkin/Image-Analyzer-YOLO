from typing import List
from pydantic import BaseModel

class Detection(BaseModel):
    label: str
    confidence: float
    bbox: List[int]

def _detect_contour(image_path: str) -> List[Detection]:
    import cv2, numpy as np
    img = cv2.imread(image_path)
    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, None, iterations=1)
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dets: List[Detection] = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w * h < 100:
            continue
        dets.append(Detection(label="blob", confidence=1.0, bbox=[int(x), int(y), int(x+w), int(y+h)]))
    if not dets:
        h, w = gray.shape[:2]
        dets.append(Detection(label="blob", confidence=1.0, bbox=[0, 0, int(w), int(h)]))
    return dets
