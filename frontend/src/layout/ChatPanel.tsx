import { useState } from "react";

import ChatInput from "../features/chat/components/ChatInput";
import ChatMessageList from "../features/chat/components/ChatMessageList";
import ChatToolbar from "../features/chat/components/ChatToolbar";

import { useAppStore } from "../stores/useAppStore";
import { useConversationStore } from "../stores/useConversationStore";

export default function ChatPanel() {
    const [draftDocumentIds, setDraftDocumentIds] = useState<string[]>([]);

    const activeConversationId = useAppStore(
        (state) => state.activeConversationId
    );

    const sendMessage = useConversationStore(
        (state) => state.sendMessage
    );

    const stopGeneration = useConversationStore(
        (state) => state.stopGeneration
    );

    const isStreaming = useConversationStore(
        (state) => state.isStreaming
    );

    const handleNewChat = () => {
        setDraftDocumentIds([]);
        useConversationStore.getState().startNewChat();
    };

    const handleSendMessage = (message: string) => {
        const documentIds = activeConversationId
            ? []
            : draftDocumentIds;

        return sendMessage(message, documentIds);
    };

    return (
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white">
            <ChatToolbar
                draftDocumentIds={draftDocumentIds}
                onDraftDocumentIdsChange={setDraftDocumentIds}
                onNewChat={handleNewChat}
            />

            <div className="min-h-0 flex-1 overflow-hidden">
                <ChatMessageList />
            </div>

            <ChatInput
                isStreaming={isStreaming}
                onSend={handleSendMessage}
                onStop={stopGeneration}
            />
        </section>
    );
}