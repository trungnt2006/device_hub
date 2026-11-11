# AGENTS.md — EXAM DIGITIZER OPERATIONAL INSTRUCTIONS

Tệp chỉ dẫn tự động dành cho AI Coding Assistant (Antigravity, OpenCode, Cursor, Windsurf) khi làm việc trong các không gian số hóa đề thi đại học.

## NGUYÊN TẮC HÀNH VI CỐT LÕI (CORE COMMANDMENTS)

1. **BẢO TOÀN NGUYÊN VĂN 100% (STRICT VERBATIM):**
   - Giữ nguyên từng từ, dấu chấm, dấu phẩy, ký hiệu toán học, thuật ngữ tiếng Anh trong thân câu hỏi và các lựa chọn A, B, C, D của tài liệu gốc.
   - Tuyệt đối không viết lại cho "mượt mà", không tự ý dịch thuật ngữ trong thân câu và phương án.
2. **XỬ LÝ CÂU KHUYẾT THÂN CÂU, CHỈ CÓ ĐÁP ÁN (BẮT BUỘC HỎI USER):**
   - Khi tài liệu bị khuyết phần thân câu hỏi và chỉ có phần đáp án/phương án: BẮT BUỘC dừng lại báo cáo số lượng + ví dụ và hỏi người dùng xem có muốn phục dựng thân câu hỏi không.
   - **Nếu người dùng nói KHÔNG:** Xóa bỏ hoàn toàn các câu khuyết này và đánh lại số thứ tự liên tục `Câu 1, 2, 3...`.
   - **Nếu người dùng nói CÓ:** Dựa vào đáp án và phương án còn sót lại, đối chiếu Slide/Giáo trình môn học để **phục dựng lại thân câu hỏi chuẩn học thuật** khớp 100% với đáp án gốc.
3. **XỬ LÝ CÂU THIẾU PHƯƠNG ÁN (FLASHCARD / TỰ LUẬN NGẮN - BẮT BUỘC HỎI USER):**
   - Nếu đề gốc chỉ có Câu hỏi và 1 Đáp án (dạng flashcard/tự luận ngắn), bắt buộc hỏi người dùng xem có cần chuyển thành trắc nghiệm 4 lựa chọn không.
   - **Nếu KHÔNG:** Xóa bỏ. **Nếu CÓ:** Sinh thêm 3 phương án nhiễu cùng họ (Sibling Concepts).
4. **CẤM ÂM THẦM SỬA ĐÁP ÁN:**
   - Nếu phát hiện đáp án gốc sai, lập bảng đối soát (Đề gốc vs Kiến thức chuẩn giáo trình) và trình báo trực tiếp cho người dùng.
   - Chỉ sửa khi người dùng bấm đồng ý.
5. **ĐÓNG GÓI CHUẨN AZOTA 1-CLICK:**
   - Luôn lưu file đầu ra vào thư mục `Azota/[tên_file] - azota.docx`.
   - Đáp án đúng gạch chân và in đậm chữ cái phương án (`<u><b>A.</b></u>`).
   - Căn lề 2-2-2-2 cm, Font Times New Roman 11pt, giãn dòng 1.15.
   - Kết thúc tài liệu bằng chữ `HẾT` in đậm căn giữa 14pt.
