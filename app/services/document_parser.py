from pathlib import Path

from pypdf import PdfReader
from docx import Document


def parse_pdf(
    file_path: str
) -> str:

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def parse_docx(
    file_path: str
) -> str:

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def parse_txt(
    file_path: str
) -> str:

    return Path(
        file_path
    ).read_text(
        encoding="utf-8"
    )


def parse_document(
    file_path: str
) -> str:

    extension = (
        Path(file_path)
        .suffix
        .lower()
    )

    if extension == ".pdf":
        return parse_pdf(file_path)

    if extension == ".docx":
        return parse_docx(file_path)

    if extension in [
        ".txt",
        ".md"
    ]:
        return parse_txt(file_path)

    raise ValueError(
        f"Unsupported file format: {extension}"
    )