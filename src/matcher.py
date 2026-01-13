import logging
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import process, fuzz

LOG = logging.getLogger(__name__)


def _bool_to_str(v: Optional[bool]) -> str:
    if v is True:
        return "True"
    if v is False:
        return "False"
    return ""


def compare_requirement_to_schema(req: Dict[str, Any], schema_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    # prepare map of schema keys
    schema_map = {f["field_key"].lower(): f for f in schema_fields}
    req_key = (req.get("field_key") or "").strip()
    req_key_l = req_key.lower()

    report: Dict[str, Any] = {
        "req_id": req.get("req_id"),
        "field_key": req_key,
        "expected_type": req.get("type"),
        "actual_type": None,
        "expected_required": _bool_to_str(req.get("required")),
        "actual_required": None,
        "found": "NO",
        "status": "MISSING",
        "differences": "",
        "best_match_key": None,
        "best_match_score": None,
        "raw_json_path": None,
    }

    # exact match
    if req_key_l in schema_map:
        s = schema_map[req_key_l]
        report["found"] = "YES"
        report["actual_type"] = s.get("type")
        report["actual_required"] = _bool_to_str(s.get("required"))
        report["raw_json_path"] = s.get("raw_json_path")
        diffs = _compute_diffs(req, s)
        report["differences"] = "; ".join(diffs) if diffs else ""
        report["status"] = "MATCHED" if not diffs else "MISMATCH"
        report["best_match_key"] = s.get("field_key")
        report["best_match_score"] = 100
        return report

    # fuzzy match
    choices = [f["field_key"] for f in schema_fields]
    if choices:
        best: Tuple[str, int, int] = process.extractOne(req_key, choices, scorer=fuzz.token_sort_ratio) or (None, 0, None)
        best_key, best_score, _ = best
        report["best_match_key"] = best_key
        report["best_match_score"] = int(best_score or 0)

        if best_score >= 85:
            # POSSIBLE_MATCH
            s = next((f for f in schema_fields if f["field_key"] == best_key), None)
            if s:
                report["found"] = "POSSIBLE"
                report["actual_type"] = s.get("type")
                report["actual_required"] = _bool_to_str(s.get("required"))
                report["raw_json_path"] = s.get("raw_json_path")
                diffs = _compute_diffs(req, s)
                report["differences"] = "; ".join(diffs) if diffs else ""
                report["status"] = "POSSIBLE_MATCH"
                return report

    # else missing
    return report


def _compute_diffs(req: Dict[str, Any], schema_field: Dict[str, Any]) -> List[str]:
    diffs: List[str] = []
    # type
    if (req.get("type") or "").strip().lower() and (schema_field.get("type") or "").strip().lower():
        if req.get("type").strip().lower() != str(schema_field.get("type")).strip().lower():
            diffs.append(f"type: expected={req.get('type')} actual={schema_field.get('type')}")

    # required
    r_expected = req.get("required")
    r_actual = schema_field.get("required")
    if r_expected is not None and r_actual is not None:
        if bool(r_expected) != bool(r_actual):
            diffs.append(f"required: expected={r_expected} actual={r_actual}")

    # options
    if req.get("options") and schema_field.get("options"):
        exp_opts = [str(x).strip().lower() for x in (req.get("options") or [])]
        act_opts_raw = schema_field.get("options")
        if isinstance(act_opts_raw, dict):
            act_opts = [str(v).strip().lower() for v in act_opts_raw.values()]
        elif isinstance(act_opts_raw, list):
            act_opts = [str(x).strip().lower() for x in act_opts_raw]
        else:
            act_opts = [str(act_opts_raw).strip().lower()]
        if set(exp_opts) != set(act_opts):
            diffs.append(f"options differ: expected={req.get('options')} actual={schema_field.get('options')}")

    # basic validations (min_len/max_len/regex)
    val = schema_field.get("validations") or {}
    if isinstance(val, dict):
        if req.get("min_len") and val.get("minLength") and int(req.get("min_len")) != int(val.get("minLength")):
            diffs.append(f"min_len: expected={req.get('min_len')} actual={val.get('minLength')}")
        if req.get("max_len") and val.get("maxLength") and int(req.get("max_len")) != int(val.get("maxLength")):
            diffs.append(f"max_len: expected={req.get('max_len')} actual={val.get('maxLength')}")
        if req.get("regex") and val.get("pattern") and str(req.get("regex")).strip() != str(val.get("pattern")).strip():
            diffs.append(f"regex: expected={req.get('regex')} actual={val.get('pattern')}")

    return diffs


__all__ = ["compare_requirement_to_schema"]
