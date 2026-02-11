from datetime import datetime, timezone

from app.analysis.budget_delta import budget_delta
from app.analysis.document_processing import process_document_text
from app.analysis.semantic_diff import semantic_diff
from app.ingestion.base import NormalizedRecord
from app.ingestion.pipeline import IngestionPipeline
from app.ragg.briefs import generate_organizer_brief
from app.search.service import SearchDoc, SearchService


def test_ingest_meeting_and_document_extraction_metadata():
    pipeline = IngestionPipeline()
    rec = NormalizedRecord(
        record_type="meeting",
        stable_id="meeting:1",
        canonical_url="https://whatcom.legistar.com/MeetingDetail.aspx?ID=1",
        payload={
            "id": "meeting:1",
            "title": "County Council",
            "meeting_datetime": "2026-01-10T10:00:00+00:00",
            "location": "Council Chambers",
            "agenda_status": "Final",
        },
        source_id="test",
        content_hash="abc",
        retrieved_at=datetime.now(timezone.utc),
        robots_policy="allow",
    )
    pipeline._validate(rec)

    extracted = process_document_text("Account | Amount\n001-123 | 100\n")
    assert extracted.text
    assert extracted.table_json
    assert extracted.citations[0]["page"] == 1


def test_budget_diff_outputs_structured_json():
    old = [{"account": "001-100", "amount": 100}]
    new = [{"account": "001-100", "amount": 150, "provenance": {"doc": "budget_v2"}}]
    result = budget_delta(old, new)
    assert result["changes"][0]["delta"] == 50
    assert result["changes"][0]["provenance"]["doc"] == "budget_v2"


def test_semantic_diff_detects_moved_clause():
    old_sections = {"2.1": "Maintain sidewalks", "2.2": "Publish annual report"}
    new_sections = {"4.3": "Maintain sidewalks", "2.2": "Publish annual report"}
    changes = semantic_diff(old_sections, new_sections)
    assert any(c.change_type == "moved" for c in changes)


def test_news_search_returns_relevant_items():
    service = SearchService()
    service.index(SearchDoc(id="news1", text="County council housing ordinance update", metadata={"type": "news"}))
    hits = service.fts("housing")
    assert hits and hits[0].id == "news1"


def test_organizer_brief_has_factual_and_theory_citations():
    brief = generate_organizer_brief(
        "housing ordinance",
        factual_hits=[{"text": "Council passed amendment", "citation": {"doc": "minutes"}}],
        theory_hits=[{"text": "Organizing framework", "citation": {"doc": "zotero-item"}}],
    )
    assert brief["evidence"][0]["source_type"] == "factual"
    assert brief["interpretation"][0]["source_type"] == "theory"
