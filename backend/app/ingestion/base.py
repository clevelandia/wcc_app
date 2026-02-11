from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, Protocol


@dataclass(frozen=True)
class DiscoveredItem:
    stable_id: str
    canonical_url: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RawFetch:
    body: bytes
    headers: dict[str, str]
    robots_policy: str


@dataclass(frozen=True)
class NormalizedRecord:
    record_type: str
    stable_id: str
    canonical_url: str
    payload: dict[str, Any]
    source_id: str
    content_hash: str
    retrieved_at: datetime
    robots_policy: str


class SourceAdapter(Protocol):
    source_id: str

    def discover(self) -> list[DiscoveredItem]: ...

    def fetch(self, item: DiscoveredItem) -> RawFetch: ...

    def parse(self, raw: RawFetch) -> list[NormalizedRecord]: ...

    def link(self, records: list[NormalizedRecord]) -> list[NormalizedRecord]: ...


class AdapterError(RuntimeError):
    pass


def make_content_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
