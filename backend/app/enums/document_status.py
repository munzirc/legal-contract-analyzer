from enum import Enum


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    EXTRACTING = "EXTRACTING"
    VALIDATING = "VALIDATING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    READY = "READY"
    REJECTED = "REJECTED"
    FAILED = "FAILED"