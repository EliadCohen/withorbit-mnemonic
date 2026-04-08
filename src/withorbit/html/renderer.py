from html import escape
from importlib.resources import files

from jinja2 import Template
from markdown_it import MarkdownIt

from withorbit.core.models import AnnotatedSection, Prompt


def render_orbit_block(prompts: list[Prompt], color: str) -> str:
    """Render an <orbit-reviewarea> HTML block from a list of prompts."""
    prompt_tags = []
    for p in prompts:
        attrs = f'question="{escape(p.question)}" answer="{escape(p.answer)}"'
        if p.question_attachment:
            attrs += f' question-attachments="{escape(p.question_attachment)}"'
        if p.answer_attachment:
            attrs += f' answer-attachments="{escape(p.answer_attachment)}"'
        prompt_tags.append(f"  <orbit-prompt {attrs}></orbit-prompt>")
    inner = "\n".join(prompt_tags)
    return f'<orbit-reviewarea color="{color}">\n{inner}\n</orbit-reviewarea>'


def render_html(annotated_sections: list[AnnotatedSection], color: str) -> str:
    """Render annotated sections into a complete HTML page with Orbit widgets."""
    md = MarkdownIt()
    content_parts: list[str] = []

    for section in annotated_sections:
        section_html = md.render(section.section.content)
        content_parts.append(section_html)

        if section.prompts:
            orbit_block = render_orbit_block(section.prompts, color)
            content_parts.append(orbit_block)

    content = "\n".join(content_parts)

    # Extract title from first heading
    title = "Document"
    for section in annotated_sections:
        if section.section.heading not in ("(document)", "(preamble)"):
            title = section.section.heading
            break

    template_text = files("withorbit.html").joinpath("template.html").read_text()
    template = Template(template_text)
    return template.render(title=title, color=color, content=content)
