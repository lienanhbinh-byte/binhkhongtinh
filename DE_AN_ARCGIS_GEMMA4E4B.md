# Đề án tự động hóa phân loại đối tượng vùng phủ bề mặt trong ArcGIS bằng Gemma 4 E4B

## 1) Bức tranh tổng thể

Định hướng triển khai nên theo mô hình **rule-first, AI-second**:

- **Lõi quyết định** đặt trong ArcGIS/geodatabase với dữ liệu line, point, polygon, raster, bảng quy tắc.
- **Topology + polygon hóa + rule engine** là nguồn kết luận chính thức.
- **Gemma 4 E4B** đóng vai trò kiểm tra thị giác (QC), phát hiện nghi vấn, không ghi đè quyết định nghiệp vụ.

Kiến trúc phù hợp:

- **ArcGIS Pro Add-in** (DockPane 3 tab): Topology, Tạo Vùng, Phân Loại & QC.
- **Python/ArcPy geoprocessing engine** thực thi xử lý nặng.
- Có thể gọi tool Python từ Add-in qua `ExecuteToolAsync`.

## 2) Ràng buộc kỹ thuật bắt buộc

1. **Topology scope**
   - Topology nằm trong **feature dataset**.
   - Feature class tham gia topology phải cùng feature dataset với topology.
   - Thêm lớp vào topology làm topology “dirty”, cần validate lại.
   - Khuyến nghị có bước staging: copy lớp line về working feature dataset trước khi xử lý.

2. **License ArcGIS**
   - Topology và Feature To Polygon yêu cầu **Standard/Advanced**.
   - Feature To Point dùng được từ Basic.
   - Nếu dùng Extract By Mask / Zonal Statistics cần extension phù hợp (ví dụ Spatial Analyst).

3. **Feature To Polygon**
   - Không dựa vào Preserve attributes.
   - Luồng đúng: polygon hóa trước, sau đó spatial join/rule engine gán thuộc tính từ point.

4. **File geodatabase concurrency**
   - Phù hợp nhóm nhỏ.
   - Nhiều client có thể truy cập đồng thời nhưng không thuận lợi cho chỉnh sửa đồng thời trên cùng dataset.
   - Nên chuẩn bị khả năng nâng cấp sang enterprise geodatabase.

## 3) Thiết kế workflow 3 tab

## Tab 1 — Topology & khép vùng

### Input
- Một hoặc nhiều lớp line.

### Xử lý chính
- Copy dữ liệu vào working feature dataset.
- Tạo topology với tolerance mặc định theo spatial reference.
- Thêm rules bắt buộc:
  - Must Not Have Dangles
  - Must Not Overlap
  - Must Not Self-Overlap
  - Must Not Self-Intersect
  - Must Be Single Part
- Rules tùy chọn theo nghiệp vụ:
  - Must Not Intersect Or Touch Interior
  - Must Not Have Pseudo Nodes
  - Endpoint Must Be Covered By
- Validate topology.
- Safe auto-fix (Snap/Extend trong ngưỡng nhỏ cấu hình).
- Lỗi còn lại chuyển review thủ công.

### Output
- `topology_status`
- `topology_error_count`
- `qc_issue_point` (lỗi chưa sửa)
- log geoprocessing
- danh sách line auto-fix và line cần review.

## Tab 2 — Tạo polygon từ line

### Xử lý chính
1. Chuẩn hóa đầu vào.
2. Polygon hóa bằng Feature To Polygon.
3. Chuẩn hóa đầu ra + tính hình học.

### Trường hệ thống đề xuất
- `polygon_id`
- `rule72_code`, `rule72_name`
- `area_m2`, `area_ha`, `perimeter_m`
- `point_count`, `dominant_point_class`
- `classification_source`
- `qc_status`, `ai_status`
- `google_lat`, `google_lng`, `google_maps_url`

## Tab 3 — Phân loại từ point + QC + AI

### Xử lý chính
1. Spatial join point vào polygon.
2. Rule engine theo bảng cấu hình chuẩn 72 (không hard-code).
3. Cập nhật lớp vùng theo điểm (majority/priority).
4. Kiểm tra ngưỡng diện tích và point count.
5. Sinh `qc_issue_point` cho trường hợp fail/review.
6. Tạo điểm đại diện bằng Feature To Point (`INSIDE`).
7. Chuyển tọa độ WGS84 + sinh Google Maps satellite URL.
8. Cắt raster theo polygon và gửi AI review.

### Trạng thái vận hành đề xuất
- `PASS`
- `REVIEW`
- `FAIL`
- `EXCEPTION`

## 4) Vai trò Gemma 4 E4B trong hệ thống

Gemma 4 E4B phù hợp cho lớp **multimodal screening/QC**:

- Đối chiếu nhãn rule-based với crop ảnh vùng.
- Trả cảnh báo nghi vấn + bằng chứng thị giác.
- Đề xuất ưu tiên review thủ công.
- Có thể tích hợp function calling để gọi tool nội bộ.

### Nguyên tắc bắt buộc
- AI không phải quyết định pháp lý cuối cùng.
- AI không ghi đè trực tiếp rule-based classification.
- Nếu ảnh mơ hồ/che phủ thì đặt `needs_manual_review=true`.

### Schema JSON đầu ra AI đề xuất

```json
{
  "polygon_id": "PLG_000123",
  "predicted_object_code": "72_A01",
  "predicted_object_name": "Vùng phủ bề mặt loại A",
  "confidence": 0.84,
  "matches_rule_based_class": true,
  "visible_evidence": ["..."],
  "warnings": ["..."],
  "needs_manual_review": false,
  "review_priority": "medium"
}
```

## 5) Mô hình dữ liệu và rule control

Các lớp/bảng cốt lõi:

- `wrk_line_*`
- `wrk_point_survey`
- `wrk_polygon_surface`
- `qc_issue_point`
- `tbl_rule72_object`
- `tbl_rule72_threshold`
- `tbl_transform_profile`
- `tbl_ai_review_log`
- `tbl_processing_run`

Khuyến nghị tận dụng geodatabase capabilities:

- **Subtypes**
- **Domains**
- **Contingent Values**
- **Attribute Rules**
  - immediate calculation
  - constraint
  - validation

## 6) Chuyển tọa độ VN-2000 sang Google đúng cách

Nguyên tắc:

1. “VN-2000” phải xác định rõ CRS nguồn (zone/kinh tuyến trục).
2. Chọn transformation theo extent thực tế qua `ListTransformations`.
3. Cho phép custom transformation khi dữ liệu đo đạc đặc thù.

Quy trình:

- Feature To Point (`INSIDE`) trên polygon.
- Project sang WGS84 với transformation phù hợp.
- Tính `google_lat`/`google_lng`.
- Sinh URL:

```text
https://www.google.com/maps/@?api=1&map_action=map&center={lat},{lng}&zoom=19&basemap=satellite
```

## 7) Cấu trúc repo đề xuất

```text
surface-qc-arcgis/
  addin/
  gp_toolbox/
  scripts/
    run_topology.py
    polygonize.py
    classify_from_points.py
    qc_metrics.py
    clip_raster_by_polygon.py
    gemma_review.py
    export_google_review.py
    transformations.py
  config/
  docs/
  tests/
```

## 8) 3 quyết định cần chốt trước khi code production

1. Định nghĩa pháp lý/chuyên môn đầy đủ của “chuẩn 72” và mapping field chính thức.
2. CRS nguồn VN-2000 cụ thể theo khu vực dữ liệu.
3. Quy định trách nhiệm AI (QC support) vs con người (phê duyệt cuối).

---

Tài liệu này dùng như blueprint triển khai giai đoạn 2 theo hướng ổn định, truy vết được, dễ mở rộng và kiểm soát rủi ro AI.
