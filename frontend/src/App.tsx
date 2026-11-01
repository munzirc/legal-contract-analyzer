import { useEffect } from "react";
import { Toaster } from "sonner";

import AppSidebar from "./layout/AppSidebar";
import PdfViewerPanel from "./layout/PdfViewerPanel";
import ChatPanel from "./layout/ChatPanel";

import { useAppStore } from "./stores/useAppStore";
import { useDocumentStore } from "./stores/useDocumentStore";
import { useConversationStore } from "./stores/useConversationStore";
import { connectProgressStream } from "./features/documents/progress-stream";
export default function App() {
  const sidebarExpanded = useAppStore(
    (state) => state.sidebarExpanded
  );

  const fetchDocuments = useDocumentStore(
    (state) => state.fetchDocuments
  );

  const fetchConversations = useConversationStore(
    (state) => state.fetchConversations
  );

  useEffect(() => {
    fetchDocuments();
    fetchConversations();
    connectProgressStream();
  }, [fetchDocuments, fetchConversations]);

  return (
    <>
      <main className="h-screen overflow-hidden bg-slate-50 text-slate-900">
        <div
          className="grid h-full transition-[grid-template-columns] duration-200 ease-in-out"
          style={{
            gridTemplateColumns: sidebarExpanded
              ? "260px minmax(0, 1fr)"
              : "68px minmax(0, 1fr)",
          }}
        >
          <AppSidebar />

          <div className="grid min-h-0 min-w-0 grid-cols-2 gap-3 p-3">
            <PdfViewerPanel />
            <ChatPanel />
          </div>
        </div>
      </main>
      <Toaster
        position="top-right"
        richColors
        closeButton
        duration={3000}
      />
    </>
  );
}
