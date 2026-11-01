import { API_BASE_URL } from "./api";
import type { DocumentProgress } from "./types";
import { useDocumentStore } from "../../stores/useDocumentStore";

let eventSource: EventSource | null = null;

export function connectProgressStream(): void {
  // Reuse an existing connection if it is connecting or already open.
  if (
    eventSource &&
    eventSource.readyState !== EventSource.CLOSED
  ) {
    return;
  }

  eventSource = new EventSource(
    `${API_BASE_URL}/api/processing/progress`
  );

  eventSource.addEventListener("document_progress", (event) => {
    try {
      const progress = JSON.parse(
        (event as MessageEvent).data
      ) as DocumentProgress;

      useDocumentStore
        .getState()
        .setDocumentProgress(progress);
    } catch (error) {
      console.error("Failed to parse document progress event:", error);
    }
  });

  eventSource.addEventListener("queue_idle", () => {
    eventSource?.close();
    eventSource = null;
  });
}