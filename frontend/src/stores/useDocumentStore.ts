import { create } from "zustand";
import { toast } from "sonner";
import type { Document, DocumentProgress } from "../features/documents/types";
import { connectProgressStream } from "../features/documents/progress-stream";
import {
    getDocuments,
    uploadDocument,
    deleteDocument
} from "../features/documents/api";
import { useAppStore } from "./useAppStore";



interface DocumentState {
    documents: Document[];
    documentProgress: Record<string, DocumentProgress>;

    isLoadingDocuments: boolean;
    isUploading: boolean;

    setDocumentProgress: (progress: DocumentProgress) => void;

    fetchDocuments: () => Promise<void>;
    uploadNewDocument: (file: File) => Promise<void>;
    deleteDocumentById: (documentId: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set) => ({
    documents: [],
    documentProgress: {},

    isLoadingDocuments: false,
    isUploading: false,


    setDocumentProgress: (progress) =>
        set((state) => ({
            documentProgress: {
                ...state.documentProgress,
                [progress.document_id]: progress,
            },
        })),

    fetchDocuments: async () => {
        set({ isLoadingDocuments: true });

        try {
            const documents = await getDocuments();
            set({ documents });
        } catch (error: unknown) {
            toast.error(
                error instanceof Error
                    ? error.message
                    : "Failed to load documents."
            );
        } finally {
            set({ isLoadingDocuments: false });
        }
    },

    uploadNewDocument: async (file) => {
        set({ isUploading: true });
 
        let response: any;
 
        try {
            response =await uploadDocument(file);

            const documents = await getDocuments();

            set({ documents });
            toast.success("Document uploaded successfully.");
            connectProgressStream();
        } catch (error: unknown) {
            toast.error("Failed to upload document!");
        } finally {
            set({ isUploading: false });
        }
    },

    deleteDocumentById: async (documentId) => {
        await deleteDocument(documentId);

        set((state) => ({
            documents: state.documents.filter(
                (document) => document.id !== documentId
            ),
        }));

        const activeDocumentId = useAppStore.getState().activeDocumentId;

        if (activeDocumentId === documentId) {
            useAppStore.getState().setActiveDocument(null);
        }
    },


}));