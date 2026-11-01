import os
import logging
import uuid

from app.db.database import SessionLocal
from sqlalchemy import select
from app.enums.document_status import DocumentStatus
from app.models.document_model import Document

from app.models.document_page import DocumentPage
from app.services.document_service.extraction_service.structure_builder.canonical_text_builder import (
    PageTextRange,
)

from app.models.document_chunk_model import DocumentChunk
from app.models.chunk_embedding import ChunkEmbedding, EmbeddingStatus
from app.enums.processing_stage import ProcessingStage
from app.services.document_service.document_processing.processing_errors import (
    ExtractionStageError,
    StructureDetectionStageError,
    ChunkingStageError,
    EmbeddingPieceStageError,
    EmbeddingStageError
)
from app.services.document_service.document_processing.run_embedding_stage import (
    run_embedding_stage,
)
from app.services.document_service.section_based_chunks.chunking.save_chunks import (
    save_chunks,
)
from app.services.document_service.document_processing.run_chunking_stage import (
    run_chunking_stage,
)
from app.services.document_service.document_processing.run_extraction_stage import (
    run_extraction_stage,
)
from app.services.document_service.document_processing.run_structure_detection_stage import (
    run_structure_detection_stage
)

from app.services.document_service.document_processing.run_embedding_piece_stage import (
    run_embedding_piece_stage,
)

from app.services.document_service.section_based_chunks.chunking.status import (
    update_document_status,
)



logger = logging.getLogger(__name__)


def _set_document_status(
    document_id: uuid.UUID,
    status: DocumentStatus,
) -> None:
    """Update document status in its own transaction."""
    with SessionLocal() as db:
        with db.begin():
            update_document_status(db, document_id, status)


def _record_stage_failure(
    document_id: uuid.UUID,
    status: DocumentStatus,
    error: Exception,
) -> None:
    """Persist a failure status after the stage transaction has rolled back."""
    try:
        _set_document_status(document_id, status)
    except Exception:
        logger.exception(
            "Could not record failure status %s for document %s",
            status.value,
            document_id,
        )

    logger.error(
        "Document %s failed during processing.",
        document_id,
        exc_info=(type(error), error, error.__traceback__),
    )


def process_document(document_id: uuid.UUID) -> bool:
    # Read the initial state.
    with SessionLocal() as db:
        document = db.get(Document, document_id)

        if document is None:
            logger.error("Document not found: %s", document_id)
            return False

        status = document.status

    if status == DocumentStatus.READY:
        logger.info("Document %s is already ready.", document_id)
        return True

    # ---------------------------------------------------------
    # Stage 1: Extraction
    # ---------------------------------------------------------
    extraction_statuses = {
        DocumentStatus.UPLOADED,
        DocumentStatus.EXTRACTING,
        DocumentStatus.EXTRACTION_FAILED,
    }

    if status in extraction_statuses:
        try:
            # Persist the in-progress status before starting extraction.
            _set_document_status(
                document_id,
                DocumentStatus.EXTRACTING,
            )

            # Extraction, canonical text, page ranges and next status
            # are committed atomically.
            with SessionLocal() as db:
                with db.begin():
                    run_extraction_stage(
                        db=db,
                        document_id=document_id,
                    )

                    update_document_status(
                        db,
                        document_id,
                        DocumentStatus.VALIDATING,
                    )

            status = DocumentStatus.VALIDATING

            logger.info(
                "Extraction completed for document %s.",
                document_id,
            )

        except Exception as error:
            _record_stage_failure(
                document_id,
                DocumentStatus.EXTRACTION_FAILED,
                error,
            )

            raise ExtractionStageError(
                stage=ProcessingStage.EXTRACTION,
                message=str(error),
            ) from error

    
    # ---------------------------------------------------------
    # Stage 2: Structure detection and validation
    # ---------------------------------------------------------
    structure_statuses = {
        DocumentStatus.VALIDATING,
        DocumentStatus.STRUCTURE_DETECTION_FAILED,
    }

    if status in structure_statuses:
        try:
            _set_document_status(
                document_id,
                DocumentStatus.VALIDATING,
            )

            # Read persisted inputs using a short-lived session.
            with SessionLocal() as db:
                document = db.get(Document, document_id)

                if document is None:
                    raise ValueError(
                        f"Document not found: {document_id}"
                    )

                canonical_text = document.canonical_text
                existing_structure = document.validated_structure

            if not canonical_text or not canonical_text.strip():
                raise ValueError(
                    "Canonical text is missing; extraction must run first."
                )

            # Only call the detector if structure has not been persisted.
            if existing_structure is None:
                serialized_structure = run_structure_detection_stage(
                    canonical_text
                )

                # Persist structure and next status atomically.
                with SessionLocal() as db:
                    with db.begin():
                        document = db.get(Document, document_id)

                        if document is None:
                            raise ValueError(
                                f"Document not found: {document_id}"
                            )

                        document.validated_structure = serialized_structure

                        update_document_status(
                            db,
                            document_id,
                            DocumentStatus.CHUNKING,
                        )
            else:
                # An empty list is valid and must not trigger detection again.
                _set_document_status(
                    document_id,
                    DocumentStatus.CHUNKING,
                )

            status = DocumentStatus.CHUNKING

            logger.info(
                "Structure processing completed for document %s.",
                document_id,
            )

        except Exception as error:
            _record_stage_failure(
                document_id,
                DocumentStatus.STRUCTURE_DETECTION_FAILED,
                error,
            )

            raise StructureDetectionStageError(
                stage=ProcessingStage.STRUCTURE_DETECTION,
                message=str(error),
            ) from error


    
    # ---------------------------------------------------------
    # Stage 3: Chunking
    # ---------------------------------------------------------
    chunking_statuses = {
        DocumentStatus.CHUNKING,
        DocumentStatus.CHUNKING_FAILED,
    }

    if status in chunking_statuses:
        try:
            _set_document_status(
                document_id,
                DocumentStatus.CHUNKING,
            )

            # Load persisted inputs using a short-lived session.
            with SessionLocal() as db:
                document = db.get(Document, document_id)

                if document is None:
                    raise ValueError(
                        f"Document not found: {document_id}"
                    )

                canonical_text = document.canonical_text
                stored_structure = document.validated_structure

                pages = db.scalars(
                    select(DocumentPage)
                    .where(
                        DocumentPage.document_id == document_id
                    )
                    .order_by(DocumentPage.page_number)
                ).all()

                page_ranges = [
                    PageTextRange(
                        page_number=page.page_number,
                        start_offset=page.start_offset,
                        end_offset=page.end_offset,
                    )
                    for page in pages
                ]

            # Build chunks after closing the read session.
            chunks = run_chunking_stage(
                canonical_text=canonical_text,
                stored_structure=stored_structure,
                page_ranges=page_ranges,
            )

            # Replace chunks and advance the status atomically.
            with SessionLocal() as db:
                with db.begin():
                    save_chunks(
                        db=db,
                        document_id=document_id,
                        chunks=chunks,
                    )

                    update_document_status(
                        db,
                        document_id,
                        DocumentStatus.EMBEDDING_PIECES,
                    )

            status = DocumentStatus.EMBEDDING_PIECES

            logger.info(
                "Chunking completed for document %s: %s chunks.",
                document_id,
                len(chunks),
            )
            

        except Exception as error:
            _record_stage_failure(
                document_id,
                DocumentStatus.CHUNKING_FAILED,
                error,
            )

            raise ChunkingStageError(
                stage=ProcessingStage.CHUNKING,
                message=str(error),
            ) from error
        
        # TEST ONLY: This is deliberately outside the chunking try/except.
        raise_document_id = os.environ.get(
            "JURIQA_TEST_EXCEPTION_AFTER_CHUNKING_DOCUMENT_ID"
        )

        if raise_document_id == str(document_id):
            logger.error(
                "TEST EXCEPTION: Raising an exception after chunking "
                "for document %s.",
                document_id,
            )
            raise RuntimeError(
                f"Test exception after chunking for document {document_id}"
            )
    
    # ---------------------------------------------------------
    # Stage 4: Embedding-piece creation
    # ---------------------------------------------------------
    embedding_piece_statuses = {
        DocumentStatus.EMBEDDING_PIECES,
        DocumentStatus.EMBEDDING_PIECES_FAILED,
    }

    if status in embedding_piece_statuses:
        try:
            _set_document_status(
                document_id,
                DocumentStatus.EMBEDDING_PIECES,
            )

            with SessionLocal() as db:
                with db.begin():
                    piece_count = run_embedding_piece_stage(
                        db=db,
                        document_id=document_id,
                    )

                    # Piece creation and the next status are atomic.
                    update_document_status(
                        db,
                        document_id,
                        DocumentStatus.EMBEDDING,
                    )

            status = DocumentStatus.EMBEDDING

            logger.info(
                "Created %s embedding pieces for document %s.",
                piece_count,
                document_id,
            )

        except Exception as error:
            _record_stage_failure(
                document_id,
                DocumentStatus.EMBEDDING_PIECES_FAILED,
                error,
            )
            raise EmbeddingPieceStageError(
                stage=ProcessingStage.EMBEDDING_PIECES,
                message=str(error)
            ) from error

    
    # ---------------------------------------------------------
    # Stage 5: Generate and save embeddings
    # ---------------------------------------------------------
    embedding_statuses = {
        DocumentStatus.EMBEDDING,
        DocumentStatus.EMBEDDING_FAILED,
    }

    if status in embedding_statuses:
        try:
            # Persist the in-progress status before starting.
            _set_document_status(
                document_id,
                DocumentStatus.EMBEDDING,
            )

            # Generate and save each vector independently.
            with SessionLocal() as db:
                completed_count = run_embedding_stage(
                    db=db,
                    document_id=document_id,
                )

            # Verify every piece is completed and has a vector.
            with SessionLocal() as db:
                pieces = db.execute(
                    select(
                        ChunkEmbedding.status,
                        ChunkEmbedding.embedding,
                    )
                    .join(
                        DocumentChunk,
                        DocumentChunk.id == ChunkEmbedding.chunk_id,
                    )
                    .where(
                        DocumentChunk.document_id == document_id,
                    )
                ).all()

            if not pieces:
                raise ValueError(
                    "No embedding pieces found for this document."
                )

            incomplete_count = sum(
                1
                for piece in pieces
                if (
                    piece.status != EmbeddingStatus.COMPLETED
                    or piece.embedding is None
                )
            )

            if incomplete_count:
                raise RuntimeError(
                    f"Document still has {incomplete_count} "
                    "incomplete embedding pieces."
                )

            # The document is ready only after verification succeeds.
            _set_document_status(
                document_id,
                DocumentStatus.READY,
            )

            status = DocumentStatus.READY

            logger.info(
                "Embedding processing completed for document %s. "
                "%s new pieces completed.",
                document_id,
                completed_count,
            )

        except Exception as error:
            _record_stage_failure(
                document_id,
                DocumentStatus.EMBEDDING_FAILED,
                error,
            )
            raise EmbeddingStageError(
                stage=ProcessingStage.EMBEDDING,
                message=str(error)
            ) from error


    logger.info(
        "Document %s reached status %s.",
        document_id,
        status.value,
    )
    
    return True

    
