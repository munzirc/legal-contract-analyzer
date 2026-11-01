import ChatInput from "../features/chat/components/ChatInput";
import ChatMessageList from "../features/chat/components/ChatMessageList";
import ChatToolbar from "../features/chat/components/ChatToolbar";


export default function ChatPanel() {
  return (
    <section className="flex min-h-0 min-w-0 flex-col overflow-scroll rounded-xl border border-slate-200 bg-white">
      <ChatToolbar />
      <div className="min-h-0 flex-1 overflow-hidden">
        <ChatMessageList />
      </div>

      <ChatInput />
    </section>
  );
}