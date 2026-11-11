"""
Azota Formatter Engine for Exam Digitizer
Formats digitized questions into standard Azota 1-Click .docx files.
Standards:
- Margins: 2cm on all 4 sides
- Font: Times New Roman 11pt, line spacing 1.15
- Question: Bold 'Câu X: '
- Options: Left indent 0.2 inch. Correct answer underlined and bold ('<u><b>A.</b></u>')
- Explanation: Bold Green 'Lời giải:', followed by theory and grey italic citation ('📌 Nguồn: ...')
- End of Document: Centered bold 'HẾT' in 14pt
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


class AzotaDocxBuilder:
    def __init__(self):
        self.doc = Document()
        self._setup_page_layout()

    def _setup_page_layout(self):
        for section in self.doc.sections:
            section.top_margin = Inches(0.79)     # ~2 cm
            section.bottom_margin = Inches(0.79)  # ~2 cm
            section.left_margin = Inches(0.79)    # ~2 cm
            section.right_margin = Inches(0.79)   # ~2 cm

    def add_question(self, index, q_data):
        """
        q_data format:
        {
            "stem": "Nội dung câu hỏi...",
            "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
            "correct_key": "A",
            "explanation": "Chi tiết giải thích...",
            "citation": "Slide... | Mức độ: Bloom 2 | Phân hệ: ..."
        }
        """
        # Question stem
        p_q = self.doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(6)
        p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.line_spacing = 1.15

        r_prefix = p_q.add_run(f"Câu {index}: ")
        r_prefix.bold = True
        r_prefix.font.name = "Times New Roman"
        r_prefix.font.size = Pt(11)

        r_stem = p_q.add_run(q_data["stem"])
        r_stem.font.name = "Times New Roman"
        r_stem.font.size = Pt(11)

        # 4 Options
        options = q_data.get("options", {})
        correct_key = q_data.get("correct_key", "A").upper()

        for opt_key in ["A", "B", "C", "D"]:
            opt_text = options.get(opt_key, "")
            p_opt = self.doc.add_paragraph()
            p_opt.paragraph_format.left_indent = Inches(0.2)
            p_opt.paragraph_format.space_before = Pt(1)
            p_opt.paragraph_format.space_after = Pt(1)
            p_opt.paragraph_format.line_spacing = 1.15

            r_key = p_opt.add_run(f"{opt_key}. ")
            r_key.font.name = "Times New Roman"
            r_key.font.size = Pt(11)

            if opt_key == correct_key:
                r_key.bold = True
                r_key.underline = True

            r_val = p_opt.add_run(opt_text)
            r_val.font.name = "Times New Roman"
            r_val.font.size = Pt(11)

        # Explanation block
        exp = q_data.get("explanation", "").strip()
        citation = q_data.get("citation", "").strip()

        if exp or citation:
            p_exp = self.doc.add_paragraph()
            p_exp.paragraph_format.space_before = Pt(3)
            p_exp.paragraph_format.space_after = Pt(2)
            p_exp.paragraph_format.line_spacing = 1.15

            r_exp_title = p_exp.add_run("Lời giải:\n")
            r_exp_title.bold = True
            r_exp_title.font.name = "Times New Roman"
            r_exp_title.font.size = Pt(11)
            r_exp_title.font.color.rgb = RGBColor(0, 102, 0)  # Green

            r_exp_chose = p_exp.add_run(f"Chọn {correct_key}.\n")
            r_exp_chose.bold = True
            r_exp_chose.font.name = "Times New Roman"
            r_exp_chose.font.size = Pt(11)

            if exp:
                r_exp_body = p_exp.add_run(f"{exp}\n")
                r_exp_body.font.name = "Times New Roman"
                r_exp_body.font.size = Pt(10.5)

            if citation:
                r_cite = p_exp.add_run(f"📌 Nguồn: {citation}")
                r_cite.italic = True
                r_cite.font.name = "Times New Roman"
                r_cite.font.size = Pt(10)
                r_cite.font.color.rgb = RGBColor(85, 85, 85)  # Dark Grey

    def finalize_and_save(self, output_path):
        """Append HẾT marker and save document."""
        p_end = self.doc.add_paragraph()
        p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_end.paragraph_format.space_before = Pt(18)
        p_end.paragraph_format.space_after = Pt(12)

        r_end = p_end.add_run("HẾT")
        r_end.bold = True
        r_end.font.name = "Times New Roman"
        r_end.font.size = Pt(14)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self.doc.save(output_path)
        print(f"Azota 1-Click DOCX successfully saved at: {output_path}")
