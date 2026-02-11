from __future__ import annotations

from bs4 import BeautifulSoup
import requests

from app.ingestion.base import DiscoveredItem, NormalizedRecord, RawFetch, SourceAdapter, make_content_hash, now_utc


class LegistarHTMLFallbackAdapter(SourceAdapter):
    source_id = "whatcom_legistar_html"

    def __init__(self, listing_url: str) -> None:
        self.listing_url = listing_url

    def discover(self) -> list[DiscoveredItem]:
        html = requests.get(self.listing_url, timeout=20).text
        soup = BeautifulSoup(html, "html.parser")
        items: list[DiscoveredItem] = []
        for link in soup.select("a[href*='MeetingDetail.aspx?ID=']")[:10]:
            href = link.get("href", "")
            meeting_id = href.split("ID=")[-1]
            canonical = f"https://whatcom.legistar.com/{href.lstrip('/')}"
            items.append(DiscoveredItem(stable_id=f"meeting:{meeting_id}", canonical_url=canonical, metadata={"title": link.text.strip()}))
        return items

    def fetch(self, item: DiscoveredItem) -> RawFetch:
        html = requests.get(item.canonical_url, timeout=20).text.encode("utf-8")
        return RawFetch(body=html, headers={"ETag": make_content_hash(html)}, robots_policy="allow")

    def parse(self, raw: RawFetch) -> list[NormalizedRecord]:
        soup = BeautifulSoup(raw.body, "html.parser")
        title = soup.title.text.strip() if soup.title else "Whatcom County Meeting"
        return [
            NormalizedRecord(
                record_type="meeting",
                stable_id=f"meeting:html:{make_content_hash(raw.body)[:12]}",
                canonical_url="https://whatcom.legistar.com",
                payload={"id": f"meeting:html:{make_content_hash(raw.body)[:12]}", "title": title, "meeting_datetime": now_utc().isoformat()},
                source_id=self.source_id,
                content_hash=raw.headers.get("ETag", make_content_hash(raw.body)),
                retrieved_at=now_utc(),
                robots_policy=raw.robots_policy,
            )
        ]

    def link(self, records: list[NormalizedRecord]) -> list[NormalizedRecord]:
        return records
