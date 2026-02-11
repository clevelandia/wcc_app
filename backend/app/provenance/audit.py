from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FetchAuditEvent:
    source_id: str
    url: str
    headers: dict[str, str]
    robots_policy: str
    fetched_at: datetime


@dataclass
class AuditLog:
    events: list[FetchAuditEvent] = field(default_factory=list)

    def record(self, source_id: str, url: str, headers: dict[str, str], robots_policy: str) -> None:
        self.events.append(
            FetchAuditEvent(
                source_id=source_id,
                url=url,
                headers=headers,
                robots_policy=robots_policy,
                fetched_at=datetime.now(timezone.utc),
            )
        )
