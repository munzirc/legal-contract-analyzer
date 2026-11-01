
import { LuArrowUp } from "react-icons/lu";

export default function ChatInput() {
  return (
    <div className="shrink-0 border-t border-slate-200 p-3">
      <div className="flex items-end gap-2 rounded-xl border border-slate-200 bg-white p-2 transition focus-within:border-brand-400 focus-within:ring-2 focus-within:ring-brand-100">
        <textarea
          rows={2}
        //   disabled
          placeholder="Ask a question about your selected documents..."
          className="min-w-0 flex-1 resize-none bg-transparent p-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
        />

        <button
          type="button"
        //   disabled
          aria-label="Send message"
          className="rounded-lg bg-brand-500 p-2.5 text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <LuArrowUp size={17} />
        </button>
      </div>
    </div>
  );
}
