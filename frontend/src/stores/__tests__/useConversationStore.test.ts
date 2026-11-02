
import { beforeEach, describe, expect, it, vi } from "vitest";

import type {
    ChatStreamEvent,
    ConversationMessage,
} from "../../features/chat/types";

const mocks = vi.hoisted(() => ({
    getConversations: vi.fn(),
    deleteConversation: vi.fn(),
    getConversationHistory: vi.fn(),
    addConversationDocuments: vi.fn(),
    removeConversationDocument: vi.fn(),
    streamChat: vi.fn(),
    toastSuccess: vi.fn(),
    toastError: vi.fn(),
}));

vi.mock("sonner", () => ({
    toast: {
        success: mocks.toastSuccess,
        error: mocks.toastError,
    },
}));

vi.mock("../../features/conversations/api", () => ({
    getConversations: mocks.getConversations,
    deleteConversation: mocks.deleteConversation,
}));

vi.mock("../../features/chat/api", () => ({
    getConversationHistory: mocks.getConversationHistory,
    addConversationDocuments: mocks.addConversationDocuments,
    removeConversationDocument: mocks.removeConversationDocument,
    streamChat: mocks.streamChat,
}));

import { useConversationStore } from "../useConversationStore";
import { useAppStore } from "../useAppStore";

const conversationA = "conversation-a";
const conversationB = "conversation-b";
const documentA = "document-a";

function createMessage(
    id: string,
    role: "USER" | "ASSISTANT",
    content: string,
    evidence: ConversationMessage["evidence"] = []
): ConversationMessage {
    return {
        id,
        role,
        content,
        created_at: "2026-10-30T10:00:00Z",
        evidence,
    };
}

function createEvent(
    type: ChatStreamEvent["type"],
    data: unknown
): ChatStreamEvent {
    return { type, data } as ChatStreamEvent;
}

function emit(event: ChatStreamEvent) {
    const callback = mocks.streamChat.mock.calls[0]?.[1];

    if (!callback) {
        throw new Error("Stream event callback was not registered.");
    }

    callback(event);
}

function resetStores() {
    useAppStore.setState({
        activeConversationId: null,
    });

    useConversationStore.setState({
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
    });
}

describe("useConversationStore streaming", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        resetStores();

        mocks.getConversations.mockResolvedValue([]);
        mocks.deleteConversation.mockResolvedValue({ deleted: true });
        mocks.getConversationHistory.mockResolvedValue({
            conversation_id: conversationA,
            document_ids: [documentA],
            messages: [],
        });
        mocks.addConversationDocuments.mockResolvedValue({
            conversation_id: conversationA,
            document_ids: [documentA],
        });
        mocks.removeConversationDocument.mockResolvedValue({
            conversation_id: conversationA,
            document_ids: [],
        });

        mocks.streamChat.mockImplementation(
            async (
                _request: unknown,
                _onEvent: (event: ChatStreamEvent) => void
            ) => { }
        );
    });

    it("activates a new conversation when its first message arrives", async () => {
        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize this contract", [documentA]);

        emit(
            createEvent("user_message", {
                conversation_id: conversationA,
                message: createMessage(
                    "user-message-1",
                    "USER",
                    "Summarize this contract"
                ),
            })
        );

        await sendPromise;

        expect(useAppStore.getState().activeConversationId).toBe(
            conversationA
        );

        expect(
            useConversationStore.getState().conversationDocumentIds
        ).toEqual([documentA]);

        expect(useConversationStore.getState().messages).toHaveLength(1);
    });

    it("does not activate a new conversation after navigation", async () => {
        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize this contract", [documentA]);

        // Simulate the user navigating to another conversation and
        // then starting a new chat before the first SSE event arrives.
        useAppStore.getState().setActiveConversation(conversationB);
        useAppStore.getState().setActiveConversation(null);

        emit(
            createEvent("user_message", {
                conversation_id: conversationA,
                message: createMessage(
                    "user-message-1",
                    "USER",
                    "Summarize this contract"
                ),
            })
        );

        await sendPromise;

        expect(useAppStore.getState().activeConversationId).toBeNull();
        expect(useConversationStore.getState().messages).toHaveLength(0);
    });

    it("ignores events from an inactive conversation without aborting the stream", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        const sendPromise = useConversationStore
            .getState()
            .sendMessage("What is the security deposit?");

        useAppStore.getState().setActiveConversation(conversationB);

        emit(
            createEvent("answer", {
                conversation_id: conversationA,
                message: createMessage(
                    "assistant-message-1",
                    "ASSISTANT",
                    "The security deposit is specified in the contract."
                ),
            })
        );

        expect(useConversationStore.getState().messages).toHaveLength(0);
        expect(mocks.streamChat.mock.calls[0]?.[2]?.aborted).toBe(false);

        await sendPromise;
    });

    it("updates the conversation when the user returns while streaming", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        const sendPromise = useConversationStore
            .getState()
            .sendMessage("What is the security deposit?");

        useAppStore.getState().setActiveConversation(conversationB);

        // This event is ignored while B is active.
        emit(
            createEvent("answer", {
                conversation_id: conversationA,
                message: createMessage(
                    "assistant-message-1",
                    "ASSISTANT",
                    "First answer"
                ),
            })
        );

        // Return to A while the stream is still open.
        useAppStore.getState().setActiveConversation(conversationA);

        emit(
            createEvent("answer", {
                conversation_id: conversationA,
                message: createMessage(
                    "assistant-message-2",
                    "ASSISTANT",
                    "Second answer"
                ),
            })
        );

        expect(useConversationStore.getState().messages).toHaveLength(1);
        expect(useConversationStore.getState().messages[0].content).toBe(
            "Second answer"
        );

        await sendPromise;
    });

    it("handles an error without a conversation ID", async () => {
        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize this contract", [documentA]);

        emit(
            createEvent("error", {
                conversation_id: null,
                message: "Unable to start the agent.",
            })
        );

        await sendPromise;

        expect(useConversationStore.getState().streamingError).toBe(
            "Unable to start the agent."
        );

        expect(mocks.toastError).toHaveBeenCalledWith(
            "Unable to start the agent."
        );
    });

    it("does not add duplicate messages", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize the contract");

        const event = createEvent("answer", {
            conversation_id: conversationA,
            message: createMessage(
                "assistant-message-1",
                "ASSISTANT",
                "Summary"
            ),
        });

        emit(event);
        emit(event);

        expect(useConversationStore.getState().messages).toHaveLength(1);

        await sendPromise;
    });

    it("does not abort the stream when starting a new chat", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize the contract");

        const signal = mocks.streamChat.mock.calls[0]?.[2];

        useConversationStore.getState().startNewChat();

        expect(signal?.aborted).toBe(false);
        expect(useConversationStore.getState().isStreaming).toBe(true);
        expect(useAppStore.getState().activeConversationId).toBeNull();

        await sendPromise;
    });

    it("aborts the frontend stream when stopGeneration is called", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize the contract");

        const signal = mocks.streamChat.mock.calls[0]?.[2];

        useConversationStore.getState().stopGeneration();

        expect(signal?.aborted).toBe(true);
        expect(useConversationStore.getState().isStreaming).toBe(false);

        await sendPromise;
    });

    it("keeps streaming active until the stream finishes", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        let resolveStream!: () => void;

        mocks.streamChat.mockImplementation(
            async (
                _request: unknown,
                _onEvent: (event: ChatStreamEvent) => void
            ) => {
                await new Promise<void>((resolve) => {
                    resolveStream = resolve;
                });
            }
        );

        const sendPromise = useConversationStore
            .getState()
            .sendMessage("Summarize the contract");

        const emitEvent = (
            type: ChatStreamEvent["type"],
            data: unknown
        ) => {
            const callback = mocks.streamChat.mock.calls[0]?.[1];

            if (!callback) {
                throw new Error("Stream event callback was not registered.");
            }

            callback(createEvent(type, data));
        };

        emitEvent("answer", {
            conversation_id: conversationA,
            message: createMessage(
                "assistant-message-1",
                "ASSISTANT",
                "Contract summary"
            ),
        });

        expect(useConversationStore.getState().isStreaming).toBe(true);
        expect(useConversationStore.getState().messages).toHaveLength(1);

        resolveStream();
        await sendPromise;

        expect(useConversationStore.getState().isStreaming).toBe(false);
    });

    it("preserves SSE messages received while conversation history is loading", async () => {
        useAppStore.getState().setActiveConversation(conversationA);

        let resolveHistory!: (value: {
            conversation_id: string;
            document_ids: string[];
            messages: ConversationMessage[];
        }) => void;

        mocks.getConversationHistory.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveHistory = resolve;
                })
        );

        const historyPromise = useConversationStore
            .getState()
            .fetchConversationHistory(conversationA);

        // Simulate an SSE message arriving before history finishes.
        useConversationStore.setState((state) => ({
            messages: [
                ...state.messages,
                createMessage(
                    "assistant-message-2",
                    "ASSISTANT",
                    "New answer from SSE"
                ),
            ],
        }));

        // The backend history contains an older message.
        resolveHistory({
            conversation_id: conversationA,
            document_ids: [documentA],
            messages: [
                createMessage(
                    "user-message-1",
                    "USER",
                    "Original question"
                ),
            ],
        });

        await historyPromise;

        const messages = useConversationStore.getState().messages;

        expect(messages).toHaveLength(2);
        expect(messages.map((message) => message.id)).toEqual([
            "user-message-1",
            "assistant-message-2",
        ]);

        expect(
            useConversationStore.getState().conversationDocumentIds
        ).toEqual([documentA]);

        expect(useConversationStore.getState().isLoadingHistory).toBe(false);
    });

    it("ignores a stale history response after switching conversations", async () => {
        let resolveHistoryA!: (value: {
            conversation_id: string;
            document_ids: string[];
            messages: ConversationMessage[];
        }) => void;

        mocks.getConversationHistory.mockImplementation(
            (conversationId: string) => {
                if (conversationId === conversationA) {
                    return new Promise((resolve) => {
                        resolveHistoryA = resolve;
                    });
                }

                return Promise.resolve({
                    conversation_id: conversationB,
                    document_ids: [],
                    messages: [
                        createMessage(
                            "message-b",
                            "USER",
                            "Conversation B message"
                        ),
                    ],
                });
            }
        );

        useAppStore.getState().setActiveConversation(conversationA);

        const historyPromiseA = useConversationStore
            .getState()
            .fetchConversationHistory(conversationA);

        // Switch to B before A's request finishes.
        useAppStore.getState().setActiveConversation(conversationB);

        const historyPromiseB = useConversationStore
            .getState()
            .fetchConversationHistory(conversationB);

        await historyPromiseB;

        expect(useConversationStore.getState().messages).toHaveLength(1);
        expect(useConversationStore.getState().messages[0].id).toBe("message-b");

        // Now let the older A request finish.
        resolveHistoryA({
            conversation_id: conversationA,
            document_ids: [documentA],
            messages: [
                createMessage(
                    "message-a",
                    "USER",
                    "Conversation A message"
                ),
            ],
        });

        await historyPromiseA;

        expect(useAppStore.getState().activeConversationId).toBe(conversationB);
        expect(useConversationStore.getState().messages).toHaveLength(1);
        expect(useConversationStore.getState().messages[0].id).toBe("message-b");
        expect(useConversationStore.getState().conversationDocumentIds).toEqual([]);
    });
});
