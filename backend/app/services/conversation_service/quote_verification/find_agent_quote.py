
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class QuoteOccurrence:
    start_offset: int
    end_offset: int



def build_quote_pattern(quote: str) -> re.Pattern[str] | None:
    """
    Build a regex that tolerates whitespace and punctuation
    differences between words in an agent-generated quote.

    Preserve punctuation inside tokens, such as 4.2,
    5,00,000, and 10%.
    """
    if not quote or not quote.strip():
        return None

    tokens: list[str] = re.findall(
        r"[^\W_]+(?:[.,/-][^\W_]+)*%?",
        quote,
        flags=re.UNICODE,
    )

    if not tokens:
        return None

    pattern: str = r"[\W_]+".join(
        re.escape(token)
        for token in tokens
    )

    return re.compile(pattern, re.IGNORECASE)



def find_quote_occurrences(
    canonical_text: str,
    quote: str,
) -> list[QuoteOccurrence]:
    """
    Search the original canonical text directly.

    Returned offsets refer to canonical_text.
    """
    pattern = build_quote_pattern(quote)

    if pattern is None:
        return []

    occurrences: list[QuoteOccurrence] = []

    # Lookahead allows overlapping occurrences to be found.
    lookahead_pattern = re.compile(
        rf"(?=({pattern.pattern}))",
        pattern.flags,
    )

    for match in lookahead_pattern.finditer(canonical_text):
        start: int = match.start(1)
        end: int = match.end(1)

        occurrences.append(
            QuoteOccurrence(
                start_offset=start,
                end_offset=end,
            )
        )

    return occurrences
