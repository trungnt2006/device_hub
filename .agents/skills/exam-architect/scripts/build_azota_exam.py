import re
import sys
import os
import json
import random
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from question_auditor import QuestionAuditor

def strip_xml_invalid_chars(s):
    if not s:
        return ""
    return re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', s)

def clean_text(s):
    if not s:
        return ""
    s = s.replace('\xa0', ' ').replace('\u200b', '')
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    s = re.sub(r'\\(\*|_)', r'\1', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = strip_xml_invalid_chars(s)
    return s.strip()

NEGATION_TERMS = ("KHÔNG", "NGOẠI TRỪ", "SAI")

def safe_swap_option_labels_in_explanation(expl, mapping):
    """
    Cập nhật nhãn phương án A/B/C/D trong Lời giải khi hoán vị phương án
    mà TUYỆT ĐỐI KHÔNG làm hỏng mạo từ tiếng Anh 'A' (như 'A hyperplane', 'A clear business need').
    mapping: dict ánh xạ từ nhãn cũ sang nhãn mới, ví dụ {'A': 'B', 'B': 'A', 'C': 'C', 'D': 'D'}.
    """
    if not expl or all(k == v for k, v in mapping.items()):
        return expl

    # Chỉ thay thế khi A/B/C/D đứng trong ngữ cảnh chỉ phương án trắc nghiệm rõ ràng
    contextual_pattern = re.compile(
        r'(\b(?:Chọn|Phương án|phương án|Đáp án|đáp án|Câu|câu)\s+)([A-D])(\b)'
        r'|(\+\s*)([A-D])(\s*\((?:Đúng|Sai)\)\s*:)'
        r'|(-\s*Phương án\s+)([A-D])(\s*(?:\((?:Đúng|Sai)\))?\s*:)'
        r'|(\()([A-D])(\)\s*(?:sai|đúng|bị loại|thất bại|là\b))'
    )

    def _repl(m):
        if m.group(2):
            return f"{m.group(1)}{mapping.get(m.group(2), m.group(2))}{m.group(3)}"
        if m.group(5):
            return f"{m.group(4)}{mapping.get(m.group(5), m.group(5))}{m.group(6)}"
        if m.group(8):
            return f"{m.group(7)}{mapping.get(m.group(8), m.group(8))}{m.group(9)}"
        if m.group(11):
            return f"{m.group(10)}{mapping.get(m.group(11), m.group(11))}{m.group(12)}"
        return m.group(0)

    return contextual_pattern.sub(_repl, expl)


def safe_permute_question_options(item, new_order):
    """
    Hoán vị thứ tự phương án của 1 câu hỏi theo new_order (danh sách 4 chữ cái cũ ứng với vị trí A, B, C, D mới).
    Ví dụ new_order = ['B', 'A', 'C', 'D'] nghĩa là phương án B cũ sẽ lên vị trí A mới.
    """
    labels = ['A', 'B', 'C', 'D']
    old_opts = item.get('options', {})
    if len(old_opts) != 4 or set(new_order) != set(labels):
        return item

    old_to_new = {old_lbl: labels[new_idx] for new_idx, old_lbl in enumerate(new_order)}
    new_opts = {labels[new_idx]: old_opts[old_lbl] for new_idx, old_lbl in enumerate(new_order)}
    old_ans = item.get('ans', 'A').upper()
    new_ans = old_to_new.get(old_ans, old_ans)

    updated = dict(item)
    updated['options'] = new_opts
    updated['ans'] = new_ans
    if 'explanation' in updated and updated['explanation']:
        updated['explanation'] = safe_swap_option_labels_in_explanation(updated['explanation'], old_to_new)
    return updated


def safe_balance_and_shuffle_exam(items, shuffle_questions=False, balance_answers=False, seed=42):
    """
    Tùy chọn trộn ngẫu nhiên thứ tự câu hỏi giữa các chương (giống đề thi thật)
    và cân bằng phân bố đáp án A/B/C/D (~25%) không tạo chuỗi lặp >= 3 câu liên tiếp.
    """
    rng = random.Random(seed)
    work_items = [dict(it) for it in items]

    if shuffle_questions:
        rng.shuffle(work_items)

    if balance_answers and len(work_items) >= 4:
        labels = ['A', 'B', 'C', 'D']
        n = len(work_items)
        base = n // 4
        rem = n % 4
        target_pool = []
        for idx_l, lbl in enumerate(labels):
            target_pool.extend([lbl] * (base + (1 if idx_l < rem else 0)))

        # Xáo trộn target_pool sao cho không có >= 3 đáp án liên tiếp trùng nhau
        for _ in range(500):
            rng.shuffle(target_pool)
            has_streak = any(
                target_pool[i] == target_pool[i - 1] == target_pool[i - 2]
                for i in range(2, len(target_pool))
            )
            if not has_streak:
                break

        for idx, it in enumerate(work_items):
            cur_ans = it.get('ans', 'A').upper()
            desired_ans = target_pool[idx]
            if cur_ans != desired_ans:
                # Chỉ đổi chỗ cur_ans và desired_ans
                new_order = list(labels)
                i_cur = labels.index(cur_ans)
                i_des = labels.index(desired_ans)
                new_order[i_cur], new_order[i_des] = new_order[i_des], new_order[i_cur]
                work_items[idx] = safe_permute_question_options(it, new_order)

    return work_items

def add_rich_text(paragraph, text, base_bold=False):
    """Thêm text vào paragraph, tự động in đậm các từ khóa phủ định theo quy tắc HUB."""
    if not text:
        return
    pattern = "(" + "|".join(re.escape(t) for t in NEGATION_TERMS) + ")"
    for seg in re.split(pattern, text):
        if not seg:
            continue
        r = paragraph.add_run(seg)
        r.bold = True if seg in NEGATION_TERMS else base_bold

def export_mock_exam_for_students(items, subject_title, duration_minutes, output_path):
    """
    MODE A: Clean Student Mock Exam (NO answers underlined, NO explanations).
    Includes student header for exam condition practice.
    """
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)
        
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    
    # Document Core Properties
    core_props = doc.core_properties
    core_props.title = f"Đề thi mô phỏng: {subject_title}"
    core_props.subject = subject_title
    core_props.author = "Exam Architect (HUB v4.1)"
    core_props.category = "Đề thi thử sinh viên"
    core_props.comments = f"Đề thi thử mô phỏng {len(items)} câu trắc nghiệm (không đáp án) dành cho sinh viên tự bấm giờ làm bài."
    
    # Header Table
    tbl = doc.add_table(rows=2, cols=2)
    tbl.autofit = True
    c00 = tbl.cell(0, 0).paragraphs[0]
    c00.add_run("TRƯỜNG ĐẠI HỌC NGÂN HÀNG TP.HCM\nKHOA HỆ THỐNG THÔNG TIN QUẢN LÝ").bold = True
    c00.runs[0].font.size = Pt(10)
    
    c01 = tbl.cell(0, 1).paragraphs[0]
    c01.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c01.add_run(f"ĐỀ THI MÔ PHỎNG (MOCK EXAM)\nMôn học: {subject_title}\nThời gian làm bài: {duration_minutes} phút").bold = True
    c01.runs[0].font.size = Pt(10)
    
    c10 = tbl.cell(1, 0).paragraphs[0]
    c10.add_run("Họ và tên SV: ........................................................\nMSSV: ....................................... Lớp: ..................").italic = True
    c10.runs[0].font.size = Pt(10)
    
    c11 = tbl.cell(1, 1).paragraphs[0]
    c11.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c11.add_run(f"Số lượng câu hỏi: {len(items)} câu\n(Thí sinh không được sử dụng tài liệu)").italic = True
    c11.runs[0].font.size = Pt(10)
    
    doc.add_paragraph("-------------------------------------------------------------------------------------------------------").alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    for idx, item in enumerate(items, start=1):
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.line_spacing = 1.15
        
        r_q = p_q.add_run(f"Câu {idx}: ")
        r_q.bold = True
        
        q_lines = item['question'].split('\n')
        add_rich_text(p_q, clean_text(q_lines[0]))
        for sub_l in q_lines[1:]:
            p_sub = doc.add_paragraph()
            p_sub.paragraph_format.left_indent = Inches(0.2)
            p_sub.paragraph_format.space_before = Pt(0)
            p_sub.paragraph_format.space_after = Pt(2)
            p_sub.paragraph_format.line_spacing = 1.15
            add_rich_text(p_sub, clean_text(sub_l))
            
        for opt_k in ['A', 'B', 'C', 'D']:
            if opt_k in item['options']:
                p_opt = doc.add_paragraph()
                p_opt.paragraph_format.left_indent = Inches(0.2)
                p_opt.paragraph_format.space_before = Pt(0)
                p_opt.paragraph_format.space_after = Pt(2)
                p_opt.paragraph_format.line_spacing = 1.15
                
                r_k = p_opt.add_run(f"{opt_k}. ")
                r_k.bold = True
                p_opt.add_run(clean_text(item['options'][opt_k]))
                
    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(20)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("--- HẾT ---")
    r_end.bold = True
    
    doc.save(output_path)
    print(f"[Mode A] Saved Student Mock Exam: {os.path.basename(output_path)}")

def export_azota_package(items, subject_title, output_path, subtitle="", shuffle_questions=False, balance_answers=False, seed=42):
    """
    MODE C: Azota 1-Click Package (.docx with underlined correct answer, explanations & metadata).
    """
    if shuffle_questions or balance_answers:
        items = safe_balance_and_shuffle_exam(
            items,
            shuffle_questions=shuffle_questions,
            balance_answers=balance_answers,
            seed=seed
        )
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)
        
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    
    # 1. Document Core Properties (Metadata in File -> Info)
    core_props = doc.core_properties
    core_props.title = f"Đề thi: {subject_title} - {subtitle}".strip(" -")
    core_props.subject = subject_title
    core_props.author = "Exam Architect (HUB v4.1)"
    core_props.category = "Ngân hàng câu hỏi trắc nghiệm đại học"
    core_props.comments = f"Đề thi {len(items)} câu trắc nghiệm chuẩn Azota 1-Click."
    
    # 2. Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    
    r1 = p_title.add_run(f"BỘ ĐỀ THI TRẮC NGHIỆM: {subject_title.upper()}\n")
    r1.bold = True
    r1.font.size = Pt(13)
    
    if subtitle:
        r2 = p_title.add_run(f"{subtitle}\n")
        r2.bold = True
        r2.font.size = Pt(11)
        
    r3 = p_title.add_run("(File định dạng chuẩn Azota 1-Click: Đáp án gạch chân, Lời giải chi tiết & Metadata học thuật)\n")
    r3.italic = True
    r3.font.size = Pt(10)
    r3.font.color.rgb = RGBColor(100, 100, 100)
    
    doc.add_paragraph("-------------------------------------------------------------------------------------------------------").alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 3. Question Rendering Loop
    for idx, item in enumerate(items, start=1):
        ans = item['ans'].upper()
        
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.line_spacing = 1.15
        
        r_q = p_q.add_run(f"Câu {idx}: ")
        r_q.bold = True
        
        q_lines = item['question'].split('\n')
        add_rich_text(p_q, clean_text(q_lines[0]))
        for sub_l in q_lines[1:]:
            p_sub = doc.add_paragraph()
            p_sub.paragraph_format.left_indent = Inches(0.2)
            p_sub.paragraph_format.space_before = Pt(0)
            p_sub.paragraph_format.space_after = Pt(2)
            p_sub.paragraph_format.line_spacing = 1.15
            add_rich_text(p_sub, clean_text(sub_l))
            
        for opt_k in ['A', 'B', 'C', 'D']:
            if opt_k in item['options']:
                p_opt = doc.add_paragraph()
                p_opt.paragraph_format.left_indent = Inches(0.2)
                p_opt.paragraph_format.space_before = Pt(0)
                p_opt.paragraph_format.space_after = Pt(2)
                p_opt.paragraph_format.line_spacing = 1.15
                
                is_correct = (opt_k == ans)
                r_k = p_opt.add_run(f"{opt_k}. ")
                if is_correct:
                    r_k.underline = True
                    r_k.bold = True
                    
                p_opt.add_run(clean_text(item['options'][opt_k]))
                
        p_sol = doc.add_paragraph()
        p_sol.paragraph_format.left_indent = Inches(0.2)
        p_sol.paragraph_format.space_before = Pt(2)
        p_sol.paragraph_format.space_after = Pt(4)
        p_sol.paragraph_format.line_spacing = 1.15
        
        r_sol_lbl = p_sol.add_run("Lời giải:\n")
        r_sol_lbl.bold = True
        r_sol_lbl.font.color.rgb = RGBColor(0, 112, 192)
        
        r_pick = p_sol.add_run(f"Chọn {ans}.\n")
        r_pick.bold = True
        
        expl = clean_text(item.get('explanation', ''))
        expl = re.sub(rf"^Chọn\s+{ans}\.?\s*", "", expl, flags=re.IGNORECASE).strip()
        
        if expl:
            r_expl = p_sol.add_run(expl + "\n")
            r_expl.font.color.rgb = RGBColor(70, 70, 70)
            
        # Metadata block for question: Clean citation, Bloom, Subtopic (NO internal format jargon, NO redundant faculty tags)
        meta_parts = []
        cit = item.get('citation')
        if cit:
            if isinstance(cit, dict):
                src = cit.get('source', '')
                src = re.sub(r',?\s*Bộ môn KHMT\s*-\s*Khoa HTTTQL,?\s*HUB', '', src, flags=re.IGNORECASE).strip()
                src = re.sub(r',?\s*Khoa HTTTQL,?\s*HUB', '', src, flags=re.IGNORECASE).strip()
                pg = cit.get('page')
                sec = cit.get('section')
                ref = src
                if sec: ref += f", Mục {sec}"
                if pg: ref += f", Trang {pg}"
                meta_parts.append(f"Nguồn: {ref}")
            elif isinstance(cit, str) and cit.strip():
                src = re.sub(r',?\s*Bộ môn KHMT\s*-\s*Khoa HTTTQL,?\s*HUB', '', cit, flags=re.IGNORECASE).strip()
                src = re.sub(r',?\s*Khoa HTTTQL,?\s*HUB', '', cit, flags=re.IGNORECASE).strip()
                meta_parts.append(f"Nguồn: {src}")
                
        if item.get('bloom'):
            meta_parts.append(f"Mức độ: {item['bloom']}")
        if item.get('subtopic'):
            meta_parts.append(f"Chủ đề: {item['subtopic']}")
            
        if meta_parts:
            r_meta = p_sol.add_run("📌 [Metadata: " + " | ".join(meta_parts) + "]")
            r_meta.italic = True
            r_meta.font.size = Pt(9.5)
            r_meta.font.color.rgb = RGBColor(0, 102, 153)
            
    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(20)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("HẾT")
    r_end.bold = True
    r_end.font.size = Pt(13)
    
    doc.save(output_path)
    print(f"[Mode C] Saved Azota Package DOCX: {os.path.basename(output_path)}")

def export_master_bank(items, spec, json_output_path, md_output_path):
    """
    MODE B: Master Question Bank (JSON & Markdown with complete metadata and citations).
    """
    # 1. Export JSON
    payload = {
        "spec": spec,
        "total_questions": len(items),
        "questions": items
    }
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[Mode B] Saved Master Bank JSON: {os.path.basename(json_output_path)}")
    
    # 2. Export Markdown
    with open(md_output_path, 'w', encoding='utf-8') as f:
        f.write(f"# NGÂN HÀNG CÂU HỎI TRẮC NGHIỆM: {spec.get('subject_metadata', {}).get('name', 'MÔN HỌC')}\n\n")
        f.write(f"- **Mã môn:** {spec.get('subject_metadata', {}).get('code', 'N/A')}\n")
        f.write(f"- **Trạng thái nguồn:** `{spec.get('subject_metadata', {}).get('source_status', 'inferred')}`\n")
        f.write(f"- **Tổng số câu:** {len(items)}\n\n---\n\n")
        
        for idx, it in enumerate(items, start=1):
            f.write(f"### Câu {idx}: {it['question']}\n\n")
            for opt_k in ['A', 'B', 'C', 'D']:
                if opt_k in it['options']:
                    is_ans = (opt_k == it['ans'].upper())
                    star = "**" if is_ans else ""
                    f.write(f"- {star}{opt_k}. {it['options'][opt_k]}{star}\n")
            f.write(f"\n* **Đáp án đúng:** `{it['ans'].upper()}`\n")
            f.write(f"* **Lời giải:** {it.get('explanation', '')}\n")
            cit = it.get('citation', {})
            f.write(f"* **Bằng chứng nguồn (Citation):** {cit.get('source', 'N/A')} - Chương {cit.get('chapter', 'N/A')} ({cit.get('section', 'N/A')}) | Độ tin cậy: `{cit.get('confidence', 1.0)}`\n")
            f.write(f"* **Mức độ Bloom:** `{it.get('bloom_level', 'understand')}` | **Dạng bẫy:** `{it.get('trap_type', 'standard')}`\n\n---\n\n")
            
    print(f"[Mode B] Saved Master Bank Markdown: {os.path.basename(md_output_path)}")
