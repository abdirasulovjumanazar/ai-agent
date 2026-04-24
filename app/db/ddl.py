SCHEMA: dict[str, list[str]] = {
    "students": [
        "id (integer)",
        "name (varchar)",
        "email (varchar)",
        "age (integer)",
        "enrolled_at (date)",
        "phone (varchar)",
        "address (text)",
        "gpa (numeric)",
    ],
    "teachers": [
        "id (integer)",
        "name (varchar)",
        "email (varchar)",
        "subject (varchar)",
        "hired_at (date)",
    ],
    "courses": [
        "id (integer)",
        "title (varchar)",
        "teacher_id (integer)",
        "credits (integer)",
        "description (text)",
        "start_date (date)",
        "end_date (date)",
        "max_students (integer)",
    ],
    "enrollments": [
        "id (integer)",
        "student_id (integer)",
        "course_id (integer)",
        "grade (numeric)",
        "enrolled_at (date)",
        "status (varchar)",
    ],
    "grades": [
        "id (integer)",
        "student_id (integer)",
        "course_id (integer)",
        "grade (numeric)",
        "grade_type (varchar)",
        "graded_at (date)",
    ],
    "parents": [
        "id (integer)",
        "name (varchar)",
        "phone (varchar)",
        "student_id (integer)",
        "relation (varchar)",
    ],
    "payments": [
        "id (integer)",
        "student_id (integer)",
        "amount (numeric)",
        "paid_at (timestamp)",
        "status (varchar)",
    ],
    "attendance": [
        "id (integer)",
        "student_id (integer)",
        "course_id (integer)",
        "date (date)",
        "status (varchar)",
    ],
}


def get_cache() -> dict[str, list[str]]:
    return SCHEMA


def schema_to_str(tables: dict[str, list[str]]) -> str:
    lines = []
    for table, cols in tables.items():
        lines.append(f"Table: {table}")
        for col in cols:
            lines.append(f"  - {col}")
    return "\n".join(lines)


def get_full_schema() -> str:
    return schema_to_str(SCHEMA)
