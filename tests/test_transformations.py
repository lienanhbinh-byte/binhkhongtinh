import pytest

from scripts.transformations import build_google_maps_url, select_best_transformation


def test_select_best_transformation_first_candidate():
    picked = select_best_transformation("A", "B", None, lambda *_: ["VN_2000_To_WGS_1984_2"])
    assert picked == "VN_2000_To_WGS_1984_2"


def test_select_best_transformation_raises_when_empty():
    with pytest.raises(ValueError):
        select_best_transformation("A", "B", None, lambda *_: [])


def test_google_maps_url():
    url = build_google_maps_url(10.1, 106.2, 19)
    assert "basemap=satellite" in url
