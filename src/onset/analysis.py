"""Hourly profile of attack onset, user-level bootstrap and sensitivity analyses."""
import numpy as np
import pandas as pd

from onset import config


def user_hour_matrix(df) -> np.ndarray:
    """Users × 24 matrix of attack onsets per local clock hour."""
    return (pd.crosstab(df["hashed_userid"], df["hour"])
              .reindex(columns=range(24), fill_value=0).to_numpy())


def hourly_profile(M, user_weighted=False) -> np.ndarray:
    """Proportion of onsets per hour. user_weighted=True gives each user the same weight."""
    if user_weighted:
        return (M / M.sum(axis=1, keepdims=True)).mean(axis=0)
    counts = M.sum(axis=0)
    return counts / counts.sum()


def bootstrap_profiles(M, n_boot, seed, user_weighted=False) -> np.ndarray:
    """Bootstrap distribution of the hourly profile, resampling users (attacks are clustered within users)."""
    rng = np.random.default_rng(seed)
    boot = np.empty((n_boot, 24))
    for i in range(n_boot):
        boot[i] = hourly_profile(M[rng.integers(0, M.shape[0], M.shape[0])], user_weighted)
    return boot


def headache_days_per_month(df, cap_h=config.DURATION_CAP_H) -> pd.Series:
    """Headache days per user and calendar month (local days covered by an attack; durations capped at cap_h)."""
    start = df["starttime_local_unix_timestamp"].to_numpy()
    end = np.minimum(df["endtime_local_unix_timestamp"].to_numpy(), start + cap_h * 3600)
    first_day, last_day = start // 86400, end // 86400
    n = (last_day - first_day + 1).astype(int)
    users = np.repeat(df["hashed_userid"].to_numpy(), n)
    days = np.repeat(first_day, n) + (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n))
    hd = pd.DataFrame({"u": users, "day": days}).drop_duplicates()
    hd["month"] = pd.to_datetime(hd["day"], unit="D").dt.to_period("M")
    return hd.groupby(["u", "month"]).size()


def users_with_chronic_month(df, min_days=config.CHRONIC_DAYS) -> set:
    """Users with at least one calendar month with min_days or more headache days."""
    hdm = headache_days_per_month(df)
    return set(hdm[hdm >= min_days].index.get_level_values(0))


def summarize(sub, label, n_boot, user_weighted=False) -> dict:
    """Share of onsets between 06:00 and 11:00 (95% CI, user bootstrap), modal and minimum hour."""
    M = user_hour_matrix(sub)
    prop = hourly_profile(M, user_weighted)
    peak = bootstrap_profiles(M, n_boot, config.SEED, user_weighted)[:, config.PEAK_HOURS].sum(axis=1)
    return {"analysis": label, "attacks": int(M.sum()), "users": int(M.shape[0]),
            "share_06_11": float(prop[config.PEAK_HOURS].sum()),
            "ci_low": float(np.percentile(peak, 2.5)), "ci_high": float(np.percentile(peak, 97.5)),
            "modal_hour": int(prop.argmax()), "min_hour": int(prop.argmin())}


def robustness_table(df) -> pd.DataFrame:
    """Main analysis and pre-specified sensitivity analyses (Supplementary Table 2)."""
    w = df[(df["start_local"] >= config.ORIGINAL_WINDOW[0]) & (df["start_local"] < config.ORIGINAL_WINDOW[1])]
    chronic = users_with_chronic_month(df)
    sens = config.N_BOOT_SENSITIVITY
    rows = [summarize(df, "All attacks (2014–2023)", config.N_BOOT_MAIN),
            summarize(df, "Each user weighted equally", sens, user_weighted=True),
            summarize(w, "Original study window only (Jan 2018 – Jun 2020)", sens),
            summarize(df[df["no_attack_previous_day"]], "No attack on the previous day", sens),
            summarize(df[~df["hashed_userid"].isin(chronic)], "Excluding users with any month with ≥ 15 headache days", sens),
            summarize(df[~(df["gap_prev_end_h"] < config.GAP_H)], "Excluding attacks starting < 48 h after the previous one", sens),
            summarize(df[df["entry_mode"] == "now"], "Start time recorded in real time ('now')", sens),
            summarize(df[df["entry_mode"] == "manual"], "Start time entered retrospectively", sens)]
    for y in range(2015, 2023):
        rows.append(summarize(df[df["start_local"].dt.year == y], f"Year {y}", sens))
    return pd.DataFrame(rows)


def reporting_characteristics(df) -> dict:
    """Descriptive statistics of reporting (Supplementary Table 2, upper part)."""
    per_user = df.groupby("hashed_userid").size()
    g = df.groupby("hashed_userid")["start_local"].agg(["min", "max"])
    span = (g["max"] - g["min"]).dt.days
    rate = per_user[span >= 90] / (span[span >= 90] / 30.44)
    return {"attacks": int(len(df)), "users": int(per_user.size),
            "attacks_per_user_median": float(per_user.median()),
            "attacks_per_user_q1": float(per_user.quantile(.25)), "attacks_per_user_q3": float(per_user.quantile(.75)),
            "attacks_per_month_active_median": float(rate.median()),
            "attacks_per_month_active_q1": float(rate.quantile(.25)), "attacks_per_month_active_q3": float(rate.quantile(.75)),
            "logged_within_24h": float(df["delay_s"].between(0, 86400).mean()),
            "entry_now": float((df["entry_mode"] == "now").mean()),
            "entry_preset": float((df["entry_mode"] == "preset").mean()),
            "entry_manual": float((df["entry_mode"] == "manual").mean())}
