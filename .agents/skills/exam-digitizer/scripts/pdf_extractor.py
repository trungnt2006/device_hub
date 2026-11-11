"""
PDF Extractor Engine for Exam Digitizer
Supports multi-layer extraction:
- Layer 1: Vector Yellow Highlighting (page.get_drawings)
- Layer 2: Annotations (Highlight Type 8) & Font styling (Bold, Colors)
- Layer 3: Answer Tables Parsing & Watermark Filtering
"""

import re
import fitz  # PyMuPDF


class PDFExamExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_yellow_rects(self, page):
        """Extract yellow highlight rectangles from drawings."""
        yellow_rects = []
        for d in page.get_drawings():
            fill = d.get('fill')
            if fill:
                r, g, b = fill[:3]
                # Match yellow / yellowish orange fill
                if r > 0.7 and g > 0.7 and b < 0.4:
                    yellow_rects.append(d['rect'])
        return yellow_rects

    def is_line_highlighted(self, line_bbox, yellow_rects):
        """Check if a text line intersects with any yellow highlight rectangle."""
        for yr in yellow_rects:
            if line_bbox.intersects(yr):
                intersect = line_bbox & yr
                if intersect.width > 5:
                    return True
        return False

    def clean_text(self, text):
        """Filter out common third-party watermarks and junk."""
        junk_patterns = [
            r'Studocu is not sponsored.*',
            r'Downloaded by.*',
            r'lOMoARcPSD.*',
            r'Trang \d+/\d+',
            r'Page \d+ of \d+'
        ]
        cleaned = text
        for pat in junk_patterns:
            cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def parse_answer_table(self, text):
        """Parse structured answer tables like 1.A, 2.B, 3.D etc."""
        answers = {}
        for m in re.finditer(r'(\d+)[\.\s]+([A-Da-d])\b', text):
            q_num = int(m.group(1))
            ans_letter = m.group(2).upper()
            answers[q_num] = ans_letter
        return answers
