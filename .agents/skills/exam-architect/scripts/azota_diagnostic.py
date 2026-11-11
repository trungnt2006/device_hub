import re
import sys
import json

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class AzotaDiagnostic:
    """
    Phân tích kết quả thi Azota và sinh Meta-Prompt cho NotebookLM
    """
    def __init__(self):
        pass

    def parse_azota_text(self, text):
        lines = text.strip().split('\n')
        score_info = {}
        # Parse header
        m_score = re.search(r'Trắc nghiệm:\s*([\d\.]+)\s*\(([\d]+)/([\d]+)\s*câu\)', text)
        if m_score:
            score_info['score'] = float(m_score.group(1))
            score_info['correct_count'] = int(m_score.group(2))
            score_info['total_count'] = int(m_score.group(3))

        # Parse questions
        # Pattern for question blocks: Câu X. ... | Đáp án đúng: X | ...
        q_blocks = re.findall(r'(Câu\s+(\d+)\.[\s\S]*?\|\s*Đáp án đúng:\s*([A-D])\s*\|([\s\S]*?)(?=\nCâu\s+\d+\.|\Z|----HẾT---))', text)
        
        parsed_questions = []
        for full_block, q_num, correct_ans, result_row in q_blocks:
            q_num = int(q_num)
            # Find chosen answer: ✓X means chosen correct, ✗X means chosen wrong
            chosen_ans = None
            is_correct = False
            
            m_correct = re.search(r'✓([A-D])', result_row)
            m_wrong = re.search(r'✗([A-D])', result_row)
            
            if m_correct:
                chosen_ans = m_correct.group(1)
                is_correct = True
            elif m_wrong:
                chosen_ans = m_wrong.group(1)
                is_correct = False

            # Extract stem
            lines_block = full_block.strip().split('\n')
            stem = lines_block[0]
            # Options
            options = {}
            for l in lines_block[1:]:
                m_opt = re.findall(r'([A-D])\.\s*([^A-D\t\n]+)', l)
                for opt_let, opt_txt in m_opt:
                    options[opt_let] = opt_txt.strip()

            parsed_questions.append({
                'num': q_num,
                'stem': stem,
                'correct_ans': correct_ans,
                'chosen_ans': chosen_ans,
                'is_correct': is_correct,
                'options': options,
                'raw': full_block.strip()
            })

        return score_info, parsed_questions

    def generate_notebooklm_prompt(self, score_info, wrong_questions, subject="Kho dữ liệu"):
        if not wrong_questions:
            return "Chúc mừng! Bạn đã trả lời đúng 100% các câu hỏi."

        prompt_lines = [
            f"Bạn là một Giảng viên/Chuyên gia hàng đầu về môn học '{subject}'.",
            "Dựa trên toàn bộ tài liệu nguồn (Slide bài giảng, Giáo trình) mà tôi đã tải lên trong cuốn Notebook này, "
            "hãy đóng vai trò người hướng dẫn học tập (Personal AI Tutor) phân tích chi tiết và giảng giải cặn kẽ các câu trắc nghiệm mà tôi đã làm sai dưới đây.",
            "",
            "### YÊU CẦU GIẢNG DẠY:",
            "1. **Chỉ ra bản chất kiến thức cốt lõi:** Trích dẫn chính xác khái niệm, nguyên lý hoặc sơ đồ quy trình được đề cập trong Slide/Giáo trình nguồn.",
            "2. **Giải mã bẫy nhận thức:** Phân tích chi tiết vì sao phương án tôi chọn lại SAI (nó gây hiểu nhầm ở điểm nào, hay thuộc về ngữ cảnh nào khác) và vì sao đáp án chuẩn lại ĐÚNG.",
            "3. **Bảng so sánh đối ngẫu:** Nếu câu hỏi liên quan đến cặp khái niệm đối ngẫu (như Reconciled Data vs Derived Data, OLTP vs OLAP, Logical vs Physical Data Mart), hãy lập bảng so sánh bản chất 3-4 tiêu chí.",
            "4. **Đúc kết quy tắc ghi nhớ nhanh:** Tóm tắt 1-2 câu thần chú hoặc mẹo ghi nhớ logic cho từng chủ đề để tôi không bao giờ bị bẫy lại trong kỳ thi thật.",
            "",
            "---",
            f"### DANH SÁCH {len(wrong_questions)} CÂU HỎI TÔI ĐÃ LÀM SAI TRONG BÀI KIỂM TRA:",
            ""
        ]

        for i, q in enumerate(wrong_questions, start=1):
            chosen = q['chosen_ans'] or "Chưa rõ"
            correct = q['correct_ans']
            chosen_text = q['options'].get(chosen, '')
            correct_text = q['options'].get(correct, '')
            
            prompt_lines.append(f"#### Câu {q['num']}:")
            prompt_lines.append(f"- **Thân câu hỏi:** {q['stem']}")
            prompt_lines.append(f"- **Tôi đã chọn (SAI):** {chosen}. {chosen_text}")
            prompt_lines.append(f"- **Đáp án chuẩn (ĐÚNG):** {correct}. {correct_text}")
            prompt_lines.append("")

        return "\n".join(prompt_lines)
