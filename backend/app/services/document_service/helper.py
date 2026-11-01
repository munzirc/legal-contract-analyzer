
def build_line_offsets(text: str) -> tuple[list[int], int]:
    line_offsets: list[int] = []
    current_offset = 0

    for line in text.splitlines(keepends=True):
        line_offsets.append(current_offset)
        current_offset += len(line)

    total_lines = len(line_offsets)

    return line_offsets, total_lines


def get_offsets(
    text: str,
    line_offsets: list[int],
    start_line: int,
    end_line: int,
) -> tuple[int, int]:

    total_lines = len(line_offsets)

    if not 1 <= start_line <= total_lines:
        raise ValueError("start_line is outside the document.")

    if not start_line <= end_line <= total_lines:
        raise ValueError("Invalid end_line.")

    start_offset = line_offsets[start_line - 1]

    if end_line == total_lines:
        end_offset = len(text)
    else:
        end_offset = line_offsets[end_line]

    return start_offset, end_offset