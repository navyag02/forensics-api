import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

from event_routes import router
from aggregator import aggregate_events

app = FastAPI()
app.include_router(router)
client = TestClient(app)

EVENTS = json.loads((Path(__file__).parent / "person4_events.json").read_text(encoding="utf-8"))

def test_person4_data_aggregates_and_preserves_sources():
    df, sources, warnings = aggregate_events(EVENTS)
    assert len(df) >= 3
    # FILE-009 has no user and is inferred from Laptop-07's other observations.
    rahul = df[df["user"] == "Rahul"]
    assert not rahul.empty
    assert any("FILE-009" in ids for ids in sources.values())
    assert any("inferred" in w for w in warnings)

def test_event_endpoint_flags_rahul_not_amit_at_default_threshold():
    response = client.post("/detect-from-events", json={"events": EVENTS, "include_all": True})
    assert response.status_code == 200, response.text
    payload = response.json()
    rahul = [x for x in payload["anomalies"] if x["user"] == "Rahul"]
    amit = [x for x in payload["anomalies"] if x["user"] == "Amit"]
    assert rahul and amit
    assert max(x["score"] for x in rahul) >= 0.8
    assert max(x["score"] for x in amit) < 0.8
    incident = max(rahul, key=lambda x: x["score"])
    assert "NET-002" in incident["source_event_ids"]
    assert "FILE-003" in incident["source_event_ids"]
    assert "USB-002" in incident["source_event_ids"]

def test_event_validation_rejects_timezone_and_empty_list():
    bad = dict(EVENTS[0])
    bad["timestamp"] = "2026-09-21T02:41:03+05:30"
    assert client.post("/detect-from-events", json={"events": [bad]}).status_code == 422
    assert client.post("/detect-from-events", json={"events": []}).status_code == 422

def test_response_discloses_rule_based_scoring():
    response = client.post("/detect-from-events", json={"events": EVENTS, "include_all": True})
    assert "rule-based" in response.json()["summary"]["scoring_method"]
