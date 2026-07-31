from ingest.sources.wikidata import _NOISE_NAME_RE, _is_food


def _entity(*p31_ids: str) -> dict:
    claims = {}
    if p31_ids:
        claims["P31"] = [
            {"mainsnak": {"datavalue": {"value": {"id": qid}}}} for qid in p31_ids
        ]
    return {"claims": claims}


def test_is_food_keeps_food_classes():
    assert _is_food(_entity("Q2095"), {"Q2095": "food"}) is True
    assert _is_food(_entity("Q7465498"), {"Q7465498": "dish"}) is True
    assert _is_food(_entity("Q13317"), {"Q13317": "yogurt"}) is True


def test_is_food_drops_non_food_classes():
    assert _is_food(_entity("Q33506"), {"Q33506": "museum"}) is False
    assert _is_food(_entity("Q16521"), {"Q16521": "taxon"}) is False
    assert _is_food(_entity("Q482994"), {"Q482994": "home appliance"}) is False
    assert _is_food(_entity("Q1"), {"Q1": "fermentation process"}) is False


def test_is_food_keeps_mixed_classes():
    labels = {"Q1": "food", "Q2": "organization"}
    assert _is_food(_entity("Q1", "Q2"), labels) is True


def test_is_food_drops_all_non_food_classes():
    labels = {"Q1": "organization", "Q2": "manufacturer"}
    assert _is_food(_entity("Q1", "Q2"), labels) is False


def test_is_food_keeps_items_without_p31():
    assert _is_food(_entity(), {}) is True


def test_noise_name_filter():
    assert _NOISE_NAME_RE.search("pickling") is not None
    assert _NOISE_NAME_RE.search("Pickle lifter") is not None
    assert _NOISE_NAME_RE.search("kimchi refrigerator") is not None
    assert _NOISE_NAME_RE.search("kimchi") is None
    assert _NOISE_NAME_RE.search("sauerkraut") is None
