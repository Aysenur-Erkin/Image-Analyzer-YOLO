import os, shutil
from fastapi import UploadFile

def save_to_disk(file: UploadFile, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        file.file.seek(0)
    except Exception:
        pass
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
