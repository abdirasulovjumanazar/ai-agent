from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.engine import Connection
from app.logger import get_logger

log = get_logger("chunker")


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict


# ── helpers ────────────────────────────────────────────────────────────────

def _v(val, default: str = "—") -> str:
    return str(val) if val is not None else default


def _join(items: list[str], sep: str = ", ") -> str:
    return sep.join(items) if items else "—"


# ── student chunks ─────────────────────────────────────────────────────────

def _student_chunks(conn: Connection) -> list[Chunk]:
    students = conn.execute(text(
        "SELECT id, name, email, age, gpa, phone, address, enrolled_at::text FROM students"
    )).mappings().fetchall()

    chunks = []
    for s in students:
        sid = s["id"]

        enrollments = conn.execute(text("""
            SELECT c.title, e.grade, e.status
            FROM enrollments e JOIN courses c ON c.id = e.course_id
            WHERE e.student_id = :sid
        """), {"sid": sid}).mappings().fetchall()

        grades = conn.execute(text("""
            SELECT c.title, g.grade_type, g.grade
            FROM grades g JOIN courses c ON c.id = g.course_id
            WHERE g.student_id = :sid
            ORDER BY c.title, g.grade_type
        """), {"sid": sid}).mappings().fetchall()

        payments = conn.execute(text(
            "SELECT amount, status, paid_at::text FROM payments WHERE student_id = :sid"
        ), {"sid": sid}).mappings().fetchall()

        att = conn.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'present') AS present,
                COUNT(*) FILTER (WHERE status = 'absent')  AS absent,
                COUNT(*) FILTER (WHERE status = 'late')    AS late,
                COUNT(*)                                   AS total
            FROM attendance WHERE student_id = :sid
        """), {"sid": sid}).mappings().fetchone()

        parents = conn.execute(text(
            "SELECT name, relation, phone FROM parents WHERE student_id = :sid"
        ), {"sid": sid}).mappings().fetchall()

        parts = [
            f"Talaba: {s['name']}.",
            f"Email: {_v(s['email'])}.",
            f"Yoshi: {_v(s['age'])}.",
            f"GPA: {_v(s['gpa'])}.",
            f"Telefon: {_v(s['phone'])}.",
            f"Manzil: {_v(s['address'])}.",
            f"Ro'yxatga olingan: {_v(s['enrolled_at'])}.",
        ]

        if enrollments:
            items = [
                f"{e['title']} (status:{_v(e['status'])}, baho:{_v(e['grade'])})"
                for e in enrollments
            ]
            parts.append(f"Yozilgan kurslar ({len(enrollments)} ta): {_join(items)}.")

        if grades:
            items = [
                f"{g['title']}-{g['grade_type']}:{_v(g['grade'])}"
                for g in grades
            ]
            parts.append(f"Baholar: {_join(items)}.")

        if payments:
            items = [
                f"{p['amount']}$ ({p['status']}, {_v(p['paid_at'])})"
                for p in payments
            ]
            parts.append(f"To'lovlar: {_join(items)}.")

        if att and att["total"]:
            parts.append(
                f"Davomat: {att['present']}/{att['total']} dars "
                f"(kelmagan:{att['absent']}, kechikkan:{att['late']})."
            )

        if parents:
            items = [f"{p['name']} ({p['relation']}, {p['phone']})" for p in parents]
            parts.append(f"Ota-ona: {_join(items)}.")

        chunks.append(Chunk(
            id=f"student_{sid}",
            text=" ".join(parts),
            metadata={"type": "student", "name": s["name"], "entity_id": str(sid)},
        ))

    log.info(f"chunker: {len(chunks)} student chunks")
    return chunks


# ── course chunks ──────────────────────────────────────────────────────────

def _course_chunks(conn: Connection) -> list[Chunk]:
    courses = conn.execute(text("""
        SELECT c.id, c.title, c.credits, c.description,
               c.start_date::text, c.end_date::text, c.max_students,
               t.name AS teacher_name
        FROM courses c LEFT JOIN teachers t ON t.id = c.teacher_id
    """)).mappings().fetchall()

    chunks = []
    for c in courses:
        cid = c["id"]

        students = conn.execute(text("""
            SELECT s.name, e.grade, e.status
            FROM enrollments e JOIN students s ON s.id = e.student_id
            WHERE e.course_id = :cid
            ORDER BY s.name
        """), {"cid": cid}).mappings().fetchall()

        avg = conn.execute(text("""
            SELECT ROUND(AVG(grade), 2) FROM grades
            WHERE course_id = :cid AND grade IS NOT NULL
        """), {"cid": cid}).scalar()

        att_pct = conn.execute(text("""
            SELECT ROUND(
                COUNT(*) FILTER (WHERE status='present') * 100.0
                / NULLIF(COUNT(*), 0), 1
            ) FROM attendance WHERE course_id = :cid
        """), {"cid": cid}).scalar()

        parts = [
            f"Kurs: {c['title']}.",
            f"O'qituvchi: {_v(c['teacher_name'])}.",
            f"Kreditlar: {_v(c['credits'])}.",
            f"Boshlanish: {_v(c['start_date'])}. Tugash: {_v(c['end_date'])}.",
            f"Maksimal talabalar: {_v(c['max_students'])}.",
        ]

        if c.get("description"):
            parts.append(f"Tavsif: {c['description']}.")

        if students:
            items = [
                f"{s['name']} ({s['status']}, baho:{_v(s['grade'])})"
                for s in students
            ]
            parts.append(f"Talabalar ({len(students)} ta): {_join(items)}.")

        if avg is not None:
            parts.append(f"O'rtacha baho: {avg}.")

        if att_pct is not None:
            parts.append(f"Davomat foizi: {att_pct}%.")

        chunks.append(Chunk(
            id=f"course_{cid}",
            text=" ".join(parts),
            metadata={"type": "course", "title": c["title"], "entity_id": str(cid)},
        ))

    log.info(f"chunker: {len(chunks)} course chunks")
    return chunks


# ── teacher chunks ─────────────────────────────────────────────────────────

def _teacher_chunks(conn: Connection) -> list[Chunk]:
    teachers = conn.execute(text(
        "SELECT id, name, email, subject, hired_at::text FROM teachers"
    )).mappings().fetchall()

    chunks = []
    for t in teachers:
        tid = t["id"]

        courses = conn.execute(text(
            "SELECT title, credits FROM courses WHERE teacher_id = :tid ORDER BY title"
        ), {"tid": tid}).mappings().fetchall()

        student_cnt = conn.execute(text("""
            SELECT COUNT(DISTINCT e.student_id)
            FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            WHERE c.teacher_id = :tid
        """), {"tid": tid}).scalar()

        parts = [
            f"O'qituvchi: {t['name']}.",
            f"Mutaxassislik: {_v(t['subject'])}.",
            f"Email: {_v(t['email'])}.",
            f"Ishga kirgan: {_v(t['hired_at'])}.",
        ]

        if courses:
            items = [f"{c['title']} ({c['credits']} kredit)" for c in courses]
            parts.append(f"O'qitadigan kurslar ({len(courses)} ta): {_join(items)}.")

        if student_cnt:
            parts.append(f"Jami o'quvchilar soni: {student_cnt} ta.")

        chunks.append(Chunk(
            id=f"teacher_{tid}",
            text=" ".join(parts),
            metadata={"type": "teacher", "name": t["name"], "entity_id": str(tid)},
        ))

    log.info(f"chunker: {len(chunks)} teacher chunks")
    return chunks


# ── summary chunks ─────────────────────────────────────────────────────────

def _summary_chunks(conn: Connection) -> list[Chunk]:
    s = conn.execute(text("""
        SELECT COUNT(*)                  AS total,
               ROUND(AVG(gpa), 2)        AS avg_gpa,
               MAX(gpa)                  AS max_gpa,
               MIN(gpa)                  AS min_gpa
        FROM students
    """)).mappings().fetchone()

    top = conn.execute(text("""
        SELECT name, gpa FROM students ORDER BY gpa DESC NULLS LAST LIMIT 3
    """)).mappings().fetchall()

    payments = conn.execute(text("""
        SELECT status, COUNT(*) AS cnt, COALESCE(SUM(amount), 0) AS total
        FROM payments GROUP BY status ORDER BY status
    """)).mappings().fetchall()

    att_pct = conn.execute(text("""
        SELECT ROUND(
            COUNT(*) FILTER (WHERE status='present') * 100.0
            / NULLIF(COUNT(*), 0), 1
        ) FROM attendance
    """)).scalar()

    course_cnt = conn.execute(text("SELECT COUNT(*) FROM courses")).scalar()
    teacher_cnt = conn.execute(text("SELECT COUNT(*) FROM teachers")).scalar()

    pay_lines = _join([
        f"{p['status']}: {p['cnt']} ta ({p['total']}$)" for p in payments
    ])
    top_students = _join([f"{t['name']} (GPA:{t['gpa']})" for t in top])

    text_body = (
        f"Maktab umumiy statistikasi. "
        f"Jami talabalar: {s['total']} ta. "
        f"O'rtacha GPA: {_v(s['avg_gpa'])}. "
        f"Eng yuqori GPA: {_v(s['max_gpa'])}. Eng past GPA: {_v(s['min_gpa'])}. "
        f"Top 3 talaba: {top_students}. "
        f"Jami kurslar: {course_cnt} ta. "
        f"Jami o'qituvchilar: {teacher_cnt} ta. "
        f"To'lovlar: {pay_lines}. "
        f"Umumiy davomat: {_v(att_pct)}%."
    )

    log.info("chunker: 1 summary chunk")
    return [Chunk(
        id="summary_school",
        text=text_body,
        metadata={"type": "summary"},
    )]


# ── public API ─────────────────────────────────────────────────────────────

def build_all_chunks(conn: Connection) -> list[Chunk]:
    """Barcha entity chunklarini qurib qaytaradi."""
    return (
        _student_chunks(conn)
        + _course_chunks(conn)
        + _teacher_chunks(conn)
        + _summary_chunks(conn)
    )
