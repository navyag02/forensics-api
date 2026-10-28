import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from features import build_features, usual_ip_map, FEATURES

NUMERIC = {"login_hour": "login time (hour)", "failed_logins": "failed logins",
           "file_accesses": "file accesses", "events_per_hour": "activity per hour"}
FLAGS = {"off_hours": "off-hours access", "external_ip": "external IP address",
         "new_ip": "IP not usual for this user"}
COUNTS = ["failed_logins", "file_accesses", "events_per_hour"]

def train(path="data/logs.csv"):
    raw = pd.read_csv(path)
    usual_ip = usual_ip_map(raw)
    df = build_features(raw, usual_ip)
    X = df[FEATURES]
    model = IsolationForest(n_estimators=200, contamination=0.05,
                            random_state=42).fit(X)
    raw = -model.score_samples(X)  # higher = more unusual
    stats = {
        "lo": float(raw.min()),
        "hi": float(raw.max()),
        "usual_ip": usual_ip,
        "median": X.median().to_dict(),
        "mad": (X - X.median()).abs().median().replace(0, 1).to_dict(),
    }
    joblib.dump((model, stats), "model.joblib")
    print("Model trained and saved to model.joblib")


def explain(row, stats):
    skip = row["missing_fields"] if "missing_fields" in row.index else []
    parts = []
    for f, name in NUMERIC.items():
        if f in skip:
            continue
        dev = abs(row[f] - stats["median"][f]) / stats["mad"][f]
        if dev >= 3:
            parts.append((dev, f"{name}: {row[f]} vs typical ~{stats['median'][f]:.0f}"))
    parts.sort(reverse=True)
    reasons = [p[1] for p in parts[:3]]
    for f, name in FLAGS.items():
        if row[f] == 1 and stats["median"][f] == 0:
            reasons.append(name)
    if not reasons:
        if len(skip) == len(COUNTS):
            return "Insufficient data: no activity counts supplied"
        return "No single indicator is far from typical"
    return "Unusual " + "; ".join(reasons)


def score(df):
    model, stats = joblib.load("model.joblib")
    df = df.copy()
    mask = df[COUNTS].isna().values
    df["missing_fields"] = [[c for c, m in zip(COUNTS, row) if m] for row in mask]
    for c in COUNTS:
        df[c] = df[c].fillna(stats["median"][c]).astype(int)
    df = build_features(df, stats["usual_ip"])
    raw = -model.score_samples(df[FEATURES])
    scaled = (raw - stats["lo"]) / (stats["hi"] - stats["lo"])
    df["score"] = np.clip(scaled, 0, 1).round(2)
    df["reason"] = [explain(r, stats) for _, r in df.iterrows()]
    return df

if __name__ == "__main__":
    train()