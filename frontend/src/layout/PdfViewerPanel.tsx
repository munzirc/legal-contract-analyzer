
import { useEffect, useState } from "react";
import {
  LuFileText,
  LuMaximize2,
  LuMinus,
  LuPlus,
} from "react-icons/lu";

import { useAppStore } from "../stores/useAppStore";
import { useDocumentStore } from "../stores/useDocumentStore";
import { usePdfDocument } from "../features/pdf_viewer/hooks/usePdfDocument";
import PdfDocument from "../features/pdf_viewer/components/PdfDocument";

export default function PdfViewerPanel() {
  const [zoom, setZoom] = useState(1);

  const activeDocumentId = useAppStore(
    (state) => state.activeDocumentId
  );

  const activeDocument = useDocumentStore((state) =>
    state.documents.find(
      (document) => document.id === activeDocumentId
    )
  );

  const { pdfDocument, loading, error } =
    usePdfDocument(activeDocumentId);

  const zoomIn = () => {
    setZoom((current) => Math.min(current + 0.2, 3));
  };

  const zoomOut = () => {
    setZoom((current) => Math.max(current - 0.2, 0.4));
  };

  const resetZoom = () => {
    setZoom(1);
  };

  useEffect(() => {
    setZoom(1);
  }, [activeDocumentId]);


  return (
    <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white">
      <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b border-slate-200 px-4">
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <LuFileText
            size={18}
            className="shrink-0 text-brand-600"
          />

          <div className="min-w-0">
            <h1
              className="truncate text-sm font-semibold text-slate-900"
              title={activeDocument?.filename ?? "PDF viewer"}
            >
              {activeDocument?.filename ?? "PDF viewer"}
            </h1>

            {pdfDocument && (
              <p className="text-xs text-slate-500">
                {pdfDocument.numPages} pages
              </p>
            )}
          </div>
        </div>

        {pdfDocument && !loading && !error && (
          <div className="flex shrink-0 items-center gap-1">
            <button
              type="button"
              onClick={zoomOut}
              disabled={zoom <= 0.4}
              title="Zoom out"
              className="rounded-md p-2 text-slate-600 transition hover:bg-brand-50 hover:text-brand-600 disabled:opacity-40"
            >
              <LuMinus size={16} />
            </button>

            <span className="w-12 text-center text-xs font-medium tabular-nums text-slate-600">
              {Math.round(zoom * 100)}%
            </span>

            <button
              type="button"
              onClick={zoomIn}
              disabled={zoom >= 3}
              title="Zoom in"
              className="rounded-md p-2 text-slate-600 transition hover:bg-brand-50 hover:text-brand-600 disabled:opacity-40"
            >
              <LuPlus size={16} />
            </button>

            <button
              type="button"
              onClick={resetZoom}
              title="Fit page"
              className="rounded-md p-2 text-slate-600 transition hover:bg-brand-50 hover:text-brand-600"
            >
              <LuMaximize2 size={16} />
            </button>
          </div>
        )}
      </header>

      <div className="min-h-0 flex-1 overflow-hidden">
        {!activeDocumentId && (
          <div className="flex h-full items-center justify-center p-6">
            <div className="max-w-xs text-center">
              <LuFileText
                size={38}
                strokeWidth={1.3}
                className="mx-auto mb-3 text-slate-300"
              />

              <p className="text-sm font-medium text-slate-900">
                Your document will appear here
              </p>

              <p className="mt-1 text-sm leading-5 text-slate-500">
                Select a document to read and review its citations.
              </p>
            </div>
          </div>
        )}

        {activeDocumentId && loading && (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-slate-500">
              Loading PDF...
            </p>
          </div>
        )}

        {activeDocumentId && error && (
          <div className="flex h-full items-center justify-center p-6">
            <p className="max-w-md text-center text-sm text-red-600">
              {error}
            </p>
          </div>
        )}

        {pdfDocument && !loading && !error && (
          <PdfDocument
            document={pdfDocument}
            zoom={zoom}
          />
        )}
      </div>
    </section>
  );

}
