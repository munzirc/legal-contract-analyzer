import type { ConversationMessage } from "../types";

interface ChatMessageProps {
  message: ConversationMessage;
}

export default function ChatMessage({
  message,
}: ChatMessageProps) {
  const isUser = message.role === "USER";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
          isUser
            ? "bg-brand-500 text-white"
            : "bg-slate-100 text-slate-900"
        }`}
      >
        <p className="whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </div>
  );
}