from typing import Dict
import cv2
import numpy as np
from app.models.detection import Detection

def compute_statistics(image_path: str, det: Detection) -> Dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"area": 0, "histogram": []}
    x1,y1,x2,y2 = det.bbox
    x1 = max(0, int(x1)); y1 = max(0, int(y1))
    x2 = min(img.shape[1], int(x2)); y2 = min(img.shape[0], int(y2))
    roi = img[y1:y2, x1:x2]
    area = int((x2 - x1) * (y2 - y1))
    if roi.size == 0:
        return {"area": 0, "histogram": []}
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [16], [0,256]).flatten()
    hist = hist / (hist.sum() + 1e-6)
    return {"area": area, "histogram": hist.astype(float).tolist()}
