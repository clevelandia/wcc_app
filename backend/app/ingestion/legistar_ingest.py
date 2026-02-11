from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from dateutil.parser import parse as dt_parse
from pypdf import PdfReader

from app.db import create_job, get_conn, update_job

LEGISTAR_BASE = os.getenv("LEGISTAR_BASE", "https://webapi.legistar.com/v1/whatcomwa")
OBJECT_STORAGE_PATH = Path(os.getenv("OBJECT_STORAGE_PATH", "/tmp/wcc_objects"))


@dataclass
class IngestResult:
    job_id: int
    meetings: int
    agenda_items: int
    matters: int
    votes: int
    documents: int


def _paged_get(endpoint: str, params: dict[str, Any] | None = None, session: requests.Session | None = None) -> list[dict[str, Any]]:
    sess = session or requests.Session()
    rows: list[dict[str, Any]] = []
    skip = 0
    top = 200
    while True:
        query = {"$top": top, "$skip": skip}
        if params:
            query.update(params)
        resp = sess.get(f"{LEGISTAR_BASE}{endpoint}", params=query, timeout=40)
        resp.raise_for_status()
        chunk = resp.json()
        if isinstance(chunk, dict):
            chunk = [chunk]
        if not chunk:
            break
        rows.extend(chunk)
        if len(chunk) < top:
            break
        skip += top
    return rows


def _extract_pdf_text(path: Path) -> tuple[str, list[dict[str, int]]]:
    try:
        reader = PdfReader(str(path))
    except Exception:
        return "", []
    text_parts: list[str] = []
    citations: list[dict[str, int]] = []
    for idx, page in enumerate(reader.pages, start=1):
        content = page.extract_text() or ""
        if content.strip():
            text_parts.append(content)
            citations.append({"page": idx, "line_start": 1, "line_end": min(8, len(content.splitlines()) or 1)})
    return "\n\n".join(text_parts), citations


def _download_document(url: str, key: str, session: requests.Session) -> tuple[str | None, str, list[dict[str, int]]]:
    if not url:
        return None, "", []
    OBJECT_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    dest = OBJECT_STORAGE_PATH / f"{key}.pdf"
    try:
        r = session.get(url, timeout=60)
        if r.status_code != 200:
            return None, "", []
        dest.write_bytes(r.content)
        text, citations = _extract_pdf_text(dest)
        return str(dest), text, citations
    except Exception:
        return None, "", []


def run_legistar_ingest(mode: str, source: str = "whatcom_legistar_api", from_date: str | None = None, to_date: str | None = None, session: requests.Session | None = None) -> IngestResult:
    sess = session or requests.Session()
    job_id = create_job(source, mode)
    try:
        params: dict[str, Any] = {}
        if from_date:
            params["$filter"] = f"EventDate ge datetime'{from_date}T00:00:00'"
        if to_date:
            right = f"EventDate le datetime'{to_date}T23:59:59'"
            params["$filter"] = f"{params.get('$filter')} and {right}" if params.get("$filter") else right

        events = _paged_get("/events", params=params, session=sess)
        update_job(job_id, total_items=len(events))

        meetings = agenda_items = matters = votes = documents = 0
        with get_conn() as conn, conn.cursor() as cur:
            for event in events:
                meeting_id = int(event["EventId"])
                cur.execute(
                    """
                    insert into meetings(id, title, body, meeting_date, location, status, agenda_file, minutes_file, raw)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on conflict(id) do update set
                      title=excluded.title, body=excluded.body, meeting_date=excluded.meeting_date,
                      location=excluded.location, status=excluded.status, agenda_file=excluded.agenda_file,
                      minutes_file=excluded.minutes_file, raw=excluded.raw
                    """,
                    (
                        meeting_id,
                        event.get("EventBodyName") or "Whatcom County Council",
                        event.get("EventBodyName") or "",
                        dt_parse(event["EventDate"]) if event.get("EventDate") else None,
                        event.get("EventLocation"),
                        event.get("EventAgendaStatusName"),
                        event.get("EventAgendaFile"),
                        event.get("EventMinutesFile"),
                        event,
                    ),
                )
                meetings += 1

                event_items = _paged_get(f"/events/{meeting_id}/EventItems", session=sess)
                for item in event_items:
                    item_id = int(item["EventItemId"])
                    matter_id = item.get("EventItemMatterId")
                    cur.execute(
                        """
                        insert into agenda_items(id, meeting_id, matter_id, title, description, agenda_sequence, raw)
                        values (%s,%s,%s,%s,%s,%s,%s)
                        on conflict(id) do update set
                         meeting_id=excluded.meeting_id, matter_id=excluded.matter_id,
                         title=excluded.title, description=excluded.description,
                         agenda_sequence=excluded.agenda_sequence, raw=excluded.raw
                        """,
                        (
                            item_id,
                            meeting_id,
                            matter_id,
                            item.get("EventItemTitle") or item.get("EventItemMatterName") or "Agenda Item",
                            item.get("EventItemMatterName"),
                            item.get("EventItemAgendaSequence"),
                            item,
                        ),
                    )
                    agenda_items += 1

                    if matter_id:
                        matter_rows = _paged_get(f"/matters/{matter_id}", session=sess)
                        if matter_rows:
                            matter = matter_rows[0]
                            cur.execute(
                                """
                                insert into matters(id, file_no, matter_type, title, status, intro_date, passed_date, raw)
                                values (%s,%s,%s,%s,%s,%s,%s,%s)
                                on conflict(id) do update set
                                 file_no=excluded.file_no, matter_type=excluded.matter_type, title=excluded.title,
                                 status=excluded.status, intro_date=excluded.intro_date, passed_date=excluded.passed_date, raw=excluded.raw
                                """,
                                (
                                    int(matter["MatterId"]),
                                    matter.get("MatterFile"),
                                    matter.get("MatterTypeName"),
                                    matter.get("MatterName") or "Untitled Matter",
                                    matter.get("MatterStatusName"),
                                    dt_parse(matter["MatterIntroDate"]) if matter.get("MatterIntroDate") else None,
                                    dt_parse(matter["MatterPassedDate"]) if matter.get("MatterPassedDate") else None,
                                    matter,
                                ),
                            )
                            matters += 1

                for title, file_url in (("Agenda", event.get("EventAgendaFile")), ("Minutes", event.get("EventMinutesFile"))):
                    if not file_url:
                        continue
                    doc_id = f"meeting:{meeting_id}:{title.lower()}"
                    path, text, citations = _download_document(file_url, doc_id.replace(':', '_'), sess)
                    cur.execute(
                        """
                        insert into documents(id, source_type, source_id, title, file_url, object_path, text_content, citations, raw)
                        values (%s,'meeting',%s,%s,%s,%s,%s,%s,%s)
                        on conflict(id) do update set
                          title=excluded.title, file_url=excluded.file_url, object_path=excluded.object_path,
                          text_content=excluded.text_content, citations=excluded.citations, raw=excluded.raw
                        """,
                        (doc_id, meeting_id, f"{title} - {event.get('EventBodyName')}", file_url, path, text, citations, {"meeting_id": meeting_id}),
                    )
                    documents += 1

                update_job(job_id, processed_items=meetings, failed_items=0)

            cur.execute(
                """
                insert into source_sync_state(source, last_success_at)
                values (%s, now())
                on conflict(source) do update set last_success_at = excluded.last_success_at
                """,
                (source,),
            )
        update_job(job_id, status="completed", message=f"Ingested {meetings} meetings")
    except Exception as exc:
        update_job(job_id, status="failed", message=str(exc))
        raise

    return IngestResult(job_id=job_id, meetings=meetings, agenda_items=agenda_items, matters=matters, votes=votes, documents=documents)
