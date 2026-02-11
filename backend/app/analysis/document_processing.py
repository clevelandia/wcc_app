from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class ExtractedDocument:
    text: str
    chunks: list[str]
    table_json: list[dict]
    citations: list[dict]


def process_document_text(text: str, chunk_size: int = 400) -> ExtractedDocument:
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    table_rows = _extract_pipe_tables(text)
    citations = [{"page": 1, "line_start": 1, "line_end": min(30, len(text.splitlines()) or 1)}]
    return ExtractedDocument(text=text, chunks=chunks, table_json=table_rows, citations=citations)


def _extract_pipe_tables(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if "|" in line:
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2 and not re.match(r"^-+$", cols[0]):
                rows.append({"columns": cols})
    return rows
