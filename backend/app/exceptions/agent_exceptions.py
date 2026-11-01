from google.genai.errors import APIError

def get_api_error_message(error: APIError) -> str:
    status_code = getattr(error, "code", None)

    if status_code in (429, 500, 503, 504):
        return (
            "The AI service is temporarily unavailable. "
            "Please try again shortly."
        )

    return (
        "The AI service request failed. "
        "Please try again. If the issue persists, contact support."
    )