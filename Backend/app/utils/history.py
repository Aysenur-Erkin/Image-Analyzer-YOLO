import os, json
from typing import List, Optional, Dict, Any, Tuple
from app.core.config import settings

def _history_path() -> str:
    return os.path.join(settings.UPLOAD_DIR, "history.jsonl")

def _is_under_uploads(p: str) -> bool:
    up = os.path.abspath(settings.UPLOAD_DIR)
    ap = os.path.abspath(p)
    return ap == up or ap.startswith(up + os.sep)

def _unlink(p: Optional[str]) -> None:
    if not p or not os.path.exists(p):
        return
    if not _is_under_uploads(p):
        return
    os.remove(p)

def _paths_from_entry(entry: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    orig = None
    if entry.get("filename"):
        orig = os.path.join(settings.UPLOAD_DIR, entry["filename"])

    ann = None
    ann_url = entry.get("annotated_url")
    if isinstance(ann_url, str) and ann_url.startswith("/static/"):
        ann = os.path.join(settings.UPLOAD_DIR, ann_url[len("/static/"):])
    return orig, ann

def append_history(entry: Dict[str, Any]) -> None:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(_history_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def list_history(limit: int = 20) -> List[Dict[str, Any]]:
    p = _history_path()
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    items = [json.loads(l) for l in lines][-limit:]
    return list(reversed(items))

def get_history_by_id(hid: str) -> Optional[Dict[str, Any]]:
    p = _history_path()
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        for l in reversed(list(f)):
            if not l.strip():
                continue
            try:
                obj = json.loads(l)
            except json.JSONDecodeError:
                continue
            if obj.get("id") == hid:
                return obj
    return None

def delete_history_item(hid: str) -> Optional[Dict[str, Any]]:
    p = _history_path()
    if not os.path.exists(p):
        return None

    deleted = None
    with open(p, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    items = []
    for l in lines:
        try:
            obj = json.loads(l)
        except json.JSONDecodeError:
            continue
        if obj.get("id") == hid and deleted is None:
            deleted = obj
            orig, ann = _paths_from_entry(obj)
            _unlink(orig)
            _unlink(ann)
            continue
        items.append(obj)

    if deleted is None:
        return None

    with open(p, "w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return deleted

def clear_history() -> int:
    p = _history_path()
    if not os.path.exists(p):
        return 0

    count = 0
    with open(p, "r", encoding="utf-8") as f:
        for l in f:
            if not l.strip():
                continue
            try:
                obj = json.loads(l)
            except json.JSONDecodeError:
                continue
            orig, ann = _paths_from_entry(obj)
            _unlink(orig)
            _unlink(ann)
            count += 1
    os.remove(p)
    return count
