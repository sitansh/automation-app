import logging
from typing import Dict, Any, List
import pandas as pd

LOG = logging.getLogger(__name__)


REQUIRED_COLUMNS = {"req_id", "field_key", "type", "required"}


def load_requirements(path: str) -> List[Dict[str, Any]]:
    if path.lower().endswith(('.xls', '.xlsx')):
        df = pd.read_excel(path, dtype=str)
    else:
        df = pd.read_csv(path, dtype=str)

    cols = set(c.strip() for c in df.columns)
    missing = REQUIRED_COLUMNS - set(c.strip() for c in df.columns)
    if missing:
        LOG.error("Missing required columns in requirements file: %s", missing)
        raise ValueError(f"Missing required columns: {missing}")

    df = df.fillna("")

    rows: List[Dict[str, Any]] = []
    for _, r in df.iterrows():
        item = {
            "req_id": str(r.get("req_id") or "").strip(),
            "field_key": str(r.get("field_key") or "").strip(),
            "type": str(r.get("type") or "").strip(),
            "required": _coerce_bool(r.get("required")),
            "label": _maybe_str(r.get("label")),
            "min_len": _maybe_int(r.get("min_len")),
            "max_len": _maybe_int(r.get("max_len")),
            "regex": _maybe_str(r.get("regex")),
            "options": _maybe_list(r.get("options")),
        }
        rows.append(item)

    return rows


def _coerce_bool(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "y", "required"):
        return True
    if s in ("false", "0", "no", "n", "optional"):
        return False
    return None


def _maybe_str(v):
    return None if v is None or str(v).strip() == "" else str(v).strip()


def _maybe_int(v):
    try:
        if v is None or str(v).strip() == "":
            return None
        return int(float(v))
    except Exception:
        return None


def _maybe_list(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    # assume comma-separated
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return parts if parts else None


__all__ = ["load_requirements"]
