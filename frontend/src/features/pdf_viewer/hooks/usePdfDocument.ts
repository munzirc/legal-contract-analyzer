import { useEffect, useState } from "react";
import type { PDFDocumentProxy } from "pdfjs-dist";

import { pdfjsLib } from "../pdfjs";
import { getDocumentPdfUrl } from "../api";

interface UsePdfDocumentReturn {
  pdfDocument: PDFDocumentProxy | null;
  loading: boolean;
  error: string | null;
}

export function usePdfDocument(
  documentId: string | null
): UsePdfDocumentReturn {
  const [pdfDocument, setPdfDocument] =
    useState<PDFDocumentProxy | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!documentId) {
      setPdfDocument(null);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    const loadingTask = pdfjsLib.getDocument({
      url: getDocumentPdfUrl(documentId),
      disableRange: false,
      disableStream: true,
      disableAutoFetch: true,
    });

    setPdfDocument(null);
    setLoading(true);
    setError(null);

    loadingTask.promise
      .then((document) => {
        if (!cancelled) {
          setPdfDocument(document);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load PDF."
          );
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
      void loadingTask.destroy();
    };
  }, [documentId]);

  return {
    pdfDocument,
    loading,
    error,
  };
}