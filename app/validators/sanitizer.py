import re

import bleach


def sanitize_text(text: str) -> str:
    cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
    return cleaned.strip()


def contains_html(text: str) -> bool:
    return sanitize_text(text) != text.strip()


def contains_sql_patterns(text: str) -> bool:
    sql_patterns = [
        r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE)\b",
        r"(--|;|/\*|\*/)",
        r"\bOR\b\s+1\s*=\s*1\b",
        r"\bAND\b\s+1\s*=\s*1\b",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in sql_patterns)
