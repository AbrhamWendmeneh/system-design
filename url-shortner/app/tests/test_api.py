import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


@pytest.fixture(autouse=True)
def clean_data():
    """Give every integration test an empty, deterministic data store."""
    connection = app_module.get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE urls RESTART IDENTITY")
        connection.commit()
    finally:
        connection.close()

    app_module.cache.flushdb()
    yield
    app_module.cache.flushdb()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_shorten_requires_url(client):
    response = client.post("/shorten", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing URL in request body"}


@pytest.mark.integration
def test_shorten_persists_and_caches_url(client):
    long_url = "https://www.google.com"

    response = client.post("/shorten", json={"url": long_url})

    assert response.status_code == 201
    assert response.get_json() == {
        "short_code": "1",
        "short_url": "http://localhost:5000/1",
    }
    assert app_module.cache.get("1") == long_url

    connection = app_module.get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT long_url FROM urls WHERE id = 1")
            assert cursor.fetchone() == (long_url,)
    finally:
        connection.close()


@pytest.mark.integration
def test_redirect_uses_cached_url(client):
    app_module.cache.set("a", "https://example.com/cached")

    response = client.get("/a")

    assert response.status_code == 302
    assert response.location == "https://example.com/cached"


@pytest.mark.integration
def test_redirect_falls_back_to_database_and_warms_cache(client):
    long_url = "https://example.com/from-database"
    created = client.post("/shorten", json={"url": long_url})
    short_code = created.get_json()["short_code"]
    app_module.cache.delete(short_code)

    response = client.get(f"/{short_code}")

    assert response.status_code == 302
    assert response.location == long_url
    assert app_module.cache.get(short_code) == long_url


@pytest.mark.integration
def test_unknown_valid_short_code_returns_404(client):
    response = client.get("/zzz")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Short URL not found"}


def test_invalid_short_code_returns_404(client):
    response = client.get("/favicon.ico")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Short URL not found"}
