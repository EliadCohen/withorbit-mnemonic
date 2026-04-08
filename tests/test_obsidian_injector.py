from withorbit.core.models import AnnotatedSection, Prompt, Section
from withorbit.obsidian.injector import inject_orbit_callouts, _strip_existing_callouts


def _make_annotated(heading: str, level: int, content: str,
                    start: int, end: int, prompts: list[Prompt]) -> AnnotatedSection:
    return AnnotatedSection(
        section=Section(heading=heading, level=level, content=content,
                        start_line=start, end_line=end),
        prompts=prompts,
    )


def test_inject_single_section():
    md = "# Intro\n\nSome content here."
    sections = [
        _make_annotated("Intro", 1, "# Intro\n\nSome content here.", 0, 3,
                        [Prompt(question="What is X?", answer="X is Y.")])
    ]
    result = inject_orbit_callouts(md, sections, "violet")
    assert "> [!orbit]- Review: Intro" in result
    assert "> **Q:** What is X?" in result
    assert "> **A:** X is Y." in result
    assert 'orbit-reviewarea color="violet"' in result
    assert 'orbit-prompt question="What is X?"' in result


def test_idempotent():
    md = "# Intro\n\nSome content here."
    sections = [
        _make_annotated("Intro", 1, "# Intro\n\nSome content here.", 0, 3,
                        [Prompt(question="What is X?", answer="X is Y.")])
    ]
    first = inject_orbit_callouts(md, sections, "violet")
    second = inject_orbit_callouts(first, sections, "violet")
    # Should have exactly one callout, not two
    assert second.count("> [!orbit]") == 1


def test_strip_existing_callouts():
    md = """# Intro

Some content.

> [!orbit]- Review: Intro
> **Q:** Old question?
> **A:** Old answer.
>
> <orbit-reviewarea color="violet">
>   <orbit-prompt question="Old question?" answer="Old answer."></orbit-prompt>
> </orbit-reviewarea>

More content after."""
    stripped = _strip_existing_callouts(md)
    assert "[!orbit]" not in stripped
    assert "More content after." in stripped
    assert "# Intro" in stripped


def test_no_prompts_no_callout():
    md = "# Intro\n\nSome content."
    sections = [
        _make_annotated("Intro", 1, "# Intro\n\nSome content.", 0, 3, [])
    ]
    result = inject_orbit_callouts(md, sections, "violet")
    assert "[!orbit]" not in result
