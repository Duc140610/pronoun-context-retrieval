# PROJECT PLAN: Context Retrieval cho dịch đại từ nhân xưng Anh–Việt

> File này là nguồn định hướng duy nhất của dự án. Mọi thay đổi phạm vi phải thảo luận trước, rồi ghi vào mục **Nhật ký thay đổi** ở cuối file.
> Tiến độ theo dõi ở `PROJECT_PROGRESS.md`.

---

## 1. Tổng quan

**Đề tài (PR1):** Xây dựng pipeline truy hồi các lượt hội thoại liên quan trước khi dịch, tập trung vào câu chứa đại từ, cho cặp Anh→Việt.

**Câu hỏi nghiên cứu (RQ):** Context retrieval có giúp cải thiện dịch đại từ so với sentence-only và full-context MT không?

**Câu hỏi phụ:**
- RQ1: BM25, dense, hybrid+rerank có hơn last-K (lấy các lượt gần nhất) không?
- RQ2: Khoảng cách giữa Oracle và retrieval là do retrieval kém hay do mô hình dịch không tận dụng được context?
- RQ3: Recall@K cao hơn có đi kèm We Accuracy cao hơn không?

**Ràng buộc từ đề bài:** dùng dữ liệu song ngữ/hội thoại Anh–Việt công khai; **không** dùng dataset 3.800 truy vấn tự xây dựng.

**Thời gian:** 6 tuần.

---

## 2. Phạm vi

> Các lựa chọn thu hẹp dưới đây là **đề xuất của dự án**, đề bài không yêu cầu. Hiện **chốt tạm, chưa hỏi giảng viên**; mốc gặp giảng viên: trước khi bắt đầu Tuần 3 (xem mục 9).

**Trọng tâm (gán tay toàn bộ mẫu):** đại từ *we/us/our* và cách dịch sang *chúng ta / chúng tôi / chúng mình* (inclusive vs exclusive). Hiểu "We Translation Accuracy" theo Vu 2024 (Bảng 10); cần xác nhận.

**Gán tay đầy đủ trên mẫu nhỏ (100–150 câu):** các đại từ I, you, he, she, they, để có nhãn thật cho mọi loại đại từ.

**Đo tự động (phần mẫu còn lại):** Pronoun Accuracy dùng lớp tương đương.

**Ngoài phạm vi:** huấn luyện/fine-tune mô hình dịch; phân tích attention; ngôn ngữ khác; Consistency theo cặp người nói–người nghe (phụ đề không có nhãn người nói).

---

## 3. Pipeline

```
Kho hội thoại (tài liệu đã qua kiểm tra ranh giới)
        ↓
Câu truy vấn: câu nguồn chứa "we/us/our" (chọn từ cặp căn chỉnh 1:1)
        ↓
Ứng viên = các dòng tiếng Anh TRƯỚC câu hiện tại trong cùng phim (kho 100–150 dòng)
        ↓
Retriever → top-K   (random / last-K / BM25 / dense / hybrid+rerank / oracle)
        ↓
Prompt MT = câu nguồn + K lượt context (giữ thứ tự thời gian)
        ↓
Bản dịch tiếng Việt  (cache toàn bộ)
        ↓
Đánh giá: We Acc, Pronoun Acc, Consistency, BLEU/COMET, Recall@K
```

**Quy tắc bất biến:**
1. Không bao giờ lấy lượt **sau** câu hiện tại (tránh rò rỉ).
2. K cố định cho mọi retriever (mặc định K=3) để so sánh công bằng.
3. Một prompt dịch cố định cho mọi hệ thống; chỉ phần context thay đổi.
4. Cache mọi output (retrieval và bản dịch); với retrieval, lưu xếp hạng top-20 (hoặc toàn bộ) để tính lại Recall@K. Không gọi lại API không cần thiết.
5. Tập test bị **đóng băng** sau khi gán nhãn xong; không tinh chỉnh dựa trên test.
6. Mọi lựa chọn (K, N, seed, mô hình, ngưỡng lọc, từ điển) nằm trong `config.py` hoặc file nhãn, không hard-code.

---

## 4. Các hệ thống so sánh

| # | Hệ thống | Ghi chú |
|---|----------|---------|
| 1 | Sentence-only | Không context; là mốc mô hình |
| 2 | Random-K | Chặn dưới |
| 3 | Last-K | Baseline mạnh, bắt buộc phải so |
| 4a | Full-context (N=20) | 20 lượt gần nhất |
| 4b | Full-context (toàn kho) | Toàn bộ kho ứng viên |
| 5 | BM25 + MT | |
| 6 | Dense + MT | multilingual-e5 hoặc bge-m3 |
| 7 | Hybrid + rerank + MT | RRF, rồi cross-encoder rerank |
| 8 | Oracle | Đưa đúng `support_ids`; chỉ chạy trên tập con có `support_ids` |
| (tùy chọn) | src+hyp | Dùng bản dịch trước làm context; sinh tuần tự nên chậm |

**Biến thể nếu còn thời gian:** LLM làm reranker với câu hỏi "câu nào giúp xác định người nghe/nhóm người *we*?". Lý do: cross-encoder chuẩn chấm tương đồng chủ đề, không chấm vai trò xưng hô.

---

## 5. Dữ liệu và gán nhãn

**Nguồn chính:** OpenSubtitles en-vi (OPUS), **phiên bản v2018**. Đã khảo sát: 3886 tài liệu, 3.681.737 cặp, trung bình khoảng 947 câu mỗi tài liệu. Giấy phép: **[cần ghi]**.
**Dự phòng:** TED en-vi (Qi et al. 2018), chỉ khi quá ít tài liệu đạt kiểm tra. Lưu ý nhãn gán trên OpenSubtitles không chuyển sang TED được. *(Đã chốt không cần dùng, xem kết quả bên dưới.)*

**Bước chặn đầu tiên:** `src/check_boundaries.py`, lọc theo tài liệu, đọc từ file `.ids`. Tiêu chí tài liệu đạt:
- C1: id câu tiếng Anh **và tiếng Việt** tăng đơn điệu nghiêm ngặt, 0 vi phạm (hai phía; chỉ tiếng Anh cho 2.891 tài liệu, cả hai phía cho 2.073).
- C2: `max_en_id >= 200` (id tiếng Anh lớn nhất trong `.ids`, là cận dưới của số dòng thật).
- C3: tỉ lệ liên kết 1:1 ≥ 0.85 (chọn theo phân phối: phân vị 25% là 0.852, trung vị 0.918).
- C4: mỗi mã phim chỉ giữ một file. Mã phim là phần tử thứ 3 của đường dẫn (`en/<năm>/<mã_phim>/<id_phụ_đề>.xml.gz`). OPUS đã chỉ giữ một bản mỗi phim nên C4 không loại thêm tài liệu nào.
- C5: kho dựng được chỉ chứa dòng cùng tài liệu. Kiểm trên XML thật, chạy trên **tập phim con** (xem bên dưới), điều kiện: `n_s >= max_en_id` (số thẻ `<s>` thật không nhỏ hơn id lớn nhất trong `.ids`) và id thẻ `<s>` liên tục từ 1, khớp thứ tự với `.ids`.

**Kết quả C1–C4 (toàn bộ `.ids`):** 3.886 tài liệu → 2.060 sau C1+C2 (2.060 phim duy nhất) → **1.566 phim** sau C3 và C4.

**Quy tắc quyết định:** còn ≥ 500 phim → dùng OpenSubtitles; 200–500 phim → dùng, ghi hạn chế; < 200 phim → thảo luận, cân nhắc TED. **Quyết định: dùng OpenSubtitles** (1.566 ≥ 500).

**Lấy XML:** server OPUS không phục vụ XML lẻ; chỉ có `en.zip` (ZIP64, khoảng 25 GB, 586.785 file). Dùng HTTP Range: đọc Central Directory (~68 MB, cache ra đĩa), rồi tải đúng khối byte của từng file. Đường dẫn trong zip: `OpenSubtitles/xml/` + đường dẫn `.ids` bỏ đuôi `.gz`. Đã kiểm chứng trên một tài liệu (1154 thẻ `<s>` = `max_en_id`). XML đã tải lưu ở `data/raw/` (không đưa vào git).

**Tập phim con và chia tập:** chia dev/test **theo mã phim** bằng hàm băm MD5 tất định trên `seed:mã_phim` (seed 20261110, tỉ lệ dev 0.70; thực tế trên 1.566 phim là 0.676), thực hiện trước khi gán nhãn. Sau đó sắp theo giá trị băm và lấy **400 phim (280 dev, 120 test)**; nếu cần thêm thì lấy tiếp theo thứ tự cũ. Số câu mẫu tối đa mỗi phim: `MAX_WE_PER_MOVIE` (hiện 3, cân nhắc 3–5), để mẫu không bị vài phim chi phối. Đóng băng test ngay sau bước kappa.

**Kho:** quanh mỗi mẫu có 100–150 dòng **tiếng Anh** liên tiếp trước nó trong cùng phim, tính trên toàn bộ dòng của file XML nguồn (không chỉ các cặp căn chỉnh), vì alignment có khoảng trống lớn. Câu truy vấn chọn từ cặp căn chỉnh 1:1 để reference ít nhiễu.

**Mẫu đánh giá:**
- 250–300 câu chứa *we/us/our*. Câu chỉ chứa *let's* bị loại khỏi mẫu chính (dự kiến gần như luôn inclusive và thường dịch không có đại từ; sẽ đếm lại); báo cáo số lượng bị loại.
- **Nhãn theo từng lần xuất hiện** (nghĩa **gốc** của câu tiếng Anh, không dựa vào reference): *inclusive* / *exclusive* / *generic* / *unclear*. Kết quả chính tính trên inclusive và exclusive; báo cáo tỉ lệ generic và unclear.
- 120–150 câu có `support_ids`: các dòng trong cửa sổ 30 dòng trước mà người đọc cần để xác định người nghe/nhóm (gồm cả dòng chứa đại từ khác cùng chỉ nhóm). Câu có nhãn chỉ xác định được nhờ dòng sau gắn cờ `label_from_future`, loại khỏi Recall@K và Oracle, báo cáo tỉ lệ.
- Cụm *we* liền kề có nhãn `same_group_as_prev` (gán tay, không suy từ khoảng cách).
- Cờ tùy chọn (quyết định sau khi gán thử): `via_pronoun`, `needs_intra_sentence_reasoning`.
- Một tập con 100–150 câu (nằm trong mẫu trên) được gán tay đầy đủ cho các đại từ khác (I/you/he/she/they): các cách dịch hợp lệ theo ngữ cảnh. **Gán thử 20 câu và bấm giờ ở tuần 2** trước khi chốt kích thước tập con.
- Gán lần hai cho 60–80 câu để tính Cohen's kappa. Nếu không có người thứ hai: intra-annotator agreement (tự gán lại sau vài ngày), ghi rõ là hạn chế. Nếu sau này có người thứ hai, phải xong trước khi đóng băng test.

**Phương án cắt giảm (nếu trượt tiến độ):** 150 câu, trong đó 80–100 câu có `support_ids`.

**Lưu ý:** cần xác nhận với giảng viên rằng bộ gán tay này (quy mô nhỏ, mục đích kiểm chứng) không vi phạm yêu cầu "không dùng dataset 3.800 truy vấn tự xây dựng".

---

## 6. Metric

| Metric | Định nghĩa |
|--------|-----------|
| **We Accuracy** | So lớp inclusive/exclusive của bản dịch với nhãn gán tay. Báo cáo **hai mức**: (a) mức câu: mọi lần xuất hiện đều đúng (như Vu 2024); (b) mức từng lần xuất hiện. Với mỗi mức báo **ba số**: accuracy trên ca xác định được, độ phủ (tỉ lệ ca xác định), và cận dưới (tính ca không xác định là sai). Bản dịch lược bỏ *we* là hợp lệ trong tiếng Việt nên không chỉ tính là sai. Số chính chốt sau khi thấy tỉ lệ lược bỏ trên dev. Luôn kèm mốc ngẫu nhiên, mốc lớp đa số, mốc Sentence-only. |
| **Pronoun Accuracy** | Với các đại từ khác. Trên tập con gán tay đầy đủ: so với tập cách dịch hợp lệ đã gán. Trên phần còn lại: so loại đại từ/xưng hô với reference theo lớp tương đương (từ điển đại từ tiếng Việt), đo thô. Báo cáo riêng hai phần. |
| **Consistency** | Trên các cụm *we* liền kề cùng nhóm (`same_group_as_prev`): tỷ lệ cặp được dịch cùng một lớp xưng hô. |
| **BLEU / COMET** | SacreBLEU và wmt22-comet-da, chủ yếu để kiểm soát chất lượng dịch chung. |
| **Recall@K** | Tỷ lệ truy vấn mà top-K chứa ít nhất một dòng thuộc `support_ids` (không gồm ca `label_from_future`); có thể báo thêm tỷ lệ phủ toàn bộ. Báo cáo kèm MRR. |

**Từ điển nhận diện lớp (hoàn thiện ở tuần 2):** inclusive: chúng ta, chúng mình, tụi mình, bọn mình; exclusive: chúng tôi, chúng em, chúng con, tụi tôi, bọn tôi; *mình* hoặc *ta* đứng một mình không tính tự động.

**Kiểm chứng hàm chấm:** kiểm tay 50–100 bản dịch để xác nhận hàm chấm tự động khớp với người; báo cáo độ khớp.
**Thống kê:** paired bootstrap resampling cho chênh lệch giữa các hệ thống; báo cáo khoảng tin cậy.

---

## 7. Roadmap 6 tuần

### Tuần 1: Bài toán, đặc tả, dữ liệu thô
**Kiến thức cần nắm:** hệ thống xưng hô tiếng Việt; *we* inclusive/exclusive; anaphora và antecedent; context-aware MT; IR cơ bản (query, document, top-K, Recall@K, MRR).
**Việc cần làm:**
- [x] Đọc Müller 2018, Choudhary 2025, Vu 2024.
- [~] Viết trang đặc tả (bản nháp v0.2; cập nhật tài liệu): chuyển sang Tuần 2.
- [ ] Gửi đặc tả cho giảng viên: hoãn đến mốc gặp trước Tuần 3.
- [~] Tải và khảo sát OpenSubtitles en-vi (phiên bản v2018 đã ghi; còn giấy phép).
- [x] Viết `check_boundaries.py`, chạy toàn bộ `.ids` (C1–C4); quyết định nguồn dữ liệu. C5 chuyển sang Tuần 2.
**Hoàn thành khi:** có kết quả kiểm tra ranh giới và quyết định nguồn dữ liệu (đã xong); đặc tả v0.2 hoàn chỉnh; đã chọn ngày gặp giảng viên (hai mục sau chuyển sang đầu Tuần 2).

### Tuần 2: Kho hội thoại, lọc câu *we*, thử thư viện nặng
**Kiến thức cần nắm:** tách từ tiếng Việt (underthesea/VnCoreNLP); chuẩn hóa Unicode NFC; regex.
**Việc cần làm:**
- [ ] Hoàn tất việc dở của Tuần 1: tra giấy phép corpus, đặc tả v0.2, chọn ngày gặp giảng viên.
- [ ] Dọn `check_boundaries.py` (bỏ khối chẩn đoán); đưa `fetch_xml.py` vào `src/`, thử trên 3 phim, rồi tải XML cho 400 phim.
- [ ] Chạy C5 trên 400 phim; báo tỉ lệ đạt và phân phối `n_s / max_en_id`.
- [ ] Dựng kho 100–150 dòng tiếng Anh từ file XML; lọc câu nguồn có *we/us/our*; trích lớp *chúng tôi/chúng ta/chúng mình* phía Việt.
- [ ] Lập từ điển đại từ/xưng hô tiếng Việt và lớp tương đương.
- [ ] Chọn 250–300 câu ứng viên.
- [ ] Gán thử 20 câu (đủ loại đại từ), bấm giờ, chốt kích thước tập con gán đầy đủ.
- [ ] **Cài thử và chạy thử** COMET, sentence-transformers, reranker trên Kaggle/Colab.
**Hoàn thành khi:** có file dữ liệu ứng viên; C5 đã chạy; cả ba thư viện nặng chạy được trên một ví dụ nhỏ.

### Tuần 3: Gán nhãn, kappa, đóng băng test
**Điều kiện bắt đầu:** đã gặp giảng viên (mục 9).
**Kiến thức cần nắm:** Cohen's kappa; viết guideline gán nhãn; xử lý trường hợp mơ hồ.
**Việc cần làm:**
- [ ] Viết guideline gán nhãn (1–2 trang), gồm quy tắc cho ca mơ hồ.
- [ ] Gán nhãn từng lần xuất hiện cho toàn bộ mẫu; gán `support_ids`, `label_from_future`, `same_group_as_prev`.
- [ ] Gán đầy đủ các đại từ khác trên tập con 100–150 câu.
- [ ] Gán lại (intra-annotator, hoặc người thứ hai nếu có); tính kappa.
- [ ] **Đóng băng test.**
**Hoàn thành khi:** có file nhãn cuối cùng và giá trị kappa. Nếu chưa xong vào cuối tuần, áp dụng phương án cắt giảm ở mục 5.

### Tuần 4: Baseline MT, metric, kiểm hàm chấm
**Kiến thức cần nắm:** prompting LLM cho dịch (Choudhary Phụ lục A.3); BLEU/SacreBLEU; COMET; paired bootstrap.
**Việc cần làm:**
- [ ] Chọn mô hình dịch; cố định phiên bản, prompt và temperature 0 trên dev. Kiểm tra sớm trên 30 câu: Oracle có tốt hơn Sentence-only không; nếu không, đổi mô hình.
- [ ] Chạy hệ thống 1, 2, 3 và Oracle; cache output.
- [ ] Cài hàm chấm We Acc (hai mức, ba số), Pronoun Acc, Consistency, BLEU/COMET.
- [ ] Kiểm tay 50–100 bản dịch; chấm trên reference (phải ≈ 100%).
**Hoàn thành khi:** có bảng kết quả hệ thống 1–3 và Oracle trên dev; độ khớp hàm chấm với người đã được ghi lại.

### Tuần 5: Retrieval và chạy toàn bộ
**Kiến thức cần nắm:** BM25; bi-encoder và cosine similarity; cross-encoder rerank; Reciprocal Rank Fusion; Recall@K, MRR, nDCG.
**Việc cần làm:**
- [ ] Cài BM25, dense, hybrid + rerank; tính Recall@K và MRR theo `support_ids`.
- [ ] Chạy hệ thống 4–7 trên dev, chốt K; chạy toàn bộ hệ thống trên test **một lần**.
- [ ] (Nếu còn thời gian) biến thể LLM-reranker.
**Hoàn thành khi:** có kết quả test đầy đủ cho các hệ thống 1–8, đã cache.

### Tuần 6: Phân tích và viết báo cáo
**Kiến thức cần nắm:** khoảng tin cậy; tương quan (Pearson/Spearman); phân tích lỗi định tính.
**Việc cần làm:**
- [ ] Phân tích ba trục: loại đại từ; khoảng cách đến dòng tín hiệu (kèm phân phối nhãn theo khoảng cách); độ dài hội thoại.
- [ ] Liên hệ Recall@K với We Acc (RQ3, lưu ý tương quan không phải nhân quả); so Oracle với retrieval (RQ2).
- [ ] Bảng ví dụ định tính (như Bảng 3 của Choudhary).
- [ ] Viết báo cáo, làm slide; để 3–4 ngày cuối cho rà soát.
**Cấu trúc báo cáo:** Giới thiệu → Related work → Bài toán và dữ liệu → Phương pháp → Metric → Kết quả → Phân tích lỗi → Hạn chế → Kết luận.
**Hoàn thành khi:** báo cáo và slide hoàn chỉnh. Kết quả âm tính vẫn hợp lệ nếu phân tích trung thực.

---

## 8. Rủi ro và cách xử lý

| Rủi ro | Xử lý |
|--------|-------|
| Ranh giới phim không tin cậy | Lọc theo tài liệu ở tuần 1 (C1–C4), C5 ở tuần 2; dự phòng TED |
| Gán nhãn trước khi kiểm tra ranh giới, nhãn mất khi đổi nguồn | `check_boundaries` là cổng bắt buộc trước khi gán |
| Cùng một phim nằm ở cả dev và test | Chia theo mã phim bằng hàm băm, mỗi phim một file |
| Tải XML từ xa lỗi hoặc dở dang | Ghi `.tmp` rồi đổi tên sau khi parse thành công; log lỗi từng phim; cache Central Directory |
| Gán nhãn tốn thời gian hơn dự tính | Phương án cắt giảm còn 150 câu |
| Không có người gán thứ hai | Intra-annotator agreement + ghi rõ hạn chế |
| Phụ đề dịch sai làm nhãn nhiễu | Gán nhãn theo nghĩa câu gốc tiếng Anh |
| Hàm chấm tự động sai (tiếng Việt nhiều cách dịch hợp lệ, hay lược chủ ngữ) | Lớp tương đương + báo ba số + kiểm tay 50–100 bản dịch |
| Mô hình dịch rẻ quá yếu, không tận dụng context | Kiểm tra sớm Oracle và Sentence-only trên 30 câu |
| last-K thắng áp đảo | Không phải lỗi: là kết quả hợp lệ; Oracle giúp giải thích |
| Gold heuristic (nếu phải dùng) thiên về recency | Chỉ làm gold phụ và nêu rõ giới hạn |
| Thư viện nặng gây lỗi muộn | Chạy thử từ tuần 2 |
| Chi phí API/GPU | Ước lượng ở tuần 4; cache mọi output |
| Sinh tuần tự (src+hyp) chậm | Chỉ làm nếu còn thời gian |

---

## 9. Quyết định chốt tạm và câu hỏi mở

**Mốc bắt buộc:** gặp giảng viên trước khi bắt đầu Tuần 3.

| Điểm mở | Chốt tạm | Nếu giảng viên đổi ý |
|---|---|---|
| Gold cho Recall@K | Gán tay `support_ids` trên 120–150 câu | Thêm nhãn heuristic từ reference làm gold phụ, tính lại Recall@K từ xếp hạng đã cache |
| Trọng tâm | *we* toàn mẫu; đại từ khác gán tay trên 100–150 câu, còn lại đo tự động | Đo thô thêm đại từ khác trong các câu *we* đã chọn: chỉ chấm lại. Đo trên câu không chứa *we* hoặc gán tay toàn mẫu: phải chọn mẫu thêm, dịch thêm, gán thêm |
| We Accuracy | Inclusive/exclusive theo Vu 2024 | Đổi từ điển; nếu định nghĩa khác hẳn thì nhãn phải gán lại |
| Người gán thứ hai | Intra-annotator trước; nhờ bạn học nếu tìm được (trước khi đóng băng test) | Thêm kappa giữa hai người |
| Dữ liệu | OpenSubtitles v2018 lọc theo tài liệu (**đã chốt**, 1.566 phim đạt); TED không cần | Đổi nguồn sau khi gán nhãn là mất nhãn, nên cổng kiểm tra ở tuần 1 |
| Mô hình dịch | Thử mô hình rẻ/miễn phí, cố định một mô hình | Đổi mô hình = chạy lại bằng cache mới; tham số trong `config.py` |

**Câu hỏi cho giảng viên:**
- [ ] Bộ gán tay 250–300 câu và Recall@K qua `support_ids` có được chấp nhận không? (Nếu không: dùng nhãn heuristic từ reference, Recall@K kém tin cậy hơn.)
- [ ] Ưu tiên *we* toàn mẫu, đại từ khác gán đầy đủ chỉ trên mẫu nhỏ, có được không?
- [ ] "We Translation Accuracy" có đúng là inclusive/exclusive (theo Vu 2024)?
- [ ] Consistency định nghĩa trên cụm *we* liền kề cùng nhóm có chấp nhận được không?
- [ ] Có người gán thứ hai không?
- [ ] Dùng API hay GPU (loại nào)? Mô hình dịch nào?

---

## 10. Cấu trúc thư mục

```
pronoun-context-retrieval/
├── PROJECT_PLAN.md
├── PROJECT_PROGRESS.md
├── config.py        # seed, K, N, mô hình, ngưỡng lọc, từ điển
├── requirements.txt
├── data/            # boundaries_table.csv, selected_docs.csv, split_movies.csv (vào git)
│   └── raw/         # XML tải về, central_directory_index.pkl (không đưa vào git)
├── notebooks/       # script thăm dò, không import vào src/
├── src/             # check_boundaries, split, fetch_xml, filter_we, retrievers, translate, metrics
├── cache/           # output retrieval (top-20) và bản dịch
├── results/         # bảng kết quả, phân tích
└── report/
```

---

## 11. Tài liệu tham khảo

1. Müller et al. (2018). *A Large-Scale Test Set for the Evaluation of Context-Aware Pronoun Translation in NMT.* WMT. https://aclanthology.org/W18-6307/
2. Choudhary et al. (2025). *Exploring Context Strategies in LLMs for Discourse-Aware MT.* Findings of EMNLP. https://aclanthology.org/2025.findings-emnlp.1324/
3. Vu et al. (2024). *Context-Aware MT with Source Coreference Explanation.* TACL. https://aclanthology.org/2024.tacl-1.48/

**Tài liệu bổ sung (đã có trong project):** Mąka et al. (2025), COLING, về attention head và khử nhập nhằng đại từ (chỉ đọc lướt, ngoài phạm vi).

---

## 12. Nhật ký thay đổi

| Ngày | Thay đổi | Lý do |
|------|----------|-------|
| 2026-11-08 | Tạo bản đầu tiên | Hợp nhất đề bài PR1 với góp ý về gán nhãn, kho lớn hơn, Oracle |
| 2026-11-08 | Phạm vi trung gian: *we* gán tay toàn mẫu; I/you/he/she/they gán tay đầy đủ trên tập con 100–150 câu, phần còn lại đo tự động; thêm bước gán thử 20 câu ở tuần 2 | Gán đầy đủ mọi đại từ trên toàn mẫu ước tính thêm 30–50 giờ, dễ trượt tiến độ |
| 2026-11-10 | Chốt tạm các điểm mở, chưa hỏi giảng viên; đặt mốc gặp trước Tuần 3; bỏ yêu cầu "đã gửi đặc tả" khỏi điều kiện hoàn thành Tuần 1 | Sinh viên muốn tự hiểu dự án trước khi gặp |
| 2026-11-10 | Kho ứng viên tính trên toàn bộ dòng tiếng Anh; truy vấn chọn từ cặp 1:1 | Alignment có khoảng trống lớn (T1.7) |
| 2026-11-10 | Nhãn *we* thành 4 loại theo từng lần xuất hiện; thêm `label_from_future`; loại câu chỉ có *let's*; thêm cờ tùy chọn; We Acc báo ba số | Phản biện đặc tả v0.1 |
| 2026-11-10 | Lọc theo tài liệu (tiêu chí C1–C5) thay vì chuyển sang TED; chia dev/test theo mã phim | Nhãn không chuyển nguồn được; dữ liệu dư nhiều (T1.8) |
| 2026-11-10 | C1 áp dụng cả hai phía (Anh và Việt); C2 dùng `max_en_id >= 200`; C3 chốt 0.85 | Kết quả T1.8 (2.060 / 1.566) dùng tiêu chí này; chỉ tiếng Anh cho 2.891 tài liệu |
| 2026-11-10 | C5 chạy trên tập phim con (400 phim: 280 dev, 120 test, chia bằng hàm băm trước khi chọn) thay vì toàn bộ; điều kiện `n_s >= max_en_id` và id liên tục | Chỉ lấy được XML qua HTTP Range trên `en.zip`; mẫu cuối chỉ cần vài trăm phim |
| 2026-11-10 | Chốt nguồn OpenSubtitles v2018 (1.566 phim đạt C1–C4); không dùng TED; thêm `MAX_WE_PER_MOVIE` | Vượt xa ngưỡng 500 phim; tránh vài phim chi phối mẫu |
