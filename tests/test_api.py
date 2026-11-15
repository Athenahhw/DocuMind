
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200


def test_search_route_exists():
    routes = {
        (route.path, method)
        for route in app.routes
        for method in getattr(route, "methods", [])
    }

    assert ("/search", "POST") in routes


def test_ask_route_exists():
    routes = {
        (route.path, method)
        for route in app.routes
        for method in getattr(route, "methods", [])
    }

    assert ("/ask", "POST") in routes


def test_unknown_endpoint():
    response = client.get(
        "/this-endpoint-does-not-exist"
    )

    assert response.status_code == 404
