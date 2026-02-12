from fastapi.testclient import TestClient

from app.main import app


def test_jobs_endpoint(monkeypatch):
    import app.api.routes as api_routes

    expected_jobs = [
        {'id': 42, 'source': 'whatcom_legistar_api', 'status': 'completed'},
    ]
    monkeypatch.setattr(api_routes, 'list_jobs', lambda: expected_jobs)

    with TestClient(app) as client:
        response = client.get('/api/jobs')

    assert response.status_code == 200
    assert response.json() == {'items': expected_jobs}
