import json
from src.schema_loader import extract_fields


def test_extract_fields_basic():
    data = {
        "form": {
            "fields": [
                {"name": "firstName", "type": "text", "required": True, "label": "First Name"},
                {"name": "lastName", "type": "text", "required": True, "label": "Last Name"},
            ]
        }
    }

    fields = extract_fields(data)
    keys = {f["field_key"] for f in fields}
    assert "firstName" in keys
    assert "lastName" in keys
