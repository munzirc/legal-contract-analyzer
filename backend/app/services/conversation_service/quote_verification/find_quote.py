from dataclasses import dataclass


@dataclass(frozen=True)
class QuoteOccurrence:
    start_offset: int
    end_offset: int



def normalized_to_original_offset(
    normalized_offset: int,
    whitespace_runs: list[dict[str, int]],
) -> int:
    original_offset = normalized_offset

    for run in whitespace_runs:
        run_offset = run["normalized_offset"]
        original_length = (
            run["original_end"] - run["original_start"]
        )

        # Leading whitespace has no corresponding character in
        # normalized_text, so account for its full original length.
        if run_offset == 0 and run["original_start"] == 0:
            original_offset += original_length
            continue

        # Interior whitespace is represented by one normalized space.
        # Include its expansion only for offsets after that space.
        if run_offset >= normalized_offset:
            break

        original_offset += original_length - 1

    return original_offset


def find_quote_occurrences(
    canonical_text: str,
    normalized_text: str,
    whitespace_runs: list[dict[str, int]],
    quote: str,
) -> list[QuoteOccurrence]:
    normalized_quote = " ".join(quote.split())

    if not normalized_quote:
        return []

    occurrences: list[QuoteOccurrence] = []
    search_from = 0

    while True:
        match_start = normalized_text.find(
            normalized_quote,
            search_from,
        )

        if match_start == -1:
            break

        match_end = match_start + len(normalized_quote)

        original_start = normalized_to_original_offset(
            match_start,
            whitespace_runs,
        )
        original_end = normalized_to_original_offset(
            match_end,
            whitespace_runs,
        )

        # Verify the actual passage in the original canonical text.
        original_quote = canonical_text[
            original_start:original_end
        ]

        if " ".join(original_quote.split()) == normalized_quote:
            occurrences.append(
                QuoteOccurrence(
                    start_offset=original_start,
                    end_offset=original_end,
                )
            )

        # Find overlapping occurrences too.
        search_from = match_start + 1

    return occurrences