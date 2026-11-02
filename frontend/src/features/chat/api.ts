
import { API_BASE_URL } from "../documents/api";
import type {
    ChatRequest,
    ChatStreamEvent,
    ConversationHistory,
    ConversationDocumentsResponse,
} from "./types";

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

export async function removeConversationDocument(conversationId: string, documentId: string): Promise<ConversationDocumentsResponse> {
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

// Chat streaming

async function getStreamErrorMessage(response: Response): Promise<string> {
    const responseText = await response.text();

    if (responseText) {
        try {
            const data = JSON.parse(responseText);
            return data.detail ?? "Failed to start chat.";
        } catch {
            return responseText;
        }
    }

    return "Failed to start chat.";
}

export async function streamChat(
    request: ChatRequest,
    onEvent: (event: ChatStreamEvent) => void,
    signal?: AbortSignal
): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
        },
        body: JSON.stringify(request),
        signal,
    });

    if (!response.ok) {
        throw new Error(await getStreamErrorMessage(response));
    }

    if (!response.body) {
        throw new Error("The server did not return a response stream.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";
    let eventName = "";
    let dataLines: string[] = [];

    function dispatchEvent(): void {
        if (!eventName || dataLines.length === 0) {
            eventName = "";
            dataLines = [];
            return;
        }

        const eventTypes = [
            "user_message",
            "answer",
            "progress",
            "evidence",
            "complete",
            "error",
        ] as const;

        if (!eventTypes.includes(eventName as (typeof eventTypes)[number])) {
            eventName = "";
            dataLines = [];
            return;
        }

        const dataText = dataLines.join("\n");

        try {
            const data = JSON.parse(dataText);

            onEvent({
                type: eventName as ChatStreamEvent["type"],
                data,
            } as ChatStreamEvent);
        } catch {
            throw new Error(
                `Failed to parse the "${eventName}" event from the server.`
            );
        }

        eventName = "";
        dataLines = [];
    }

    function processLine(line: string): void {
        // Ignore comments and heartbeat lines.
        if (line.startsWith(":")) {
            return;
        }

        // An empty line marks the end of an SSE event.
        if (line === "") {
            dispatchEvent();
            return;
        }

        const separatorIndex = line.indexOf(":");

        const field =
            separatorIndex === -1
                ? line
                : line.slice(0, separatorIndex);

        let value =
            separatorIndex === -1
                ? ""
                : line.slice(separatorIndex + 1);

        // SSE removes at most one leading space after the colon.
        if (value.startsWith(" ")) {
            value = value.slice(1);
        }

        if (field === "event") {
            eventName = value;
        } else if (field === "data") {
            dataLines.push(value);
        }
    }

    try {
        while (true) {
            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(value, { stream: true });

            let newlineIndex = buffer.indexOf("\n");

            while (newlineIndex !== -1) {
                let line = buffer.slice(0, newlineIndex);

                if (line.endsWith("\r")) {
                    line = line.slice(0, -1);
                }

                processLine(line);

                buffer = buffer.slice(newlineIndex + 1);
                newlineIndex = buffer.indexOf("\n");
            }
        }

        // Flush any remaining decoder bytes.
        buffer += decoder.decode();

        // Process a final line if the stream ended without a newline.
        if (buffer.length > 0) {
            processLine(buffer.endsWith("\r") ? buffer.slice(0, -1) : buffer);
        }

        // Dispatch a final event if the stream ended without a blank line.
        dispatchEvent();
    } finally {
        reader.releaseLock();
    }
}
