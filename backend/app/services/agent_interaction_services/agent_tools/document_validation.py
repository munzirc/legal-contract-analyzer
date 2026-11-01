from uuid import UUID


def validate_document_ids(
    requested_ids: list[str],
    authorized_ids: set[UUID],
) -> tuple[list[UUID] | None, str | None]:
    """
    Validate UUIDs and ensure every requested document is authorized.

    Returns:
        (parsed_ids, None) on success.
        (None, error_code) on failure.
    """

    if (
        not isinstance(requested_ids, list)
        or not requested_ids
        or not all(isinstance(item, str) and item.strip() for item in requested_ids)
    ):
        return None, "INVALID_DOCUMENT_IDS"

    try:
        parsed_ids = list(dict.fromkeys(
            UUID(item.strip()) for item in requested_ids
        ))
    except (ValueError, AttributeError, TypeError):
        return None, "INVALID_DOCUMENT_IDS"

    if any(doc_id not in authorized_ids for doc_id in parsed_ids):
        return None, "UNAUTHORIZED_DOCUMENT"

    return parsed_ids, None