"""Utilities cho chọn transformation và sinh link Google Maps."""
from __future__ import annotations

from typing import Any


def select_best_transformation(from_sr: Any, to_sr: Any, extent: Any, list_transformations_func: Any) -> str:
    candidates = list_transformations_func(from_sr, to_sr, extent)
    if not candidates:
        raise ValueError("Không tìm thấy geographic transformation phù hợp")
    return str(candidates[0])


def build_google_maps_url(lat: float, lng: float, zoom: int = 19) -> str:
    return (
        "https://www.google.com/maps/@?api=1&map_action=map"
        f"&center={lat},{lng}&zoom={zoom}&basemap=satellite"
    )


def add_google_fields(*_: Any, **__: Any) -> None:
    raise NotImplementedError("ArcPy field management should run in ArcGIS runtime")


def project_feature_class(*_: Any, **__: Any) -> None:
    raise NotImplementedError("ArcPy project should run in ArcGIS runtime")
