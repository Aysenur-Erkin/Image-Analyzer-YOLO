import os, json
from typing import List, Optional, Dict, Any, Tuple
from app.core.config import settings

def _history_path() -> str:
    return os.path.join(settings.UPLOAD_DIR, "history.jsonl")

def _is_under_uploads(p: str) -> bool:
    up = os.path.abspath(settings.UPLOAD_DIR)
    ap = os.path.abspath(p)
    return ap.startswith(up)

def _safe_unlink(p: str) -> None:
    try:
        if p and os.path.exists(p) and _is_under_uploads(p):
            os.remove(p)
    except Exception as e:
        print(f"[history] unlink warn: {p} -> {e}")

def _paths_from_entry(entry: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    orig_from_filename = os.path.join(settings.UPLOAD_DIR, entry.get("filename", "")) if entry.get("filename") else None

    ann_url = entry.get("annotated_url")
    ann_path = None
    if ann_url and isinstance(ann_url, str) and ann_url.startswith("/static/"):
        rel = ann_url[len("/static/"):]  # "annotated/xyz.png" gibi
        ann_path = os.path.join(settings.UPLOAD_DIR, rel)

    return (orig_from_filename, ann_path)

def append_history(entry: Dict[str, Any]) -> None:
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(_history_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[history] warning: {e}")

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
            except Exception:
                continue
            if obj.get("id") == hid:
                return obj
    return None

def delete_history_item(hid: str) -> Optional[Dict[str, Any]]:
    p = _history_path()
    if not os.path.exists(p):
        return None

    deleted: Optional[Dict[str, Any]] = None
    with open(p, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    items = []
    for l in lines:
        try:
            obj = json.loads(l)
        except Exception:
            continue
        if obj.get("id") == hid and deleted is None:
            deleted = obj
            orig_p, ann_p = _paths_from_entry(obj)
            _safe_unlink(orig_p or "")
            _safe_unlink(ann_p or "")
            continue
        items.append(obj)

    if deleted is None:
        return None

    try:
        with open(p, "w", encoding="utf-8") as f:
            for obj in items:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[history] rewrite warn: {e}")

    return deleted

def clear_history() -> int:
    p = _history_path()
    if not os.path.exists(p):
        return 0

    count = 0
    try:
        with open(p, "r", encoding="utf-8") as f:
            for l in f:
                if not l.strip():
                    continue
                try:
                    obj = json.loads(l)
                except Exception:
                    continue
                orig_p, ann_p = _paths_from_entry(obj)
                _safe_unlink(orig_p or "")
                _safe_unlink(ann_p or "")
                count += 1
    except Exception as e:
        print(f"[history] clear warn: {e}")

    try:
        os.remove(p)
    except Exception as e:
        print(f"[history] remove history.jsonl warn: {e}")

    return count
