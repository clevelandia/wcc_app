from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint(monkeypatch):
    import app.main as app_main

    monkeypatch.setattr(app_main, 'init_db', lambda: None)
    with TestClient(app) as client:
        response = client.get('/api/health')

        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}
