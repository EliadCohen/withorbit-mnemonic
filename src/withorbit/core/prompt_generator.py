import json
import subprocess

import click

from withorbit.core.markdown_parser import parse_sections
from withorbit.core.models import AnnotatedSection, Prompt, Section

SYSTEM_PROMPT = """\
You are an expert author of spaced repetition prompts following the mnemonic medium \
principles (quantum.country, numinous.productions/ttft).

Given a section of an essay and the full essay for context, generate spaced repetition prompts.

Principles:
- ATOMIC: each prompt tests exactly one concept
- UNAMBIGUOUS: exactly one correct answer
- CONCISE answers (1-2 sentences max)
- For early sections, include 1 easy "warm-up" prompt
- Use the essay's terminology; support LaTeX ($...$) for math if the essay uses it
- Focus on underlying concepts, not meta-content about the essay itself
- Prompts should form an interconnected web — later prompts can build on earlier concepts
- Generate 2-5 prompts per section. Fewer for short/simple sections, more for dense technical ones.
- It is better to have fewer excellent prompts than many mediocre ones.
"""

PROMPT_JSON_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "prompts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                },
                "required": ["question", "answer"],
            },
        },
    },
    "required": ["prompts"],
})


def generate_prompts(
    full_document: str,
    section: Section,
    section_index: int,
    total_sections: int,
    verbose: bool = False,
) -> list[Prompt]:
    """Generate spaced repetition prompts for a section by calling Claude Code CLI."""
    user_prompt = f"""\
Generate spaced repetition prompts for section {section_index + 1} of {total_sections}.

SECTION TO GENERATE PROMPTS FOR:
{section.content}

FULL DOCUMENT (for context only — generate prompts only for the section above):
{full_document}"""

    cmd = [
        "claude",
        "--print",
        "--output-format", "json",
        "--system-prompt", SYSTEM_PROMPT,
        "--json-schema", PROMPT_JSON_SCHEMA,
        "--tools", "",
        "--model", "sonnet",
        "--no-session-persistence",
        "-p", user_prompt,
    ]

    if verbose:
        click.echo(f"  Calling Claude for section: {section.heading}", err=True)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        click.echo(f"  Warning: Claude returned error for section '{section.heading}': {result.stderr}", err=True)
        return []

    try:
        response = json.loads(result.stdout)

        if response.get("is_error"):
            click.echo(f"  Warning: Claude error for '{section.heading}': {response.get('result', '')}", err=True)
            return []

        # --json-schema puts structured output in "structured_output" field
        parsed = response.get("structured_output")
        if parsed is None:
            # Fallback: try parsing the "result" text as JSON
            text = response.get("result", "")
            parsed = json.loads(text)

        return [Prompt(question=p["question"], answer=p["answer"]) for p in parsed["prompts"]]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        if verbose:
            click.echo(f"  Warning: Failed to parse response for '{section.heading}': {e}", err=True)
            click.echo(f"  Raw stdout: {result.stdout[:500]}", err=True)
        return []


def generate_all_prompts(
    markdown_text: str,
    verbose: bool = False,
) -> list[AnnotatedSection]:
    """Parse markdown into sections and generate prompts for each."""
    sections = parse_sections(markdown_text)
    annotated: list[AnnotatedSection] = []

    click.echo(f"Found {len(sections)} sections. Generating prompts...", err=True)

    for i, section in enumerate(sections):
        if section.heading == "(preamble)" and len(section.content.strip()) < 50:
            annotated.append(AnnotatedSection(section=section, prompts=[]))
            continue

        prompts = generate_prompts(
            full_document=markdown_text,
            section=section,
            section_index=i,
            total_sections=len(sections),
            verbose=verbose,
        )
        annotated.append(AnnotatedSection(section=section, prompts=prompts))
        click.echo(f"  [{i + 1}/{len(sections)}] {section.heading}: {len(prompts)} prompts", err=True)

    total = sum(len(a.prompts) for a in annotated)
    click.echo(f"Generated {total} prompts total.", err=True)
    return annotated
