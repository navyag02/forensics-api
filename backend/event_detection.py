"""Explainable event-window risk scoring for the Person 4 data-exfiltration scenario.

This is a transparent prototype rule score, not a trained/validated ML classifier.
The original /detect-anomalies model remains separate and unchanged.
"""
from __future__ import annotations
import pandas as pd

def score_event_windows(df):
    out = df.copy()
    scores, reasons, flags = [], [], []
    for r in out.to_dict("records"):
        points, why = 0.0, []
        if r.get("failed_logins", 0) >= 5:
            points += 0.20; why.append("multiple failed logins")
        if r.get("sensitive_file_accesses", 0) > 0:
            points += 0.15; why.append("sensitive-file activity")
        if r.get("usb_writes", 0) > 0:
            points += 0.20; why.append("USB write activity")
        if r.get("external_contacts", 0) > 0:
            points += 0.20; why.append("connection to a public IP address")
        if r.get("outbound_transfers", 0) > 0:
            points += 0.25; why.append("outbound transfer to a public IP address")
        if r.get("sensitive_usb_writes", 0) > 0:
            points += 0.20; why.append("sensitive file written to USB")
        if r.get("sensitive_file_accesses", 0) > 0 and r.get("outbound_transfers", 0) > 0:
            points += 0.15; why.append("sensitive-file activity followed by outbound transfer")
        if r.get("usb_writes", 0) > 0 and r.get("external_contacts", 0) > 0:
            points += 0.10; why.append("USB and external-network activity in the same window")
        scores.append(round(min(points, 1.0), 2))
        reasons.append("; ".join(why) if why else "No configured exfiltration indicator observed")
    out["score"] = scores
    out["reason"] = reasons
    return out
