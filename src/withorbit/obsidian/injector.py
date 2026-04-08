import re
from html import escape

from withorbit.core.models import AnnotatedSection, Prompt


def _build_callout(section_heading: str, prompts: list[Prompt], color: str) -> str:
    """Build an Obsidian [!orbit] callout block with plain Q&A and Orbit HTML."""
    lines = [f"> [!orbit]- Review: {section_heading}"]

    # Plain text Q&A for edit-mode readability
    for i, p in enumerate(prompts):
        if i > 0:
            lines.append(">")
        lines.append(f"> **Q:** {p.question}")
        lines.append(f"> **A:** {p.answer}")

    lines.append(">")

    # Orbit HTML for reading-view interactivity
    lines.append(f'> <orbit-reviewarea color="{color}">')
    for p in prompts:
        q = escape(p.question)
        a = escape(p.answer)
        attrs = f'question="{q}" answer="{a}"'
        if p.question_attachment:
            attrs += f' question-attachments="{escape(p.question_attachment)}"'
        if p.answer_attachment:
            attrs += f' answer-attachments="{escape(p.answer_attachment)}"'
        lines.append(f">   <orbit-prompt {attrs}></orbit-prompt>")
    lines.append("> </orbit-reviewarea>")

    return "\n".join(lines)


_ORBIT_CALLOUT_RE = re.compile(
    r"^> \[!orbit\].*\n(?:>.*\n)*",
    re.MULTILINE,
)


def _strip_existing_callouts(markdown_text: str) -> str:
    """Remove all existing [!orbit] callouts for idempotent re-insertion."""
    # Match callout blocks: start with "> [!orbit]" and continue while lines start with ">"
    lines = markdown_text.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("> [!orbit]"):
            # Skip all lines of this callout (lines starting with ">")
            while i < len(lines) and lines[i].startswith(">"):
                i += 1
            # Skip trailing blank line after callout
            if i < len(lines) and lines[i].strip() == "":
                i += 1
        else:
            result.append(lines[i])
            i += 1
    return "\n".join(result)


def inject_orbit_callouts(
    markdown_text: str,
    annotated_sections: list[AnnotatedSection],
    color: str,
) -> str:
    """Insert [!orbit] callouts into markdown after each section's content.

    Idempotent: existing [!orbit] callouts are removed before re-inserting.
    """
    cleaned = _strip_existing_callouts(markdown_text)
    lines = cleaned.split("\n")

    # Collect insertion points and callout blocks (back-to-front to preserve line numbers)
    # We need to recalculate line positions after stripping callouts, so we re-parse
    from withorbit.core.markdown_parser import parse_sections

    fresh_sections = parse_sections(cleaned)

    # Match annotated sections to fresh sections by heading
    heading_to_prompts: dict[str, list[Prompt]] = {}
    for ann in annotated_sections:
        if ann.prompts:
            heading_to_prompts[ann.section.heading] = ann.prompts

    # Build insertions back-to-front
    insertions: list[tuple[int, str]] = []
    for section in reversed(fresh_sections):
        prompts = heading_to_prompts.get(section.heading)
        if prompts:
            callout = _build_callout(section.heading, prompts, color)
            insertions.append((section.end_line, callout))

    for line_num, callout in insertions:
        # Insert callout block with surrounding blank lines
        callout_lines = ["", callout, ""]
        lines[line_num:line_num] = callout_lines

    return "\n".join(lines)
