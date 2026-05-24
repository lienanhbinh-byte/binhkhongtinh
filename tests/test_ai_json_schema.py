import pytest

from scripts.gemma_review import needs_manual_review, validate_review_schema


def test_validate_review_schema_ok():
    payload = {
        "polygon_id": "P1",
        "predicted_object_code": "72_A01",
        "predicted_object_name": "Loai A",
        "confidence": 0.9,
        "matches_rule_based_class": True,
        "visible_evidence": ["evidence"],
        "warnings": [],
        "needs_manual_review": False,
        "review_priority": "medium",
    }
    assert validate_review_schema(payload)["polygon_id"] == "P1"


def test_validate_review_schema_missing_key():
    with pytest.raises(ValueError):
        validate_review_schema({"polygon_id": "P1"})


def test_needs_manual_review_from_threshold():
    payload = {
        "polygon_id": "P1",
        "predicted_object_code": "72_A01",
        "predicted_object_name": "Loai A",
        "confidence": 0.5,
        "matches_rule_based_class": True,
        "visible_evidence": ["evidence"],
        "warnings": [],
        "needs_manual_review": False,
        "review_priority": "medium",
    }
    assert needs_manual_review(payload, 0.7) is True
