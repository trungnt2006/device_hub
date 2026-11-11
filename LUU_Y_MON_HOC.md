# LƯU Ý QUAN TRỌNG KHI RA ĐỀ MÔN KHAI PHÁ DỮ LIỆU (DATA MINING - HUB)

> **Mục đích:** Bản ghi nhớ bắt buộc cho Agent khi thiết kế đề thi trắc nghiệm môn Khai phá dữ liệu tại HUB, rút kinh nghiệm trực tiếp từ tài liệu ôn tập và phản hồi của người dùng.

---

## 1. NGUYÊN TẮC ĐỌC TÀI LIỆU ÔN TẬP (`Noi Dung On final.docx`)
Dựa theo phần *"Một số kinh nghiệm ôn tập"* ngay đầu tài liệu gốc (P1 - P4):
1. **Chỉ ra đề vào các mục có đánh Heading:** Những mục có tiêu đề rõ ràng là phạm vi trọng tâm xuất hiện trong ngân hàng câu hỏi.
2. **Tuyệt đối không ra đề vào các đoạn bị GẠCH NGANG (Strikethrough):**
   - Tài liệu ghi rõ: *"Những phần bị gạch ngang: nên xem để giúp hiểu thêm, nhưng không cần nhớ thuộc lòng."*
   - Cấm bới móc chi tiết vào các phần bị gạch ngang để ép thí sinh học vẹt.
3. **Phần công thức và tính toán:**
   - Chỉ học thuộc và ra đề vào **những phần công thức ĐƠN GIẢN, nhất là những đoạn có ví dụ tính toán cụ thể trong tài liệu**.
   - Cấm tự bịa ra các bài toán tính toán nhiều bước phức tạp (như lan truyền ngược nhiều lớp, cập nhật trọng số chi tiết, biến đổi ma trận phức tạp...) gây quá tải thời gian làm bài.

---

## 2. KHỐNG CHẾ HẠN NGẠCH CÂU TÍNH TOÁN (TỐI ĐA 15% – 20%)
- **Hạn ngạch:** Trong đề 50 câu, số lượng câu tính toán số học **CHỈ ĐƯỢC DAO ĐỘNG TỪ 6 ĐẾN 8 CÂU** (tuyệt đối không để vượt quá 10 câu / 20%).
- **Tiêu chuẩn tính toán:** Phải là loại **tính nhanh 30 giây**, số liệu chẵn, bấm máy hoặc nhẩm được ngay.
- **80% còn lại (42–44 câu)** phải tập trung vào:
  - Bản chất thuật toán (tại sao dùng, giải quyết vấn đề gì, ưu/nhược điểm).
  - Tình huống lựa chọn mô hình và đánh đổi kỹ thuật (Trade-offs).
  - So sánh đối ngẫu bằng câu hỏi tổ hợp mệnh đề `(i), (ii)`.
  - Quy trình và thứ tự các bước vận hành.

---

## 3. QUY TẮC NGÔN NGỮ: THUẦN VIỆT 100% — CẤM CHÈN (TIẾNG ANH) BỪA BÃI
- **Mặc định:** Thân câu và 4 phương án dùng 100% tiếng Việt học thuật chuẩn theo bài giảng/slide của trường.
- **Cấm tuyệt đối** mở ngoặc chèn tiếng Anh kiểu lặp từ:
  - ❌ `Phân lớp nhị phân (Binary)` $\rightarrow$ ✅ `Phân lớp nhị phân`
  - ❌ `Độ nhạy (Recall)` $\rightarrow$ ✅ `Độ nhạy` (hoặc dùng `Recall` độc lập)
  - ❌ `Độ hợp lý (Likelihood)` $\rightarrow$ ✅ `Độ hợp lý`
- **Ngoại lệ cho danh từ kỹ thuật quốc tế:** Chỉ dùng tiếng Anh khi đó là danh từ riêng kỹ thuật chuẩn quốc tế không có từ dịch tiếng Việt phổ biến (như *SMOTE, Dropout, Random Forest, AdaBoost, One-Hot Encoding, Gradient Descent, Kernel Trick, Support Vectors*...). Khi dùng thì viết trực tiếp từ đó, KHÔNG mở ngoặc lặp lại.
- **Vị trí giải thích tiếng Anh:** Toàn bộ đối chiếu thuật ngữ tiếng Anh gốc hãy đẩy xuống phần **`Lời giải:`** để phục vụ việc tra cứu học tập.

---

## 4. CHỐNG ĐOÁN MÒ THEO ĐỘ DÀI
- Số câu có đáp án đúng là phương án dài nhất duy nhất **không được vượt quá 30% – 35% toàn đề**.
- Khi đáp án đúng dài hơn $1.35$ lần trung bình các phương án sai $\rightarrow$ **bắt buộc phải rút gọn đáp án đúng** và bổ sung chi tiết hợp lý cho các phương án sai.
- 4 phương án trong cùng một câu phải có cùng kiểu câu và cùng cấu trúc ngữ pháp (tính song hành cú pháp).

---

## 5. BẢN ĐỒ CÁC DẠNG BÀI TÍNH TOÁN THEO TỪNG CHƯƠNG
Khi ra đề cho các chương, chỉ chọn đúng các dạng tính toán kinh điển sau:
- **Chương 2 (Tiền xử lý):** Z-score, Min-Max Scaling, Phân thùng (Binning mean/boundary), IQR ngoại lai.
- **Chương 3 (Luật kết hợp):** Support count, Support (%), Confidence (%), Lift, số lượng ứng viên Apriori.
- **Chương 4 (Phân lớp):** Gini node, Information Gain 2 nhánh, Naive Bayes 1 bước, Balanced Accuracy (99/1), Ma trận nhầm lẫn (Accuracy, Precision, Recall, F1), K-fold mean.
- **Chương 5 (Gom cụm):** Khoảng cách Euclidean/Manhattan giữa 2 điểm, cập nhật Centroid K-means (trung bình tọa độ), phân loại điểm DBSCAN (Core/Border/Noise theo MinPts và $\epsilon$).
