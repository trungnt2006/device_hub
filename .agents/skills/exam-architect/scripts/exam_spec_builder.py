import json
import math

def allocate_matrix_2d(total_questions, chapter_weights, bloom_weights):
    """
    Allocates an exact 2D matrix (Chapters x Bloom Levels) using the 
    Constrained Largest Remainder Method (Hamilton-Hare method extended to 2D),
    ensuring all row sums and column sums strictly equal the integer targets.
    """
    chapters = list(chapter_weights.keys())
    blooms = list(bloom_weights.keys())
    
    # 1. Allocate Chapter totals (Rows)
    total_ch_w = sum(chapter_weights.values())
    exact_ch = {c: (w / total_ch_w) * total_questions for c, w in chapter_weights.items()}
    floor_ch = {c: int(math.floor(exact_ch[c])) for c in chapters}
    rem_ch = sorted(chapters, key=lambda c: exact_ch[c] - floor_ch[c], reverse=True)
    ch_diff = total_questions - sum(floor_ch.values())
    for i in range(ch_diff):
        floor_ch[rem_ch[i]] += 1
    row_targets = floor_ch
    
    # 2. Allocate Bloom totals (Columns)
    total_bl_w = sum(bloom_weights.values())
    exact_bl = {b: (w / total_bl_w) * total_questions for b, w in bloom_weights.items()}
    floor_bl = {b: int(math.floor(exact_bl[b])) for b in blooms}
    rem_bl = sorted(blooms, key=lambda b: exact_bl[b] - floor_bl[b], reverse=True)
    bl_diff = total_questions - sum(floor_bl.values())
    for i in range(bl_diff):
        floor_bl[rem_bl[i]] += 1
    col_targets = floor_bl
    
    # 3. Compute 2D continuous weights: w_ij = (row_target_i / total) * (col_target_j / total) * total
    matrix = {c: {b: 0 for b in blooms} for c in chapters}
    remainders = []
    
    curr_row_sums = {c: 0 for c in chapters}
    curr_col_sums = {b: 0 for b in blooms}
    
    for c in chapters:
        for b in blooms:
            exact_val = (row_targets[c] * col_targets[b]) / total_questions
            int_val = int(math.floor(exact_val))
            matrix[c][b] = int_val
            curr_row_sums[c] += int_val
            curr_col_sums[b] += int_val
            remainders.append((c, b, exact_val - int_val))
            
    # Sort cells by descending fractional remainder
    remainders.sort(key=lambda x: x[2], reverse=True)
    
    # Distribute remaining points while respecting row and column targets
    for c, b, rem in remainders:
        if curr_row_sums[c] < row_targets[c] and curr_col_sums[b] < col_targets[b]:
            matrix[c][b] += 1
            curr_row_sums[c] += 1
            curr_col_sums[b] += 1
            
    # Clean up any leftover discrepancy
    for c in chapters:
        while curr_row_sums[c] < row_targets[c]:
            # find col with capacity
            for b in blooms:
                if curr_col_sums[b] < col_targets[b]:
                    matrix[c][b] += 1
                    curr_row_sums[c] += 1
                    curr_col_sums[b] += 1
                    break
            else:
                # col full, add to highest weight bloom
                best_b = max(blooms, key=lambda b: col_targets[b])
                matrix[c][best_b] += 1
                curr_row_sums[c] += 1
                curr_col_sums[best_b] += 1
                
    return {
        "total_questions": total_questions,
        "row_targets": row_targets,
        "col_targets": col_targets,
        "matrix_2d": matrix
    }

def create_exam_spec(subject_name, subject_code, source_status, question_count, duration_minutes, chapter_weights, bloom_weights, references, output_path):
    allocation = allocate_matrix_2d(question_count, chapter_weights, bloom_weights)
    
    spec = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "spec_version": "3.0",
        "subject_metadata": {
            "name": subject_name,
            "code": subject_code,
            "institution": "Banking University of Ho Chi Minh City (HUB)",
            "source_status": source_status # "verified" | "inferred" | "user_defined"
        },
        "exam_parameters": {
            "type": "multiple_choice",
            "question_count": question_count,
            "duration_minutes": duration_minutes,
            "options_per_question": 4,
            "answer_distribution_mode": "approximately_balanced", # target ~25% with tolerance +/- 2
            "max_consecutive_same_answers": 2 # Flag if >= 3 consecutive same answers
        },
        "bloom_distribution": allocation["col_targets"],
        "chapter_distribution": allocation["row_targets"],
        "matrix_2d_chapter_x_bloom": allocation["matrix_2d"],
        "source_references": references,
        "validation_flags": {
            "require_citations": True,
            "require_independent_verification": True,
            "require_audit_report": True
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
        
    return spec
