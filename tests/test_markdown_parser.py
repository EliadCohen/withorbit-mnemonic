from withorbit.core.markdown_parser import parse_sections


def test_no_headings():
    text = "Just a paragraph.\n\nAnother paragraph."
    sections = parse_sections(text)
    assert len(sections) == 1
    assert sections[0].heading == "(document)"
    assert sections[0].level == 0
    assert "Just a paragraph" in sections[0].content


def test_single_heading():
    text = "# Introduction\n\nSome content here."
    sections = parse_sections(text)
    assert len(sections) == 1
    assert sections[0].heading == "Introduction"
    assert sections[0].level == 1


def test_multiple_headings():
    text = "# First\n\nContent 1.\n\n## Second\n\nContent 2.\n\n# Third\n\nContent 3."
    sections = parse_sections(text)
    assert len(sections) == 3
    assert sections[0].heading == "First"
    assert sections[0].level == 1
    assert sections[1].heading == "Second"
    assert sections[1].level == 2
    assert sections[2].heading == "Third"
    assert sections[2].level == 1


def test_preamble_before_first_heading():
    text = "Some preamble text.\n\n# Heading\n\nContent."
    sections = parse_sections(text)
    assert len(sections) == 2
    assert sections[0].heading == "(preamble)"
    assert "preamble text" in sections[0].content
    assert sections[1].heading == "Heading"


def test_section_content_includes_heading():
    text = "# My Section\n\nParagraph one.\n\nParagraph two."
    sections = parse_sections(text)
    assert "# My Section" in sections[0].content
    assert "Paragraph one" in sections[0].content


def test_heading_in_code_block_ignored():
    text = "# Real Heading\n\n```\n# Not a heading\n```\n\nMore content."
    sections = parse_sections(text)
    assert len(sections) == 1
    assert sections[0].heading == "Real Heading"


def test_line_numbers():
    text = "# First\n\nContent.\n\n# Second\n\nMore content."
    sections = parse_sections(text)
    assert sections[0].start_line == 0
    assert sections[0].end_line == 4
    assert sections[1].start_line == 4
    assert sections[1].end_line == 7
