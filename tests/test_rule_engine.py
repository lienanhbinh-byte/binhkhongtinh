from scripts.classify_from_points import (
    PointRecord,
    PolygonRecord,
    classify_polygon,
    parse_rule72_objects,
    parse_threshold_rules,
)


def test_classify_pass():
    objects = parse_rule72_objects([
        {"rule72_code": "72_A01", "rule72_name": "Loai A"},
    ])
    thresholds = parse_threshold_rules([
        {"rule72_code": "72_A01", "min_points": 1, "max_points": 3, "min_area_m2": 0, "max_area_m2": 500},
    ])
    result = classify_polygon(
        PolygonRecord("P1", 100),
        [PointRecord("P1", "72_A01")],
        objects,
        thresholds,
    )
    assert result["survey_status"] == "PASS"


def test_classify_missing_points_fail():
    result = classify_polygon(PolygonRecord("P1", 100), [], {}, {})
    assert result["survey_status"] == "FAIL"
