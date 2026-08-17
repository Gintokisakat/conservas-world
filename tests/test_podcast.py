"""Tests del índice de podcasts (4.5): listado, filtros, topics y frontend."""

from app.main import app
from app.services.podcast import EPISODES, ferments_out, list_episodes, topics_out
from fastapi.testclient import TestClient

client = TestClient(app)


def test_episodes_curated():
    assert len(EPISODES) >= 15
    assert any(e.show == "FermUp" for e in EPISODES)
    assert any(e.show == "Ferment Radio" for e in EPISODES)


def test_episodes_have_urls():
    assert all(e.url.startswith("https://") for e in EPISODES)


def test_list_episodes_filter_topic():
    out = list_episodes(topic="ciencia", lang="es")
    assert out and all(e["topic"] == "ciencia" for e in out)


def test_list_episodes_filter_ferment():
    out = list_episodes(ferment="miso", lang="es")
    assert out
    for e in out:
        assert any("miso" in f.lower() for f in e["ferments"])


def test_list_episodes_bilingual():
    es = list_episodes(lang="es")
    en = list_episodes(lang="en")
    assert es[0]["title"] != en[0]["title"]


def test_topics_out():
    es = topics_out("es")
    en = topics_out("en")
    assert len(es) == len(en)
    assert es[0]["label"] != en[0]["label"]
    assert ferments_out()


def test_endpoint_list():
    r = client.get("/podcast?lang=es")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == len(EPISODES)
    assert body[0]["show"] in {"FermUp", "Ferment Radio"}


def test_endpoint_filter_ferment():
    r = client.get("/podcast?ferment=miso")
    assert r.status_code == 200
    for e in r.json():
        assert any("miso" in f.lower() for f in e["ferments"])


def test_endpoint_topics():
    r = client.get("/podcast/topics?lang=en")
    assert r.status_code == 200
    body = r.json()
    assert "topics" in body and "ferments" in body
    assert body["ferments"]


def test_endpoint_public_api():
    assert client.get("/api/v1/podcast").status_code == 200


def test_frontend_podcast_integration():
    html = client.get("/").text
    assert 'id="podcast-btn"' in html
    assert 'id="podcast-modal"' in html
    js = client.get("/static/app.js").text
    for marker in ["openPodcastModal", "renderPodcastEpisodes", "podcast-topic-filter",
                   "podcast-ferment-filter", "podcast-ferment-tag"]:
        assert marker in js, marker