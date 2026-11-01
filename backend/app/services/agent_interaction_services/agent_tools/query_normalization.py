import re
import unicodedata


def normalize_search_query(query: str) -> str:
    """Normalize query formatting without changing its meaning."""
    query = unicodedata.normalize("NFKC", query)

    # Normalize common Unicode punctuation.
    query = (
        query
        .replace("\u2013", "-")  # en dash
        .replace("\u2014", "-")  # em dash
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )

    # Collapse repeated whitespace.
    query = re.sub(r"\s+", " ", query).strip()

    # Remove accidental quotation marks around the entire query.
    query = query.strip("\"'").strip()

    return query


def normalize_search_queries(queries: list[str]) -> list[str]:
    """Normalize queries and remove formatting-equivalent duplicates."""
    normalized : list[str] = []
    seen : set[str] = set()

    for query in queries:
        query = normalize_search_query(query)

        if query and query.casefold() not in seen:
            seen.add(query.casefold())
            normalized.append(query)

    return normalized