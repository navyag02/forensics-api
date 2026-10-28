"""Normalize, de-duplicate and aggregate Person 4's normalized observations."""
from __future__ import annotations

from datetime import datetime
from ipaddress import ip_address
from collections import defaultdict
import pandas as pd

SENSITIVE_TERMS = ("confidential", "secret", "payroll", "financial", "customer", "credential")


def _parse_ts(value):
    ts = datetime.fromisoformat(str(value))
    if ts.tzinfo is not None:
        raise ValueError("timestamps must be ISO format without a timezone")
    return ts


def _is_external(value):
    if not value:
        return False
    try:
        return ip_address(str(value)).is_global
    except ValueError:
        return False


def _canonical_action(e):
    action = str(e.get("action") or "").upper()
    if action == "LOGIN":
        return "login_success"  # Outcome is not present in source data; see warning.
    if action in {"LOGIN_FAILED", "FAILED_LOGIN", "AUTH_FAILURE"}:
        return "login_failed"
    if action in {"FILE_ACCESS", "READ", "COPY"}:
        return "file_access"
    if action == "FILE_WRITE":
        return "usb_connect"  # USB write is separately preserved as a feature.
    if action == "CONNECT" and e.get("usb"):
        return "usb_connect"
    if action in {"NETWORK_CONNECTION", "CONNECTION", "OUTBOUND_TRANSFER"}:
        return "network_connection"
    if action == "TRANSFER":
        return "network_connection"
    return "other"


def _dedupe_key(e):
    """Collapse cross-source duplicate observations while retaining all source IDs."""
    action = str(e.get("action") or "").upper()
    file_name = (e.get("file") or "").lower()
    if action in {"FILE_ACCESS", "READ"}:
        logical = "file_read"
    elif action in {"NETWORK_CONNECTION", "CONNECTION"}:
        logical = "network_connection"
    elif action in {"OUTBOUND_TRANSFER", "TRANSFER"}:
        logical = "outbound_transfer"
    else:
        logical = action.lower()
    # Timestamp rounded to 5-second buckets: SYS-002 and FILE-001 are 2 sec apart.
    ts = _parse_ts(e["timestamp"])
    bucket = int(ts.timestamp()) // 5
    return (e.get("device"), e.get("user") or None, logical, file_name,
            e.get("ip") or e.get("destination"), bucket)


def aggregate_events(events):
    """Return (window DataFrame, source-ID mapping, warnings).

    Windows are keyed by hour, user and device. `ip` is not used as a host IP:
    Person 4's network `ip` is treated as the remote/destination address.
    """
    if not events:
        return pd.DataFrame(), {}, []

    warnings = [
        "LOGIN records have no outcome; mapped to login_success as a neutral placeholder.",
        "Network-log ip is treated as the remote address, not the device's own IP.",
        "Deduplication collapses likely cross-source duplicates within a 5-second bucket; inspect source IDs before evidentiary use.",
    ]
    prepared = []
    # Infer only the missing user on FILE-009 from the observed device mapping.
    device_users = {}
    for e in events:
        if e.get("device") and e.get("user"):
            device_users.setdefault(e["device"], set()).add(e["user"])
    for original in events:
        e = dict(original)
        e["timestamp"] = _parse_ts(e["timestamp"])
        if not e.get("user") and e.get("device"):
            candidates = device_users.get(e["device"], set())
            if len(candidates) == 1:
                e["user"] = next(iter(candidates))
                e["user_attribution"] = "inferred_from_device"
                warnings.append(f"User inferred for {e.get('recordId', 'unknown event')} from device {e['device']}.")
            else:
                e["user"] = "UNKNOWN"
                e["user_attribution"] = "unresolved"
                warnings.append(f"User unresolved for {e.get('recordId', 'unknown event')}; grouped as UNKNOWN.")
        e["user"] = e.get("user") or "UNKNOWN"
        e["device"] = e.get("device") or "UNKNOWN_DEVICE"
        e["source_event_id"] = str(e.get("recordId") or e.get("event_id") or "")
        e["event_type"] = _canonical_action(e)
        e["external_ip"] = _is_external(e.get("ip") or e.get("destination"))
        e["is_sensitive_file"] = bool(e.get("file") and any(t in e["file"].lower() for t in SENSITIVE_TERMS))
        prepared.append(e)

    # Group likely duplicate rows into one logical action, preserving all IDs.
    logical_events = {}
    for e in sorted(prepared, key=lambda x: x["timestamp"]):
        key = _dedupe_key(e)
        if key not in logical_events:
            logical_events[key] = {**e, "_source_ids": [e["source_event_id"]]}
        else:
            prior = logical_events[key]
            if e["source_event_id"]:
                prior["_source_ids"].append(e["source_event_id"])
            # Prefer a known user attribution and retain any useful fields.
            for field in ("user", "file", "ip", "destination", "usb"):
                if not prior.get(field) and e.get(field):
                    prior[field] = e[field]
    unique = list(logical_events.values())

    groups = defaultdict(list)
    for e in unique:
        window = e["timestamp"].replace(minute=0, second=0, microsecond=0)
        groups[(window, e["user"], e["device"])].append(e)

    rows, sources = [], {}
    for n, ((window, user, device), group) in enumerate(sorted(groups.items()), start=1):
        wid = f"WIN-{n:04d}"
        all_ids = []
        for e in sorted(group, key=lambda x: x["timestamp"]):
            all_ids.extend(x for x in e["_source_ids"] if x)
        usb_writes = sum(str(e.get("action", "")).upper() == "FILE_WRITE" for e in group)
        outbound = sum(
            str(e.get("action", "")).upper() in {"OUTBOUND_TRANSFER", "TRANSFER"}
            and (e.get("external_ip") or _is_external(e.get("destination")))
            for e in group
        )
        external_contacts = sum(
            e.get("external_ip", False) and str(e.get("action", "")).upper()
            in {"CONNECTION", "NETWORK_CONNECTION", "OUTBOUND_TRANSFER", "TRANSFER"}
            for e in group
        )
        sensitive_accesses = sum(e.get("is_sensitive_file", False) for e in group)
        sensitive_usb_writes = sum(
            str(e.get("action", "")).upper() == "FILE_WRITE" and e.get("is_sensitive_file", False)
            for e in group
        )
        file_accesses = sum(e["event_type"] == "file_access" for e in group)
        failed_logins = sum(e["event_type"] == "login_failed" for e in group)
        rows.append({
            "event_id": wid, "timestamp": min(e["timestamp"] for e in group),
            "user": user, "device": device,
            "failed_logins": int(failed_logins),
            "file_accesses": int(file_accesses),
            "events_per_hour": int(len(group)),
            "usb_writes": int(usb_writes),
            "outbound_transfers": int(outbound),
            "external_contacts": int(external_contacts),
            "sensitive_file_accesses": int(sensitive_accesses),
            "sensitive_usb_writes": int(sensitive_usb_writes),
            "remote_ips": sorted({str(e.get("ip") or e.get("destination")) for e in group if e.get("ip") or e.get("destination")}),
            "user_attribution": "inferred" if any(e.get("user_attribution") == "inferred_from_device" for e in group) else "observed",
        })
        sources[wid] = all_ids
    return pd.DataFrame(rows), sources, list(dict.fromkeys(warnings))
