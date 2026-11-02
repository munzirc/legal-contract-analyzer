
import { useState } from "react";
import { toast } from "sonner";
import {
  LuChevronDown,
  LuChevronRight,
  LuFileText,
  LuTrash2,
  LuLoaderCircle,
} from "react-icons/lu";

import { useDocumentStore } from "../../../stores/useDocumentStore";
import { useAppStore } from "../../../stores/useAppStore";

import type { DocumentStatus } from "../../../features/documents/types";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const statusConfig: Record<
  DocumentStatus,
  { label: string; className: string }
> = {
  UPLOADED: { label: "Uploaded", className: "bg-blue-100 text-blue-700" },
  EXTRACTING: { label: "Extracting", className: "bg-blue-100 text-blue-700" },
  EXTRACTION_FAILED: { label: "Extraction failed", className: "bg-red-100 text-red-700" },
  VALIDATING: { label: "Analyzing", className: "bg-blue-100 text-blue-700" },
  STRUCTURE_DETECTION_FAILED: { label: "Analysis failed", className: "bg-red-100 text-red-700" },
  CHUNKING: { label: "Organizing", className: "bg-blue-100 text-blue-700" },
  CHUNKING_FAILED: { label: "Processing failed", className: "bg-red-100 text-red-700" },
  EMBEDDING_PIECES: { label: "Preparing", className: "bg-blue-100 text-blue-700" },
  EMBEDDING_PIECES_FAILED: { label: "Preparation failed", className: "bg-red-100 text-red-700" },
  EMBEDDING: { label: "Processing", className: "bg-blue-100 text-blue-700" },
  EMBEDDING_FAILED: { label: "Processing failed", className: "bg-red-100 text-red-700" },
  READY: { label: "Ready", className: "bg-green-100 text-green-700" },
  REJECTED: { label: "Rejected", className: "bg-red-100 text-red-700" },
  FAILED: { label: "Failed", className: "bg-red-100 text-red-700" },
};

export default function DocumentDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [documentToDelete, setDocumentToDelete] = useState<{
    id: string;
    filename: string;
  } | null>(null);

  const documents = useDocumentStore((state) => state.documents);
  const documentProgress = useDocumentStore(
    (state) => state.documentProgress
  );
  const isLoading = useDocumentStore(
    (state) => state.isLoadingDocuments
  );
  const deleteDocumentById = useDocumentStore(
    (state) => state.deleteDocumentById
  );

  const activeDocumentId = useAppStore(
    (state) => state.activeDocumentId
  );
  
  const setActiveDocument = useAppStore(
    (state) => state.setActiveDocument
  );

  const handleDelete = async () => {
    if (!documentToDelete) return;

    const { id } = documentToDelete;

    setDeletingId(id);

    try {
      await deleteDocumentById(id);

      toast.success("Document deleted successfully.");
      setDocumentToDelete(null);
    } catch (error: unknown) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to delete document."
      );
    } finally {
      setDeletingId(null);
    }
  };


  return (
    <section>
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="flex w-full items-center justify-between rounded-lg px-2 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        aria-expanded={isOpen}
      >
        <span className="flex items-center gap-2">
          <LuFileText size={17} />
          Documents
          <span className="text-xs font-normal text-slate-400">
            {documents.length}
          </span>
        </span>

        {isOpen ? (
          <LuChevronDown size={16} />
        ) : (
          <LuChevronRight size={16} />
        )}
      </button>

      {isLoading && documents.length === 0 && (
        <p className="px-2 py-3 text-xs text-slate-400">
          Loading documents...
        </p>
      )}

      {isOpen && (
        <div className="mt-1 max-h-48 space-y-2 overflow-y-auto pl-2 custom-scrollbar">
          
          {!isLoading && documents.length === 0 && (
            <p className="px-2 py-3 text-xs text-slate-400">
              No documents uploaded yet.
            </p>
          )}

          {documents.map((document) => {
            const progress = documentProgress[document.id];

            const currentStatus =
              progress?.document_status ?? document.status;

            const status = statusConfig[currentStatus];
            const isSelected = activeDocumentId === document.id;
            const isDeleting = deletingId === document.id;

            const isProcessing =
              progress?.is_currently_processing === true;

            return (
              <div
                key={document.id}
                className={`group relative min-w-0 overflow-hidden rounded-lg transition ${isSelected
                    ? "bg-brand-50 ring-1 ring-inset ring-brand-200"
                    : "hover:bg-slate-50"
                  }`}
              >
                <div
                  className={`flex min-w-0 items-center gap-1 pr-1 transition-colors duration-300 ${isProcessing ? "bg-brand-100/50 opacity-30" : ""
                    }`}
                >
                  <button
                    type="button"
                    onClick={() => setActiveDocument(document.id)}
                    title={`${document.filename} - ${status.label}`}
                    className="flex min-w-0 flex-1 cursor-pointer items-start gap-2 rounded-lg px-2 py-2 text-left"
                  >
                    <LuFileText
                      size={16}
                      className={`mt-0.5 shrink-0 ${isSelected ? "text-brand-600" : "text-slate-500"
                        }`}
                    />

                    <span className="min-w-0 flex-1">
                      <span
                        className={`block truncate text-xs font-medium ${isSelected ? "text-brand-700" : "text-slate-700"
                          }`}
                      >
                        {document.filename}
                      </span>

                      <span className="mt-1 flex flex-wrap items-center gap-1.5">
                        <span className="text-[11px] text-slate-400">
                          {document.page_count} pages
                        </span>

                        <span
                          className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${status.className}`}
                        >
                          {status.label}
                        </span>
                      </span>
                    </span>
                  </button>

                  <button
                    type="button"
                    disabled={isDeleting}
                    onClick={() =>
                      setDocumentToDelete({
                        id: document.id,
                        filename: document.filename,
                      })
                    }
                    title="Delete document"
                    aria-label={`Delete ${document.filename}`}
                    className="shrink-0 rounded-md p-1.5 text-slate-400 opacity-0 transition hover:bg-red-50 hover:text-red-600 focus-visible:opacity-100 group-hover:opacity-100 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <LuTrash2 size={15} />
                  </button>
                </div>

                {isProcessing && (
                  <div className="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden rounded-lg px-3">
                    <div className="absolute inset-0 document-wave" />

                    <div className="relative z-10 flex items-center gap-2">
                      <LuLoaderCircle
                        size={14}
                        className="animate-spin text-brand-600"
                      />

                      <span className="text-[11px] font-semibold text-brand-800">
                        {progress.message}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <AlertDialog
        open={documentToDelete !== null}
        onOpenChange={(open) => {
          if (!open && deletingId === null) {
            setDocumentToDelete(null);
          }
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Delete document?
            </AlertDialogTitle>

            <AlertDialogDescription>
              Are you sure you want to delete{" "}
              <span className="font-medium text-slate-900">
                {documentToDelete?.filename}
              </span>
              ? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <AlertDialogFooter>
            <AlertDialogCancel disabled={deletingId !== null}>
              Cancel
            </AlertDialogCancel>

            <AlertDialogAction
              disabled={deletingId !== null}
              onClick={(event) => {
                event.preventDefault();
                void handleDelete();
              }}
              className="bg-red-600 text-white hover:bg-red-700"
            >
              {deletingId !== null ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );

}
