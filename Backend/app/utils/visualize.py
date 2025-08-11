import os, cv2
from typing import Iterable

def _color_for_label(label: str) -> tuple[int,int,int]:
    h = abs(hash(label))
    return (50 + (h % 180), 50 + ((h // 7) % 180), 50 + ((h // 13) % 180))

def draw_bboxes(image_path: str, detections: Iterable, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = cv2.imread(image_path)
    if img is None:
        return
    for det in detections:
        x1,y1,x2,y2 = map(int, det.bbox)
        color = _color_for_label(det.label)
        cv2.rectangle(img, (x1,y1), (x2,y2), color, 2)
        label = f"{det.label} {det.confidence:.2f}"
        (tw,th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(0, y1 - th - 6)
        cv2.rectangle(img, (x1, top), (x1+tw+6, top+th+6), color, -1)
        cv2.putText(img, label, (x1+3, top+th+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
    cv2.imwrite(output_path, img)
