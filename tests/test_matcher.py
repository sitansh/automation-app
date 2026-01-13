from src.matcher import compare_requirement_to_schema


def test_compare_exact_match():
    req = {"req_id": "1", "field_key": "firstName", "type": "text", "required": True}
    schema = [{"field_key": "firstName", "type": "text", "required": True}]
    rep = compare_requirement_to_schema(req, schema)
    assert rep["status"] == "MATCHED"
