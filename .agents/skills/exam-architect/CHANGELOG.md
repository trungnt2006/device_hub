# CHANGELOG - EXAM ARCHITECT

## [4.5.0] - 2026-11-08
### Added
- **Quy tắc Cấm Trích dẫn Vị trí Kiến thức trong Thân câu hỏi (`SKILL.md`, `AGENTS.md`, `question_auditor.py`):**
  - Cấm tuyệt đối việc đưa các cụm chỉ vị trí tài liệu như `(Slide Chương X, trang Y)`, `(Tài liệu Chương X, mục Y)`, `(Bài giảng Chương X)`, `(Ngân hàng câu hỏi - Câu Z)` vào trong thân câu hỏi (`question` / `stem`) hoặc phương án lựa chọn (`A, B, C, D`). Toàn bộ thông tin nguồn trích dẫn chỉ được phép đặt trong phần `Lời giải:` và `Metadata`.
  - Bổ sung bộ lọc `loc_citation_re` ở **Tầng 1 (Hard Errors)** trong `question_auditor.py` để tự động chặn cứng nếu phát hiện trích dẫn vị trí kiến thức trong thân câu hỏi.
- **Tối ưu Tỷ lệ Phối hợp Nguồn phôi (20%–30% Test Bank + 70%–80% Câu hỏi Mới) & Cơ chế Blacklist Chống trùng lặp chéo giữa các đề:**
  - Điều chỉnh tỷ lệ lấy từ Trắc nghiệm mẫu / Test Bank về mức **20% – 30%** (ưu tiên các câu chưa từng xuất hiện ở các đề trước) và dành **70% – 80%** thiết kế câu hỏi mới từ Giáo trình, Bài giảng chi tiết (`Chương *.docx`) và các phần kiến thức chuyên sâu trong Slide.
  - Khi tạo đề mới, bắt buộc quét danh sách thân câu hỏi (`Câu X:`) của các đề trước trong `Azota/` để lập **Blacklist chống trùng lặp chéo** (nhưng tuyệt đối không học lại phương án hay lời giải từ `Azota/` để chống *Model Autophagy*).
- **Chống Bơm chữ tạo "Phương án Người rơm" (Anti-Strawman Padding):**
  - Bổ sung quy tắc giới hạn độ dài phương án chuẩn đề thi đại học ($10 - 20$ từ, cảnh báo ở Tầng 2 khi trung bình $> 24$ từ) nhằm ngăn chặn AI bơm chữ bịa đặt vô lý vào 3 phương án sai để đuổi theo độ dài của đáp án đúng.

## [4.4.0] - 2026-11-07
### Added
- **Thắt chặt Quy tắc Tư duy Ngữ nghĩa ở Tầng AI (`SKILL.md` & `AGENTS.md`) — Cấm Phương án Tự giải nghĩa quá đà:**
  - Thiết lập **3 Khuôn mẫu Câu hỏi theo Mục đích Khảo thí (Strict Semantic Stem–Option Alignment)**:
    1. *Khuôn mẫu 1 (Câu hỏi Nhận diện Thuật ngữ / Khái niệm - Bloom 1–2):* Khi thân câu đã mô tả bản chất/định nghĩa, 4 phương án A, B, C, D **chỉ được ghi tên thuật ngữ ngắn gọn** (`A. Hướng chủ đề (Subject-Oriented).`, `B. Tích hợp (Integrated).`), cấm tuyệt đối nối thêm đuôi giải thích ý nghĩa làm lộ đáp án.
    2. *Khuôn mẫu 2 (Câu hỏi Phân tích Bản chất / Cơ chế của Thuật ngữ - Bloom 2–3):* Thân câu nêu đích danh tên thuật ngữ, 4 phương án chỉ mô tả cơ chế/hành động mà không gắn nhãn tên 4 thuật ngữ ở đầu câu.
    3. *Khuôn mẫu 3 (Câu hỏi Tình huống Kép - Bloom 3–4):* Chỉ khi thân câu hỏi rõ 2 vế (tên giải pháp/hiện tượng VÀ nguyên nhân/cơ chế thực thi trong bối cảnh đó), phương án mới được phép kết hợp cả hai.
  - Bổ sung **Giao thức Tự Kiểm tra "Che Thuật Ngữ" (The Blind-Term Self-Test):** Buộc AI tự kiểm chứng xem nếu che tên thuật ngữ ở đầu 4 phương án thì phần chữ còn lại có làm lộ đáp án không; nếu có phải cắt bỏ ngay.
- **Tái cấu trúc `question_auditor.py` theo hướng Linh hoạt, Không gò bó cực đoan:**
  - *Tầng 1 (Hard Errors):* Chỉ chặn cứng các lỗi cấu trúc khách quan 100% và lỗi thiên vị độc tôn (chỉ duy nhất đáp án đúng có `(English Term)` hoặc dài gấp $> 2.0$ lần câu dài thứ nhì). Loại bỏ các từ khóa kỹ thuật dễ bắt nhầm (`bằng tay`, `xóa sạch dữ liệu`, `lớp học`...) khỏi danh sách cấm cứng.
  - *Tầng 2 (Contextual Warnings):* Đưa bộ nhận diện `Thuật ngữ (English) + Đuôi giải thích` về mức **Cảnh báo Ngữ nghĩa AI** để nhắc Agent áp dụng *Bài test Che Thuật Ngữ* mà không chặn oan các câu hỏi tình huống vận dụng sâu (Bloom 3–4).

## [4.3.0] - 2026-10-31
### Added
- **Chuẩn hóa HUB Exam Standards v4.3 & 5 Điều Răn Thép:**
  1. *Nguyên tắc Song hành Cú pháp (Grammatical Parallelism):* Cả 4 phương án bắt buộc cùng một kiểu câu và cùng từ loại mở đầu; tính toán định lượng hệ số biến thiên độ dài ($CV \le 0.28$).
  2. *Đồng nhất Hệ quy chiếu Bản thể (Homogeneous Domain):* 100% phương án sai phải thuộc cùng một phạm trù chuyên môn học thuật; loại bỏ triệt để các hành vi vật lý đời thường, thủ công thô sơ.
  3. *Cơ chế 4 Kỹ thuật Tạo sai Khách quan:* Đảo chiều quan hệ (Inversion), Đánh tráo khái niệm song sinh (Sibling Swapping), Thiếu điều kiện ràng buộc (Missing Prerequisite), Xáo trộn trình tự (Displacement).
  4. *Chuỗi Mắt xích & Quy trình Đồng dạng:* Nếu phương án có cấu trúc mũi tên quy trình (`->`), bắt buộc cả 4 phương án đều phải có cấu trúc mũi tên tương ứng.
  5. *Cách ly Chống Lây nhiễm AI Slop (Anti-Contamination Boundary):* Mọi đề thi Word Azota lưu vào `Azota/`; khi quét tài nguyên nguồn để làm đề, TUYỆT ĐỐI LOẠI TRỪ 100% thư mục `Azota/` để chống hiện tượng Model Autophagy.
- **Ràng buộc Chia đợt Bắt buộc (Mandatory Batching - Max 25 câu/lần):** Khi sinh đề số lượng lớn (40-50 câu), bắt buộc chia làm 2 đợt để bảo toàn token suy luận và chất lượng phương án nhiễu.
- **Nâng cấp toàn diện `question_auditor.py`:** Mở rộng danh sách đen từ khóa tấu hài/đời thường, bổ sung kiểm tra từ ngữ cực đoan, kiểm tra tính song hành quy trình và tính toán CV chuẩn xác.

## [4.2.0] - 2026-10-29
### Added
- **Lệnh Meta-Prompt cho NotebookLM (Quick Command #5):** Tự động phân tích kết quả thi Azota, lọc 100% các câu làm sai (`✗`), phân loại lỗ hổng kiến thức và sinh Meta-Prompt chuẩn hóa sẵn sàng 1-Click để dán vào NotebookLM.
- **Bộ công cụ `azota_diagnostic.py`:** Trích xuất kết quả thi Azota và tự động sinh Meta-Prompt.
- **Quy tắc Đối xứng Chú thích Tiếng Anh (English Term Symmetry):** Chặn đứng lỗi thiên vị hình thức (chỉ duy nhất câu đúng có tiếng Anh) hoặc ngược lại.
- **Quy tắc Chống thiên vị diễn giải (No Elaboration Bias) & Chống bắt chữ (Anti-Clang Association).**

## [4.1.0] - 2026-10-26
### Added
- **Định hướng chuyên sâu 100% vào Ra đề (Question Authoring).**
- **Bộ 4 Định dạng câu hỏi chuyên sâu.**
- **Cơ chế Phân rã Chủ đề con & Chống trùng lặp khái niệm (Topic Coverage & Anti-Redundancy).**

## [4.0.0] - 2026-10-26
### Added
- **Đổi tên chính thức thành Exam Architect** theo định hướng chuẩn khảo thí quốc tế.
- **Hệ thống 4 lệnh vận hành 1-chạm:** Tạo đề, Hấp thụ Test Bank, Kiểm định đề, Tối ưu đề.
- **Hệ thống kiểm định 2 tầng & Minh bạch học thuật.**
- **Bộ công cụ `testbank_ingester.py`.**

## [3.0.0] - 2026-10-25
### Added
- Kiến trúc 3 thành phần: Spec Builder (Hamilton-Hare) - Independent Auditor - Exporter.
- Xuất bản 3 chế độ: Chế độ A (Mock Exam SV), Chế độ B (Master Bank), Chế độ C (Azota Package).
- Bộ 10 Quy tắc Vàng thiết kế câu hỏi.

## [2.0.0] - 2026-10-24
### Added
- Thích ứng động theo từng môn học (Subject-adaptive: Tính toán, Lý thuyết, Hệ thống).
- Trích xuất tự động từ Đề cương môn học (DCMH).
