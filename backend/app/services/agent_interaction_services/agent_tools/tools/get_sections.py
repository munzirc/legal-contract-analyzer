
from uuid import UUID

from sqlalchemy import (
    column,
    func,
    or_,
    select,
    true,
    literal,
    and_
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.elements import ColumnElement

from app.db.database import SessionLocal
from app.models.document_model import Document
from app.models.document_chunk_model import DocumentChunk
from app.schemas.sections_schema import (
    DocumentSectionsResult,
    MatchedSection,
)

def normalize_section_sql(expression):
    
    
    
    expression = func.replace(expression, r"\u2014", "-")
    expression = func.replace(expression, r"\u2013", "-")
    expression = func.replace(expression, r"\u2010", "-")
    expression = func.replace(expression, r"\u2011", "-")
    expression = func.replace(expression, r"\u2012", "-")
    expression = func.replace(expression, r"\u2212", "-")
    
    return func.regexp_replace(
        func.lower(func.coalesce(expression, "")),
        r"[^[:alnum:].]",
        "",
        "g",
    )


def normalize_identifier_sql(expression):
    """Standardize identifier punctuation for database comparison."""

    return func.lower(
        func.replace(
            func.replace(
                func.coalesce(expression, ""),
                "\u2014",
                "-",
            ),
            "\u2013",
            "-",
        )
    )


def normalize_title_sql(expression):
    """Remove punctuation and whitespace for title comparison."""

    return func.regexp_replace(
        func.lower(func.coalesce(expression, "")),
        r"[^[:alnum:]]",
        "",
        "g",
    )


def get_sections(
    document_id: UUID,
    section_queries: list[str],
) -> DocumentSectionsResult:

    with SessionLocal() as db:
        document = db.get(Document, document_id)

        if document is None:
            raise ValueError(f"Document not found: {document_id}")

        canonical_text = document.canonical_text or ""

        if not section_queries:
            return DocumentSectionsResult(
                document_id=str(document.id),
                filename=document.filename,
                sections=[],
            )

        matched_sections: list[MatchedSection] = []
        seen_matches: set[tuple[UUID, int, int]] = set()

        def add_match(
            chunk_id: UUID,
            level: str,
            identifier: str,
            title: str | None,
            start: int | None,
            end: int | None,
        ) -> None:

            if start is None or end is None:
                return

            if not (0 <= start < end <= len(canonical_text)):
                return

            match_key = (chunk_id, start, end)

            if match_key in seen_matches:
                return

            seen_matches.add(match_key)

            matched_sections.append(
                MatchedSection(
                    chunk_id=str(chunk_id),
                    level=level,
                    identifier=identifier,
                    title=title,
                    start_offset=start,
                    end_offset=end,
                    text=canonical_text[start:end],
                )
            )

        # --------------------------------------------------
        # 1. Match parent sections
        # --------------------------------------------------

        parent_conditions: list[ColumnElement[bool]] = []

        for query in section_queries:
            print("Original query:", query)
            print("Query representation:", repr(query))
            
            query_identifier = normalize_identifier_sql(
                literal(query)
            )

            query_title = normalize_title_sql(
                literal(query)
            )

            stored_identifier = normalize_identifier_sql(
                DocumentChunk.section_identifier
            )

            stored_title = normalize_title_sql(
                DocumentChunk.section_title
            )
            
            stored_combined = normalize_section_sql(
                func.concat(
                    DocumentChunk.section_identifier,
                    " ",
                    DocumentChunk.section_title,
                )
            )

            query_combined = normalize_section_sql(literal(query))

            parent_conditions.append(
                or_(
                    stored_identifier == query_identifier,
                    stored_title.contains(query_title),
                    and_(
                        func.length(query_combined) > 0,
                        stored_combined.contains(query_combined),
                    ),
                )
            )

        parent_statement = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                or_(*parent_conditions),
            )
            .order_by(DocumentChunk.chunk_index)
        )

        parent_chunks = (
            db.execute(parent_statement)
            .scalars()
            .all()
        )

        for chunk in parent_chunks:
            add_match(
                chunk_id=chunk.id,
                level="section",
                identifier=chunk.section_identifier,
                title=chunk.section_title,
                start=chunk.section_start_offset,
                end=chunk.section_end_offset,
            )

        # --------------------------------------------------
        # 2. Match subsections
        # --------------------------------------------------

        subsection = (
            func.jsonb_array_elements(DocumentChunk.subsections)
            .table_valued(column("value", JSONB))
            .lateral("subsection")
        )

        subsection_identifier = subsection.c.value["identifier"].astext
        subsection_title = subsection.c.value["title"].astext

        subsection_conditions: list[ColumnElement[bool]] = []

        for query in section_queries:
            query_identifier = normalize_identifier_sql(
                literal(query)
            )

            query_title = normalize_title_sql(
                literal(query)
            )

            stored_identifier = normalize_identifier_sql(
                subsection_identifier
            )

            stored_title = normalize_title_sql(
                subsection_title
            )
            
            stored_combined = normalize_section_sql(
                func.concat(
                    subsection_identifier,
                    " ",
                    subsection_title,
                )
            )

            query_combined = normalize_section_sql(literal(query))

            subsection_conditions.append(
                or_(
                    stored_identifier == query_identifier,
                    stored_title.contains(query_title),
                    and_(
                        func.length(query_combined) > 0,
                        stored_combined.contains(query_combined),
                    ),
                )
            )

        subsection_statement = (
            select(
                DocumentChunk.id,
                subsection.c.value,
            )
            .select_from(
                DocumentChunk
            )
            .join(
                subsection,
                true(),
            )
            .where(
                DocumentChunk.document_id == document_id,
                or_(*subsection_conditions),
            )
            .order_by(DocumentChunk.chunk_index)
        )

        subsection_rows = db.execute(
            subsection_statement
        ).all()

        for chunk_id, subsection_data in subsection_rows:
            add_match(
                chunk_id=chunk_id,
                level="subsection",
                identifier=subsection_data.get("identifier"),
                title=subsection_data.get("title"),
                start=subsection_data.get("start_offset"),
                end=subsection_data.get("end_offset"),
            )

        # Keep results in document order.
        matched_sections.sort(
            key=lambda section: section.start_offset
        )

        return DocumentSectionsResult(
            document_id=str(document.id),
            filename=document.filename,
            sections=matched_sections,
        )
