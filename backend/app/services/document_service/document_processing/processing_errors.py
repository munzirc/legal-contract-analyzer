from app.enums.processing_stage import ProcessingStage

class DocumentProcessingError(Exception):
    def __init__(
        self,
        stage: ProcessingStage,
        message: str,
    ) -> None:
        self.stage = stage
        self.message = message
        super().__init__(f"{stage.value}: {message}")


class ExtractionStageError(DocumentProcessingError):
    pass


class StructureDetectionStageError(DocumentProcessingError):
    pass


class ChunkingStageError(DocumentProcessingError):
    pass


class EmbeddingPieceStageError(DocumentProcessingError):
    pass


class EmbeddingStageError(DocumentProcessingError):
    pass