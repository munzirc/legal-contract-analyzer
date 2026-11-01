
import { useEffect, useRef } from "react";

import { useConversationStore } from "../../../stores/useConversationStore";

import ChatEmptyState from "./ChatEmptyState";
import ChatMessage from "./ChatMessage";

export default function ChatMessageList() {
    const messages = useConversationStore(
        (state) => state.messages
    );

    const isLoading = useConversationStore(
        (state) => state.isLoadingHistory
    );

    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!isLoading && messages.length > 0) {
            bottomRef.current?.scrollIntoView({
                behavior: "instant",
                block: "end",
            });
        }
    }, [messages, isLoading]);

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-sm text-slate-500">
                    Loading conversation...
                </p>
            </div>
        );
    }

    if (messages.length === 0) {
        return <ChatEmptyState />;
    }

    return (
        <div className="custom-scrollbar h-full overflow-y-auto px-4 py-4">
            <div className="space-y-4">
                {messages.map((message) => (
                    <ChatMessage
                        key={message.id}
                        message={message}
                    />
                ))}

                <div ref={bottomRef} />
            </div>
        </div>
    );
}
