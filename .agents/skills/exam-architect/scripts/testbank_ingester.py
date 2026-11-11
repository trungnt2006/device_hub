import re
import sys
import os
import json

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import pypdf
except ImportError:
    pypdf = None

class TestBankIngester:
    """
    Analyzes and ingests questions from academic Test Banks (e.g. Pearson, McGraw-Hill)
    to extract authoring patterns, Sibling Concepts, and high-difficulty traps.
    """
    def __init__(self, knowledge_file=None):
        self.knowledge_file = knowledge_file or os.path.join(
            os.path.dirname(__file__), '..', 'references', 'testbank_knowledge.json'
        )
        self.knowledge = self.load_knowledge()

    def load_knowledge(self):
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "sources_ingested": [],
            "sibling_concept_clusters": [],
            "sample_stems": [],
            "contrast_pairs": []
        }

    def save_knowledge(self):
        os.makedirs(os.path.dirname(self.knowledge_file), exist_ok=True)
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

    def extract_text_from_pdf(self, pdf_path, max_pages=150):
        if not pypdf:
            print("Lỗi: Thư viện pypdf chưa được cài đặt. Vui lòng chạy 'pip install pypdf'.")
            return ""
        try:
            reader = pypdf.PdfReader(pdf_path)
            total = len(reader.pages)
            pages_to_read = min(total, max_pages)
            print(f"Đang đọc {pages_to_read} / {total} trang từ {pdf_path}...")
            full_text = ""
            for i in range(pages_to_read):
                t = reader.pages[i].extract_text() or ""
                full_text += f"\n[PAGE_{i+1}]\n" + t
            return full_text
        except Exception as e:
            print(f"Lỗi khi đọc file PDF: {e}")
            return ""

    def ingest_pdf(self, pdf_path, max_pages=150):
        text = self.extract_text_from_pdf(pdf_path, max_pages)
        if not text:
            return 0

        # Pattern for standard Pearson MCQs:
        # e.g.:
        # 21) Question text...
        # A) opt1
        # B) opt2
        # C) opt3
        # D) opt4
        # Answer: C
        # Diff: 2 Page Ref: 59-60
        pattern = re.compile(
            r'(\d+)[\.\)]\s*(.+?)\n'
            r'[A-D]\)\s*(.+?)\n'
            r'[A-D]\)\s*(.+?)\n'
            r'[A-D]\)\s*(.+?)\n'
            r'[A-D]\)\s*(.+?)\n'
            r'Answer:\s*([A-D])',
            re.DOTALL
        )

        matches = pattern.findall(text)
        print(f"Đã phát hiện {len(matches)} câu hỏi trắc nghiệm chuẩn Test Bank.")

        clusters = []
        for m in matches:
            q_num = m[0]
            stem = m[1].strip()
            opts = [m[2].strip(), m[3].strip(), m[4].strip(), m[5].strip()]
            ans = m[6].strip()

            # If all 4 options are short nouns/phrases (< 60 chars), they represent a Sibling Concept Cluster!
            if all(len(o) < 60 for o in opts) and len(set(opts)) == 4:
                clusters.append({
                    "stem": stem,
                    "siblings": opts,
                    "correct_answer": ans
                })

        filename = os.path.basename(pdf_path)
        if filename not in self.knowledge["sources_ingested"]:
            self.knowledge["sources_ingested"].append(filename)

        self.knowledge["sibling_concept_clusters"].extend(clusters[:50])
        self.save_knowledge()

        print(f"=== KẾT QUẢ HẤP THỤ TEST BANK TỪ GS.TS ===")
        print(f"- Nguồn tài liệu: {filename}")
        print(f"- Số nhóm 'Thuật ngữ cùng họ' (Sibling Concepts) đã trích xuất: {len(clusters)}")
        print(f"- Tri thức mới đã được nạp tự động vào {self.knowledge_file}.")
        return len(clusters)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        ingester = TestBankIngester()
        ingester.ingest_pdf(path)
    else:
        print("Cách dùng: python testbank_ingester.py <duong_dan_file_testbank.pdf>")
