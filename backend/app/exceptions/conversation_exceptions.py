class ConversationHasNoDocumentsError(Exception):
    """Raised when a conversation has no associated documents."""


class DocumentNotReadyError(Exception):
    """Raised when an associated document is not ready for analysis."""
    
class ConversationNotFoundError(Exception):
    """Raised when a conversation does not exist."""


class DocumentNotFoundError(Exception):
    """Raised when one or more requested documents do not exist."""


class ConversationDocumentNotFoundError(Exception):
    """Raised when a document is not associated with a conversation."""
    
class AgentResponseError(Exception):
    def __init__(
        self,
        message: str = "Sorry, I couldn't produce an answer. Please try again.",
    ):
        self.message = message
        super().__init__(self.message)