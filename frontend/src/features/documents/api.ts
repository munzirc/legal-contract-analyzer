import type { Document, UploadedDocument } from "./types";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? ""
).replace(/\/$/, "");

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = "Something went wrong.";

    try {
      const error = await response.json();
      message = error.detail ?? message;
    } catch {
      // Use the default error message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents`);
  return handleResponse<Document[]>(response);
}

export async function uploadDocument(
  file: File
): Promise<UploadedDocument> {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    throw new Error("Only PDF files are supported.");
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  return handleResponse<UploadedDocument>(response);
}

export async function deleteDocument(
  documentId: string
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/documents/${documentId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    let message = "Failed to delete document.";

    try {
      const error = await response.json();
      message = error.message ?? error.detail ?? message;
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }
}