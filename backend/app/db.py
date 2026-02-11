from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wcc:wcc@postgres:5432/wcc")


@contextmanager
def get_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                create table if not exists ingest_jobs (
                    id bigserial primary key,
                    source text not null,
                    mode text not null,
                    status text not null default 'running',
                    total_items int not null default 0,
                    processed_items int not null default 0,
                    failed_items int not null default 0,
                    retries int not null default 0,
                    message text,
                    created_at timestamptz not null default now(),
                    updated_at timestamptz not null default now()
                );

                create table if not exists source_sync_state (
                    source text primary key,
                    etag text,
                    last_modified text,
                    last_success_at timestamptz
                );

                create table if not exists meetings (
                    id bigint primary key,
                    title text not null,
                    body text,
                    meeting_date timestamptz,
                    location text,
                    status text,
                    agenda_file text,
                    minutes_file text,
                    raw jsonb not null default '{}'::jsonb,
                    search tsvector generated always as (
                      to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body,''))
                    ) stored
                );
                create index if not exists idx_meetings_search on meetings using gin(search);
                create index if not exists idx_meetings_date on meetings(meeting_date desc);

                create table if not exists agenda_items (
                    id bigint primary key,
                    meeting_id bigint references meetings(id) on delete cascade,
                    matter_id bigint,
                    title text not null,
                    description text,
                    agenda_sequence int,
                    raw jsonb not null default '{}'::jsonb,
                    search tsvector generated always as (
                      to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,''))
                    ) stored
                );
                create index if not exists idx_agenda_search on agenda_items using gin(search);

                create table if not exists matters (
                    id bigint primary key,
                    file_no text,
                    matter_type text,
                    title text not null,
                    status text,
                    intro_date timestamptz,
                    passed_date timestamptz,
                    raw jsonb not null default '{}'::jsonb,
                    search tsvector generated always as (
                      to_tsvector('english', coalesce(title,'') || ' ' || coalesce(file_no,''))
                    ) stored
                );
                create index if not exists idx_matters_search on matters using gin(search);

                create table if not exists votes (
                    id text primary key,
                    matter_id bigint references matters(id) on delete cascade,
                    meeting_id bigint,
                    person_name text,
                    vote_value text,
                    raw jsonb not null default '{}'::jsonb
                );

                create table if not exists documents (
                    id text primary key,
                    source_type text not null,
                    source_id bigint,
                    title text not null,
                    file_url text,
                    object_path text,
                    text_content text,
                    citations jsonb not null default '[]'::jsonb,
                    raw jsonb not null default '{}'::jsonb,
                    search tsvector generated always as (
                      to_tsvector('english', coalesce(title,'') || ' ' || coalesce(text_content,''))
                    ) stored
                );
                create index if not exists idx_documents_search on documents using gin(search);
                """
            )


def create_job(source: str, mode: str, total_items: int = 0) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "insert into ingest_jobs(source, mode, total_items) values (%s,%s,%s) returning id",
            (source, mode, total_items),
        )
        row = cur.fetchone()
        return int(row["id"])


def update_job(job_id: int, **kwargs: int | str) -> None:
    if not kwargs:
        return
    sets = [f"{k} = %s" for k in kwargs.keys()] + ["updated_at = now()"]
    values = list(kwargs.values()) + [job_id]
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"update ingest_jobs set {', '.join(sets)} where id = %s", values)


def list_jobs(limit: int = 30) -> list[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("select * from ingest_jobs order by created_at desc limit %s", (limit,))
        return list(cur.fetchall())
