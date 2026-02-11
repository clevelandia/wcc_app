from __future__ import annotations

from contextlib import contextmanager

from fastapi.testclient import TestClient

from app.ingestion.legistar_ingest import _paged_get
from app.main import app


class FakeResponse:
    def __init__(self, payload, code=200):
        self._payload = payload
        self.status_code = code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('http error')

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = 0

    def get(self, *_args, **kwargs):
        skip = kwargs['params'].get('$skip', 0)
        self.calls += 1
        if skip == 0:
            return FakeResponse([{'EventId': 1}, {'EventId': 2}])
        if skip == 200:
            return FakeResponse([{'EventId': 3}])
        return FakeResponse([])


def test_backfill_paginates_all_pages():
    rows = _paged_get('/events', session=FakeSession())
    assert len(rows) == 3
    assert rows[-1]['EventId'] == 3


class FakeCursor:
    def __init__(self):
        self._rows = []

    def execute(self, query, params=None):
        q = query.lower()
        if 'from meetings' in q:
            self._rows = [{'id': 22, 'title': 'Housing Ordinance Hearing', 'date': None, 'score': 0.5, 'snippet': 'Housing <b>ordinance</b> hearing'}]
        else:
            self._rows = []

    def fetchall(self):
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


class FakeConn:
    def cursor(self):
        return FakeCursor()


@contextmanager
def fake_conn_cm():
    yield FakeConn()


def test_search_endpoint_returns_real_shape(monkeypatch):
    from app.api import routes
    import app.main as app_main

    monkeypatch.setattr(routes, 'get_conn', fake_conn_cm)
    monkeypatch.setattr(app_main, 'init_db', lambda: None)
    client = TestClient(app)
    resp = client.get('/api/search?q=ordinance&types=meetings')
    assert resp.status_code == 200
    data = resp.json()
    assert data['results']
    assert data['results'][0]['title'] == 'Housing Ordinance Hearing'
    assert data['results'][0]['citations']
