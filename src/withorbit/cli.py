import click


@click.group()
@click.option("--color", default="violet", help="Orbit theme color", type=click.Choice(
    ["red", "orange", "brown", "yellow", "lime", "green",
     "turquoise", "cyan", "blue", "violet", "purple", "pink"],
))
@click.option("--dry-run", is_flag=True, help="Show generated prompts without writing output")
@click.option("--verbose", is_flag=True, help="Print debug information")
@click.pass_context
def cli(ctx: click.Context, color: str, dry_run: bool, verbose: bool) -> None:
    """Generate mnemonic medium spaced repetition prompts using Orbit."""
    ctx.ensure_object(dict)
    ctx.obj["color"] = color
    ctx.obj["dry_run"] = dry_run
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output HTML file path")
@click.pass_context
def html(ctx: click.Context, input_file: str, output: str | None) -> None:
    """Convert Markdown to HTML with embedded Orbit review prompts."""
    from pathlib import Path

    from withorbit.core.markdown_parser import parse_sections
    from withorbit.core.prompt_generator import generate_all_prompts
    from withorbit.html.renderer import render_html

    markdown_text = Path(input_file).read_text()
    annotated_sections = generate_all_prompts(markdown_text, verbose=ctx.obj["verbose"])

    if ctx.obj["dry_run"]:
        _print_prompts(annotated_sections)
        return

    html_output = render_html(annotated_sections, color=ctx.obj["color"])

    if output is None:
        output = str(Path(input_file).with_suffix(".html"))

    Path(output).write_text(html_output)
    click.echo(f"Written to {output}")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output Markdown file path")
@click.option("--in-place", is_flag=True, help="Modify the input file directly")
@click.pass_context
def obsidian(ctx: click.Context, input_file: str, output: str | None, in_place: bool) -> None:
    """Insert Orbit review callouts into an Obsidian Markdown note."""
    from pathlib import Path

    from withorbit.core.prompt_generator import generate_all_prompts
    from withorbit.obsidian.injector import inject_orbit_callouts

    input_path = Path(input_file)
    markdown_text = input_path.read_text()
    annotated_sections = generate_all_prompts(markdown_text, verbose=ctx.obj["verbose"])

    if ctx.obj["dry_run"]:
        _print_prompts(annotated_sections)
        return

    result = inject_orbit_callouts(markdown_text, annotated_sections, color=ctx.obj["color"])

    if in_place:
        input_path.write_text(result)
        click.echo(f"Updated {input_file}")
    else:
        out_path = Path(output) if output else input_path.with_stem(input_path.stem + "_orbit")
        out_path.write_text(result)
        click.echo(f"Written to {out_path}")


def _print_prompts(annotated_sections: list) -> None:
    for section in annotated_sections:
        if section.prompts:
            click.echo(f"\n## {section.section.heading}")
            for p in section.prompts:
                click.echo(f"  Q: {p.question}")
                click.echo(f"  A: {p.answer}")
                click.echo()
