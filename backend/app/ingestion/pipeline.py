from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import ValidationError

from app.ingestion.base import NormalizedRecord, SourceAdapter
from app.models.entities import AgendaItem, Document, Meeting, NewsItem


@dataclass
class QuarantineRecord:
    stable_id: str
    reason: str
    payload: dict[str, Any]
    timestamp: datetime


@dataclass
class InMemoryStore:
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def upsert(self, stable_id: str, payload: dict[str, Any], content_hash: str) -> bool:
        existing = self.records.get(stable_id)
        if existing and existing["content_hash"] == content_hash:
            return False
        self.records[stable_id] = {"payload": payload, "content_hash": content_hash}
        return True


class IngestionPipeline:
    def __init__(self) -> None:
        self.store = InMemoryStore()
        self.quarantine: list[QuarantineRecord] = []

    def run_adapter(self, adapter: SourceAdapter) -> dict[str, int]:
        inserted = 0
        duplicates = 0
        errors = 0
        for item in adapter.discover():
            raw = adapter.fetch(item)
            records = adapter.link(adapter.parse(raw))
            for record in records:
                try:
                    self._validate(record)
                    changed = self.store.upsert(record.stable_id, record.payload, record.content_hash)
                    inserted += 1 if changed else 0
                    duplicates += 0 if changed else 1
                except ValidationError as exc:
                    errors += 1
                    self.quarantine.append(
                        QuarantineRecord(
                            stable_id=record.stable_id,
                            reason=str(exc),
                            payload=record.payload,
                            timestamp=datetime.utcnow(),
                        )
                    )
        return {"inserted": inserted, "duplicates": duplicates, "errors": errors}

    def _validate(self, record: NormalizedRecord) -> None:
        if record.record_type == "meeting":
            Meeting.model_validate(record.payload | {"canonical_url": record.canonical_url, "provenance": self._prov(record)})
        elif record.record_type == "agenda_item":
            AgendaItem.model_validate(record.payload | {"canonical_url": record.canonical_url, "provenance": self._prov(record)})
        elif record.record_type == "document":
            Document.model_validate(record.payload | {"canonical_url": record.canonical_url, "provenance": self._prov(record)})
        elif record.record_type == "news_item":
            NewsItem.model_validate(record.payload | {"canonical_url": record.canonical_url, "provenance": self._prov(record)})

    @staticmethod
    def _prov(record: NormalizedRecord) -> dict[str, Any]:
        return {
            "source_id": record.source_id,
            "content_hash": record.content_hash,
            "retrieved_at": record.retrieved_at,
            "robots_policy": record.robots_policy,
        }
