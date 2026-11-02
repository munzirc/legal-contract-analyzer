import { useState } from "react";
import { LuArrowUp, LuSquare } from "react-icons/lu";

interface ChatInputProps {
    isStreaming: boolean;
    onSend: (message: string) => Promise<void>;
    onStop: () => void;
}

export default function ChatInput({
    isStreaming,
    onSend,
    onStop,
}: ChatInputProps) {
    const [message, setMessage] = useState("");

    const canSend = message.trim().length > 0 && !isStreaming;

    const handleSend = async () => {
        const trimmedMessage = message.trim();

        if (!trimmedMessage || isStreaming) {
            return;
        }
        
        setMessage("");
        await onSend(trimmedMessage);
    };

    const handleKeyDown = (
        event: React.KeyboardEvent<HTMLTextAreaElement>
    ) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (canSend) {
                void handleSend();
            }
        }
    };

    return (
        <div className="shrink-0 border-t border-slate-200 p-3">
            <div className="flex items-end gap-2 rounded-xl border border-slate-200 bg-white p-2 transition focus-within:border-brand-400 focus-within:ring-2 focus-within:ring-brand-100">
                <textarea
                    rows={2}
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isStreaming}
                    placeholder="Ask a question about your selected documents..."
                    className="max-h-40 min-w-0 flex-1 resize-y bg-transparent p-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-60"
                />

                {isStreaming ? (
                    <button
                        type="button"
                        onClick={onStop}
                        aria-label="Stop generating"
                        title="Stop generating"
                        className="rounded-lg bg-red-500 p-2.5 text-white transition hover:bg-red-600"
                    >
                        <LuSquare size={17} />
                    </button>
                ) : (
                    <button
                        type="button"
                        onClick={() => void handleSend()}
                        disabled={!canSend}
                        aria-label="Send message"
                        title="Send message"
                        className="rounded-lg bg-brand-500 p-2.5 text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        <LuArrowUp size={17} />
                    </button>
                )}
            </div>

            <p className="mt-2 text-center text-[11px] text-slate-400">
                Enter to send · Shift + Enter for a new line
            </p>
        </div>
    );
}