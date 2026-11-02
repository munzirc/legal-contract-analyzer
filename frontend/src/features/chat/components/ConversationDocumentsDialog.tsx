import { useEffect, useMemo, useState } from "react";

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "../../../components/ui/dialog";

import { Checkbox } from "../../../components/ui/checkbox";

import { useAppStore } from "../../../stores/useAppStore";
import { useDocumentStore } from "../../../stores/useDocumentStore";
import { useConversationStore } from "../../../stores/useConversationStore";

interface ConversationDocumentsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    draftDocumentIds: string[];
    onDraftDocumentIdsChange: (ids: string[]) => void;
}

export default function ConversationDocumentsDialog({
    open,
    onOpenChange,
    draftDocumentIds,
    onDraftDocumentIdsChange,
}: ConversationDocumentsDialogProps) {
    const activeConversationId = useAppStore(
        (state) => state.activeConversationId
    );

    const isNewChat = !activeConversationId;

    const documents = useDocumentStore((state) => state.documents);

    const isLoadingDocuments = useDocumentStore(
        (state) => state.isLoadingDocuments
    );

    const conversationDocumentIds = useConversationStore(
        (state) => state.conversationDocumentIds
    );

    const isUpdatingDocuments = useConversationStore(
        (state) => state.isUpdatingDocuments
    );

    const addDocumentsToConversation = useConversationStore(
        (state) => state.addDocumentsToConversation
    );

    const removeDocumentFromConversation = useConversationStore(
        (state) => state.removeDocumentFromConversation
    );

    const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);

    const currentDocumentIds = isNewChat
        ? draftDocumentIds
        : conversationDocumentIds;

    useEffect(() => {
        if (open) {
            setSelectedDocumentIds([]);
        }
    }, [open]);

    const attachedDocuments = useMemo(
        () =>
            currentDocumentIds.map((documentId) => ({
                id: documentId,
                document: documents.find(
                    (document) => document.id === documentId
                ),
            })),
        [currentDocumentIds, documents]
    );

    const availableDocuments = useMemo(
        () =>
            documents.filter(
                (document) =>
                    document.status === "READY" &&
                    !currentDocumentIds.includes(document.id)
            ),
        [documents, currentDocumentIds]
    );

    const toggleDocumentSelection = (documentId: string) => {
        if (isNewChat) {
            const updatedIds = draftDocumentIds.includes(documentId)
                ? draftDocumentIds.filter((id) => id !== documentId)
                : [...draftDocumentIds, documentId];

            onDraftDocumentIdsChange(updatedIds);
            return;
        }

        setSelectedDocumentIds((current) =>
            current.includes(documentId)
                ? current.filter((id) => id !== documentId)
                : [...current, documentId]
        );
    };

    const handleAddDocuments = async () => {
        if (
            isNewChat ||
            selectedDocumentIds.length === 0 ||
            isUpdatingDocuments
        ) {
            return;
        }

        await addDocumentsToConversation(selectedDocumentIds);

        const updatedIds = useConversationStore.getState()
            .conversationDocumentIds;

        const allAdded = selectedDocumentIds.every((id) =>
            updatedIds.includes(id)
        );

        if (allAdded) {
            setSelectedDocumentIds([]);
        }
    };

    const handleRemoveDocument = async (documentId: string) => {
        if (isNewChat) {
            onDraftDocumentIdsChange(
                draftDocumentIds.filter((id) => id !== documentId)
            );
            return;
        }

        if (isUpdatingDocuments) {
            return;
        }

        await removeDocumentFromConversation(documentId);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-h-[85vh] overflow-hidden sm:max-w-lg">
                <DialogHeader>
                    <DialogTitle>Conversation documents</DialogTitle>

                    <DialogDescription>
                        {isNewChat
                            ? "Select the documents you want to use in this new conversation."
                            : "Manage the documents used as context for this conversation."}
                    </DialogDescription>
                </DialogHeader>

                <div className="flex min-h-0 flex-col gap-6 overflow-y-auto py-2">
                    <section className="space-y-3">
                        <div className="flex items-center justify-between">
                            <h3 className="text-sm font-semibold text-slate-900">
                                Selected documents
                            </h3>

                            <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700">
                                {currentDocumentIds.length} selected
                            </span>
                        </div>

                        {attachedDocuments.length === 0 ? (
                            <p className="rounded-lg border border-dashed border-slate-200 px-4 py-6 text-center text-sm text-slate-500">
                                No documents selected.
                            </p>
                        ) : (
                            <div className="divide-y divide-slate-100 rounded-lg border border-slate-200">
                                {attachedDocuments.map(({ id, document }) => (
                                    <div
                                        key={id}
                                        className="flex items-center justify-between gap-3 px-3 py-3"
                                    >
                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-medium text-slate-800">
                                                {document?.filename ?? "Document unavailable"}
                                            </p>
                                        </div>

                                        <button
                                            type="button"
                                            disabled={!isNewChat && isUpdatingDocuments}
                                            onClick={() => handleRemoveDocument(id)}
                                            className="shrink-0 rounded-md px-2 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>

                    <section className="space-y-3">
                        <div>
                            <h3 className="text-sm font-semibold text-slate-900">
                                Available documents
                            </h3>

                            <p className="mt-1 text-xs text-slate-500">
                                Only ready documents from your library are shown.
                            </p>
                        </div>

                        {isLoadingDocuments ? (
                            <p className="py-5 text-center text-sm text-slate-500">
                                Loading documents...
                            </p>
                        ) : availableDocuments.length === 0 ? (
                            <p className="rounded-lg border border-dashed border-slate-200 px-4 py-6 text-center text-sm text-slate-500">
                                No other ready documents available.
                            </p>
                        ) : (
                            <div className="divide-y divide-slate-100 rounded-lg border border-slate-200">
                                {availableDocuments.map((document) => (
                                    <label
                                        key={document.id}
                                        className="flex cursor-pointer items-center gap-3 px-3 py-3 transition hover:bg-slate-50"
                                    >
                                        <Checkbox
                                            checked={
                                                isNewChat
                                                    ? false
                                                    : selectedDocumentIds.includes(document.id)
                                            }
                                            disabled={!isNewChat && isUpdatingDocuments}
                                            onCheckedChange={() =>
                                                toggleDocumentSelection(document.id)
                                            }
                                        />

                                        <span className="min-w-0 truncate text-sm text-slate-700">
                                            {document.filename}
                                        </span>
                                    </label>
                                ))}
                            </div>
                        )}
                    </section>
                </div>

                <DialogFooter>
                    <button
                        type="button"
                        onClick={() => onOpenChange(false)}
                        className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                    >
                        Close
                    </button>

                    {!isNewChat && (
                        <button
                            type="button"
                            disabled={
                                selectedDocumentIds.length === 0 ||
                                isUpdatingDocuments
                            }
                            onClick={handleAddDocuments}
                            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {isUpdatingDocuments
                                ? "Updating..."
                                : `Add selected (${selectedDocumentIds.length})`}
                        </button>
                    )}
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}