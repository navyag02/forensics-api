import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
os.makedirs("data", exist_ok=True)

# CHANGE THIS LATER to match the names/IPs in the team's graph
USERS = {
    "Rahul": "192.168.1.21",
    "Priya": "192.168.1.34",
    "Amit": "192.168.1.47",
    "Neha": "192.168.1.58",
    "Vikram": "192.168.1.63",
}
START = pd.Timestamp("2026-09-01")
EXTERNAL_FIRST_OCTETS = [45, 85, 91, 103, 185, 203]


def normal(n):
    rows = []
    for _ in range(n):
        u = str(rng.choice(list(USERS)))
        hour = int(np.clip(rng.normal(11, 2.5), 8, 19))
        ts = START + pd.Timedelta(days=int(rng.integers(0, 14)),
                                  hours=hour, minutes=int(rng.integers(0, 60)))
        rows.append(dict(timestamp=ts, user=u, ip=USERS[u],
                         failed_logins=int(rng.poisson(0.3)),
                         file_accesses=int(rng.poisson(12)),
                         events_per_hour=int(rng.poisson(6)), label=0))
    return rows


def obvious_anomalies(n):
    """Night time + external IP + many failed logins + bulk file access."""
    rows = []
    for _ in range(n):
        u = str(rng.choice(list(USERS)))
        ts = START + pd.Timedelta(days=int(rng.integers(0, 14)),
                                  hours=int(rng.integers(0, 5)),
                                  minutes=int(rng.integers(0, 60)))
        ip = (f"{rng.choice(EXTERNAL_FIRST_OCTETS)}.{rng.integers(1, 255)}."
              f"{rng.integers(1, 255)}.{rng.integers(1, 255)}")
        rows.append(dict(timestamp=ts, user=u, ip=ip,
                         failed_logins=int(rng.integers(6, 15)),
                         file_accesses=int(rng.integers(30, 60)),
                         events_per_hour=int(rng.integers(20, 40)), label=1))
    return rows


def subtle_anomalies(n):
    """Looks normal except heavy file access. Harder to catch."""
    rows = normal(n)
    for r in rows:
        r["file_accesses"] = int(rng.integers(35, 55))
        r["label"] = 1
    return rows


def benign_night_shift(n):
    """Legit late-night user (Vikram). Ideally NOT flagged."""
    rows = normal(n)
    for r in rows:
        r["timestamp"] = r["timestamp"].normalize() + pd.Timedelta(
            hours=int(rng.integers(22, 24)), minutes=int(rng.integers(0, 60)))
        r["user"] = "Vikram"
        r["ip"] = USERS["Vikram"]
    return rows


showcase = [dict(timestamp=pd.Timestamp("2026-09-14 02:43:00"), user="Rahul",
                 ip="85.21.44.9", failed_logins=12, file_accesses=37,
                 events_per_hour=25, label=1)]

rows = (normal(1400) + obvious_anomalies(30) + subtle_anomalies(15)
        + benign_night_shift(40) + showcase)
df = pd.DataFrame(rows).sort_values("timestamp")
df.to_csv("data/logs.csv", index=False)
print("Saved", len(df), "rows")
print(df["label"].value_counts())