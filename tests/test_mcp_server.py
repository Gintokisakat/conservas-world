import asyncio

import pytest


@pytest.fixture()
def mcp_server(session_factory, monkeypatch):
    from tests.conftest import _seed

    session = session_factory()
    _seed(session)
    session.commit()
    session.close()

    import mcp_server.server as mod

    monkeypatch.setattr(mod, "SessionLocal", session_factory)
    return mod.create_server()


def _call_tool(server, name, arguments=None):
    from mcp import types

    params = types.CallToolRequestParams(name=name, arguments=arguments or {})
    entry = server.get_request_handler("tools/call")
    return asyncio.run(entry.handler(None, params))


def _text(result):
    return result.content[0].text


def test_mcp_tools_registered():
    from mcp_server.server import _TOOLS

    assert [t.name for t in _TOOLS] == [
        "search_products",
        "get_product",
        "get_ingredients",
        "get_timer",
        "lookup_barcode",
    ]
    by_name = {t.name: t for t in _TOOLS}
    assert by_name["search_products"].input_schema["required"] == ["q"]
    assert by_name["get_product"].input_schema["required"] == ["product_id"]


def test_mcp_list_tools(mcp_server):
    from mcp import types

    entry = mcp_server.get_request_handler("tools/list")
    result = asyncio.run(entry.handler(None, types.PaginatedRequestParams()))
    assert len(result.tools) == 5


def test_mcp_search_products(mcp_server):
    import json

    result = _call_tool(mcp_server, "search_products", {"q": "miso", "limit": 5})
    assert not result.is_error
    rows = json.loads(_text(result))
    assert any(r["name"] == "Miso" for r in rows)


def test_mcp_get_product_and_timer(mcp_server):
    import json

    result = _call_tool(mcp_server, "get_product", {"product_id": 1})
    assert not result.is_error
    product = json.loads(_text(result))
    assert product["name"] == "Miso"
    assert "fermentation_time" in product
    assert "ingredients" in product

    result = _call_tool(mcp_server, "get_timer", {"product_id": 1})
    assert not result.is_error
    timer = json.loads(_text(result))
    assert timer["estimated_days"] == {"min": 90, "max": 720}
    assert timer["model"].startswith("Q10")


def test_mcp_get_ingredients(mcp_server):
    import json

    result = _call_tool(mcp_server, "get_ingredients", {"limit": 10})
    assert not result.is_error
    rows = json.loads(_text(result))
    names = {r["name"]: r for r in rows}
    assert names["soybean"]["n_products"] >= 1


def test_mcp_lookup_barcode(mcp_server, monkeypatch):
    import mcp_server.server as mod

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"product": {"product_name": "Miso", "brands": "Fermentos SL"}}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def get(self, url):
            return FakeResponse()

    monkeypatch.setattr(mod.httpx, "Client", FakeClient)
    result = _call_tool(mcp_server, "lookup_barcode", {"barcode": "8412345678901"})
    assert not result.is_error
    import json

    data = json.loads(_text(result))
    assert data["name"] == "Miso"
    assert data["in_db"] == {"id": 1, "name": "Miso"}


def test_mcp_unknown_tool(mcp_server):
    result = _call_tool(mcp_server, "no_such_tool")
    assert result.is_error


def test_mcp_parse_days():
    from mcp_server.server import _parse_days

    assert _parse_days("3-24 meses") == (90, 720)
    assert _parse_days("2-4 semanas") == (14, 28)
    assert _parse_days("1 día") == (1, 1)
    assert _parse_days("6-12 horas") is None
    assert _parse_days(None) is None
