"""Rule-first phân loại polygon từ point khảo sát.

Module này tách phần rule engine (testable) khỏi phần ArcPy I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping
from collections import Counter


@dataclass(frozen=True)
class ThresholdRule:
    object_code: str
    min_points: int
    max_points: int
    min_area_m2: float
    max_area_m2: float


@dataclass(frozen=True)
class PointRecord:
    polygon_id: str
    point_class: str


@dataclass(frozen=True)
class PolygonRecord:
    polygon_id: str
    area_m2: float


def parse_rule72_objects(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}
    for row in rows:
        code = str(row["rule72_code"])
        result[code] = {
            "rule72_name": str(row.get("rule72_name", "")),
            "priority": str(row.get("priority", "100")),
        }
    return result


def parse_threshold_rules(rows: Iterable[Mapping[str, Any]]) -> Dict[str, ThresholdRule]:
    result: Dict[str, ThresholdRule] = {}
    for row in rows:
        code = str(row["rule72_code"])
        result[code] = ThresholdRule(
            object_code=code,
            min_points=int(row.get("min_points", 0)),
            max_points=int(row.get("max_points", 999999)),
            min_area_m2=float(row.get("min_area_m2", 0)),
            max_area_m2=float(row.get("max_area_m2", 1e20)),
        )
    return result


def classify_polygon(
    polygon: PolygonRecord,
    points: List[PointRecord],
    rule72_objects: Dict[str, Dict[str, str]],
    thresholds: Dict[str, ThresholdRule],
) -> Dict[str, Any]:
    if not points:
        return {
            "polygon_id": polygon.polygon_id,
            "rule72_code": "",
            "rule72_name": "",
            "point_count": 0,
            "dominant_point_class": "",
            "survey_status": "FAIL",
            "qc_reason": "MISSING_SURVEY_POINT",
        }

    class_counter = Counter(p.point_class for p in points)
    dominant_class, _ = class_counter.most_common(1)[0]
    point_count = len(points)

    rule_name = rule72_objects.get(dominant_class, {}).get("rule72_name", "")
    threshold = thresholds.get(dominant_class)

    status = "PASS"
    reasons: List[str] = []

    if threshold:
        if point_count < threshold.min_points or point_count > threshold.max_points:
            status = "REVIEW"
            reasons.append("POINT_COUNT_OUT_OF_RANGE")
        if polygon.area_m2 < threshold.min_area_m2 or polygon.area_m2 > threshold.max_area_m2:
            status = "REVIEW" if status == "PASS" else status
            reasons.append("AREA_OUT_OF_RANGE")
    else:
        status = "REVIEW"
        reasons.append("NO_THRESHOLD_CONFIG")

    if len(class_counter) > 1:
        status = "REVIEW"
        reasons.append("POINT_CLASS_CONFLICT")

    return {
        "polygon_id": polygon.polygon_id,
        "rule72_code": dominant_class,
        "rule72_name": rule_name,
        "point_count": point_count,
        "dominant_point_class": dominant_class,
        "survey_status": status,
        "qc_reason": ";".join(reasons),
    }


def run_classification(*_: Any, **__: Any) -> None:
    """Entry point để nối với ArcPy workflow ở môi trường ArcGIS Pro.

    Triển khai thao tác ArcPy thực tế (Spatial Join, UpdateCursor, FeatureToPoint)
    ở bước tích hợp khi có môi trường ArcGIS.
    """
    raise NotImplementedError("ArcPy integration should be implemented in ArcGIS runtime")
