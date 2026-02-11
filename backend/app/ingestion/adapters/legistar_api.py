from __future__ import annotations

import json
from typing import Any

import requests

from app.ingestion.base import DiscoveredItem, NormalizedRecord, RawFetch, SourceAdapter, make_content_hash, now_utc


class LegistarAPIAdapter(SourceAdapter):
    source_id = "whatcom_legistar_api"

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def discover(self) -> list[DiscoveredItem]:
        data = requests.get(self.endpoint, timeout=20).json()
        items: list[DiscoveredItem] = []
        for row in data:
            meeting_id = str(row["EventId"])
            items.append(
                DiscoveredItem(
                    stable_id=f"meeting:{meeting_id}",
                    canonical_url=f"https://whatcom.legistar.com/MeetingDetail.aspx?ID={meeting_id}",
                    metadata=row,
                )
            )
        return items

    def fetch(self, item: DiscoveredItem) -> RawFetch:
        body = json.dumps(item.metadata).encode("utf-8")
        return RawFetch(body=body, headers={"ETag": make_content_hash(body)}, robots_policy="allow")

    def parse(self, raw: RawFetch) -> list[NormalizedRecord]:
        payload: dict[str, Any] = json.loads(raw.body)
        meeting_id = str(payload["EventId"])
        record = NormalizedRecord(
            record_type="meeting",
            stable_id=f"meeting:{meeting_id}",
            canonical_url=f"https://whatcom.legistar.com/MeetingDetail.aspx?ID={meeting_id}",
            payload={
                "id": f"meeting:{meeting_id}",
                "title": payload.get("EventBodyName", "Whatcom County Council"),
                "meeting_datetime": payload["EventDate"],
                "location": payload.get("EventLocation"),
                "agenda_status": payload.get("EventAgendaStatusName", "Unknown"),
            },
            source_id=self.source_id,
            content_hash=raw.headers.get("ETag", make_content_hash(raw.body)),
            retrieved_at=now_utc(),
            robots_policy=raw.robots_policy,
        )
        return [record]

    def link(self, records: list[NormalizedRecord]) -> list[NormalizedRecord]:
        return records
