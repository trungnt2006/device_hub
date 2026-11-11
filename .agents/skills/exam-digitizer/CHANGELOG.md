# Changelog

Tất cả các thay đổi đáng chú ý của dự án **Exam Digitizer** sẽ được ghi lại trong tài liệu này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án tuân thủ [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-11-05

### Added
- **Quy tắc 3A: Xử lý câu hỏi khuyết thân câu, chỉ có đáp án/phương án (Missing Stem / Answer-Only):**
  - **Cơ chế bắt buộc hỏi xác nhận người dùng (tương tự câu Flashcard):** Khi phát hiện câu bị mất phần câu hỏi và chỉ có phần đáp án/phương án, Agent bắt buộc dừng lại báo cáo số lượng + ví dụ và hỏi người dùng.
  - **Nhánh "KHÔNG":** Xóa bỏ hoàn toàn câu khuyết thân khỏi đề thi và đánh lại số thứ tự liên tục (`Câu 1, 2, 3...`).
  - **Nhánh "CÓ":** Dựa vào nội dung đáp án đúng (và phương án nhiễu nếu có), đối chiếu ngược với Slide bài giảng / Giáo trình của môn học để **phục dựng lại thân câu hỏi chuẩn học thuật** khớp logic 100% với đáp án gốc.
- **Nâng cấp Auditor (`digitizer_auditor.py`):**
  - Bổ sung phương thức `scan_anomalies(questions)` tự động quét và gom nhóm 2 loại câu bất thường: *Missing Stem (3A)* và *Missing Options / Flashcard (3B)* để xuất bảng hỏi người dùng trước khi xử lý.

## [2.0.0] - 2026-10-31

### Added
- **5 Quy tắc thép bất biến (Core Integrity Rules):**
  - Nguyên tắc bất khả xâm phạm: Nguyên văn 100% câu từ (Verbatim stem & options).
  - Tôn trọng nội dung đáp án gốc kết hợp hoán vị phân bổ đều ~25%.
  - Ràng buộc chặn đứng câu hỏi thiếu phương án (Flashcard/tự luận ngắn): Bắt buộc hỏi người dùng trước khi hành động.
  - Cấm âm thầm sửa đáp án: Báo cáo đối soát giáo trình trước, sửa sau khi được phê duyệt.
  - Phân tích bẫy thi và dịch thuật chỉ được phép nằm trong khối `Lời giải:`.
- **Thứ bậc nguồn dẫn chứng 3 tầng (Citation Hierarchy):**
  - Slide giảng viên trực tiếp dạy $\ge$ Giáo trình chuẩn quốc tế (Textbook) > Tài liệu kỹ thuật chính thức > Tài liệu mạng.
- **Phương pháp luận ánh xạ ma trận Đề cương môn học (DCMH):**
  - Tự động phân loại câu hỏi vào từng chương dựa trên ma trận từ khóa.
- **Quy trình bóc tách kỹ thuật đa tầng (Deep Extraction Engine):**
  - Lớp 1: Bóc tách vector tô vàng (Yellow drawing rects) bằng PyMuPDF.
  - Lớp 2: Quét Annotations và cờ font chữ in đậm/màu sắc.
  - Lớp 3: Bóc tách bảng đáp án và làm sạch watermark bên thứ ba.
- **Quy chuẩn đóng gói Word Azota 1-Click:**
  - Định dạng chuẩn cho Azota import trực tiếp không lỗi.

## [1.0.0] - 2026-10-15

### Added
- Khởi tạo kỹ năng số hóa đề thi từ PDF scan và đề LMS.
- Bóc tách văn bản thô sang định dạng trắc nghiệm 4 lựa chọn.
