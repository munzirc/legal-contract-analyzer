
import { useState } from "react";
import {
    LuMessagesSquare,
    LuTrash2,
} from "react-icons/lu";

import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "../../../components/ui/alert-dialog";

import { useAppStore } from "../../../stores/useAppStore";
import { useConversationStore } from "../../../stores/useConversationStore";

export default function ConversationList() {
    const [conversationToDelete, setConversationToDelete] =
        useState<string | null>(null);

    const conversations = useConversationStore(
        (state) => state.conversations
    );

    const isLoading = useConversationStore(
        (state) => state.isLoadingConversations
    );

    const fetchError = useConversationStore(
        (state) => state.fetchError
    );

    const fetchConversationHistory = useConversationStore(
        (state) => state.fetchConversationHistory
    );

    const deleteConversation = useConversationStore(
        (state) => state.deleteConversation
    );

    const activeConversationId = useAppStore(
        (state) => state.activeConversationId
    );

    const setActiveConversation = useAppStore(
        (state) => state.setActiveConversation
    );

    const handleConversationClick = (conversationId: string) => {
        if (activeConversationId === conversationId) return;

        setActiveConversation(conversationId);
        fetchConversationHistory(conversationId);
    };

    const handleDeleteConversation = async () => {
        if (!conversationToDelete) return;

        await deleteConversation(conversationToDelete);
        setConversationToDelete(null);
    };

    const selectedConversation = conversations.find(
        (conversation) =>
            conversation.conversation_id === conversationToDelete
    );

    return (
        <>
            <section className="flex min-h-0 flex-1 flex-col">
                <h2 className="mb-3 flex shrink-0 items-center gap-2 px-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    <LuMessagesSquare size={15} />
                    Conversations
                </h2>

                <div className="custom-scrollbar min-h-0 flex-1 space-y-1 overflow-y-auto pr-1">
                    {isLoading && (
                        <p className="px-2 py-2 text-xs text-slate-400">
                            Loading conversations...
                        </p>
                    )}

                    {!isLoading && fetchError && (
                        <p className="px-2 py-2 text-xs text-red-500">
                            {fetchError}
                        </p>
                    )}

                    {!isLoading &&
                        !fetchError &&
                        conversations.length === 0 && (
                            <p className="px-2 py-2 text-xs leading-5 text-slate-400">
                                Your conversations will appear here.
                            </p>
                        )}

                    {!isLoading &&
                        conversations.map((conversation) => {
                            const conversationId =
                                conversation.conversation_id;

                            const isActive =
                                activeConversationId === conversationId;

                            return (
                                <div
                                    key={conversationId}
                                    className={`group flex items-center gap-1 rounded-lg pr-1 transition ${
                                        isActive
                                            ? "bg-brand-50"
                                            : "hover:bg-slate-50"
                                    }`}
                                >
                                    <button
                                        type="button"
                                        onClick={() =>
                                            handleConversationClick(
                                                conversationId
                                            )
                                        }
                                        title={
                                            conversation.title ||
                                            "Untitled Conversation"
                                        }
                                        className={`min-w-0 flex-1 truncate rounded-lg px-3 py-2 text-left text-sm transition ${
                                            isActive
                                                ? "font-medium text-brand-600"
                                                : "text-slate-600"
                                        }`}
                                    >
                                        {conversation.title ||
                                            "Untitled Conversation"}
                                    </button>

                                    <button
                                        type="button"
                                        title="Delete conversation"
                                        aria-label={`Delete ${
                                            conversation.title ||
                                            "untitled conversation"
                                        }`}
                                        onClick={() =>
                                            setConversationToDelete(
                                                conversationId
                                            )
                                        }
                                        className="shrink-0 rounded-md p-1.5 text-slate-400 opacity-0 transition hover:bg-red-50 hover:text-red-600 group-hover:opacity-100 focus:opacity-100"
                                    >
                                        <LuTrash2 size={15} />
                                    </button>
                                </div>
                            );
                        })}
                </div>
            </section>

            <AlertDialog
                open={conversationToDelete !== null}
                onOpenChange={(open) => {
                    if (!open) setConversationToDelete(null);
                }}
            >
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>
                            Delete conversation?
                        </AlertDialogTitle>

                        <AlertDialogDescription>
                            Are you sure you want to delete{" "}
                            <span className="font-medium text-slate-800">
                                {selectedConversation?.title ||
                                    "this conversation"}
                            </span>
                            ? This will permanently delete its chat history.
                            Your original library documents will remain untouched.
                        </AlertDialogDescription>
                    </AlertDialogHeader>

                    <AlertDialogFooter>
                        <AlertDialogCancel>
                            Cancel
                        </AlertDialogCancel>

                        <AlertDialogAction
                            onClick={handleDeleteConversation}
                            className="bg-red-600 text-white hover:bg-red-700"
                        >
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    );
}
