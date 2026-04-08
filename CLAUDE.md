# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

withorbit generates spaced repetition prompts for Markdown documents using the mnemonic medium approach (quantum.country, numinous.productions/ttft). It embeds prompts using Orbit web components (`<orbit-reviewarea>`, `<orbit-prompt>`).

## Commands

```bash
uv sync                              # Install dependencies
uv run pytest tests/ -v              # Run all tests
uv run pytest tests/test_markdown_parser.py::test_no_headings  # Single test
uv run withorbit --help              # CLI help
uv run withorbit html input.md -o output.html    # Markdown → HTML with Orbit widgets
uv run withorbit obsidian input.md --in-place     # Insert [!orbit] callouts into Obsidian notes
uv run withorbit --dry-run html input.md          # Preview prompts without writing
```

## Architecture

- **`src/withorbit/cli.py`** — Click CLI with `html` and `obsidian` subcommands. Shared options: `--color`, `--dry-run`, `--verbose`.
- **`src/withorbit/core/`** — Shared core used by both commands:
  - `models.py` — Pydantic models: `Prompt`, `Section`, `AnnotatedSection`
  - `markdown_parser.py` — Splits Markdown into `Section` objects at heading boundaries using markdown-it-py's token stream
  - `prompt_generator.py` — Shells out to `claude` CLI with `--json-schema` for structured output. Sends one request per section with the full document as context. The system prompt encodes mnemonic medium principles (atomicity, warm-up prompts, interconnection).
- **`src/withorbit/html/`** — Renders annotated sections to a standalone HTML page using Jinja2 template with Orbit script tag. `template.html` is loaded via `importlib.resources`.
- **`src/withorbit/obsidian/`** — Injects `> [!orbit]` callouts into Markdown. Each callout has plain-text Q&A (readable in edit mode) and Orbit HTML (interactive in reading view). Idempotent: strips existing callouts before re-inserting.

## Key Design Decisions

- Prompt generation uses Claude Code subprocess (`claude --print --output-format json --json-schema ...`) rather than the Anthropic API SDK — runs against existing Pro subscription with no extra cost.
- Obsidian callouts use `[!orbit]-` (collapsed by default) with both human-readable Q&A text AND raw Orbit HTML inside.
- The Obsidian injector is idempotent — safe to run `--in-place` repeatedly.
- HTML attributes in Orbit tags must be HTML-escaped (`html.escape`). LaTeX `$...$` passes through.
