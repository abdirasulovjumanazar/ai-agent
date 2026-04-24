from app.db.ddl import get_cache, schema_to_str
from app.logger import get_logger

log = get_logger("reducer")


def _question_matches_table(question: str, table: str, columns: list[str]) -> bool:
    q = question.lower()
    # Table nomini tekshir
    if table.lower().rstrip("s") in q or table.lower() in q:
        return True
    # Column nomlarini tekshir
    for col_info in columns:
        col_name = col_info.split(" (")[0].lower()
        if len(col_name) > 3 and col_name in q:
            return True
    return False


def reduce_schema(question: str) -> str:
    """Savol uchun faqat tegishli jadvallarni qaytaradi."""
    cache = get_cache()
    matched = {
        table: cols
        for table, cols in cache.items()
        if _question_matches_table(question, table, cols)
    }

    # Agar hech narsa topilmasa — to'liq schemani ber
    if not matched:
        log.info(f"reducer: no match — using full schema ({len(cache)} tables)")
        return schema_to_str(cache)

    matched = _expand_with_related(matched, cache)

    log.info(f"reducer: {list(matched.keys())} / {list(cache.keys())}")
    return schema_to_str(matched)


def _expand_with_related(matched: dict, cache: dict) -> dict:
    """FK graf bo'ylab iterativ kengaytiradi (forward + reverse)."""
    expanded = dict(matched)
    prev_size = 0

    while prev_size != len(expanded):
        prev_size = len(expanded)

        # Reverse FK: boshqa jadvallar expanded jadvalga ishora qilsa qo'sh
        for table, cols in cache.items():
            if table in expanded:
                continue
            for col_info in cols:
                col_name = col_info.split(" (")[0].lower()
                if not col_name.endswith("_id"):
                    continue
                referenced = col_name[:-3]
                for exp_table in list(expanded):
                    if exp_table.lower().rstrip("s") == referenced:
                        expanded[table] = cache[table]
                        break

        # Forward FK: expanded jadvalning _id ustunlari orqali referenced jadvallarni qo'sh
        for cols in list(expanded.values()):
            for col_info in cols:
                col_name = col_info.split(" (")[0].lower()
                if col_name.endswith("_id"):
                    related = col_name[:-3]
                    for table in cache:
                        if table.lower().rstrip("s") == related and table not in expanded:
                            expanded[table] = cache[table]

    return expanded
