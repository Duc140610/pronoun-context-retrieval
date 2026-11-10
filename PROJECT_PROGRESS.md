# PROJECT PROGRESS

> Cập nhật khi kết thúc buổi làm việc hoặc khi có quyết định lớn.
> Định hướng và tiêu chí hoàn thành xem ở `PROJECT_PLAN.md`.

## Trạng thái hiện tại

- **Tuần hiện tại:** Tuần 2 (đầu tuần). Tuần 1 đóng, còn 3 việc dở chuyển sang Tuần 2 (xem bên dưới).
- **Task đang làm:** dọn `check_boundaries.py`, đưa `fetch_xml.py` vào `src/`, thử trên 3 phim rồi tải 400 phim và chạy C5.
- **Cập nhật lần cuối:** 2026-11-10
- **Commit mới nhất:** `16e67aa` (C1-C4, đóng băng split dev/test), đã push.

## Quyết định chốt tạm (chưa hỏi giảng viên)

Mốc bắt buộc: **gặp giảng viên trước khi bắt đầu Tuần 3** (gán nhãn). Sau mốc đó, mỗi hướng bị bác bỏ tốn hàng chục giờ.

- Gold cho Recall@K: gán tay `support_ids` trên 120-150 câu.
- Trọng tâm: *we* gán tay toàn mẫu 250-300 câu; I/you/he/she/they gán tay đầy đủ trên tập con 100-150 câu; phần còn lại đo tự động.
- We Accuracy: inclusive/exclusive theo Vu 2024; nhãn gán trên câu tiếng Anh gốc, không dựa vào reference.
- Người gán thứ hai: intra-annotator (cách nhau vài ngày), nhờ bạn học nếu tìm được. Nếu có người thứ hai, phải xong trước khi đóng băng test.
- Dữ liệu: OpenSubtitles en-vi v2018, lọc theo tài liệu (**đã chốt**); TED không cần.
- Kho ứng viên: toàn bộ dòng tiếng Anh của phim; truy vấn chọn từ cặp căn chỉnh 1:1.
- Dev/test chia theo mã phim bằng hàm băm (**đã đóng băng**).
- Mô hình dịch: thử mô hình rẻ/miễn phí trước, cố định một mô hình, temperature 0, kiểm tra sớm trên 30 câu (Sentence-only và Oracle).

## Câu hỏi mở

- [ ] Giảng viên chấp nhận bộ gán tay 250-300 câu và Recall@K qua `support_ids`?
- [ ] Giảng viên chấp nhận ưu tiên *we* và gán đầy đủ đại từ khác chỉ trên mẫu nhỏ?
- [ ] "We Translation Accuracy" đúng là inclusive/exclusive?
- [ ] Có người gán thứ hai không?
- [ ] API hay GPU? Mô hình dịch nào?

## Danh sách task Tuần 1

- [x] **T1.1** Nắm hệ thống xưng hô tiếng Việt và *we* inclusive/exclusive
- [x] **T1.2** Đọc Müller 2018
- [x] **T1.3** Đọc Choudhary 2025
- [x] **T1.4** Đọc Vu 2024 (cách đo We Accuracy)
- [~] **T1.5** Trang đặc tả: bản nháp v0.2 trong chat; tài liệu đã tạo vẫn là v0.1. Chuyển sang Tuần 2.
- [ ] **T1.6** Gửi đặc tả cho giảng viên: hoãn đến mốc gặp trước Tuần 3
- [~] **T1.7** Tải và khảo sát OpenSubtitles en-vi. Phiên bản đã ghi: OPUS OpenSubtitles v2018. Còn thiếu: giấy phép (tra trên trang OPUS).
- [x] **T1.8** `check_boundaries.py` (C1-C4) và quyết định nguồn dữ liệu. C5 chuyển sang Tuần 2.

**Tuần 1 xong khi:** có kết quả `check_boundaries` và quyết định nguồn dữ liệu (đã xong); đặc tả v0.2 hoàn chỉnh; đã chọn ngày gặp giảng viên (hai mục này chuyển sang đầu Tuần 2).

## Kết quả T1.8

- 3.886 tài liệu trong `.ids`.
- C1 chỉ tiếng Anh: 2.891; C1 cả hai phía: 2.073. **Chọn cả hai phía** (căn chỉnh đảo thứ tự ở phía Việt làm nhiễu reference).
- C2 `max_en_id >= 200` và `n_links >= 200` gần như không khác (3.873 so với 3.868). Chọn `max_en_id`.
- Sau C1+C2: **2.060** tài liệu = 2.060 phim duy nhất, nên C4 không loại gì (OPUS chỉ giữ một bản mỗi phim).
- C3 với `min_ratio_11 = 0.85` (phân vị 25% là 0.852, trung vị 0.918): còn **1.566 phim**.
- Quyết định: dùng OpenSubtitles (1.566 >= 500); không kích hoạt TED.
- Bảng đầy đủ trước khi lọc: `data/boundaries_table.csv`. Danh sách phim đạt: `data/selected_docs.csv`.

## Chia dev/test (đóng băng)

- Phương pháp: MD5 trên `seed:mã_phim`, seed 20261110, tỉ lệ dev đặt 0.70.
- Tỉ lệ dev thực tế trên 1.566 phim: 0.6762 (lệch khoảng 2 độ lệch chuẩn, chấp nhận được vì lấy số cố định).
- Mẫu: 400 phim (280 dev, 120 test), lấy theo thứ tự giá trị băm; mở rộng sau này giữ nguyên phần cũ.
- Đã kiểm: tất định (cùng SHA256 qua hai lần chạy), dev và test không giao nhau, ổn định khi tăng n.
- Không đổi seed sau khi đã thấy kết quả (đó là tinh chỉnh trên test).
- Danh sách: `data/split_movies.csv` (commit `16e67aa`).

## Lấy XML từ xa (đã kiểm chứng)

- OPUS không phục vụ XML lẻ (lỗi `NoSuchKey`). Chỉ có `en.zip`: ZIP64, 25.071.142.020 byte, 586.785 file, server có `accept-ranges: bytes`.
- Central Directory khoảng 68 MB, cache ra `data/central_directory_index.pkl` (không đưa vào git).
- Đường dẫn trong zip: `OpenSubtitles/xml/` + đường dẫn `.ids` bỏ `.gz`.
- Thử trên `en/1990/100288/4719672.xml.gz`: 1154 thẻ `<s>` = `max_en_id`. Chưa phải kết quả C5, chỉ chứng minh luồng kỹ thuật chạy được.

## Dữ liệu đã khảo sát (T1.7)

- OpenSubtitles en-vi (OPUS v2018): 3886 tài liệu, 3.681.737 cặp (liên kết), trung bình khoảng 947 câu mỗi tài liệu.
- Mỗi dòng `.ids` gồm 4 cột (tab): đường dẫn en, đường dẫn vi, id câu en (có thể nhiều id), id câu vi. Đường dẫn có dạng `en/<năm>/<mã_phim>/<id_phụ_đề>.xml.gz`; mã phim là phần tử thứ 3.
- Alignment có liên kết 1:2, 2:1, 3:1 và có các khoảng trống lớn (ví dụ tiếng Việt nhảy từ dòng 14 sang 37 trong khi tiếng Anh nhảy 16 sang 20), nên "N dòng trước" tính trên dòng tiếng Anh, không trên cặp đã căn chỉnh.
- Reference có thể lược bỏ đại từ hoặc dịch sai.

## Ghi chú đọc phê phán (dùng cho phần Hạn chế)

- Choudhary 2025: với GPT-4o, src+hyp gần như không khác src (6/9 ô MuDA F1 bằng nhau); với Gemma 2, src+hyp cao hơn ở 8/9 ô. Tương quan Bảng 4 (r ≈ 0.25, r² ≈ 6%) chỉ là gợi ý, không phải nhân quả. Một prompt, một lần chạy, không kiểm định.
- Vu 2024 Bảng 10: We Accuracy 12.71% sát mức ngẫu nhiên theo phép tính 0.5³, nhưng phép so sánh dựa trên ba giả định không được bài xác nhận. Luôn báo kèm mốc ngẫu nhiên và lớp đa số.
- Müller 2018: accuracy tăng theo antecedent distance ở mọi hệ thống do lớp *es* chiếm đa số khi khoảng cách tăng. Phân tích theo khoảng cách cần kèm phân phối nhãn.

## Việc kế tiếp

1. Dọn khối chẩn đoán (phương án A/B/C, các `print`) khỏi `src/check_boundaries.py`; chạy lại phải ra 2.060 / 1.566. Commit riêng.
2. Đưa `fetch_xml.py` vào `src/`: bỏ `errors="ignore"` ở phần giải mã nội dung XML; thêm `data/*.pkl` vào `.gitignore`.
3. Thử `fetch_xml` trên 3 phim (một đã có cache, một dev mới, một đường dẫn sai); rồi chạy 400 phim; ghi số thành công, số lỗi, log.
4. Viết C5 (đếm thẻ `<s>`, id liên tục, so với `max_en_id`); báo tỉ lệ đạt.
5. Tra giấy phép corpus; hoàn thiện đặc tả v0.2.
6. **Chọn ngày gặp giảng viên (trước Tuần 3).** Việc này không được trôi.

## Nhật ký buổi làm việc

### 2026-11-08
- Lập roadmap, viết `PROJECT_PLAN.md` và `PROJECT_PROGRESS.md`. Chốt phạm vi trung gian.

### 2026-11-10
- Hoàn thành T1.1-T1.4 và T1.7; có bản nháp đặc tả v0.2.
- Quyết định: chốt tạm các điểm mở; đặt mốc gặp giảng viên trước Tuần 3; kho tính trên dòng tiếng Anh; chia dev/test theo mã phim; hướng lọc theo tài liệu.
- Hoàn thành T1.8: C1-C4 (2.060 -> 1.566 phim), chốt OpenSubtitles v2018; kiểm chứng đường lấy XML qua HTTP Range.
- Phát hiện khi tái lập kết quả: C1 hai phía (chỉ tiếng Anh cho 2.891, không khớp số đã ghi). Giữ hai phía và sửa plan.
- Đóng băng split dev/test (400 phim, seed 20261110); commit `16e67aa` và push.
- Chuyển C5 sang Tuần 2, chạy trên 400 phim.
