
import { useRef } from "react";
import { toast } from "sonner";
import { LuUpload, LuLoaderCircle } from "react-icons/lu";

import { useDocumentStore } from "../../../stores/useDocumentStore";

interface DocumentUploadProps {
  collapsed?: boolean;
}

export default function DocumentUpload({
  collapsed = false,
}: DocumentUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadNewDocument = useDocumentStore(
    (state) => state.uploadNewDocument
  );

  const isUploading = useDocumentStore(
    (state) => state.isUploading
  );

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    // Allow selecting the same file again.
    event.target.value = "";

    const isPdf =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {
      toast.error("Please select a PDF file.");
      return;
    }

    await uploadNewDocument(file);

  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        className="hidden"
        onChange={handleFileChange}
      />

      <button
        type="button"
        title="Upload document"
        disabled={isUploading}
        onClick={() => fileInputRef.current?.click()}
        className={`flex w-full items-center gap-3 rounded-lg bg-indigo-50 px-3 py-2.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-60 ${collapsed ? "justify-center" : ""
          }`}
      >
        {isUploading ? (
          <LuLoaderCircle className="animate-spin" size={18} />
        ) : (
          <LuUpload size={18} />
        )}

        {!collapsed && (
          <span>
            {isUploading ? "Uploading..." : "Upload document"}
          </span>
        )}
      </button>
    </div>
  );
}
