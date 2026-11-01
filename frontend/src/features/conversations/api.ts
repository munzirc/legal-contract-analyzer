import { API_BASE_URL } from "../documents/api";
import type {
  ConversationList,
  DeleteConversationResponse,
} from "./types";

export async function getConversations(): Promise<ConversationList> {
  const response = await fetch(`${API_BASE_URL}/api/conversations`);

  if (!response.ok) {
    let message = "Failed to load conversations.";

    try {
      const error = await response.json();
      message = error.detail ?? message;
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<ConversationList>;
}

export async function deleteConversation(
    conversationId: string
): Promise<DeleteConversationResponse> {
    const response = await fetch(
        `${API_BASE_URL}/api/conversations/${conversationId}`,
        {
            method: "DELETE",
        }
    );

    if (!response.ok) {
        let message = "Failed to delete conversation.";

        try {
            const error = await response.json();
            message = error.detail ?? message;
        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }

    return response.json() as Promise<DeleteConversationResponse>;
}