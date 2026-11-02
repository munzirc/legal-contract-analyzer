
import { create } from "zustand";
import { toast } from "sonner";

import type { Conversation } from "../features/conversations/types";
import type {
    ConversationMessage,
    MessageEvidence,
    ChatStreamEvent,
} from "../features/chat/types";

import {
    getConversations,
    deleteConversation,
} from "../features/conversations/api";

import {
    getConversationHistory,
    addConversationDocuments,
    removeConversationDocument,
    streamChat,
} from "../features/chat/api";

import { useAppStore } from "./useAppStore";

interface ConversationState {
    conversations: Conversation[];

    messages: ConversationMessage[];
    conversationDocumentIds: string[];

    isLoadingConversations: boolean;
    isLoadingHistory: boolean;
    isUpdatingDocuments: boolean;

    isStreaming: boolean;
    streamingConversationId: string | null;
    streamingProgress: string | null;
    streamingError: string | null;

    fetchError: string | null;

    fetchConversations: () => Promise<void>;
    fetchConversationHistory: (conversationId: string) => Promise<void>;
    startNewChat: () => void;

    sendMessage: (
        message: string,
        documentIds?: string[]
    ) => Promise<void>;

    stopGeneration: () => void;

    addDocumentsToConversation: (documentIds: string[]) => Promise<void>;
    removeDocumentFromConversation: (documentId: string) => Promise<void>;
    deleteConversation: (conversationId: string) => Promise<void>;
}

function mergeMessages(
    historyMessages: ConversationMessage[],
    currentMessages: ConversationMessage[]
): ConversationMessage[] {
    const messagesById = new Map<string, ConversationMessage>();

    for (const message of historyMessages) {
        messagesById.set(message.id, message);
    }

    for (const currentMessage of currentMessages) {
        const existingMessage = messagesById.get(currentMessage.id);

        if (!existingMessage) {
            messagesById.set(currentMessage.id, currentMessage);
            continue;
        }

        const evidenceById = new Map<string, MessageEvidence>();

        for (const evidence of existingMessage.evidence) {
            evidenceById.set(evidence.id, evidence);
        }

        for (const evidence of currentMessage.evidence) {
            evidenceById.set(evidence.id, evidence);
        }

        messagesById.set(currentMessage.id, {
            ...existingMessage,
            ...currentMessage,
            evidence: Array.from(evidenceById.values()),
        });
    }

    return Array.from(messagesById.values()).sort(
        (a, b) =>
            new Date(a.created_at).getTime() -
            new Date(b.created_at).getTime()
    );
}

export const useConversationStore = create<ConversationState>(
    (set, get) => {
        let abortController: AbortController | null = null;
        let historyRequestId = 0;

        // Identifies the currently running frontend stream request.
        let streamRequestId = 0;

        // Changes whenever the user navigates between conversations.
        let navigationVersion = 0;

        // Track navigation outside this store too, because activeConversationId
        // is owned by useAppStore.
        useAppStore.subscribe((state, previousState) => {
            if (
                state.activeConversationId !==
                previousState.activeConversationId
            ) {
                navigationVersion++;

                // Keep the stream running, but don't show its old progress
                // in the newly selected conversation.
                set({ streamingProgress: null });
            }
        });

        return {
            conversations: [],

            messages: [],
            conversationDocumentIds: [],

            isLoadingConversations: false,
            isLoadingHistory: false,
            isUpdatingDocuments: false,

            isStreaming: false,
            streamingConversationId: null,
            streamingProgress: null,
            streamingError: null,

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
                        useAppStore.getState().activeConversationId ===
                        conversationId;

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
                const requestId = ++historyRequestId;

                set({
                    messages: [],
                    conversationDocumentIds: [],
                    isLoadingHistory: true,
                });

                try {
                    const history =
                        await getConversationHistory(conversationId);

                    if (
                        requestId !== historyRequestId ||
                        useAppStore.getState().activeConversationId !==
                            conversationId
                    ) {
                        return;
                    }

                    set((state) => ({
                        messages: mergeMessages(
                            history.messages,
                            state.messages
                        ),
                        conversationDocumentIds: history.document_ids,
                    }));
                } catch (error) {
                    if (
                        requestId === historyRequestId &&
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
                        requestId === historyRequestId &&
                        useAppStore.getState().activeConversationId ===
                            conversationId
                    ) {
                        set({ isLoadingHistory: false });
                    }
                }
            },

            startNewChat: () => {
                historyRequestId++;

                useAppStore.getState().setActiveConversation(null);

                set({
                    messages: [],
                    conversationDocumentIds: [],
                    isLoadingHistory: false,
                    streamingError: null,
                });
            },

            sendMessage: async (message, documentIds = []) => {
                const trimmedMessage = message.trim();

                if (!trimmedMessage || get().isStreaming) {
                    return;
                }

                const initialConversationId =
                    useAppStore.getState().activeConversationId;

                const requestDocumentIds = initialConversationId
                    ? []
                    : documentIds;

                if (!initialConversationId && requestDocumentIds.length === 0) {
                    toast.error(
                        "Select at least one document before sending a message."
                    );
                    return;
                }

                const controller = new AbortController();
                abortController = controller;

                const currentRequestId = ++streamRequestId;
                const initialNavigationVersion = navigationVersion;

                // For a new conversation, this remains false until its
                // first user_message event identifies the conversation.
                let conversationIdResolved = Boolean(initialConversationId);

                set({
                    isStreaming: true,
                    streamingConversationId: initialConversationId,
                    streamingProgress: "Starting...",
                    streamingError: null,
                });

                const isRequestCurrent = () =>
                    streamRequestId === currentRequestId;

                const isActiveConversation = (conversationId: string) =>
                    useAppStore.getState().activeConversationId ===
                    conversationId;

                const canActivateNewConversation = () =>
                    !initialConversationId &&
                    !conversationIdResolved &&
                    navigationVersion === initialNavigationVersion &&
                    useAppStore.getState().activeConversationId === null;

                const handleError = (message: string) => {
                    if (!isRequestCurrent()) return;

                    set({
                        streamingError: message,
                        streamingProgress: null,
                    });

                    toast.error(message);
                };

                const handleEvent = (event: ChatStreamEvent) => {
                    if (!isRequestCurrent()) return;

                    // Handle errors separately because the backend may
                    // emit an error before it has identified a conversation.
                    if (event.type === "error") {
                        const conversationId =
                            event.data.conversation_id;

                        if (conversationId) {
                            if (isActiveConversation(conversationId)) {
                                handleError(event.data.message);
                            }
                        } else {
                            const belongsToCurrentView =
                                initialConversationId
                                    ? isActiveConversation(initialConversationId)
                                    : navigationVersion ===
                                          initialNavigationVersion &&
                                      useAppStore.getState()
                                          .activeConversationId === null;

                            if (belongsToCurrentView) {
                                handleError(event.data.message);
                            }
                        }

                        return;
                    }

                    const conversationId = event.data.conversation_id;

                    if (!conversationId) return;

                    // The first user message identifies a newly created
                    // conversation. Activate it only if the user hasn't
                    // navigated away since sending the request.
                    if (
                        event.type === "user_message" &&
                        !conversationIdResolved &&
                        canActivateNewConversation()
                    ) {
                        conversationIdResolved = true;

                        useAppStore
                            .getState()
                            .setActiveConversation(conversationId);

                        set({
                            conversationDocumentIds: requestDocumentIds,
                            streamingConversationId: conversationId,
                        });
                    }

                    // After the conversation is identified, all events
                    // are matched against the currently active conversation.
                    if (!isActiveConversation(conversationId)) {
                        if (event.type === "complete") {
                            void get().fetchConversations();
                        }

                        return;
                    }

                    switch (event.type) {
                        case "user_message": {
                            conversationIdResolved = true;

                            set((state) => {
                                if (
                                    state.messages.some(
                                        (message) =>
                                            message.id === event.data.message.id
                                    )
                                ) {
                                    return {};
                                }

                                return {
                                    messages: [
                                        ...state.messages,
                                        event.data.message,
                                    ],
                                };
                            });

                            break;
                        }

                        case "answer": {
                            set((state) => {
                                if (
                                    state.messages.some(
                                        (message) =>
                                            message.id === event.data.message.id
                                    )
                                ) {
                                    return {};
                                }

                                return {
                                    messages: [
                                        ...state.messages,
                                        event.data.message,
                                    ],
                                };
                            });

                            break;
                        }

                        case "evidence": {
                            set((state) => ({
                                messages: state.messages.map((message) => {
                                    if (
                                        message.id !== event.data.message_id
                                    ) {
                                        return message;
                                    }

                                    if (
                                        message.evidence.some(
                                            (evidence) =>
                                                evidence.id ===
                                                event.data.evidence.id
                                        )
                                    ) {
                                        return message;
                                    }

                                    return {
                                        ...message,
                                        evidence: [
                                            ...message.evidence,
                                            event.data.evidence,
                                        ],
                                    };
                                }),
                            }));

                            break;
                        }

                        case "progress": {
                            set({
                                streamingProgress: event.data.message,
                            });

                            break;
                        }

                        case "complete": {
                            set({
                                streamingProgress: null,
                                streamingError: null,
                            });

                            void get().fetchConversations();

                            break;
                        }
                    }
                };

                try {
                    await streamChat(
                        {
                            conversation_id: initialConversationId,
                            message: trimmedMessage,
                            document_ids: requestDocumentIds,
                        },
                        handleEvent,
                        controller.signal
                    );
                } catch (error) {
                    if (
                        error instanceof Error &&
                        error.name === "AbortError"
                    ) {
                        return;
                    }

                    if (isRequestCurrent()) {
                        handleError(
                            error instanceof Error
                                ? error.message
                                : "Something went wrong while sending your message."
                        );
                    }
                } finally {
                    // An older request must never reset the state belonging
                    // to a newer request.
                    if (isRequestCurrent()) {
                        abortController = null;

                        set({
                            isStreaming: false,
                            streamingConversationId: null,
                            streamingProgress: null,
                        });
                    }
                }
            },

            stopGeneration: () => {
                if (!abortController) return;

                // Invalidate callbacks and finally blocks from this request.
                streamRequestId++;

                abortController.abort();
                abortController = null;

                set({
                    isStreaming: false,
                    streamingConversationId: null,
                    streamingProgress: null,
                });
            },

            addDocumentsToConversation: async (documentIds) => {
                const conversationId =
                    useAppStore.getState().activeConversationId;

                if (!conversationId || documentIds.length === 0) return;
                if (get().isUpdatingDocuments) return;

                set({ isUpdatingDocuments: true });

                try {
                    const response = await addConversationDocuments(
                        conversationId,
                        documentIds
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

                if (!conversationId) return;
                if (get().isUpdatingDocuments) return;

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
        };
    }
);
