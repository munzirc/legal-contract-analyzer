
import { useState } from "react";
import { useConversationStore } from "../../../stores/useConversationStore";
import { useAppStore } from "../../../stores/useAppStore";

export default function TestChat() {
    const [documentIds, setDocumentIds] = useState("");
    const [removeDocumentId, setRemoveDocumentId] = useState("");

    const activeConversationId = useAppStore(
        (state) => state.activeConversationId
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

    const handleAddDocuments = async () => {
        const ids = [
            ...new Set(
                documentIds
                    .split(",")
                    .map((id) => id.trim())
                    .filter(Boolean)
            ),
        ];

        if (ids.length === 0) return;

        await addDocumentsToConversation(ids);
        setDocumentIds("");
    };

    const handleRemoveDocument = async () => {
        const id = removeDocumentId.trim();

        if (!id) return;

        await removeDocumentFromConversation(id);
        setRemoveDocumentId("");
    };

    return (
        <div className="mx-auto flex max-w-xl flex-col gap-5 p-6">
            <h2 className="text-lg font-semibold text-slate-900">
                Test Conversation Documents
            </h2>

            <div className="rounded-lg border border-slate-200 p-4">
                <p className="mb-2 text-sm font-medium text-slate-700">
                    Active conversation
                </p>

                <p className="break-all text-xs text-slate-500">
                    {activeConversationId ?? "No conversation selected"}
                </p>
            </div>

            <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="mb-3 text-sm font-semibold text-slate-900">
                    Add documents
                </h3>

                <textarea
                    value={documentIds}
                    onChange={(event) =>
                        setDocumentIds(event.target.value)
                    }
                    placeholder="Enter document IDs separated by commas"
                    rows={4}
                    className="w-full resize-y rounded-lg border border-slate-200 p-3 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
                />

                <button
                    type="button"
                    onClick={handleAddDocuments}
                    disabled={
                        !activeConversationId ||
                        !documentIds.trim() ||
                        isUpdatingDocuments
                    }
                    className="mt-3 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    Add documents
                </button>
            </div>

            <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="mb-3 text-sm font-semibold text-slate-900">
                    Remove document
                </h3>

                <input
                    value={removeDocumentId}
                    onChange={(event) =>
                        setRemoveDocumentId(event.target.value)
                    }
                    placeholder="Enter document ID"
                    className="w-full rounded-lg border border-slate-200 p-3 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
                />

                <button
                    type="button"
                    onClick={handleRemoveDocument}
                    disabled={
                        !activeConversationId ||
                        !removeDocumentId.trim() ||
                        isUpdatingDocuments
                    }
                    className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    Remove document
                </button>
            </div>

            <div className="rounded-lg border border-slate-200 p-4">
                <h3 className="mb-3 text-sm font-semibold text-slate-900">
                    Currently attached documents
                </h3>

                {conversationDocumentIds.length === 0 ? (
                    <p className="text-sm text-slate-500">
                        No documents attached.
                    </p>
                ) : (
                    <ul className="space-y-2">
                        {conversationDocumentIds.map((id) => (
                            <li
                                key={id}
                                className="break-all rounded-md bg-brand-50 px-3 py-2 text-xs text-brand-800"
                            >
                                {id}
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {isUpdatingDocuments && (
                <p className="text-center text-xs text-slate-500">
                    Updating conversation documents...
                </p>
            )}
        </div>
    );
}
