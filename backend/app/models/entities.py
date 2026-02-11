from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RecordType(str, Enum):
    meeting = "meeting"
    agenda_item = "agenda_item"
    matter = "matter"
    vote = "vote"
    document = "document"
    document_version = "document_version"
    change_event = "change_event"
    news_item = "news_item"
    search_index_entry = "search_index_entry"


class Provenance(BaseModel):
    source_id: str
    content_hash: str
    retrieved_at: datetime
    robots_policy: str


class BaseEntity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    canonical_url: HttpUrl
    provenance: Provenance


class Meeting(BaseEntity):
    title: str
    meeting_datetime: datetime
    location: str | None = None
    agenda_status: str | None = None


class AgendaItem(BaseEntity):
    meeting_id: str
    title: str
    description: str | None = None
    order: int
    matter_id: str | None = None


class Matter(BaseEntity):
    matter_type: str
    title: str
    status: str
    sponsor: str | None = None
    introduced_at: datetime | None = None


class Vote(BaseEntity):
    matter_id: str
    person_name: str
    vote_value: str


class CitationSpan(BaseModel):
    page: int
    line_start: int
    line_end: int


class Document(BaseEntity):
    title: str
    text: str
    page_count: int
    chunks: list[str] = Field(default_factory=list)
    table_json: list[dict[str, Any]] = Field(default_factory=list)
    citations: list[CitationSpan] = Field(default_factory=list)


class DocumentVersion(BaseEntity):
    document_id: str
    version_label: str
    created_at: datetime


class ChangeEvent(BaseEntity):
    document_id: str
    change_type: str
    summary: str
    citations: list[CitationSpan] = Field(default_factory=list)


class NewsItem(BaseEntity):
    title: str
    snippet: str
    publisher: str
    published_at: datetime | None = None


class SearchIndexEntry(BaseEntity):
    record_type: RecordType
    record_id: str
    plain_text: str
    embedding: list[float] = Field(default_factory=list)
