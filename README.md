# SUTRAM — AI-Powered Digital Forensics Investigation Framework

SUTRAM is a backend framework for detecting anomalous behaviour and reconstructing incident timelines from multi-source digital forensic logs. It was built as part of a hackathon prototype and is designed for investigator review, not automated decision-making.

---

## What it does

- Ingests raw event logs from multiple sources — system logs, file access logs, network logs, and USB activity
- Normalizes, deduplicates, and aggregates events into time windows per user and device
- Scores each window for suspicious activity using two complementary approaches:
  - **ML-based scoring** — Isolation Forest trained on synthetic log data (`/detect-anomalies`)
  - **Rule-based scoring** — transparent point system for known exfiltration indicators (`/detect-from-events`)
- Returns ranked results with plain-English explanations, severity levels, and source event IDs for investigator traceability

---

## Architecture

```
src/                        # Synthetic mock log data (JS, for frontend integration)
backend/
├── main.py                 # FastAPI app — /detect-anomalies endpoint
├── event_routes.py         # FastAPI router — /detect-from-events endpoint
├── model.py                # Isolation Forest training and scoring
├── features.py             # Feature engineering (login hour, IP flags, etc.)
├── aggregator.py           # Multi-source event normalization and deduplication
├── event_detection.py      # Rule-based risk scoring for raw event streams
├── generate_data.py        # Synthetic training data generation
├── requirements.txt        # Python dependencies
├── person4_events.json     # Sample multi-source event input
├── example_request.json    # Sample /detect-anomalies request
├── example_response.json   # Sample /detect-anomalies response
├── test_validation.py      # Tests for /detect-anomalies
├── test_task_e.py          # Tests for /detect-from-events and aggregator
└── API.md                  # Full API reference
```

---

## Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python generate_data.py       # generates data/logs.csv
python model.py               # trains and saves model.joblib
uvicorn main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

---

## Endpoints

### `GET /`
Health check. Returns `{"status": "ok"}`.

---

### `POST /detect-anomalies`
Scores pre-aggregated event records using a trained Isolation Forest model.

**Request:**
```json
{
  "records": [
    {
      "event_id": "EVT-0042",
      "timestamp": "2026-09-14T02:43:00",
      "user": "Rahul",
      "ip": "85.21.44.9",
      "failed_logins": 12,
      "file_accesses": 37,
      "events_per_hour": 25
    }
  ],
  "threshold": 0.8,
  "include_all": false
}
```

Send an empty body `{}` to score the bundled sample logs.

**Response (flagged record):**
```json
{
  "anomalies": [
    {
      "id": "ANM-001",
      "event_id": "EVT-0042",
      "timestamp": "2026-09-14T02:43:00",
      "user": "Rahul",
      "ip": "85.21.44.9",
      "score": 0.96,
      "is_anomaly": true,
      "severity": "high",
      "indicators": {
        "login_hour": 2,
        "failed_logins": 12,
        "file_accesses": 37,
        "new_ip": true,
        "external_ip": true
      },
      "reason": "Unusual file accesses: 37 vs typical ~12; failed logins: 12 vs typical ~0; off-hours access; external IP address",
      "missing_fields": [],
      "label": "Potentially anomalous activity — requires investigator review"
    }
  ],
  "summary": {
    "total_records": 1,
    "flagged": 1,
    "threshold": 0.8,
    "source": "request",
    "warnings": []
  }
}
```

| Field | Notes |
|---|---|
| `score` | 0–1, higher = more unusual. Not a probability |
| `severity` | `high` ≥ 0.8, `medium` = flagged but below 0.8, `low` = not flagged |
| `label` | Show verbatim. Only set to the alert text when `is_anomaly` is true |
| `indicators` | `null` means the field was not supplied, display as "no data" not 0 |

---

### `POST /detect-from-events`
Accepts raw normalized events from multiple log sources, aggregates them into time windows, and scores using a transparent rule-based system.

**Request:**
```json
{
  "events": [ ...see person4_events.json for full example... ],
  "threshold": 0.8,
  "include_all": false
}
```

Each event must include `recordId`, `source`, `timestamp`, `action`. See `API.md` for the full field reference.

**Key difference from `/detect-anomalies`:** This endpoint accepts raw per-event logs and handles normalization and deduplication internally. Use it when you have a stream of individual log entries rather than pre-aggregated records.

---

## Running tests

```bash
cd backend
pytest -q
```

The test suite covers input validation, missing field handling, threshold behaviour, user attribution, and the full Person 4 data-exfiltration scenario.

---

## Model details

- Algorithm: Isolation Forest (`sklearn.ensemble.IsolationForest`)
- Features: login hour, off-hours flag, failed logins, file accesses, events per hour, external IP flag, new IP flag
- Training data: synthetic logs (~1,500 normal + ~45 planted anomalies)
- Performance on synthetic data at threshold 0.8: precision 1.00, recall 0.67
- Missing count fields are filled with training medians so gaps do not generate false positives

Scores are for investigator review only. They do not constitute proof of wrongdoing.

---

## Limitations

- Trained on synthetic data; real-world accuracy is untested
- Expects one aggregated record per user per time window for `/detect-anomalies`
- Users not present in training data skip the new-IP check
- Legitimate unusual patterns (night-shift users) may be flagged at lower thresholds

---

## Built with

Python · FastAPI · scikit-learn · Pandas · NumPy · Pydantic · pytest
