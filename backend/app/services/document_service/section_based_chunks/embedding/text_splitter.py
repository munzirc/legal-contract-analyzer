
MAX_PIECE_LENGTH = 4000


def split_text(text: str) -> list[str]:
    if not text:
        return []

    pieces: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + MAX_PIECE_LENGTH, text_length)

        if end < text_length and not text[end].isspace():
            # The cut falls inside a word. Move backward to whitespace.
            while end > start and not text[end - 1].isspace():
                end -= 1

            # If there is no whitespace in this range, move forward
            # to the next whitespace so we don't create an empty piece.
            if end == start:
                end = min(start + MAX_PIECE_LENGTH, text_length)

                while end < text_length and not text[end].isspace():
                    end += 1

        piece = text[start:end]
        pieces.append(piece)

        start = end
        

    return pieces