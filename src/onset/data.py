"""Loading and validation of the de-identified attack extract.

Privacy by design: the analysis runs only on the shareable extract, whose columns are exactly USED_COLUMNS (see DATA.md);
a file with any other field is refused. User identifiers are de-identified and specific to this study (format checked); the only location information is the
device time zone. The shareable extract contains only included records: a file containing records that do not meet the
inclusion criteria (single-attack users, attacks < 2 h, criteria not attested) is refused rather than filtered.
"""
import re

import numpy as np
import pandas as pd

from onset import config

# The complete list of fields used by this analysis (see DATA.md). Nothing else is read.
USED_COLUMNS = {
    "hashed_userid": "string",                 # de-identified, study-specific user identifier (32 hexadecimal characters)
    "timezone": "string",                      # IANA time zone of the device: the only location information used
    "starttime_local": "string",               # attack start, local clock time (YYYY-MM-DD hh:mm:ss.sss)
    "starttime_utc_unix_timestamp": "int64",   # attack start, UTC (seconds)
    "endtime_utc_unix_timestamp": "int64",     # attack end, UTC (seconds)
    "starttime_local_unix_timestamp": "int64", # attack start, local clock time expressed in seconds
    "endtime_local_unix_timestamp": "int64",   # attack end, local clock time expressed in seconds
    "creation_starttime_diff_secs": "int64",   # delay between attack start and creation of the record (seconds)
    # Inclusion criteria verified by Healint at extraction; attestations, True on every row (see DATA.md)
    "research_opt_in": "boolean",              # the user opted in, within the app, to the use of their data for research
    "adult": "boolean",                        # the user is an adult
    "under_87_years": "boolean",               # the user is less than 87 years old
}
ATTESTED_CRITERIA = ["research_opt_in", "adult", "under_87_years"]
HASH_PATTERN = re.compile(r"^[0-9a-f]{32}$")


class DataValidationError(ValueError):
    pass


def read_extract(path) -> pd.DataFrame:
    """Read the shareable extract. Its columns must be exactly USED_COLUMNS: a file with any other field is refused,
    so that the analysis can only run on the shareable extract."""
    header = list(pd.read_csv(path, nrows=0).columns)
    unexpected = [c for c in header if c not in USED_COLUMNS]
    missing = [c for c in USED_COLUMNS if c not in header]
    if unexpected or missing:
        raise DataValidationError(f"The file must contain exactly the shareable fields (see DATA.md). "
                                  f"Unexpected: {unexpected}; missing: {missing}.")
    return pd.read_csv(path, dtype=USED_COLUMNS)


def validate(df: pd.DataFrame) -> None:
    """Fail loudly if the extract does not match the expected de-identified format."""
    if not df["hashed_userid"].str.fullmatch(HASH_PATTERN).all():
        raise DataValidationError("User identifiers must be 32 hexadecimal characters (de-identified study identifiers).")
    zones = set(df["timezone"].unique())
    if zones != {config.TIME_ZONE}:
        raise DataValidationError(f"Expected a single time zone {config.TIME_ZONE!r}, found {sorted(zones)}.")
    duration = df["endtime_utc_unix_timestamp"] - df["starttime_utc_unix_timestamp"]
    if (duration < config.MIN_DURATION_S).any():
        raise DataValidationError("Attacks shorter than 2 h are present; the extract should exclude them.")
    for c in ATTESTED_CRITERIA:
        if not df[c].fillna(False).all():
            raise DataValidationError(f"Records not attested as {c!r} are present; the extract should exclude them.")
    if (df.groupby("hashed_userid").size() < config.MIN_ATTACKS_PER_USER).any():
        raise DataValidationError("Users with a single attack are present; the extract should exclude them.")


def entry_mode(delay_s) -> np.ndarray:
    """How the start time was entered: 'now' (logged at onset), 'preset' (app offset), 'manual' or 'negative'."""
    d = np.asarray(delay_s, dtype=float)
    mode = np.full(d.shape, "manual", dtype=object)
    near = np.zeros(d.shape, dtype=bool)
    for p in config.PRESETS_S:
        near |= np.abs(d - p) <= config.PRESET_TOLERANCE_S
    mode[near] = "preset"
    mode[(d >= 0) & (d < config.LOGGED_NOW_MAX_S)] = "now"
    mode[d < 0] = "negative"
    return mode


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Derived variables: onset hour, interval since the previous attack, previous-day attack, entry mode."""
    df = df.copy()
    df["start_local"] = pd.to_datetime(df["starttime_local"], format="%Y-%m-%d %H:%M:%S.%f")
    df["hour"] = df["start_local"].dt.hour
    df = df.sort_values(["hashed_userid", "starttime_utc_unix_timestamp"], ignore_index=True)
    by_user = df.groupby("hashed_userid")
    prev_end = by_user["endtime_utc_unix_timestamp"].shift()
    df["gap_prev_end_h"] = (df["starttime_utc_unix_timestamp"] - prev_end) / 3600        # NaN for a user's first attack
    prev_end_local = by_user["endtime_local_unix_timestamp"].shift()
    day0 = (df["starttime_local_unix_timestamp"] // 86400) * 86400
    df["no_attack_previous_day"] = prev_end_local < (day0 - 86400)    # previous attack ended before the previous day
    df["delay_s"] = df["creation_starttime_diff_secs"]
    df["entry_mode"] = entry_mode(df["delay_s"])
    return df


def load(path) -> pd.DataFrame:
    """Read, validate and prepare the analysis dataset (all records of the shareable extract are included)."""
    df = read_extract(path)
    validate(df)
    return add_derived(df)
