"""Tests de auditoría y versión de fuentes de ingesta (roadmap 5.2)."""

from ingest.source_versions import record_source_version


def test_source_version_record_and_list(client, session_factory):
    session = session_factory()
    try:
        record_source_version(session, "FermDB", 1000, checksum="abc123hash")
        record_source_version(session, "Wikidata", 2500, checksum="def456hash")
    finally:
        session.close()

    res = client.get("/sources/versions")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2
    sources = {item["source"] for item in data["items"]}
    assert "fermdb" in sources
    assert "wikidata" in sources

    # Test idempotency / update
    session2 = session_factory()
    try:
        updated = record_source_version(session2, "fermdb", 1050, checksum="newhash")
        assert updated.records_count == 1050
    finally:
        session2.close()

    res2 = client.get("/sources/versions")
    data2 = res2.json()
    fermdb_item = next(i for i in data2["items"] if i["source"] == "fermdb")
    assert fermdb_item["records_count"] == 1050
    assert fermdb_item["checksum"] == "newhash"
