import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "fermentation_timeline.json"


def _load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_timeline_data_well_formed():
    data = _load()
    events = data["events"]
    assert len(events) >= 15
    years = [e["year"] for e in events]
    assert years == sorted(years), "los eventos deben estar ordenados por año"
    for e in events:
        assert isinstance(e["year"], int) and e["year"] != 0
        assert set(e["title"]) == {"es", "en"}
        assert set(e["description"]) == {"es", "en"}
        assert e["title"]["es"] and e["title"]["en"]
        assert e["description"]["es"] and e["description"]["en"]
        assert e["category"]


def test_timeline_has_canonical_events():
    events = _load()["events"]
    keys = {e["title"]["en"] for e in events}
    assert "Beer" in keys and "Cheese" in keys and "Leavened bread" in keys
    assert "Kvevri wine" in keys and "Vinegar" in keys
    assert "Invention of canning" in keys
    assert "Pasteurization" in keys
    assert any(e["year"] < 0 for e in events) and any(e["year"] > 0 for e in events)


def test_api_timeline(client):
    resp = client.get("/timeline")
    assert resp.status_code == 200
    assert resp.headers.get("Cache-Control") == "public, max-age=86400"
    data = resp.json()
    assert data["total"] == len(_load()["events"])
    eras = [e["era"] for e in data["events"]]
    assert eras[0] == "BCE" and eras[-1] == "CE"
    assert all(e["era"] in ("BCE", "CE") for e in data["events"])
    assert all(e["year"] > 0 for e in data["events"])  # valor absoluto
    first = data["events"][0]
    assert first["era"] == "BCE"
    assert first["title"]["es"] and first["title"]["en"]
