"""Gemma review client với schema validation."""
from __future__ import annotations

from typing import Any, Dict

REQUIRED_KEYS = {
    "polygon_id",
    "predicted_object_code",
    "predicted_object_name",
    "confidence",
    "matches_rule_based_class",
    "visible_evidence",
    "warnings",
    "needs_manual_review",
    "review_priority",
}


def validate_review_schema(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = REQUIRED_KEYS - set(payload.keys())
    if missing:
        raise ValueError(f"Thiếu key trong review JSON: {sorted(missing)}")
    if not isinstance(payload["confidence"], (int, float)):
        raise ValueError("confidence phải là số")
    if not isinstance(payload["visible_evidence"], list):
        raise ValueError("visible_evidence phải là list")
    if not isinstance(payload["warnings"], list):
        raise ValueError("warnings phải là list")
    return payload


def needs_manual_review(payload: Dict[str, Any], confidence_threshold: float = 0.7) -> bool:
    if payload.get("needs_manual_review"):
        return True
    return float(payload.get("confidence", 0)) < confidence_threshold
