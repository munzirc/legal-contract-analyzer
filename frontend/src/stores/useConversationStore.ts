
import { create } from "zustand";
import { toast } from "sonner";

import type {
    Conversation,
} from "../features/conversations/types";
import type {
    ConversationMessage,
} from "../features/chat/types";

import {
    getConversations,
    deleteConversation,
} from "../features/conversations/api";
import {
    getConversationHistory,
    addConversationDocuments,
    removeConversationDocument,
} from "../features/chat/api";

import { useAppStore } from "./useAppStore";

interface ConversationState {
    conversations: Conversation[];

    messages: ConversationMessage[];
    conversationDocumentIds: string[];

    isLoadingConversations: boolean;
    isLoadingHistory: boolean;
    isUpdatingDocuments: boolean;

    fetchError: string | null;

    fetchConversations: () => Promise<void>;
    fetchConversationHistory: (conversationId: string) => Promise<void>;
    startNewChat: () => void;
    addDocumentsToConversation: (
        documentIds: string[]
    ) => Promise<void>;

    removeDocumentFromConversation: (
        documentId: string
    ) => Promise<void>;

    deleteConversation: (conversationId: string) => Promise<void>;
}

export const useConversationStore = create<ConversationState>(
    (set) => ({
        conversations: [],

        messages: [],
        conversationDocumentIds: [],

        isLoadingConversations: false,
        isLoadingHistory: false,
        isUpdatingDocuments: false,

        fetchError: null,

        fetchConversations: async () => {
            set({
                isLoadingConversations: true,
                fetchError: null,
            });

            try {
                const conversations = await getConversations();
                set({ conversations });
            } catch (error) {
                set({
                    fetchError:
                        error instanceof Error
                            ? error.message
                            : "Failed to load conversations.",
                });
            } finally {
                set({ isLoadingConversations: false });
            }
        },

        deleteConversation: async (conversationId) => {
            try {
                const response = await deleteConversation(conversationId);

                if (!response.deleted) {
                    throw new Error("Conversation could not be deleted.");
                }

                const isActiveConversation =
                    useAppStore.getState().activeConversationId === conversationId;

                set((state) => ({
                    conversations: state.conversations.filter(
                        (conversation) =>
                            conversation.conversation_id !== conversationId
                    ),

                    ...(isActiveConversation && {
                        messages: [],
                        conversationDocumentIds: [],
                        isLoadingHistory: false,
                    }),
                }));

                if (isActiveConversation) {
                    useAppStore.getState().setActiveConversation(null);
                }

                toast.success("Conversation deleted successfully.");
            } catch (error) {
                toast.error(
                    error instanceof Error
                        ? error.message
                        : "Failed to delete conversation."
                );
            }
        },

        fetchConversationHistory: async (conversationId) => {
            set({
                messages: [],
                conversationDocumentIds: [],
                isLoadingHistory: true,
            });

            try {
                const history =
                    await getConversationHistory(conversationId);

                // Ignore responses belonging to a conversation
                // that is no longer active.
                if (
                    useAppStore.getState().activeConversationId !==
                    conversationId
                ) {
                    return;
                }

                set({
                    messages: history.messages,
                    conversationDocumentIds: history.document_ids,
                });
            } catch (error) {
                if (
                    useAppStore.getState().activeConversationId ===
                    conversationId
                ) {
                    toast.error(
                        error instanceof Error
                            ? error.message
                            : "Failed to load conversation history."
                    );
                }
            } finally {
                if (
                    useAppStore.getState().activeConversationId ===
                    conversationId
                ) {
                    set({ isLoadingHistory: false });
                }
            }
        },

        startNewChat: () => {
            useAppStore.getState().setActiveConversation(null);

            set({
                messages: [],
                conversationDocumentIds: [],
                isLoadingHistory: false,
            });
        },

        addDocumentsToConversation: async (documentIds) => {
            const conversationId =
                useAppStore.getState().activeConversationId;

            if (!conversationId || documentIds.length === 0) {
                return;
            }

            if (useConversationStore.getState().isUpdatingDocuments) {
                return;
            }

            set({ isUpdatingDocuments: true });

            try {
                const response = await addConversationDocuments(
                    conversationId,
                    documentIds
                );

                // Ignore a response if the user switched conversations.
                if (
                    useAppStore.getState().activeConversationId !==
                    conversationId
                ) {
                    return;
                }

                set({
                    conversationDocumentIds: response.document_ids,
                });

                toast.success("Documents added successfully.");
            } catch (error) {
                toast.error(
                    error instanceof Error
                        ? error.message
                        : "Failed to add documents."
                );
            } finally {
                set({ isUpdatingDocuments: false });
            }
        },

        removeDocumentFromConversation: async (documentId) => {
            const conversationId =
                useAppStore.getState().activeConversationId;

            if (!conversationId) {
                return;
            }

            if (useConversationStore.getState().isUpdatingDocuments) {
                return;
            }

            set({ isUpdatingDocuments: true });

            try {
                const response = await removeConversationDocument(
                    conversationId,
                    documentId
                );

                if (
                    useAppStore.getState().activeConversationId !==
                    conversationId
                ) {
                    return;
                }

                set({
                    conversationDocumentIds: response.document_ids,
                });

                toast.success("Document removed from conversation.");
            } catch (error) {
                toast.error(
                    error instanceof Error
                        ? error.message
                        : "Failed to remove document."
                );
            } finally {
                set({ isUpdatingDocuments: false });
            }
        },
    })
);
