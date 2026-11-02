
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

// Chat request

export interface ChatRequest {
    conversation_id: string | null;
    message: string;
    document_ids: string[];
}

// SSE event payloads

export interface ChatMessageEvent {
    conversation_id: string;
    message: ConversationMessage;
}

export interface ChatProgressEvent {
    conversation_id: string;
    message: string;
}

export interface ChatEvidenceEvent {
    conversation_id: string;
    message_id: string;
    evidence: MessageEvidence;
    index: number;
    total: number;
}

export interface ChatCompleteEvent {
    conversation_id: string;
    user_message_id: string;
    assistant_message_id: string;
    status: "completed";
}

export interface ChatErrorEvent {
    conversation_id: string | null;
    message: string;
}

// Discriminated SSE event union

export type ChatStreamEvent =
    | {
          type: "user_message";
          data: ChatMessageEvent;
      }
    | {
          type: "answer";
          data: ChatMessageEvent;
      }
    | {
          type: "progress";
          data: ChatProgressEvent;
      }
    | {
          type: "evidence";
          data: ChatEvidenceEvent;
      }
    | {
          type: "complete";
          data: ChatCompleteEvent;
      }
    | {
          type: "error";
          data: ChatErrorEvent;
      };
