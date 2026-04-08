from pydantic import BaseModel


class Prompt(BaseModel):
    question: str
    answer: str
    question_attachment: str | None = None
    answer_attachment: str | None = None


class Section(BaseModel):
    heading: str
    level: int
    content: str
    start_line: int
    end_line: int


class AnnotatedSection(BaseModel):
    section: Section
    prompts: list[Prompt]
