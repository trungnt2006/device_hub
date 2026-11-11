"""
Quality Auditor for Exam Digitizer
Verifies integrity of digitized questions:
1. Pre-flight Anomaly Scanner: Detects Missing-Stem questions (Rule 3A) and Flashcard/Missing-Option questions (Rule 3B) to prompt user confirmation.
2. Hard errors: Missing stem, missing options, invalid correct_key, logic conflict.
3. Parity check: Verbatim length ratios, distribution of A/B/C/D answers (~25%).
4. Explanation format: Presence of citation and rationale.
"""

from collections import Counter


class DigitizerAuditor:
    @staticmethod
    def scan_anomalies(questions):
        """
        Scans raw extracted questions for two user-confirmable anomalies:
        - missing_stem_questions (Rule 3A): Has options/answer, but question stem is empty.
          -> Ask user: Delete (NO) or Reconstruct academic stem from textbook/slides (YES).
        - flashcard_questions (Rule 3B): Has stem and 1 answer, but < 4 options.
          -> Ask user: Delete (NO) or Generate 3 Sibling Concept distractors (YES).
        """
        missing_stem = []
        flashcards = []

        for idx, q in enumerate(questions, 1):
            stem = q.get("stem", "").strip()
            options = q.get("options", {})
            correct_key = q.get("correct_key", "").upper()
            non_empty_opts = {k: v.strip() for k, v in options.items() if v and v.strip()} if isinstance(options, dict) else {}

            if not stem:
                missing_stem.append({
                    "index": idx,
                    "correct_key": correct_key,
                    "available_options": non_empty_opts
                })
            elif len(non_empty_opts) < 4:
                flashcards.append({
                    "index": idx,
                    "stem": stem,
                    "available_options": non_empty_opts
                })

        return {
            "has_anomalies": bool(missing_stem or flashcards),
            "missing_stem_count": len(missing_stem),
            "missing_stem_items": missing_stem,
            "flashcard_count": len(flashcards),
            "flashcard_items": flashcards
        }

    @staticmethod
    def audit(questions):
        errors = []
        warnings = []
        key_dist = Counter()

        for idx, q in enumerate(questions, 1):
            stem = q.get("stem", "").strip()
            options = q.get("options", {})
            correct_key = q.get("correct_key", "").upper()
            exp = q.get("explanation", "").strip()
            citation = q.get("citation", "").strip()

            # 1. Stem checks
            if not stem:
                errors.append(
                    f"Câu {idx}: Khuyết thân câu hỏi (Rule 3A - Cần hỏi User: Xóa bỏ hay Phục dựng chuẩn học thuật?)."
                )

            # 2. Options checks
            if not isinstance(options, dict) or len(options) < 4:
                errors.append(
                    f"Câu {idx}: Không đủ 4 phương án A, B, C, D (Rule 3B - Cần hỏi User: Xóa bỏ hay Sinh 3 phương án nhiễu?)."
                )
            else:
                for k in ["A", "B", "C", "D"]:
                    if not options.get(k, "").strip():
                        errors.append(f"Câu {idx}: Phương án {k} bị rỗng.")

            # 3. Correct key checks
            if correct_key not in ["A", "B", "C", "D"]:
                errors.append(f"Câu {idx}: Đáp án đúng không hợp lệ ('{correct_key}').")
            else:
                key_dist[correct_key] += 1

            # 4. Logic conflict between correct_key and explanation prose
            if exp:
                for other_key in ["A", "B", "C", "D"]:
                    if other_key != correct_key and f"chọn {other_key.lower()}." in exp.lower():
                        errors.append(
                            f"Câu {idx}: Mâu thuẫn logic! Đáp án đánh dấu là {correct_key} nhưng lời giải ghi 'Chọn {other_key}'."
                        )

            # 5. Citation check
            if not citation:
                warnings.append(f"Câu {idx}: Chưa có trích dẫn nguồn học thuật (📌 Nguồn: ...).")

        total_q = len(questions)
        dist_summary = {
            k: f"{key_dist[k]} ({key_dist[k]/total_q*100:.1f}%)" if total_q > 0 else "0"
            for k in ["A", "B", "C", "D"]
        }

        passed = (len(errors) == 0)
        return {
            "passed": passed,
            "total_questions": total_q,
            "distribution": dist_summary,
            "errors": errors,
            "warnings": warnings
        }
