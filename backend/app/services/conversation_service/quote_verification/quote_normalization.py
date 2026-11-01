import re
import unicodedata


UNICODE_ESCAPE_PATTERN: re.Pattern[str] = re.compile(
    r"\\u([0-9a-fA-F]{4})|\\U([0-9a-fA-F]{8})"
)

QUOTE_TRANSLATION: dict[int, str] = str.maketrans({
    "\u2018": "'",
    "\u2019": "'",
    "\u201a": "'",
    "\u201b": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u201e": '"',
    "\u201f": '"',
})


def normalize_agent_quote(quote: str) -> str:
    # Decode literal Unicode escape sequences returned by the agent.
    quote = UNICODE_ESCAPE_PATTERN.sub(
        lambda match: chr(
            int(match.group(1) or match.group(2), 16)
        ),
        quote,
    )

    # Remove escape backslashes before quotation marks.
    quote = re.sub(r"""\\(["'])""", r"\1", quote)

    # Normalize equivalent Unicode representations.
    quote = unicodedata.normalize("NFKC", quote)

    # Make typographic quotes consistent.
    quote = quote.translate(QUOTE_TRANSLATION)

    # Normalize whitespace.
    quote = re.sub(r"\s+", " ", quote).strip()

    return quote