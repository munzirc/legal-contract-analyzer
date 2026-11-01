export type DocumentStatus =
  | "UPLOADED"
  | "EXTRACTING"
  | "EXTRACTION_FAILED"
  | "VALIDATING"
  | "STRUCTURE_DETECTION_FAILED"
  | "CHUNKING"
  | "CHUNKING_FAILED"
  | "EMBEDDING_PIECES"
  | "EMBEDDING_PIECES_FAILED"
  | "EMBEDDING"
  | "EMBEDDING_FAILED"
  | "READY"
  | "REJECTED"
  | "FAILED";

export interface Document {
  id: string;
  filename: string;
  file_type: "pdf";
  status: DocumentStatus;
  page_count: number;
  created_at: string;
}

export interface UploadedDocument {
  id: string;
  filename: string;
  file_type: "pdf";
  status: DocumentStatus;
}

export type DocumentProgressStatus =
  | "processing"
  | "ready"
  | "rejected"
  | "failed"
  | "waiting_retry"
  | "queued";

export type DocumentProgressStage =
  | "preparing"
  | "ready"
  | "finished"
  | "waiting"
  | "extracting"
  | "analyzing"
  | "retrying"
  | "organizing"
  | "processing";

export interface DocumentProgress {
  document_id: string;
  document_status: DocumentStatus;
  status: DocumentProgressStatus;
  stage: DocumentProgressStage;
  message: string;
  is_currently_processing: boolean;
}