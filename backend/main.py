import ipaddress
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from event_routes import router as event_router

from model import score

MAX_RECORDS = 10000
COUNT_COLS = ["failed_logins", "file_accesses", "events_per_hour"]
LABEL = "Potentially anomalous activity — requires investigator review"
NOT_FLAGGED = "Not flagged at the current threshold"

app = FastAPI(title="Forensics Anomaly API")
app.include_router(event_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


class Record(BaseModel):
    event_id: Optional[str] = None          # echoed back so other modules can link results
    timestamp: str
    user: str = Field(min_length=1)
    ip: str
    failed_logins: Optional[int] = Field(default=None, ge=0)
    file_accesses: Optional[int] = Field(default=None, ge=0)
    events_per_hour: Optional[int] = Field(default=None, ge=0)

    @field_validator("timestamp")
    @classmethod
    def check_timestamp(cls, v):
        try:
            parsed = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("timestamp must be ISO format, e.g. 2026-09-14T02:43:00")
        if parsed.tzinfo is not None:
            raise ValueError("send timestamps without a timezone (local time)")
        return v

    @field_validator("ip")
    @classmethod
    def check_ip(cls, v):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("ip must be a valid IP address")
        return v


class Req(BaseModel):
    records: Optional[List[Record]] = Field(default=None, max_length=MAX_RECORDS)
    threshold: float = Field(default=0.8, ge=0, le=1)
    include_all: bool = False   # True = return every record with its score


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/detect-anomalies")
def detect(req: Req):
    warnings = []
    missing = {c: 0 for c in COUNT_COLS}

    if req.records is None:
        df = pd.read_csv("data/logs.csv")
        df["event_id"] = None
        source = "sample_data"
        warnings.append("No records sent: scored the bundled sample logs.")
    elif len(req.records) == 0:
        return {"anomalies": [],
                "summary": {"total_records": 0, "flagged": 0, "threshold": req.threshold,
                            "source": "request", "warnings": ["Empty records list."],
                            "missing_values_filled": missing}}
    else:
        df = pd.DataFrame([r.model_dump() for r in req.records])
        source = "request"
        missing = {c: int(df[c].isna().sum()) for c in COUNT_COLS}
        if any(missing.values()):
            warnings.append("Missing count fields were filled with typical training "
                            "values, so they do not drive the score.")

    try:
        out = score(df)
    except FileNotFoundError:
        raise HTTPException(status_code=503,
                            detail="Model not trained. Run: python model.py")

    unknown = sorted(out.loc[out["known_user"] == 0, "user"].unique())
    if unknown:
        warnings.append(f"No baseline for users {unknown}: new-IP check skipped for them.")

    out["is_anomaly"] = out["score"] >= req.threshold
    chosen = out if req.include_all else out[out["is_anomaly"]]
    chosen = chosen.sort_values("score", ascending=False)

    items = []
    for i, r in enumerate(chosen.itertuples(), start=1):
        items.append({
            "id": f"ANM-{i:03d}",
            "event_id": None if pd.isna(r.event_id) else str(r.event_id),
            "timestamp": r.timestamp.isoformat(),
            "user": r.user,
            "ip": r.ip,
            "score": float(r.score),
            "is_anomaly": bool(r.is_anomaly),
            "severity": "high" if r.score >= 0.8 else ("medium" if r.is_anomaly else "low"),
            "indicators": {
                "login_hour": int(r.login_hour),
                "failed_logins": None if "failed_logins" in r.missing_fields else int(r.failed_logins),
                "file_accesses": None if "file_accesses" in r.missing_fields else int(r.file_accesses),
                "new_ip": bool(r.new_ip),
                "external_ip": bool(r.external_ip),
            },
            "reason": r.reason,
            "missing_fields": list(r.missing_fields),
            "label": LABEL if r.is_anomaly else NOT_FLAGGED
        })

    return {"anomalies": items,
            "summary": {"total_records": len(out), "flagged": int(out["is_anomaly"].sum()),
                        "threshold": req.threshold, "source": source,
                        "warnings": warnings, "missing_values_filled": missing}}