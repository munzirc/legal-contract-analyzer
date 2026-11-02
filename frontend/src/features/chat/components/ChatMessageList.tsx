import { useEffect, useRef } from "react";
import { useAppStore } from "../../../stores/useAppStore";
import { useConversationStore } from "../../../stores/useConversationStore";
import ChatEmptyState from "./ChatEmptyState";
import ChatMessage from "./ChatMessage";

export default function ChatMessageList() {
    const messages = useConversationStore((state) => state.messages);
    const isLoadingHistory = useConversationStore(
        (state) => state.isLoadingHistory
    );
    const isStreaming = useConversationStore((state) => state.isStreaming);
    const streamingConversationId = useConversationStore(
        (state) => state.streamingConversationId
    );
    const streamingProgress = useConversationStore(
        (state) => state.streamingProgress
    );

    const activeConversationId = useAppStore(
        (state) => state.activeConversationId
    );

    const bottomRef = useRef<HTMLDivElement>(null);

    // Only show stream progress in the conversation producing that stream.
    const showStreamingProgress =
        isStreaming &&
        (streamingConversationId
            ? activeConversationId === streamingConversationId
            : activeConversationId === null);

    useEffect(() => {
        if (!isLoadingHistory && (messages.length > 0 || showStreamingProgress)) {
            bottomRef.current?.scrollIntoView({
                behavior: "instant",
                block: "end",
            });
        }
    }, [messages, isLoadingHistory, showStreamingProgress, streamingProgress]);

    if (isLoadingHistory) {
        return (
            <div className="flex h-full items-center justify-center">
                <p className="text-sm text-slate-500">
                    Loading conversation...
                </p>
            </div>
        );
    }

    if (messages.length === 0 && !showStreamingProgress) {
        return <ChatEmptyState />;
    }

    return (
        <div className="custom-scrollbar h-full overflow-y-auto px-4 py-4">
            <div className="space-y-4">
                {messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                ))}

                {showStreamingProgress && (
                    <div className="flex items-center gap-2 py-2 text-sm text-slate-500">
                        <span className="flex items-center gap-1">
                            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand-500" />
                            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand-500 [animation-delay:150ms]" />
                            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand-500 [animation-delay:300ms]" />
                        </span>

                        <span className="animate-pulse">
                            {streamingProgress || "Thinking..."}
                        </span>
                    </div>
                )}
                
                <div ref={bottomRef} />
            </div>
        </div>
    );
}