"""Demo local để chứng minh core engine có thể khởi chạy ngoài ArcGIS."""
from __future__ import annotations

import json

from scripts.classify_from_points import (
    PointRecord,
    PolygonRecord,
    classify_polygon,
    parse_rule72_objects,
    parse_threshold_rules,
)
from scripts.gemma_review import needs_manual_review, validate_review_schema
from scripts.transformations import build_google_maps_url


def main() -> None:
    rule72_objects = parse_rule72_objects(
        [
            {"rule72_code": "72_A01", "rule72_name": "Vùng loại A", "priority": 1},
            {"rule72_code": "72_B02", "rule72_name": "Vùng loại B", "priority": 2},
        ]
    )
    thresholds = parse_threshold_rules(
        [
            {
                "rule72_code": "72_A01",
                "min_points": 1,
                "max_points": 3,
                "min_area_m2": 50,
                "max_area_m2": 1000,
            }
        ]
    )

    polygon = PolygonRecord(polygon_id="PLG_001", area_m2=120)
    points = [PointRecord(polygon_id="PLG_001", point_class="72_A01")]
    result = classify_polygon(polygon, points, rule72_objects, thresholds)

    review_payload = {
        "polygon_id": "PLG_001",
        "predicted_object_code": "72_A01",
        "predicted_object_name": "Vùng loại A",
        "confidence": 0.82,
        "matches_rule_based_class": True,
        "visible_evidence": ["bề mặt đồng nhất"],
        "warnings": [],
        "needs_manual_review": False,
        "review_priority": "low",
    }
    validate_review_schema(review_payload)

    lat, lng = 10.123456, 106.123456
    output = {
        "classification": result,
        "needs_manual_review": needs_manual_review(review_payload, confidence_threshold=0.7),
        "google_maps_url": build_google_maps_url(lat, lng),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
