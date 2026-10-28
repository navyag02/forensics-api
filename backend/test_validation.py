from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
GOOD = {"event_id": "EVT-1", "timestamp": "2026-09-14T02:43:00", "user": "Rahul",
        "ip": "85.21.44.9", "failed_logins": 12, "file_accesses": 37,
        "events_per_hour": 25}


def post(body):
    return client.post("/detect-anomalies", json=body)


def test_sample_data():
    r = post({})
    assert r.status_code == 200 and r.json()["summary"]["flagged"] > 0


def test_single_record_scored_and_event_id_echoed():
    r = post({"records": [GOOD], "include_all": True})
    item = r.json()["anomalies"][0]
    assert r.status_code == 200
    assert item["event_id"] == "EVT-1" and item["score"] >= 0.8


def test_empty_records():
    r = post({"records": []})
    assert r.status_code == 200 and r.json()["summary"]["total_records"] == 0


def test_bad_ip():
    assert post({"records": [{**GOOD, "ip": "999.1.1.1"}]}).status_code == 422


def test_bad_timestamp():
    assert post({"records": [{**GOOD, "timestamp": "yesterday"}]}).status_code == 422


def test_negative_count():
    assert post({"records": [{**GOOD, "failed_logins": -1}]}).status_code == 422


def test_threshold_out_of_range():
    assert post({"records": [GOOD], "threshold": 1.5}).status_code == 422


def test_unknown_user_warns():
    r = post({"records": [{**GOOD, "user": "Stranger"}], "include_all": True})
    assert r.status_code == 200
    assert any("No baseline" in w for w in r.json()["summary"]["warnings"])


def test_missing_counts_filled_and_reported():
    rec = {k: v for k, v in GOOD.items() if k != "failed_logins"}
    r = post({"records": [rec], "include_all": True})
    assert r.json()["summary"]["missing_values_filled"]["failed_logins"] == 1
    
def test_non_flagged_record_has_honest_label():
    rec = {**GOOD, "timestamp": "2026-09-14T10:15:00", "ip": "192.168.1.21",
           "failed_logins": 0, "file_accesses": 11, "events_per_hour": 6}
    item = post({"records": [rec], "include_all": True}).json()["anomalies"][0]
    assert item["is_anomaly"] is False and item["severity"] == "low"
    assert "requires investigator review" not in item["label"]


def test_missing_fields_listed_and_not_used_in_reason():
    rec = {k: v for k, v in GOOD.items() if k != "failed_logins"}
    item = post({"records": [rec], "include_all": True}).json()["anomalies"][0]
    assert item["missing_fields"] == ["failed_logins"]
    assert "failed logins" not in item["reason"]
    assert item["indicators"]["failed_logins"] is None
    assert item["indicators"]["file_accesses"] == GOOD["file_accesses"]