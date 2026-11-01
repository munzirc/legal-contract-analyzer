
import {
    LuMessagesSquare,
    LuPanelLeftClose,
    LuPanelLeftOpen,
    LuPlus,
    LuSettings,
} from "react-icons/lu";

import { useAppStore } from "../stores/useAppStore";
import DocumentDropdown from "../features/documents/components/DocumentDropdown";
import DocumentUpload from "../features/documents/components/DocumentUpload";
import ConversationList from "../features/conversations/components/ConversationList";

export default function AppSidebar() {
    const sidebarExpanded = useAppStore(
        (state) => state.sidebarExpanded
    );

    const toggleSidebar = useAppStore(
        (state) => state.toggleSidebar
    );

    return (
        <aside className="flex min-h-0 flex-col border-r border-slate-200 bg-white">
            <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-3">
                {sidebarExpanded && (
                    <span className="text-brand-700 text-lg font-semibold tracking-tight">
                        Legal Experts
                    </span>
                )}

                <button
                    type="button"
                    onClick={toggleSidebar}
                    aria-label={
                        sidebarExpanded ? "Collapse sidebar" : "Expand sidebar"
                    }
                    title={sidebarExpanded ? "Collapse sidebar" : "Expand sidebar"}
                    className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-100"
                >
                    {sidebarExpanded ? (
                        <LuPanelLeftClose size={19} />
                    ) : (
                        <LuPanelLeftOpen size={19} />
                    )}
                </button>
            </header>

            <div className="flex min-h-0 flex-1 flex-col gap-6 p-3">
                <DocumentUpload collapsed={!sidebarExpanded} />

                {sidebarExpanded && (
                    <>
                        <DocumentDropdown />
                        <div className="shrink-0 border-t border-slate-200" />
                        <ConversationList />
                    </>
                )}
            </div>

            <footer className="shrink-0 border-t border-slate-200 p-3">
                <button
                    type="button"
                    title="Settings"
                    className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-100 ${sidebarExpanded ? "" : "justify-center"
                        }`}
                >
                    <LuSettings size={18} />
                    {sidebarExpanded && <span>Settings</span>}
                </button>
            </footer>
        </aside>
    );
}
