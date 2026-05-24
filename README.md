# binhkhongtinh

Khởi tạo bộ khung triển khai cho đề án ArcGIS + Gemma 4 E4B.

## Thành phần hiện có
- `scripts/classify_from_points.py`: rule engine phân loại polygon từ point (testable core).
- `scripts/transformations.py`: chọn transformation và tạo Google Maps URL.
- `scripts/gemma_review.py`: schema validator cho AI review JSON.
- `scripts/demo_run.py`: demo local để chứng minh core pipeline chạy được ngoài ArcGIS.
- `tests/`: unit test cho rule engine, transformation selector, JSON schema.
- `DE_AN_ARCGIS_GEMMA4E4B.md`: blueprint nghiệp vụ/kiến trúc chi tiết.

## Khởi chạy nhanh
```bash
python -m scripts.demo_run
```

## Chạy test
```bash
pytest -q
```

## Lưu ý
- Các hàm cần ArcPy runtime (`run_classification`, `add_google_fields`, `project_feature_class`) đang là placeholder, nên muốn chạy end-to-end với dữ liệu GIS thật cần ArcGIS Pro + ArcPy.
