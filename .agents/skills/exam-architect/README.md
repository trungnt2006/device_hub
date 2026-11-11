# 🏛️ EXAM ARCHITECT (v4.5)
> **AI-Powered Academic Exam Authoring, Auditing & 1-Click Azota Packaging Engine**

[![GitHub Repository](https://img.shields.io/badge/GitHub-exam--architect-blue?logo=github)](https://github.com/trungnt2006/exam-architect.git)
[![Version](https://img.shields.io/badge/version-4.5.0-green.svg)](CHANGELOG.md)
[![Standard](https://img.shields.io/badge/Academic%20Style-Pearson%20%7C%20HUB-orange.svg)](#phong-cách-ra-đề-học-hỏi-từ-test-bank-quốc-tế)

**Exam Architect** là hệ thống AI Agent chuyên nghiệp tập trung 100% vào **thiết kế, biên soạn và chuẩn hóa đề thi trắc nghiệm đại học**. Hệ thống học hỏi phong cách ra đề kinh điển từ các bộ Test Bank quốc tế (Pearson, McGraw-Hill, Wiley...), tích hợp 4 format câu hỏi chuyên sâu, thuật toán phân rã chủ đề con chống trùng lặp kiến thức, kiểm định chống tự giải nghĩa lộ bài và xuất file Word chuẩn **Azota 1-Click**.

---

## ⚡ HỆ THỐNG 5 LỆNH VẬN HÀNH 1-CHẠM (QUICK COMMANDS)

Người dùng chỉ cần đưa ra một câu lệnh ngắn gọn, Agent sẽ tự động kích hoạt toàn bộ quy trình:

```text
1. TẠO ĐỀ TỰ HÀNH:
   👉 "tạo đề 50 câu chương 1 môn này"
   👉 "làm đề thi thử 40 câu môn này"
   (Tự đọc DCMH/Slide -> Phân rã chủ đề con -> Chia ma trận Bloom -> Soạn 4 format câu hỏi -> Audit 2 tầng -> Xuất Word Azota)

2. HỌC HỎI TỪ TEST BANK:
   👉 "hấp thụ test bank [tên_file.pdf]"
   (Quét Test Bank quốc tế -> Trích xuất Sibling Concepts -> Cập nhật tri thức nâng cao chất lượng)

3. KIỂM ĐỊNH ĐỀ THI:
   👉 "kiểm định đề [tên_file]"
   (Đo độ dài Ratio, chuỗi lặp, phân bố A/B/C/D, kiểm tra trùng lặp thân câu >85%, phát hiện bẫy ngớ ngẩn & lỗi phương án tự giải nghĩa -> Báo cáo trực tiếp)

4. TỐI ƯU & CHUẨN HÓA AZOTA:
   👉 "tối ưu đề [tên_file]"
   (Cân bằng độ dài, hoán vị chia đều đáp án ~25%, thay thế phương án ngớ ngẩn, cắt bỏ đuôi tự giải nghĩa thừa -> Xuất Word Azota)

5. META-PROMPT CHO NOTEBOOKLM:
   👉 "meta prompt azota"
   👉 "phân tích kết quả này"
   (Lọc câu sai từ Azota -> Phân rã lỗ hổng kiến thức -> Xuất khối Meta-Prompt chuẩn hóa để NotebookLM giảng lại và giải mã bẫy thi)
```

---

## 📋 BỘ 4 FORMAT CÂU HỎI CHUYÊN SÂU ĐẠI HỌC

1. **Format 1: Thẩm định Tổ hợp Mệnh đề (Multi-Statement Evaluation - Linh hoạt 2 đến 4 mệnh đề):**
   - *Biến thể 1A (Cặp đối ngẫu (i) & (ii)):* 4 phương án chuẩn `(i) Đúng, (ii) Sai` v.v. để so sánh 2 trường phái đối nghịch.
   - *Biến thể 1B (Tổ hợp 3–4 mệnh đề (i), (ii), (iii), (iv)):* Đưa ra 3-4 nhận định, hỏi các nhận định đúng hoặc số lượng nhận định đúng để kiểm tra tính tổng hợp toàn chương. Triệt tiêu hoàn toàn thói quen đoán mò 50/50.
2. **Format 2: Tình huống nghiệp vụ & Đánh đổi kiến trúc (Scenario-based & Architectural Trade-offs):**
   - Mini-case thực tế (3-5 dòng) trong ngành Ngân hàng, Bán lẻ, Tài chính có ràng buộc kỹ thuật. Yêu cầu chọn giải pháp tối ưu và giải thích rõ ưu/nhược điểm (trade-off).
3. **Format 3: Trình tự quy trình & Luồng xử lý (Process Sequencing & Lifecycle Stages):**
   - Đưa ra 4-5 bước nghiệp vụ/công nghệ được đánh số `(1), (2), (3), (4)...` bị xáo trộn. Yêu cầu chọn chuỗi thực thi logic chuẩn xác.
4. **Format 4: Tính toán vi mô 30 giây (Micro-Calculation & Formula Traps):**
   - Dữ liệu ngắn gọn 2-4 dòng. Bắt buộc: giải nháp độc lập từng bước, ghi rõ đơn vị và quy ước làm tròn, bẫy sai số công thức kinh điển.

---

## 🎯 PHỦ CHỦ ĐỀ CON & CHỐNG TRÙNG LẶP KHÁI NIỆM (ANTI-REDUNDANCY)

- **Phân rã Chủ đề con (Sub-topics):** Tự động chia chương học thành 4-8 tiểu mục trước khi sinh câu hỏi.
- **Ràng buộc hạn ngạch (Topic Quotas):** Không chủ đề con nào chiếm quá 20%-25% tổng số câu hỏi của đề thi.
- **Ràng buộc đơn nhất & Đa dạng hóa góc nhìn (Concept Unique Constraint):**
  - Cấm sinh câu hỏi trùng lặp thân câu hoặc lặp lại định nghĩa chay.
  - Khi một khái niệm xuất hiện ở nhiều câu, bắt buộc phải thay đổi format và mức nhận thức Bloom (Định nghĩa đối ngẫu -> Tình huống trade-off -> Mệnh đề kết hợp Đúng/Sai).
  - Tự động kiểm tra trong `question_auditor.py`: Cảnh báo nếu hai câu hỏi có độ tương đồng từ ngữ thân câu $> 85\%$.

---

## 🏛️ ĐIỂM ĐẶC SẮC: HỌC HỎI PHONG CÁCH TỪ TEST BANK QUỐC TẾ

- **Phương án nhiễu cùng họ (Sibling Concepts):** Phương án sai không bao giờ là bịa đặt ngớ ngẩn, mà bắt buộc phải là các khái niệm anh em cùng chương trong giáo trình. Thí sinh đọc vào thấy tất cả đều quen thuộc, chỉ người hiểu bản chất mới chọn đúng.
- **Tách biệt Thuật ngữ & Định nghĩa — Cấm Phương án Tự giải nghĩa quá đà (No Self-Explaining Options):**
  - Khi thân câu hỏi đã nêu định nghĩa/bản chất và hỏi tên thuật ngữ/khái niệm, các phương án A, B, C, D **chỉ được ghi tên thuật ngữ ngắn gọn** (ví dụ: `A. Hướng chủ đề (Subject-Oriented).`, `B. Tích hợp (Integrated).`), tuyệt đối cấm nối thêm đuôi giải thích ý nghĩa vào đằng sau tên thuật ngữ làm lộ đáp án trên mặt chữ. Toàn bộ giải thích phải đưa xuống phần `Lời giải:`.
- **Thân câu hỏi đặt vấn đề (Functional Stems):** Triệt tiêu câu hỏi học vẹt "X là gì?"; đặt bài toán vào bối cảnh doanh nghiệp thực tế.
- **Cân bằng độ dài hợp lý:** Rà soát chênh lệch ký tự giữa các phương án ($Ratio \le 2.2$) nhằm triệt tiêu mẹo thi *"đáp án dài nhất là đúng"*, đồng thời giữ độ ngắn tự nhiên cho câu tính toán và câu hỏi tên thuật ngữ.
- **Cân bằng ngẫu nhiên A/B/C/D:** Tự động chia đều ~25% cho mỗi phương án, loại trừ chuỗi lặp $\ge 3$ câu liên tiếp.

---

## 🛠️ CẤU TRÚC DỰ ÁN

```text
exam-architect/
├── SKILL.md                          # Định nghĩa Skill chính thức cho Agent
├── AGENTS.md                         # File luật nạp tự động cho OpenCode / Antigravity / Cursor
├── README.md                         # Tài liệu hướng dẫn sử dụng
├── CHANGELOG.md                      # Lịch sử nâng cấp phiên bản
├── scripts/
│   ├── exam_spec_builder.py          # Thuật toán phân bổ ma trận Hamilton-Hare 2D
│   ├── question_auditor.py           # Bộ kiểm định 2 tầng độc lập (Hard Errors, Self-Explaining Tail Blocker & Warnings)
│   ├── build_azota_exam.py           # Động cơ đóng gói xuất 3 chế độ (Mock, Master, Azota 1-Click)
│   └── testbank_ingester.py          # Bộ hấp thụ tri thức Sibling Concepts từ Test Bank
└── references/
    └── testbank_knowledge.json       # Cơ sở tri thức Sibling Concepts đã hấp thụ
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT

### Dành cho Antigravity / Gemini CLI:
Copy thư mục `exam-architect` vào:
- `~/.gemini/config/skills/exam-architect` (Global)
- Hoặc `.agents/skills/exam-architect` (Workspace dự án)

### Dành cho OpenCode / Cursor:
Đặt file `AGENTS.md` tại thư mục gốc của môn học cần ôn tập. Agent sẽ tự động nạp toàn bộ luật và lệnh của Exam Architect.

---

## 📄 LICENSE
Phát triển bởi **Trung Ngo** phục vụ cộng đồng sinh viên Đại học Ngân hàng TP.HCM (HUB) và người học theo tiêu chuẩn khảo thí đại học.  
Mã nguồn mở theo giấy phép MIT.
