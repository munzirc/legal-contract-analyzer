import { API_BASE_URL } from "../documents/api";
import type { ConversationHistory, ConversationDocumentsResponse } from "./types";

export async function getConversationHistory(
    conversationId: string
): Promise<ConversationHistory> {
    const response = await fetch(
        `${API_BASE_URL}/api/conversations/${conversationId}/messages`
    );

    if (!response.ok) {
        let message = "Failed to load conversation history.";

        try {
            const error = await response.json();
            message = error.detail ?? message;
        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }

    return response.json() as Promise<ConversationHistory>;
}


export async function addConversationDocuments(
    conversationId: string,
    documentIds: string[]
): Promise<ConversationDocumentsResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/conversations/${conversationId}/documents`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                document_ids: documentIds,
            }),
        }
    );

    if (!response.ok) {
        const data = await response.json();
        throw new Error(
            data.detail ?? "Failed to add documents to conversation."
        );
    }

    return response.json();
}

export async function removeConversationDocument(
    conversationId: string,
    documentId: string
): Promise<ConversationDocumentsResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/conversations/${conversationId}/document/${documentId}`,
        {
            method: "DELETE",
        }
    );

    if (!response.ok) {
        const data = await response.json();
        throw new Error(
            data.detail ?? "Failed to remove document from conversation."
        );
    }

    return response.json();
}