from __future__ import annotations

import requests

from app.ingestion.base import DiscoveredItem, NormalizedRecord, RawFetch, SourceAdapter, make_content_hash, now_utc


class GISAdapter(SourceAdapter):
    source_id = "whatcom_gis"

    def __init__(self, endpoint: str, dataset_name: str) -> None:
        self.endpoint = endpoint
        self.dataset_name = dataset_name

    def discover(self) -> list[DiscoveredItem]:
        return [DiscoveredItem(stable_id=f"gis:{self.dataset_name}", canonical_url=self.endpoint, metadata={})]

    def fetch(self, item: DiscoveredItem) -> RawFetch:
        resp = requests.get(self.endpoint, timeout=20)
        body = resp.content
        return RawFetch(body=body, headers={"ETag": resp.headers.get("ETag", make_content_hash(body))}, robots_policy="allow")

    def parse(self, raw: RawFetch) -> list[NormalizedRecord]:
        return [
            NormalizedRecord(
                record_type="document",
                stable_id=f"gis:{self.dataset_name}:{make_content_hash(raw.body)[:8]}",
                canonical_url=self.endpoint,
                payload={
                    "id": f"gis:{self.dataset_name}:{make_content_hash(raw.body)[:8]}",
                    "title": f"GIS Dataset: {self.dataset_name}",
                    "text": raw.body.decode("utf-8", errors="ignore")[:4000],
                    "page_count": 1,
                },
                source_id=self.source_id,
                content_hash=make_content_hash(raw.body),
                retrieved_at=now_utc(),
                robots_policy=raw.robots_policy,
            )
        ]

    def link(self, records: list[NormalizedRecord]) -> list[NormalizedRecord]:
        return records
