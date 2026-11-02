import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ConversationMessage, MessageEvidence } from "../types";
import { useAppStore } from "../../../stores/useAppStore";

interface ChatMessageProps {
    message: ConversationMessage;
}

function normalizeContent(content: string): string {
    return content
        .replace(/\\([*_`~])/g, "$1")
        .trim();
}

export default function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.role === "USER";

    const handleCitationClick = (evidence: MessageEvidence) => {
        if (!evidence.is_verified || evidence.regions.length === 0) {
            return;
        }

        const { setActiveDocument, setCitationTarget } =
            useAppStore.getState();

        setActiveDocument(evidence.document_id);

        setCitationTarget({
            documentId: evidence.document_id,
            evidenceId: evidence.id,
            regions: evidence.regions,
        });
    };

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${isUser
                        ? "bg-brand-500 text-white"
                        : "bg-slate-100 text-slate-900"
                    }`}
            >
                <div className="whitespace-pre-wrap">
                    {isUser ? (
                        normalizeContent(message.content)
                    ) : (
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                p: ({ children }) => (
                                    <p className="mb-2 last:mb-0">
                                        {children}
                                    </p>
                                ),
                                strong: ({ children }) => (
                                    <strong className="font-semibold">
                                        {children}
                                    </strong>
                                ),
                                ul: ({ children }) => (
                                    <ul className="mb-2 list-disc space-y-1 pl-5">
                                        {children}
                                    </ul>
                                ),
                                ol: ({ children }) => (
                                    <ol className="mb-2 list-decimal space-y-1 pl-5">
                                        {children}
                                    </ol>
                                ),
                            }}
                        >
                            {normalizeContent(message.content)}
                        </ReactMarkdown>
                    )}
                </div>

                {!isUser && message.evidence.length > 0 && (
                    <div className="mt-4 border-t border-slate-200 pt-3">
                        <p className="mb-2 text-xs font-semibold text-slate-500">
                            Sources
                        </p>

                        <div className="space-y-2">
                            {message.evidence.map((evidence, index) => {
                                const isClickable =
                                    evidence.is_verified && evidence.regions.length > 0;

                                return (
                                    <button
                                        key={evidence.id}
                                        type="button"
                                        disabled={!isClickable}
                                        onClick={() => handleCitationClick(evidence)}
                                        className={`block w-full cursor-pointer rounded-lg border px-3 py-2 text-left text-xs transition ${isClickable
                                                ? "border-slate-200 bg-white text-slate-700 hover:border-brand-300 hover:bg-brand-50"
                                                : "border-amber-200 bg-amber-50 text-slate-700"
                                            }`}
                                        title={
                                            isClickable
                                                ? "View this passage in the document"
                                                : "This source cannot be opened because it is unverified or has no coordinates"
                                        }
                                    >
                                        <span className="mb-2 flex items-center justify-between gap-2">
                                            <span className="font-semibold text-slate-600">
                                                Source {index + 1}
                                            </span>

                                            <span
                                                className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${evidence.is_verified
                                                        ? "bg-green-100 text-green-700"
                                                        : "bg-amber-100 text-amber-800"
                                                    }`}
                                            >
                                                {evidence.is_verified ? "Verified" : "Unverified"}
                                            </span>
                                        </span>

                                        <span className="block whitespace-pre-wrap leading-5">
                                            {normalizeContent(evidence.quote)}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}