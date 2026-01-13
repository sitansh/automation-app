import requests
import logging
from typing import Any, Dict, List

LOG = logging.getLogger(__name__)


FIELD_KEY_CANDIDATES = ["field_key", "fieldKey", "name", "key", "id"]
TYPE_CANDIDATES = ["type", "fieldType", "component", "componentType"]
REQUIRED_CANDIDATES = ["required", "mandatory", "isRequired"]
LABEL_CANDIDATES = ["label", "title", "displayName"]
OPTIONS_CANDIDATES = ["options", "choices", "items"]
VALIDATIONS_CANDIDATES = ["validations", "validation", "constraints", "props"]


def load_schema_from_url(url: str, timeout: int = 10) -> Any:
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        LOG.exception("Failed to fetch or parse schema JSON: %s", e)
        raise


def extract_fields(schema_json: Any) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    def visit(node: Any, path: List[str]):
        if isinstance(node, dict):
            # detect a field if it contains any field_key candidate
            key_val = None
            for k in FIELD_KEY_CANDIDATES:
                if k in node:
                    key_val = node.get(k)
                    break

            if key_val:
                field = {
                    "field_key": str(key_val).strip() if key_val is not None else None,
                    "type": None,
                    "required": None,
                    "label": None,
                    "options": None,
                    "validations": None,
                    "raw_json_path": "/".join(path),
                    "raw": node,
                }
                for k in TYPE_CANDIDATES:
                    if k in node:
                        field["type"] = node.get(k)
                        break
                for k in REQUIRED_CANDIDATES:
                    if k in node:
                        field["required"] = node.get(k)
                        break
                for k in LABEL_CANDIDATES:
                    if k in node:
                        field["label"] = node.get(k)
                        break
                for k in OPTIONS_CANDIDATES:
                    if k in node:
                        field["options"] = node.get(k)
                        break
                for k in VALIDATIONS_CANDIDATES:
                    if k in node:
                        field["validations"] = node.get(k)
                        break

                results.append(field)

            # continue traversal
            for k, v in node.items():
                visit(v, path + [str(k)])

        elif isinstance(node, list):
            for idx, item in enumerate(node):
                visit(item, path + [f"[{idx}]"])

    visit(schema_json, ["root"])

    # normalize and dedupe by field_key (case-insensitive)
    dedup: Dict[str, Dict[str, Any]] = {}
    for f in results:
        fk = f.get("field_key")
        if not fk:
            continue
        key = fk.lower()
        if key in dedup:
            # merge minimal info
            existing = dedup[key]
            for attr in ("type", "required", "label", "options", "validations"):
                if existing.get(attr) in (None, "") and f.get(attr) not in (None, ""):
                    existing[attr] = f.get(attr)
        else:
            dedup[key] = f

    return list(dedup.values())


__all__ = ["load_schema_from_url", "extract_fields"]
