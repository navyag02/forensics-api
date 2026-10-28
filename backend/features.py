import pandas as pd

FEATURES = ["login_hour", "off_hours", "failed_logins", "file_accesses",
            "events_per_hour", "external_ip", "new_ip"]


def is_internal(ip):
    return ip.startswith(("192.168.", "10.", "172."))


def usual_ip_map(df):
    return df.groupby("user")["ip"].agg(lambda s: s.mode().iloc[0]).to_dict()


def build_features(df, usual_ip=None):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["login_hour"] = df["timestamp"].dt.hour
    df["off_hours"] = ((df["login_hour"] < 6) | (df["login_hour"] >= 22)).astype(int)
    df["external_ip"] = (~df["ip"].apply(is_internal)).astype(int)

    if usual_ip is None:                      # only used when training
        usual_ip = usual_ip_map(df)
    usual = df["user"].map(usual_ip)
    df["known_user"] = usual.notna().astype(int)
    df["new_ip"] = (usual.notna() & (df["ip"] != usual)).astype(int)
    return df