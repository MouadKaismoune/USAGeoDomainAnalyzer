import os
import sqlite3
from datetime import datetime

from database.db_manager import DB_PATH

BACKUP_DIR = os.path.join(os.path.dirname(DB_PATH), "backups")


def _ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    return BACKUP_DIR


def _fmt_size(size):
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def get_database_info():
    size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    return {
        "path": DB_PATH,
        "size": _fmt_size(size),
    }


def create_backup(label=None):
    _ensure_backup_dir()
    label = (label or "").strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = timestamp + (f"_{label}" if label else "")
    dest = os.path.join(BACKUP_DIR, f"{base}.db")

    try:
        if not os.path.exists(DB_PATH):
            from database import init_database
            init_database()
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(dest)
        with dst:
            src.backup(dst)
        src.close()
        dst.close()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    return {
        "ok": True,
        "path": dest,
        "name": base,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "size": _fmt_size(os.path.getsize(dest)),
    }


def list_backups():
    _ensure_backup_dir()
    items = []
    for name in os.listdir(BACKUP_DIR):
        if not name.endswith(".db"):
            continue
        path = os.path.join(BACKUP_DIR, name)
        try:
            st = os.stat(path)
        except OSError:
            continue
        items.append({
            "path": path,
            "name": os.path.splitext(name)[0],
            "created": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "size": _fmt_size(st.st_size),
        })
    items.sort(key=lambda x: x["created"], reverse=True)
    return items


def restore_backup(path):
    if not path or not os.path.exists(path):
        return {"ok": False, "error": "backup_not_found"}
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        src = sqlite3.connect(path)
        dst = sqlite3.connect(DB_PATH)
        with dst:
            src.backup(dst)
        src.close()
        dst.close()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True}


def delete_backup(path):
    try:
        os.remove(path)
        return {"ok": True}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}