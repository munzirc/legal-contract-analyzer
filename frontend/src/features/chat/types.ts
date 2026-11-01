export interface EvidenceRegion {
    page_number: number;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export interface MessageEvidence {
    id: string;
    document_id: string;
    quote: string;
    is_verified: boolean;
    regions: EvidenceRegion[];
}

export type MessageRole = "USER" | "ASSISTANT";

export interface ConversationMessage {
    id: string;
    role: MessageRole;
    content: string;
    created_at: string;
    evidence: MessageEvidence[];
}

export interface ConversationHistory {
    conversation_id: string;
    document_ids: string[];
    messages: ConversationMessage[];
}

export interface ConversationDocumentsResponse {
    conversation_id: string;
    document_ids: string[];
}