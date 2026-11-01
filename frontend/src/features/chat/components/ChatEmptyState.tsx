import { LuMessagesSquare } from "react-icons/lu";

export default function ChatEmptyState() {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <div className="max-w-xs text-center">
        <LuMessagesSquare
          size={36}
          strokeWidth={1.3}
          className="mx-auto mb-3 text-slate-300"
        />

        <p className="text-sm font-medium text-slate-700">
          Ask questions about your documents
        </p>

        <p className="mt-1 text-sm leading-5 text-slate-500">
          Start a conversation to analyze your contracts.
        </p>
      </div>
    </div>
  );
}