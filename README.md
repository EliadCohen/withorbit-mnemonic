# withorbit

Generate spaced repetition prompts from Markdown documents using Claude, and embed them with [Orbit](https://withorbit.com) web components — either as standalone HTML pages or directly inside Obsidian notes.

Inspired by the [mnemonic medium](https://numinous.productions/ttft/) as demonstrated by [Quantum Country](https://quantum.country): prompts are inserted at section breaks as you read, making retention deliberate rather than accidental.

## How it works

1. Your Markdown is split into sections at heading boundaries
2. Claude generates 2–5 spaced repetition prompts per section, following mnemonic medium principles (atomic, unambiguous, interconnected)
3. Prompts are embedded after each section using Orbit's `<orbit-reviewarea>` web components

Prompt generation runs via the Claude Code CLI — no separate API key or billing required beyond your existing Claude subscription.

## Installation

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/yourusername/withorbit
cd withorbit
uv sync
```

The `withorbit` command is then available via `uv run withorbit`.

To install globally:

```bash
uv tool install .
```

## Usage

### HTML output

Convert a Markdown file to a standalone HTML page with interactive Orbit review widgets:

```bash
withorbit html my-essay.md -o my-essay.html
```

Open the resulting HTML in any browser. Orbit widgets are interactive — they track your review history and schedule follow-up sessions via [withorbit.com](https://withorbit.com).

### Obsidian integration

Insert `[!orbit]` review callouts directly into an Obsidian Markdown note:

```bash
# Write to a new file
withorbit obsidian my-note.md -o my-note-orbit.md

# Modify the note in place
withorbit obsidian my-note.md --in-place
```

Each callout shows plain Q&A text (readable in Obsidian's edit mode) and includes Orbit HTML for interactive review in reading view:

```markdown
> [!orbit]- Review: Einstein's Explanation
> **Q:** What is the work function φ of a metal?
> **A:** The minimum energy required to free an electron from the metal's surface.
>
> <orbit-reviewarea color="violet">
>   <orbit-prompt question="What is the work function φ of a metal?" answer="The minimum energy required to free an electron from the metal's surface."></orbit-prompt>
> </orbit-reviewarea>
```

Callouts are collapsed by default (`[!orbit]-`) and foldable, so they don't clutter reading flow. Running `--in-place` again is safe — existing callouts are replaced, not duplicated.

> **Note:** Obsidian does not load external scripts by default. To make the `<orbit-reviewarea>` widgets interactive in reading view, install the [CustomJS](https://github.com/saml-dev/obsidian-custom-js) community plugin and load `https://js.withorbit.com/orbit-web-component.js`.

### Options

```
withorbit [--color COLOR] [--dry-run] [--verbose] COMMAND

Options:
  --color    Orbit theme color (default: violet)
             Choices: red, orange, brown, yellow, lime, green,
                      turquoise, cyan, blue, violet, purple, pink
  --dry-run  Print generated prompts without writing any files
  --verbose  Print debug output from Claude

Commands:
  html       Convert Markdown to HTML with Orbit review widgets
  obsidian   Insert [!orbit] callouts into an Obsidian Markdown note

withorbit html INPUT_FILE [-o OUTPUT_FILE]
withorbit obsidian INPUT_FILE [-o OUTPUT_FILE] [--in-place]
```

### Preview prompts before committing

Use `--dry-run` to inspect what Claude generates before writing any output:

```bash
withorbit --dry-run html my-essay.md
```

## Development

```bash
uv sync                              # Install all dependencies
uv run pytest tests/ -v              # Run tests
uv run pytest tests/test_markdown_parser.py::test_no_headings  # Single test
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. See [LICENSE](LICENSE) for details.
