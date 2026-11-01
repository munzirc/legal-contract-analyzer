
export interface Conversation {
    conversation_id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export type ConversationList = Conversation[];

export interface DeleteConversationResponse {
    conversation_id: string;
    deleted: boolean;
}
