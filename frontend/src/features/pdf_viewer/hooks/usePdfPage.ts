import { useEffect, useState } from "react";
import type { PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";

export function usePdfPage(
  document: PDFDocumentProxy | null,
  pageNumber: number
) {
  const [page, setPage] = useState<PDFPageProxy | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!document) {
      setPage(null);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    setPage(null);
    setLoading(true);
    setError(null);

    document
      .getPage(pageNumber)
      .then((loadedPage) => {
        if (!cancelled) {
          setPage(loadedPage);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load PDF page."
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
    };
  }, [document, pageNumber]);

  return { page, loading, error };
}