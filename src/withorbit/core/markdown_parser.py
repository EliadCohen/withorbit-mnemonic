from markdown_it import MarkdownIt

from withorbit.core.models import Section


def parse_sections(markdown_text: str) -> list[Section]:
    """Split markdown into sections at heading boundaries.

    Each section spans from one heading to the next (or end of document).
    If there are no headings, the entire document is returned as a single section.
    """
    md = MarkdownIt()
    tokens = md.parse(markdown_text)
    lines = markdown_text.split("\n")
    total_lines = len(lines)

    heading_positions: list[tuple[int, int, str]] = []  # (start_line, level, heading_text)

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == "heading_open":
            level = int(token.tag[1])  # h1->1, h2->2, etc.
            line = token.map[0] if token.map else 0
            # Next token is the heading inline content
            heading_text = ""
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                heading_text = tokens[i + 1].content
            heading_positions.append((line, level, heading_text))
        i += 1

    if not heading_positions:
        return [Section(
            heading="(document)",
            level=0,
            content=markdown_text,
            start_line=0,
            end_line=total_lines,
        )]

    sections: list[Section] = []

    # Content before the first heading (if any)
    first_heading_line = heading_positions[0][0]
    if first_heading_line > 0:
        pre_content = "\n".join(lines[:first_heading_line]).strip()
        if pre_content:
            sections.append(Section(
                heading="(preamble)",
                level=0,
                content=pre_content,
                start_line=0,
                end_line=first_heading_line,
            ))

    for idx, (start_line, level, heading_text) in enumerate(heading_positions):
        if idx + 1 < len(heading_positions):
            end_line = heading_positions[idx + 1][0]
        else:
            end_line = total_lines

        content = "\n".join(lines[start_line:end_line]).strip()
        sections.append(Section(
            heading=heading_text,
            level=level,
            content=content,
            start_line=start_line,
            end_line=end_line,
        ))

    return sections
