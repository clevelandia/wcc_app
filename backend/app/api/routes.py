from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.analysis.budget_delta import budget_delta
from app.analysis.semantic_diff import semantic_diff
from app.db import get_conn, init_db, list_jobs
from app.ingestion.legistar_ingest import run_legistar_ingest
from app.ragg.briefs import generate_organizer_brief

router = APIRouter()


@router.get('/health')
def health() -> dict[str, str]:
    init_db()
    return {'status': 'ok'}


@router.get('/search')
def search(
    q: str = Query(...),
    types: str | None = None,
    from_date: str | None = Query(None, alias='from'),
    to_date: str | None = Query(None, alias='to'),
) -> dict:
    type_list = set((types or 'meetings,agenda_items,ordinances,documents,news').split(','))
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None

    results: list[dict] = []
    with get_conn() as conn, conn.cursor() as cur:
        if 'meetings' in type_list:
            cur.execute(
                """
                select id, title, meeting_date as date,
                  ts_rank(search, plainto_tsquery('english', %s)) as score,
                  ts_headline('english', coalesce(title,'') || ' ' || coalesce(body,''), plainto_tsquery('english', %s)) as snippet
                from meetings
                where search @@ plainto_tsquery('english', %s)
                  and (%s::timestamptz is null or meeting_date >= %s)
                  and (%s::timestamptz is null or meeting_date <= %s)
                order by score desc, meeting_date desc
                limit 40
                """,
                (q, q, q, from_dt, from_dt, to_dt, to_dt),
            )
            results.extend({
                'id': f"meeting:{r['id']}", 'title': r['title'], 'type': 'meeting', 'date': r['date'],
                'snippet': r['snippet'], 'citations': [{'source': 'meeting record'}], 'score': float(r['score'])
            } for r in cur.fetchall())

        if 'agenda_items' in type_list:
            cur.execute(
                """
                select ai.id, ai.title, m.meeting_date as date,
                  ts_rank(ai.search, plainto_tsquery('english', %s)) as score,
                  ts_headline('english', coalesce(ai.title,'') || ' ' || coalesce(ai.description,''), plainto_tsquery('english', %s)) as snippet
                from agenda_items ai
                left join meetings m on m.id = ai.meeting_id
                where ai.search @@ plainto_tsquery('english', %s)
                order by score desc
                limit 40
                """,
                (q, q, q),
            )
            results.extend({
                'id': f"agenda_item:{r['id']}", 'title': r['title'], 'type': 'agenda_item', 'date': r['date'],
                'snippet': r['snippet'], 'citations': [{'source': 'agenda', 'line': 1}], 'score': float(r['score'])
            } for r in cur.fetchall())

        if 'ordinances' in type_list:
            cur.execute(
                """
                select id, title, passed_date as date,
                  ts_rank(search, plainto_tsquery('english', %s)) as score,
                  ts_headline('english', coalesce(title,'') || ' ' || coalesce(status,''), plainto_tsquery('english', %s)) as snippet
                from matters
                where search @@ plainto_tsquery('english', %s)
                order by score desc, passed_date desc
                limit 40
                """,
                (q, q, q),
            )
            results.extend({
                'id': f"ordinance:{r['id']}", 'title': r['title'], 'type': 'ordinance', 'date': r['date'],
                'snippet': r['snippet'], 'citations': [{'source': 'matter'}], 'score': float(r['score'])
            } for r in cur.fetchall())

        if 'documents' in type_list:
            cur.execute(
                """
                select id, title,
                  ts_rank(search, plainto_tsquery('english', %s)) as score,
                  ts_headline('english', coalesce(text_content,''), plainto_tsquery('english', %s)) as snippet,
                  citations
                from documents
                where search @@ plainto_tsquery('english', %s)
                order by score desc
                limit 40
                """,
                (q, q, q),
            )
            results.extend({
                'id': r['id'], 'title': r['title'], 'type': 'document', 'date': None,
                'snippet': r['snippet'], 'citations': r['citations'] or [], 'score': float(r['score'])
            } for r in cur.fetchall())

    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return {'results': results[:120]}


@router.get('/meetings')
def meetings(from_date: str | None = Query(None, alias='from'), to_date: str | None = Query(None, alias='to'), keyword: str | None = None) -> dict:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select id, title, body, meeting_date, location, status
            from meetings
            where (%s::timestamptz is null or meeting_date >= %s)
              and (%s::timestamptz is null or meeting_date <= %s)
              and (%s::text is null or search @@ plainto_tsquery('english', %s))
            order by meeting_date desc
            limit 200
            """,
            (from_date, from_date, to_date, to_date, keyword, keyword),
        )
        rows = list(cur.fetchall())
    return {'items': rows}


@router.get('/meetings/{meeting_id}')
def meeting_detail(meeting_id: int) -> dict:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('select * from meetings where id = %s', (meeting_id,))
        meeting = cur.fetchone()
        if not meeting:
            raise HTTPException(404, 'Meeting not found')
        cur.execute('select * from agenda_items where meeting_id=%s order by agenda_sequence nulls last, id', (meeting_id,))
        agenda = list(cur.fetchall())
        cur.execute("select * from documents where source_type='meeting' and source_id=%s", (meeting_id,))
        docs = list(cur.fetchall())
        cur.execute('select v.* from votes v where meeting_id=%s', (meeting_id,))
        vote_rows = list(cur.fetchall())
    return {'meeting': meeting, 'agenda_items': agenda, 'documents': docs, 'votes': vote_rows}


@router.get('/documents/{doc_id:path}')
def document_detail(doc_id: str) -> dict:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('select * from documents where id=%s', (doc_id,))
        doc = cur.fetchone()
        if not doc:
            raise HTTPException(404, 'Document not found')
    return {'document': doc}


@router.get('/ordinances/{matter_id}')
def ordinance_detail(matter_id: int) -> dict:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute('select * from matters where id=%s', (matter_id,))
        matter = cur.fetchone()
        if not matter:
            raise HTTPException(404, 'Ordinance not found')
        cur.execute('select * from agenda_items where matter_id=%s order by id', (matter_id,))
        versions = list(cur.fetchall())
        cur.execute('select * from votes where matter_id=%s', (matter_id,))
        vote_rows = list(cur.fetchall())
    return {'ordinance': matter, 'versions': versions, 'votes': vote_rows, 'diff': None}


@router.post('/admin/ingest')
def admin_ingest(mode: str = 'incremental', source: str = 'whatcom_legistar_api', from_date: str | None = None, to_date: str | None = None) -> dict:
    result = run_legistar_ingest(mode=mode, source=source, from_date=from_date, to_date=to_date)
    return result.__dict__


@router.get('/jobs')
def jobs() -> dict:
    return {'items': list_jobs()}

# preserve analysis endpoints
@router.post('/analysis/budget-delta')
def budget(req: dict) -> dict:
    return budget_delta(req['old_rows'], req['new_rows'])


@router.post('/analysis/semantic-diff')
def sem_diff(req: dict) -> dict:
    changes = semantic_diff(req['old_sections'], req['new_sections'])
    return {'changes': [c.__dict__ for c in changes]}


@router.post('/briefs/organizer')
def organizer_brief(req: dict) -> dict:
    return generate_organizer_brief(req['topic'], req['factual_hits'], req['theory_hits'])
