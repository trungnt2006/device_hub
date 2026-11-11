# BỘ QUY TẮC THIẾT KẾ VÀ KIỂM ĐỊNH ĐỀ THI TRẮC NGHIỆM (EXAM ARCHITECT v4.5)

**Tên hệ thống:** Exam Architect  
**Kho mã nguồn:** https://github.com/trungnt2006/exam-architect.git  
**Phạm vi áp dụng:** Toàn bộ các môn học và kỳ thi tại HUB cũng như các môn học đại học.  
**Định hướng cốt lõi:** Tập trung 100% chuyên sâu vào quy trình ra đề (Question Authoring) chất lượng cao, kiểm soát chặt chẽ ở tầng tư duy ngữ nghĩa của AI kết hợp kiểm định cấu trúc bằng Python.

---

## ⚡ HỆ THỐNG 5 LỆNH VẬN HÀNH 1-CHẠM (QUICK COMMANDS)

Khi người dùng đưa ra các lệnh ngắn gọn, Agent tự động thực thi trọn gói mà không bắt người dùng điền form thủ công:

1. **LỆNH TẠO ĐỀ:**
   👉 `"tạo đề [số câu] câu chương [X] môn này"` (hoặc `"làm đề thi thử 40 câu môn này"`)
   - **BƯỚC 0 BẮT BUỘC:** Quét đệ quy toàn bộ thư mục môn học, đặc biệt tìm các thư mục con `TN/`, `Trac_nghiem/`, `TestBank/`, `Giáo trình/`, `Slide/`, `Chương *.docx`.
   - **CÁCH LY CHỐNG LÂY NHIỄM AI SLOP & CƠ CHẾ BLACKLIST CHỐNG TRÙNG LẶP ĐỀ:** Mọi file đề thi Word Azota hoàn chỉnh **BẮT BUỘC LƯU VÀO FOLDER `Azota/`**. Khi làm đề mới, **TUYỆT ĐỐI KHÔNG ĐƯỢC HỌC LẠI PHƯƠNG ÁN HAY LỜI GIẢI TỪ THƯ MỤC `Azota/`** (để chống Model Autophagy), nhưng **BẮT BUỘC quét danh sách thân câu hỏi (`Câu X:`) của các đề trước trong `Azota/` để lập Blacklist cấm trùng lặp**.
   - **RÀNG BUỘC CHIA ĐỢT (MANDATORY BATCHING - MAX 25 CÂU/LẦN):** Khi người dùng yêu cầu 40-50 câu, BẮT BUỘC chia làm 2 đợt (Đợt 1: 1-20/25; Đợt 2: 21/26-40/50...).
   - **TỶ LỆ KHAI THÁC TRẮC NGHIỆM MẪU / TEST BANK (20% – 30%):** Chỉ lấy **20% – 30%** câu hỏi từ file trắc nghiệm mẫu (ưu tiên các câu chưa từng xuất hiện trong Blacklist các đề trước) làm phôi thực chiến; dành **70% – 80%** thiết kế câu hỏi mới chuyên sâu từ Giáo trình, Bài giảng chi tiết (`Chương *.docx`) và các phần kiến thức sâu trong Slide. Tuyệt đối CẤM hành vi lười biếng chỉ mở mỗi Slide dò từng trang đầu đặt câu hỏi quen thuộc.
   - **QUY TẮC CẤM TRÍCH DẪN VỊ TRÍ KIẾN THỨC TRONG THÂN CÂU HỎI:** Tuyệt đối **KHÔNG ĐƯỢC** đưa các cụm chỉ vị trí tài liệu như `(Slide Chương X, trang Y)`, `(Tài liệu Chương X, mục Y)`, `(Ngân hàng câu hỏi - Câu Z)` vào trong thân câu hỏi (`question` / `stem`) hoặc phương án lựa chọn (`A, B, C, D`). Toàn bộ thông tin nguồn trích dẫn chỉ được phép đặt trong phần **Lời giải chi tiết** và **Metadata** cuối câu.
   - **LƯU Ý ĐẶC THÙ MÔN HỌC (ĐỌC FILE `LUU_Y_MON_HOC.md` VÀ TÀI LIỆU ÔN TẬP GỐC):**
     + Bắt buộc đọc phần kinh nghiệm/lưu ý ở đầu tài liệu ôn tập (ví dụ `Noi Dung On final.docx`).
     + **Chỉ ra đề vào các mục có đánh Heading:** Tuyệt đối **KHÔNG** ra đề vào các phần bị gạch ngang (Strikethrough) vì tài liệu quy định *"chỉ để đọc hiểu thêm, không cần nhớ thuộc lòng"*.
     + **Khống chế hạn ngạch tính toán vi mô (Tối đa 15% – 20%):** Với đề 50 câu, chỉ ra tối đa **6 – 8 câu tính toán nhanh 30 giây** bám đúng các ví dụ mẫu có số liệu trong tài liệu. Tuyệt đối không biến đề thi thành bài kiểm tra giải tích/đại số dày đặc. 80% còn lại tập trung vào bản chất thuật toán, tình huống đánh đổi và tổ hợp mệnh đề `(i), (ii)`.
     + **Mặc định Thuần Việt 100% — Cấm chèn (Tiếng Anh) bừa bãi:** Không mở ngoặc chèn tiếng Anh kiểu lặp từ ở thân câu và phương án. Toàn bộ đối chiếu tiếng Anh đẩy xuống phần `Lời giải:`. Chỉ dùng trực tiếp tiếng Anh cho các thuật ngữ quốc tế không có từ dịch quen thuộc (SMOTE, Dropout, Random Forest...).
   - Dùng Giáo trình chính để kiểm chứng (Fact-check) và sửa lại các câu bị khoanh sai trên mạng; dùng Slide để đồng bộ thuật ngữ chấm thi của trường.
   - Tự phân rã chủ đề con (Sub-topics) và chia hạn ngạch (tối đa 25%/chủ đề).
   - Tự chia ma trận Bloom chuẩn đại học (~30% Nhận biết, ~40% Thông hiểu, ~30% Vận dụng).
   - Tự soạn thảo câu hỏi áp dụng linh hoạt 4 Format chuyên sâu, 10 Quy tắc Vàng, nguyên tắc Sibling Concepts và **Giao thức Tự Thẩm Định Ngữ Nghĩa AI (chống giải thích quá đà trong phương án)**.
   - Tự chạy script kiểm định `question_auditor.py` kiểm tra 2 tầng.
   - Tự xuất duy nhất file Word chuẩn Azota 1-Click (`<u><b>A.</b></u>`, kèm lời giải chi tiết, kết thúc bằng `HẾT`). Chỉ xuất file thi thử khi người dùng yêu cầu rõ ràng.

2. **LỆNH HỌC HỎI TỪ TEST BANK:**
   👉 `"hấp thụ test bank [tên_file.pdf]"`
   - Tự động quét file Test Bank quốc tế của tác giả (Pearson, McGraw-Hill, Wiley...).
   - Trích xuất các nhóm "Thuật ngữ cùng họ" (Sibling Concepts) và câu hỏi mẫu hay.
   - Cập nhật tri thức vào bộ nhớ để nâng cao chất lượng cho các lần tạo đề sau.

3. **LỆNH KIỂM ĐỊNH ĐỀ THI:**
   👉 `"kiểm định đề [tên_file]"`
   - Chạy script đo lường định lượng tỷ lệ độ dài ($Ratio \le 2.2$), chuỗi lặp $\ge 3$ câu, tỷ lệ phân bố đáp án A/B/C/D, phát hiện trùng lặp thân câu (>85%), lộ bài độc tôn và cảnh báo ngữ cảnh.
   - Hiển thị Báo cáo kiểm định trực tiếp trong chat (tuyệt đối không xuất file `Audit_Report.txt`).

4. **LỆNH TỐI ƯU & CHUẨN HÓA AZOTA:**
   👉 `"tối ưu đề [tên_file]"`
   - Tự động cân bằng độ dài, hoán vị chia đều đáp án ~25%, sửa phương án tấu hài thành học thuật, cắt bỏ đuôi tự giải nghĩa thừa.
   - Đóng gói xuất duy nhất file Word Azota 1-Click sạch đẹp (không tạo file Mock Exam trừ khi được yêu cầu).

5. **LỆNH META-PROMPT HỌC TẬP TỪ KẾT QUẢ AZOTA (DIAGNOSTIC & NOTEBOOKLM META-PROMPT):**
   👉 `"phân tích kết quả [text/file]"` hoặc `"meta prompt [azota]"` (hoặc tự động khi người dùng gửi kết quả thi Azota)
   - Tự động quét lọc 100% các câu làm sai (`✗`).
   - Phân loại lỗ hổng kiến thức theo chủ đề con.
   - Xuất Báo cáo chẩn đoán nhanh (Điểm số, Tỷ lệ đúng, Chủ đề bị hổng).
   - Sinh khối **Meta-Prompt sẵn sàng 1-Click** để người dùng dán trực tiếp vào **NotebookLM** (nơi đã nạp Slide/Giáo trình môn học) để NotebookLM giảng giải, so sánh đối ngẫu và củng cố kiến thức.

---

## I. NGUYÊN TẮC RA ĐỀ HỌC HỎI TỪ TEST BANK QUỐC TẾ & QUY TẮC THÉP TẦNG TƯ DUY AI

1. **Phương án nhiễu cùng họ (Sibling Concepts) & Cùng miền chuyên môn:** Phương án sai phải là các thuật ngữ, khái niệm hoặc công thức cùng cấp bậc trong chính chương đó. Triệt tiêu các phương án sai ngớ ngẩn, tấu hài hoặc lạc miền chuyên môn.
2. **QUY TẮC THÉP TẦNG AI: TÁCH BIỆT THUẬT NGỮ & ĐỊNH NGHĨA — CẤM PHƯƠNG ÁN TỰ GIẢI NGHĨA QUÁ ĐÀ (STRICT SEMANTIC STEM–OPTION ALIGNMENT):**
   - Trước khi viết 4 phương án A, B, C, D, AI **BẮT BUỘC** đối chiếu mục đích của Thân câu hỏi với **3 Khuôn mẫu Chuẩn** và thực hiện **Bài test Che Thuật Ngữ**:
     - **Khuôn mẫu 1 (Câu hỏi Nhận diện Thuật ngữ / Khái niệm / Công cụ - Bloom 1–2):** Khi thân câu đã mô tả bản chất/định nghĩa và hỏi *"đó là đặc tính / khái niệm / biểu đồ / kỹ thuật nào?"*, 4 phương án A, B, C, D **CHỈ ĐƯỢC GHI ĐÚNG TÊN THUẬT NGỮ NGẮN GỌN** (ví dụ: `A. Hướng chủ đề (Subject-Oriented).`, `B. Tích hợp (Integrated).`). **CẤM TUYỆT ĐỐI** nối thêm đuôi giải thích ý nghĩa vào sau tên thuật ngữ (như *"B. Tích hợp (Integrated) tạo lập cấu trúc lưu trữ đồng nhất"*). Toàn bộ giải thích phải đưa xuống `Lời giải:`.
     - **Khuôn mẫu 2 (Câu hỏi Phân tích Bản chất / Cơ chế của Thuật ngữ - Bloom 2–3):** Khi thân câu đã nêu đích danh tên thuật ngữ (ví dụ: *"Đặc tính Tích hợp (Integrated) đòi hỏi cơ chế xử lý nào?"*), 4 phương án A, B, C, D chỉ mô tả hành động/bản chất mà **không gắn nhãn tên 4 thuật ngữ ở đầu câu**.
     - **Khuôn mẫu 3 (Câu hỏi Tình huống Kép - Bloom 3–4):** Chỉ khi thân câu hỏi rõ cả 2 vế (*"Đây là hiện tượng gì VÀ do nguyên nhân gốc rễ nào?"* hoặc *"Giải pháp nào kèm cơ chế thực thi tương ứng là phù hợp nhất?"*), phương án mới được kết hợp `[Tên giải pháp/hiện tượng] + [Cơ chế/Nguyên nhân trong bối cảnh đó]`.
   - 🔍 **Bài test Che Thuật Ngữ bắt buộc của AI:** Giả sử che đi tên thuật ngữ ở đầu 4 phương án A, B, C, D. Nếu người đọc chỉ đọc phần đuôi còn lại mà vẫn chọn ngay được đáp án đúng nhờ khớp nghĩa với thân câu hỏi $\rightarrow$ Câu đó đang bị lỗi **Giải thích quá đà làm lộ bài** $\rightarrow$ AI **BẮT BUỘC cắt bỏ ngay phần đuôi giải thích thừa**!
3. **Triệt tiêu bẫy bắt chữ / Lộ nghĩa đen (Anti-Clang Association):** Thân câu hỏi không dùng từ ngữ đời thường để "mớm nghĩa đen" cho đáp án. Nâng cấp thân câu hỏi sang ngôn ngữ học thuật.
4. **Thân câu hỏi đặt vấn đề (Functional Stem):** Tránh câu hỏi học vẹt cộc lốc; đặt câu hỏi vào bối cảnh doanh nghiệp cần ra quyết định hoặc giải quyết tình huống kỹ thuật.
5. **Phân loại 3 nhóm môn học:**
   - *Môn Tính toán (Toán kinh tế, Thống kê, Tài chính DN, Kế toán...):* Phải giải nháp độc lập; ghi rõ kỳ hạn, đơn vị và quy ước làm tròn số; bẫy sai số công thức.
   - *Môn Lý thuyết & Pháp lý (Luật ngân hàng, Quản trị, Marketing, Tiền tệ...):* Chống học vẹt, so sánh bản chất và giải quyết tình huống nghiệp vụ ngân hàng/doanh nghiệp.
   - *Môn Công nghệ & Dữ liệu (Kho dữ liệu, CSDL, HTTT, An toàn bảo mật...):* Kiến trúc, đánh đổi giải pháp (trade-off), bẫy ngoại lệ kỹ thuật.

---

## II. QUY TRÌNH PHỐI HỢP TÀI NGUYÊN 3 TẦNG: GIÁO TRÌNH -> TN MẪU -> SLIDE

1. **Tầng 1 — Giáo trình chính (Textbooks - Nền tảng học thuật & Chân lý cốt lõi):**
   - Khởi nguồn từ giáo trình chuẩn (Inmon, Kimball, Sharda, Ponniah...) để định hình bản chất lý thuyết, cơ chế kỹ thuật sâu, công thức và quy trình chuẩn xác nhất.
2. **Tầng 2 — Trắc nghiệm mẫu / Test Bank (Khung câu hỏi & Bẫy thi thực tế):**
   - Khai thác các bài toán trắc nghiệm thực chiến mà giảng viên thường sử dụng.
   - **Cơ chế Thẩm định & Sửa lỗi (Fact-checking):** Dùng Giáo trình ở Tầng 1 để kiểm tra lại toàn bộ đáp án của trắc nghiệm mẫu, đồng thời viết thêm Lời giải thích chi tiết.
   - **Bắt buộc xuất Báo cáo Hiệu đính Đáp án (Correction Audit Report):** Tuyệt đối KHÔNG âm thầm sửa đáp án!
3. **Tầng 3 — Slide bài giảng của Giảng viên (Bộ lọc trọng tâm & Đồng bộ thuật ngữ):**
   - Dùng Slide làm bộ lọc cuối cùng để đồng bộ thuật ngữ chấm thi của trường.

---

## III. BỘ 4 ĐỊNH DẠNG CÂU HỎI CHUYÊN SÂU ĐẠI HỌC (4 IN-DEPTH EXAM FORMATS)

1. **Format 1: Thẩm định Tổ hợp Mệnh đề (Multi-Statement Evaluation - Linh hoạt 2 đến 4 mệnh đề).**
2. **Format 2: Tình huống nghiệp vụ & Đánh đổi kiến trúc (Scenario-based & Architectural Trade-offs).**
3. **Format 3: Trình tự quy trình & Luồng xử lý (Process Sequencing & Lifecycle Stages).**
4. **Format 4: Tính toán vi mô 30 giây (Micro-Calculation & Formula Traps).**

---

## IV. CƠ CHẾ PHÂN BỔ CHỦ ĐỀ CON & CHỐNG TRÙNG LẶP KHÁI NIỆM (TOPIC COVERAGE & ANTI-REDUNDANCY)

1. **Phân rã Chủ đề con (Sub-topic Decomposition):** Chia chương thành 4-8 tiểu mục trước khi ra đề.
2. **Ràng buộc Hạn ngạch (Topic Quotas):** Không chủ đề con nào chiếm quá 20%-25% tổng số câu hỏi của đề.
3. **Ràng buộc Đơn nhất Thực thể & Đa dạng Góc nhìn (Concept Unique Constraint).**

---

## V. HỆ THỐNG 10 QUY TẮC VÀNG THIẾT KẾ CÂU HỎI

1. **Cân bằng độ dài & Cấm bôi chữ giải nghĩa (Equal Length & No Padding Rule):** Khi phương án là tên thuật ngữ/khái niệm, giữ nguyên độ ngắn tự nhiên của thuật ngữ đó, cấm cố kéo dài bằng cách nối đuôi giải thích ý nghĩa vào phương án.
2. **Đồng nhất cấu trúc & Đối xứng chú thích thuật ngữ (Structural & Notational Symmetry):**
   - Cả 4 phương án cùng loại từ.
   - **Quy tắc Đối xứng Chú thích Tiếng Anh:** Nếu có `(English Term)` thì cả 4 phương án đều phải có tương ứng; nếu thuần Việt thì cả 4 phương án dùng thuần Việt.
   - **Quy tắc Chống thiên vị diễn giải & Chống tự giải nghĩa (No Elaboration Bias & No Self-Explaining Tails).**
3. **Kiểm soát phương án tổng hợp & Bẫy ngược (Smart Distractors & Reverse Traps).**
4. **Hoán vị ngẫu nhiên A/B/C/D (~25%).**
5. **Tình huống nghiệp vụ thực tế.**
6. **Bẫy nửa đúng - nửa sai (Half-Truth).**
7. **Đánh vào ngoại lệ & nghịch lý kỹ thuật.**
8. **Tráo đổi khái niệm đối ngẫu (Dichotomy).**
9. **Tính toán vi mô 30s.**
10. **Đánh đổi kiến trúc & Best Practice.**

---

## VI. QUY CHUẨN XUẤT BẢN AZOTA 1-CLICK (.DOCX)
- Tiêu đề câu: `Câu X: [Nội dung]` (in đậm `Câu X: `).
- Đáp án đúng: Gạch chân và in đậm chữ cái phương án (`<u><b>A.</b></u>`).
- Lời giải: Có khối `Lời giải:\nChọn X.\n[Giải thích chi tiết & phân tích bẫy thi]\n📌 [Metadata: Nguồn: ... | Mức độ: ... | Chủ đề: ...]`.
- Mặc định **CHỈ XUẤT BẢN DUY NHẤT 1 FILE WORD CHUẨN AZOTA** vào thư mục `Azota/`.
- Kết thúc đề: Dòng **`HẾT`** in đậm căn giữa.

---

## VII. HỆ THỐNG KIỂM ĐỊNH 2 TẦNG (PHÂN VAI PYTHON & TƯ DUY NGỮ NGHĨA AI)
1. **Tầng 1 — Lỗi Kỹ thuật & Lộ bài Độc tôn (Python Hard Errors - Chặn cứng):**
   - Chỉ chặn cứng các lỗi khách quan 100%: Thiếu phương án, đáp án ngoài A/B/C/D, trùng lặp phương án, mâu thuẫn giữa Đáp án và Lời giải, phương án lười biếng (*Tất cả đều đúng*), **thiên vị độc tôn** (chỉ duy nhất câu đúng có chú thích tiếng Anh, hoặc duy nhất câu đúng dài gấp $> 2.0$ lần câu dài thứ nhì).
2. **Tầng 2 — Cờ Cảnh báo Ngữ cảnh để AI Tự Thẩm Định (Contextual Warnings):**
   - Không dùng keyword/regex chặn cứng máy móc. Khi script phát hiện cấu trúc `Thuật ngữ (English) + mệnh đề giải thích` hoặc độ lệch độ dài, script xuất **Cờ cảnh báo (Warning)** để AI thực hiện **Bài test Che Thuật Ngữ**: nếu là câu hỏi nhận diện khái niệm (Khuôn mẫu 1) thì cắt bỏ đuôi giải thích thừa; nếu là câu hỏi tình huống kép (Khuôn mẫu 3) thì giữ nguyên.
