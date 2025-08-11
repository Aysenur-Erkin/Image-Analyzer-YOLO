from celery import Celery
from app.services.inference import run_inference
from app.services.analytics import compute_statistics
from app.core.config import settings

celery = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery.task(name="tasks.analyze_image")
def analyze_image_task(image_path: str) -> dict:

    detections = run_inference(image_path)
    objects = []
    for det in detections:
        stats = compute_statistics(image_path, det)
        objects.append({
            "label": det.label,
            "confidence": det.confidence,
            "area": stats["area"],
            "histogram": stats["histogram"]
        })
    return {"objects": objects}


