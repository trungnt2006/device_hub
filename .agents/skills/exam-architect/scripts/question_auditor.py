import re
import sys
import os
import json
import math

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class QuestionAuditor:
    """
    Hệ thống kiểm định chất lượng đề thi hai tầng chuẩn đại học (Phân vai thông minh giữa Python & Tư duy AI):
    - Tầng 1 (Hard Errors): Chỉ chặn cứng các lỗi cấu trúc khách quan 100% & lỗi lộ bài độc tôn (Single-Option Giveaway).
    - Tầng 2 (Contextual Warnings): Điểm chỉ các mẫu nghi vấn (như phương án vừa nêu thuật ngữ vừa giải thích dài, độ lệch độ dài CV...)
      để tầng Tư duy Ngữ nghĩa của AI tự thẩm định theo Khuôn mẫu câu hỏi mà không gò bó cực đoan.
    """
    def __init__(self, spec=None):
        self.spec = spec or {}
        
        # 1. Chỉ giữ các cụm từ thực sự tấu hài / đời thường phi học thuật tuyệt đối (Đã loại bỏ các từ kỹ thuật dễ bắt nhầm)
        self.silly_keywords = [
            'búa đập', 'đập vỡ', 'đi bộ quanh phòng', 'mua sắm ngoài trời',
            'pha trà', 'pha cà phê', 'chạy bộ', 'dọn dẹp bàn làm việc',
            'lau bụi', 'lau chùi', 'vứt vào thùng rác', 'rác văn phòng',
            'thùng rác tái chế', 'cửa sổ kính', 'ngừng phục vụ khách hàng vào buổi sáng'
        ]
        
        # 2. Phương án lười biếng / tổ hợp tùy tiện (CẤM TUYỆT ĐỐI)
        self.composite_phrases = [
            'tất cả các đáp án', 'tất cả đáp án', 'tất cả các phương án', 'tất cả các lựa chọn',
            'cả a và b', 'cả a, b', 'cả ba đáp án', 'cả 3 đáp án', 'cả a và c', 'cả b và c',
            'không có đáp án nào đúng', 'không có phương án nào đúng', 'tất cả đều đúng', 'tất cả đều sai'
        ]
        
        # 3. Từ ngữ Tuyệt đối hóa cực đoan (Test-Wiseness Giveaways)
        self.extreme_qualifiers = [
            'luôn luôn', 'tuyệt đối không', 'chỉ duy nhất', 'bắt buộc 100%', 'hoàn toàn không',
            'triệt để 100%', 'trong mọi trường hợp'
        ]

        # 4. Mẫu nhận diện cấu trúc: [Tên thuật ngữ <= 45 ký tự] + ([English Term]) + [Đuôi mô tả >= 12 ký tự]
        self.term_tail_re = re.compile(
            r'^([^\(\):;,\.=<>]{2,45}?)\s*'
            r'\(([A-Za-z][A-Za-z0-9\s\-/,&\'\"\+]{2,})\)\s+'
            r'([^=<>]{12,})$'
        )
        self.non_term_prefixes = (
            'vì ', 'do ', 'bởi vì ', 'nhằm ', 'để ',
            'sử dụng ', 'áp dụng ', 'triển khai ', 'thực hiện ', 'xây dựng ', 'thiết lập ',
            'chuyển đổi ', 'kết hợp ', 'tách biệt ', 'loại bỏ ',
            'chuẩn hóa ', 'phát hiện ', 'nhận diện ', 'xác định ', 'tính toán ', 'ước lượng ',
            'khởi tạo ', 'huấn luyện ', 'đánh giá ', 'kiểm tra ', 'lựa chọn ', 'trích xuất ',
            'nhận định ', 'mệnh đề ', 'phát biểu ', 'trường hợp ', 'ghép ', 'cả hai ', 'chỉ '
        )

    def audit_question(self, q, idx):
        errors = []
        warnings = []
        
        ans = q.get('ans', '').upper()
        opts = q.get('options', {})
        expl = q.get('explanation', '')
        stem = q.get('question', '') or q.get('stem', '')

        # Kiểm tra cấm chèn trích dẫn vị trí kiến thức trong thân câu hỏi hoặc phương án
        loc_citation_re = re.compile(
            r'(\bSlide\s+Chương\b|\bTài\s+liệu\s+Chương\b|\bBài\s+giảng\s+Chương\b'
            r'|\bNgân\s+hàng\s+câu\s+hỏi\b|\btrang\s+\d+|\b(?<!danh\s)mục\s+\d+\.\d+|\bcâu\s+hỏi\s+\d+)',
            re.IGNORECASE
        )
        m_loc = loc_citation_re.search(stem)
        if m_loc:
            errors.append(
                f"Câu {idx}: Vi phạm quy tắc trình bày đề thi! Không được chèn trích dẫn vị trí kiến thức "
                f"('{m_loc.group(0)}') vào trong thân câu hỏi (chỉ đặt trong Lời giải & Metadata)."
            )
        
        # --- TẦNG 1: LỖI KỸ THUẬT & LỘ BÀI ĐỘC TÔN KHÁCH QUAN 100% (HARD ERRORS) ---
        if ans not in ['A', 'B', 'C', 'D']:
            errors.append(f"Câu {idx}: Đáp án không hợp lệ ('{ans}')")
            
        if len(opts) != 4:
            errors.append(f"Câu {idx}: Không đủ 4 phương án (hiện có {len(opts)})")
        else:
            for k in ['A', 'B', 'C', 'D']:
                if not opts.get(k, '').strip():
                    errors.append(f"Câu {idx}: Phương án {k} bị rỗng!")
            
        opt_values = [v.strip().lower() for v in opts.values() if v.strip()]
        if len(opt_values) != len(set(opt_values)) and len(opt_values) > 1:
            errors.append(f"Câu {idx}: Có phương án bị trùng lặp 100% nội dung!")

        if ans and expl:
            m = re.search(r'Chọn\s+([A-D])\.', expl, re.IGNORECASE)
            if m and m.group(1).upper() != ans:
                errors.append(f"Câu {idx}: Mâu thuẫn logic! Đáp án đánh dấu là {ans} nhưng lời giải ghi 'Chọn {m.group(1).upper()}'")

        # Quét lộ vị trí tài liệu trong Thân câu hoặc Phương án (phải để ở Lời giải/Metadata)
        cit_leak_re = re.compile(r'\((?:Slide|Giáo trình|Chương|Mục|Trang|Bài giảng|Tài liệu)\s+[^)]+\)', re.IGNORECASE)
        if stem and cit_leak_re.search(stem):
            errors.append(f"Câu {idx}: Lộ nguồn/vị trí tài liệu trong thân câu hỏi ({cit_leak_re.search(stem).group(0)}). Hãy chuyển vị trí tài liệu xuống phần Lời giải / Metadata.")
        for opt_k, opt_v in opts.items():
            if cit_leak_re.search(opt_v):
                errors.append(f"Câu {idx} [{opt_k}]: Lộ nguồn/vị trí tài liệu trong phương án ({cit_leak_re.search(opt_v).group(0)}). Hãy chuyển xuống phần Lời giải.")

        # Quét cụm từ tấu hài phi học thuật rõ rệt
        for opt_k, opt_v in opts.items():
            for sk in self.silly_keywords:
                if sk in opt_v.lower():
                    errors.append(f"Câu {idx} [{opt_k}]: Phát hiện cụm từ đời thường/tấu hài phi học thuật: '{sk}'")

        # Quét phương án lười biếng
        for opt_k, opt_v in opts.items():
            for cp in self.composite_phrases:
                if cp in opt_v.lower():
                    errors.append(f"Câu {idx} [{opt_k}]: Vi phạm quy tắc khảo thí! Dùng phương án lười biếng: '{cp}'")

        # Kiểm tra lộ bài hình thức độc tôn: Duy nhất đáp án đúng có chú thích (English Term)
        # Loại trừ các chữ số La Mã (i, ii, iii, iv...) dùng để đánh số mệnh đề
        roman_set = {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x'}
        en_term_re = re.compile(r'\(([A-Za-z][A-Za-z\s\-/,&]{2,})\)')
        opts_with_en = []
        for k, v in opts.items():
            matches = [m.group(1).strip().lower() for m in en_term_re.finditer(v)]
            if any(m not in roman_set for m in matches):
                opts_with_en.append(k)

        if opts_with_en == [ans]:
            errors.append(
                f"Câu {idx}: Lộ đáp án do bất đối xứng chú thích Tiếng Anh! "
                f"Chỉ duy nhất đáp án đúng {ans} có chú thích Tiếng Anh trong ngoặc đơn."
            )
        elif len(opts_with_en) >= 3:
            warnings.append(
                f"Câu {idx}: [Cảnh báo Chú thích Tiếng Anh] {len(opts_with_en)}/4 phương án có chú thích (English) trong ngoặc. "
                f"Mặc định dùng thuần Việt; chỉ giữ tên Anh khi thuật ngữ không có bản dịch quen thuộc trong tài liệu giảng viên."
            )

        # Kiểm tra thiên vị diễn giải độc tôn: Duy nhất đáp án đúng dài gấp > 2.0 lần câu dài thứ nhì
        opt_lens = [len(v.strip()) for v in opts.values() if v.strip()]
        is_num = all(re.match(r'^[\d\s\.,%+\-*/\$₫a-zA-Z]+$', v.strip()) and len(v.strip()) < 15 for v in opts.values())
        if ans in opts and not is_num:
            ans_len = len(opts[ans].strip())
            other_lens = [len(v.strip()) for k, v in opts.items() if k != ans and v.strip()]
            if other_lens and ans_len > max(other_lens) * 2.0:
                errors.append(
                    f"Câu {idx}: Lộ đáp án do thiên vị diễn giải độc tôn! "
                    f"Đáp án đúng {ans} dài gấp hơn 2 lần phương án dài nhất còn lại ({ans_len} vs {max(other_lens)} ký tự)."
                )

        # --- TẦNG 2: CỜ CẢNH BÁO NGỮ CẢNH ĐỂ AI THẨM ĐỊNH NGỮ NGHĨA (CONTEXTUAL WARNINGS) ---
        # 1. Cảnh báo cấu trúc [Thuật ngữ (English) + Đuôi giải thích] để AI áp dụng Bài test Che Thuật Ngữ
        self_explaining_keys = []
        for opt_k, opt_v in opts.items():
            t = opt_v.strip()
            if '->' in t or '→' in t or ', còn ' in t or '; còn ' in t or '; trong khi ' in t:
                continue
            m = self.term_tail_re.match(t)
            if m:
                vn_part = m.group(1).strip()
                tail_part = m.group(3).strip()
                if vn_part.lower().startswith(self.non_term_prefixes):
                    continue
                if len(vn_part.split()) <= 7 and len(tail_part.split()) >= 4:
                    self_explaining_keys.append(opt_k)

        if len(self_explaining_keys) >= 2:
            warnings.append(
                f"Câu {idx} [{', '.join(self_explaining_keys)}]: [Cảnh báo Ngữ nghĩa AI] Các phương án có cấu trúc 'Thuật ngữ (English) + Đuôi giải thích'. "
                f"Hãy áp dụng Bài test Che Thuật Ngữ: Nếu thân câu chỉ hỏi Nhận diện tên khái niệm (Khuôn mẫu 1), BẮT BUỘC cắt bỏ phần đuôi giải thích thừa làm lộ đáp án. "
                f"Chỉ giữ lại nếu thân câu là Tình huống kép hỏi cả tên giải pháp lẫn cơ chế (Khuôn mẫu 3)."
            )

        if opt_lens and not is_num:
            # 2. Hệ số biến thiên độ dài (CV - Coefficient of Variation) — Chỉ cảnh báo khi độ dài trung bình >= 45 ký tự
            # (Tránh bắt ép AI phải "bơm chữ" vào các phương án ngắn 2-7 từ chuẩn đề thi đại học)
            mean_len = sum(opt_lens) / len(opt_lens)
            variance = sum((l - mean_len) ** 2 for l in opt_lens) / len(opt_lens)
            std_dev = math.sqrt(variance)
            cv = std_dev / mean_len if mean_len > 0 else 0
            
            if mean_len >= 45 and cv > 0.30:
                warnings.append(f"Câu {idx}: Độ lệch độ dài phương án hơi cao (CV = {cv:.2f} > 0.30). AI hãy rút gọn phương án dài thay vì bơm chữ vào phương án ngắn.")

            # 2b. Cảnh báo "Bơm văn" (Verbosity Warning) khi trung bình phương án dài quá 24 từ
            opt_word_counts = [len(v.strip().split()) for v in opts.values() if v.strip()]
            mean_words = sum(opt_word_counts) / len(opt_word_counts) if opt_word_counts else 0
            if mean_words > 24:
                warnings.append(
                    f"Câu {idx}: [Cảnh báo Độ dài / Bơm văn] Trung bình mỗi phương án dài {mean_words:.1f} từ (> 24 từ). "
                    f"Hãy cô đọng các phương án về mức 10–20 từ chuẩn đề thi đại học và kiểm tra xem 3 câu sai có bị bơm thành 'Phương án người rơm (Strawman)' không."
                )

            # 3. Cảnh báo nếu đáp án đúng dài hơn 1.35x mức trung bình các câu sai (với câu có độ dài trung bình >= 30 ký tự)
            if ans in opts and mean_len >= 30:
                ans_len = len(opts[ans].strip())
                other_lens = [len(v.strip()) for k, v in opts.items() if k != ans and v.strip()]
                if other_lens:
                    avg_other = sum(other_lens) / len(other_lens)
                    if ans_len > 1.35 * avg_other and ans_len <= max(other_lens) * 2.0:
                        warnings.append(
                            f"Câu {idx}: [Cảnh báo Độ lệch Đáp án Đúng] Đáp án đúng {ans} dài gấp {ans_len/avg_other:.2f} lần trung bình các phương án sai "
                            f"({ans_len} vs tb {avg_other:.1f} ký tự). Hãy rút gọn đáp án đúng hoặc bổ sung chi tiết hợp lý cho các phương án sai."
                        )

            # 4. Tính song hành cú pháp quy trình & Chống lộ bước đầu tiên ở Format 3
            has_arrows = [k for k, v in opts.items() if '->' in v or '→' in v]
            if 0 < len(has_arrows) < 4:
                warnings.append(f"Câu {idx}: Chỉ có {len(has_arrows)}/4 phương án có dấu mũi tên quy trình. Hãy kiểm tra tính song hành cú pháp.")
            elif len(has_arrows) == 4 and ans in opts:
                first_steps = {}
                for k, v in opts.items():
                    m_step = re.match(r'^\s*\(?(\d+|[A-Za-z])\)?\s*(?:->|→)', v.strip())
                    if m_step:
                        first_steps[k] = m_step.group(1)
                if ans in first_steps and len(first_steps) == 4:
                    ans_first = first_steps[ans]
                    same_first_count = sum(1 for v in first_steps.values() if v == ans_first)
                    if same_first_count == 1:
                        warnings.append(
                            f"Câu {idx}: [Cảnh báo Format 3] Duy nhất đáp án đúng {ans} bắt đầu bằng bước ({ans_first}). "
                            f"Nên để ít nhất 2 phương án có cùng bước mở đầu để chống loại trừ nhanh."
                        )

            # 5. Dấu hiệu đoán mò từ ngữ cực đoan
            distractor_extremes = []
            for k, v in opts.items():
                if k != ans:
                    for eq in self.extreme_qualifiers:
                        if eq in v.lower():
                            distractor_extremes.append((k, eq))
            if len(distractor_extremes) >= 2:
                warnings.append(f"Câu {idx}: Nhiều phương án sai dùng từ cực đoan ({distractor_extremes}) có thể giúp thí sinh dễ loại trừ.")

            # 6. Cảnh báo Bắt chữ / Trùng từ khóa độc tôn giữa Thân câu và Đáp án đúng (Clang Association Soft Check)
            q_text = (stem or q.get('question', '')).lower()
            if ans in opts and q_text:
                stop_words = {
                    'trong', 'của', 'các', 'những', 'được', 'không', 'nào', 'sau', 'đây', 'khi', 'với',
                    'cho', 'một', 'trên', 'theo', 'hoặc', 'nhưng', 'rằng', 'việc', 'hệ', 'thống', 'dữ',
                    'liệu', 'doanh', 'nghiệp', 'quản', 'lý', 'phân', 'tích', 'thông', 'tin', 'bằng',
                    'cách', 'thực', 'hiện', 'giúp', 'từ', 'đến', 'tại', 'về', 'và', 'là', 'có', 'để'
                }
                stem_tokens = set(re.findall(r'[a-zA-ZÀ-ỹ]{4,}', q_text)) - stop_words
                if len(stem_tokens) >= 5:
                    overlaps = {}
                    for k, v in opts.items():
                        opt_tokens = set(re.findall(r'[a-zA-ZÀ-ỹ]{4,}', v.lower())) - stop_words
                        overlaps[k] = len(stem_tokens & opt_tokens)
                    ans_ov = overlaps.get(ans, 0)
                    max_other_ov = max((v for k, v in overlaps.items() if k != ans), default=0)
                    if ans_ov >= 4 and ans_ov >= max_other_ov + 3:
                        warnings.append(
                            f"Câu {idx}: [Cảnh báo Bắt chữ / Clang Association] Đáp án đúng {ans} trùng {ans_ov} từ khóa với thân câu hỏi "
                            f"(trong khi các câu sai chỉ trùng tối đa {max_other_ov} từ). Hãy kiểm tra xem có bị lộ đáp án qua từ khóa lặp lại không."
                        )

        return errors, warnings

    def audit_exam(self, questions):
        all_errors = []
        all_warnings = []
        ans_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        all_statements_correct_qs = []
        unique_longest_count = 0
        format1_count = 0
        
        for idx, q in enumerate(questions, 1):
            errs, warns = self.audit_question(q, idx)
            all_errors.extend(errs)
            all_warnings.extend(warns)
            ans = q.get('ans', '').upper()
            if ans in ans_dist:
                ans_dist[ans] += 1
            opts = q.get('options', {})
            ans_text = opts.get(ans, '').lower()
            if re.search(r'cả\s*\(i\)\s*,\s*\(ii\)\s*và\s*\(iii\)', ans_text) or re.search(r'cả\s*3\s*(mệnh đề|nhận định|phát biểu)', ans_text):
                all_statements_correct_qs.append(idx)

            # Đếm số câu có đáp án đúng là phương án dài nhất duy nhất
            is_num = all(re.match(r'^[\d\s\.,%+\-*/\$₫a-zA-Z]+$', v.strip()) and len(v.strip()) < 15 for v in opts.values())
            if ans in opts and not is_num:
                ans_len = len(opts[ans].strip())
                other_lens = [len(v.strip()) for k, v in opts.items() if k != ans and v.strip()]
                if other_lens and ans_len > max(other_lens):
                    unique_longest_count += 1

            # Đếm số câu Format 1 (Tổ hợp mệnh đề (i), (ii))
            stem_text = q.get('question', '')
            opt_texts = " ".join(opts.values())
            all_q_text = stem_text + " " + opt_texts
            if '(i)' in all_q_text and '(ii)' in all_q_text:
                format1_count += 1
                
        if len(all_statements_correct_qs) > 1:
            all_warnings.append(
                f"[Cảnh báo Format 1B] Có {len(all_statements_correct_qs)} câu tổ hợp mệnh đề (Câu {all_statements_correct_qs}) cùng lấy 'Cả (i), (ii) và (iii)' làm đáp án đúng. "
                f"Chỉ nên giữ tối đa 1 câu là tất cả đều đúng, các câu còn lại nên cài 1 mệnh đề sai tinh vi để chống mẹo khoanh tất cả."
            )

        total = len(questions)
        if total >= 10:
            longest_ratio = (unique_longest_count / total) * 100
            if longest_ratio > 35.0:
                all_warnings.append(
                    f"[Cảnh báo Đoán mò theo độ dài] Toàn đề có {unique_longest_count}/{total} câu ({longest_ratio:.1f}%) "
                    f"có đáp án đúng là phương án dài nhất duy nhất (> 35%). Hãy rút gọn đáp án đúng hoặc bổ sung chi tiết hợp lý "
                    f"cho các phương án sai để độ dài phân bố tự nhiên."
                )

        if total >= 30 and format1_count < 2:
            all_warnings.append(
                f"[Cảnh báo Độ phủ Format] Đề thi có {total} câu (>= 30) nhưng chỉ có {format1_count} câu Format 1 "
                f"(Tổ hợp mệnh đề (i), (ii)). Khuyến nghị bổ sung thêm câu hỏi Format 1 để tăng độ phân hóa."
            )
                
        dist_report = {}
        if total > 0:
            for k, count in ans_dist.items():
                pct = (count / total) * 100
                dist_report[k] = f"{count}/{total} ({pct:.1f}%)"
                if total >= 20 and (pct < 15 or pct > 35):
                    all_warnings.append(f"Phân bố đáp án {k} lệch chuẩn: {pct:.1f}% (Chuẩn: 20% - 30%)")
                    
        return {
            'total_questions': total,
            'errors': all_errors,
            'warnings': all_warnings,
            'distribution': dist_report,
            'passed': len(all_errors) == 0
        }
