from __future__ import annotations

import feedparser

from app.ingestion.base import DiscoveredItem, NormalizedRecord, RawFetch, SourceAdapter, make_content_hash, now_utc


class RSSAdapter(SourceAdapter):
    source_id = "local_rss"

    def __init__(self, feed_url: str, publisher: str) -> None:
        self.feed_url = feed_url
        self.publisher = publisher

    def discover(self) -> list[DiscoveredItem]:
        feed = feedparser.parse(self.feed_url)
        return [
            DiscoveredItem(stable_id=f"news:{e.get('id', e.link)}", canonical_url=e.link, metadata=e)
            for e in feed.entries
        ]

    def fetch(self, item: DiscoveredItem) -> RawFetch:
        body = str(item.metadata).encode("utf-8")
        return RawFetch(body=body, headers={"ETag": make_content_hash(body)}, robots_policy="allow-snippet")

    def parse(self, raw: RawFetch) -> list[NormalizedRecord]:
        data = raw.body.decode("utf-8")
        return [
            NormalizedRecord(
                record_type="news_item",
                stable_id=f"news:{make_content_hash(raw.body)[:12]}",
                canonical_url=self.feed_url,
                payload={
                    "id": f"news:{make_content_hash(raw.body)[:12]}",
                    "title": data[:80],
                    "snippet": data[:280],
                    "publisher": self.publisher,
                    "published_at": now_utc().isoformat(),
                },
                source_id=self.source_id,
                content_hash=make_content_hash(raw.body),
                retrieved_at=now_utc(),
                robots_policy=raw.robots_policy,
            )
        ]

    def link(self, records: list[NormalizedRecord]) -> list[NormalizedRecord]:
        return records
