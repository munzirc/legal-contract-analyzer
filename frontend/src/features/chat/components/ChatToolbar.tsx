
import { useState } from "react";
import {
    LuFileText,
    LuPlus,
    LuSparkles,
} from "react-icons/lu";

import { useConversationStore } from "../../../stores/useConversationStore";
import ConversationDocumentsDialog from "./ConversationDocumentsDialog";

export default function ChatToolbar() {
    const [isDocumentsDialogOpen, setIsDocumentsDialogOpen] =
        useState(false);

    const startNewChat = useConversationStore(
        (state) => state.startNewChat
    );

    const conversationDocumentIds = useConversationStore(
        (state) => state.conversationDocumentIds
    );

    return (
        <>
            <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b border-slate-200 px-4">
                <div className="flex min-w-0 items-center gap-2">
                    <LuSparkles
                        size={19}
                        className="shrink-0 text-brand-600"
                    />

                    <h2 className="truncate text-sm font-semibold text-slate-900">
                        Ask Legal Expert
                    </h2>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        type="button"
                        onClick={startNewChat}
                        title="New chat"
                        className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-medium text-brand-700 transition hover:bg-brand-50"
                    >
                        <LuPlus size={15} />
                        <span>New chat</span>
                    </button>

                    <button
                        type="button"
                        onClick={() => setIsDocumentsDialogOpen(true)}
                        title="Manage conversation documents"
                        className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-700 transition hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700"
                    >
                        <LuFileText size={15} />
                        <span>Documents</span>

                        <span className="rounded-full bg-brand-100 px-1.5 py-0.5 text-[10px] font-semibold text-brand-700">
                            {conversationDocumentIds.length}
                        </span>
                    </button>
                </div>
            </header>

            <ConversationDocumentsDialog
                open={isDocumentsDialogOpen}
                onOpenChange={setIsDocumentsDialogOpen}
            />
        </>
    );
}
