#for risk scoring 
import pandas as pd
import numpy as np

SEV_W = {"Plumbing":1.0, "HVAC":1.1, "Electrical":1.2, "Structural":1.4, "Fire":1.5, "Other":1.0}

def zone_aggregates(df: pd.DataFrame, today=None) -> pd.DataFrame:
    d = df.copy()
    d = d.dropna(subset=["date"])
    if today is None:
        today = d["date"].max()
    win90 = today - pd.Timedelta(days=90)
    win365 = today - pd.Timedelta(days=365)

    # address-level counts
    addr_counts_12 = d[d["date"]>=win365].groupby(["zone","address"]).size().rename("addr_cnt_12")
    repeat = (addr_counts_12>=2).groupby(level=0).mean().rename("repeat_ratio").fillna(0)

    # zone counts
    cnt90 = d[d["date"]>=win90].groupby("zone").size().rename("cnt_90d").astype(float)
    cnt365 = d[d["date"]>=win365].groupby("zone").size().rename("cnt_365d").astype(float)

    fine_avg = d[d["date"]>=win365].groupby("zone")["fine_amount"].mean().rename("fine_avg")
    fine_avg = fine_avg.fillna(0)

    sev = d[d["date"]>=win365].assign(sev=d["violation_type"].map(SEV_W)).groupby("zone")["sev"].mean().rename("sev_weighted")
    agg = pd.concat([cnt90, cnt365, repeat, fine_avg, sev], axis=1).fillna(0)

    # normalize 0-1
    def norm(s): 
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9)
    agg["n_cnt90"] = norm(agg["cnt_90d"])
    agg["n_cnt365"] = norm(agg["cnt_365d"])
    agg["n_repeat"] = norm(agg["repeat_ratio"])
    agg["n_fine"] = norm(agg["fine_avg"])
    agg["n_sev"] = norm(agg["sev_weighted"])

    agg["risk_score"] = (
        0.35*agg["n_cnt90"]
      + 0.25*agg["n_cnt365"]
      + 0.20*agg["n_repeat"]
      + 0.10*agg["n_fine"]
      + 0.10*agg["n_sev"]
    )
    agg["percentile"] = agg["risk_score"].rank(pct=True)
    return agg.reset_index()

def quick_address_score(agg_df: pd.DataFrame, zone: str, address_cnt_12mo: int = 0) -> dict:
    zrow = agg_df.loc[agg_df["zone"]==zone]
    if zrow.empty:
        return {"zone": zone, "address_score": None, "risk_zone_score": None, "percentile": None}
    zone_score = float(zrow["risk_score"].values[0])
    # normalize address count vs observed range (0..5+ cap)
    addr_norm = min(address_cnt_12mo, 5) / 5.0
    address_score = 0.7*zone_score + 0.3*addr_norm
    return {
        "zone": zone,
        "risk_zone_score": zone_score,
        "percentile": float(zrow["percentile"].values[0]),
        "address_score": address_score
    }
