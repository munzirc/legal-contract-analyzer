import { API_BASE_URL } from "../documents/api";

export function getDocumentPdfUrl(documentId: string): string {
  return `${API_BASE_URL}/api/pdf/${documentId}`;
}