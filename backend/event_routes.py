"""FastAPI router for Person 4 normalized events."""
from datetime import datetime
from typing import Any, Optional
from ipaddress import ip_address

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from aggregator import aggregate_events
from event_detection import score_event_windows

router = APIRouter()
MAX_EVENTS = 50000

class NormalizedEvent(BaseModel):
    recordId: str = Field(min_length=1)
    source: str = Field(min_length=1)
    timestamp: str
    action: str = Field(min_length=1)
    user: Optional[str] = None
    device: Optional[str] = None
    file: Optional[str] = None
    usb: Optional[str] = None
    ip: Optional[str] = None
    destination: Optional[str] = None

    @field_validator("timestamp")
    @classmethod
    def valid_timestamp(cls, value):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("timestamp must be ISO format, e.g. 2026-09-21T02:43:00")
        if parsed.tzinfo is not None:
            raise ValueError("send timestamps without a timezone")
        return value

    @field_validator("ip", "destination")
    @classmethod
    def valid_optional_ip(cls, value):
        if value is not None:
            try:
                ip_address(value)
            except ValueError:
                # destination may also be a device label such as USB-003.
                if value.upper().startswith("USB-"):
                    return value
                raise ValueError("ip/destination must be an IP address or USB identifier")
        return value

class EventsRequest(BaseModel):
    events: list[NormalizedEvent] = Field(min_length=1, max_length=MAX_EVENTS)
    threshold: float = Field(default=0.8, ge=0, le=1)
    include_all: bool = False

@router.post("/detect-from-events")
def detect_from_events(req: EventsRequest):
    events = [e.model_dump() for e in req.events]
    try:
        df, sources, warnings = aggregate_events(events)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if df.empty:
        return {"anomalies": [], "summary": {"total_records": 0, "flagged": 0,
                "threshold": req.threshold, "source": "person4_events", "warnings": warnings}}
    scored = score_event_windows(df)
    scored["is_anomaly"] = scored["score"] >= req.threshold
    chosen = scored if req.include_all else scored[scored["is_anomaly"]]
    chosen = chosen.sort_values("score", ascending=False)
    anomalies = []
    for i, r in enumerate(chosen.to_dict("records"), 1):
        anomalies.append({
            "id": f"ANM-E-{i:03d}",
            "event_id": r["event_id"],
            "source_event_ids": sources.get(r["event_id"], []),
            "timestamp": pd.Timestamp(r["timestamp"]).isoformat(),
            "user": r["user"],
            "device": r["device"],
            "user_attribution": r["user_attribution"],
            "score": float(r["score"]),
            "is_anomaly": bool(r["is_anomaly"]),
            "severity": "high" if r["score"] >= 0.8 else ("medium" if r["is_anomaly"] else "low"),
            "indicators": {
                "failed_logins": int(r["failed_logins"]),
                "file_accesses": int(r["file_accesses"]),
                "events_per_hour": int(r["events_per_hour"]),
                "usb_writes": int(r["usb_writes"]),
                "outbound_transfers": int(r["outbound_transfers"]),
                "external_contacts": int(r["external_contacts"]),
                "sensitive_file_accesses": int(r["sensitive_file_accesses"]),
                "sensitive_usb_writes": int(r["sensitive_usb_writes"]),
                "remote_ips": r["remote_ips"],
            },
            "reason": r["reason"],
            "label": "Potentially anomalous activity — requires investigator review" if r["is_anomaly"] else "Not flagged at the current threshold",
        })
    return {"anomalies": anomalies, "summary": {
        "total_records": len(scored), "flagged": int(scored["is_anomaly"].sum()),
        "threshold": req.threshold, "source": "person4_events",
        "warnings": warnings,
        "scoring_method": "transparent rule-based prototype; not a validated ML model",
    }}
