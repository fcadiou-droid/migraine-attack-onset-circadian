import hashlib
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

H = 3600
D0 = 1_600_000_000 - 1_600_000_000 % 86400      # a local midnight (day 0)


def fake_hash(i):
    return hashlib.md5(f"user-{i}".encode()).hexdigest()


def synthetic_extract(rows, extra_columns=False):
    """rows = [(user_index, start_h, end_h, delay_s)] in local hours relative to day 0; local time = UTC − 5 h.
    extra_columns=True adds fields that are not part of the shareable extract (coordinates, medication): such a file
    must be refused."""
    out = []
    for u, s, e, delay in rows:
        start_local, end_local = D0 + s * H, D0 + e * H
        out.append({
            "hashed_userid": fake_hash(u),
            "timezone": "America/New_York",
            "starttime_local": pd.to_datetime(start_local, unit="s").strftime("%Y-%m-%d %H:%M:%S.000"),
            "starttime_utc_unix_timestamp": start_local + 5 * H,
            "endtime_utc_unix_timestamp": end_local + 5 * H,
            "starttime_local_unix_timestamp": start_local,
            "endtime_local_unix_timestamp": end_local,
            "creation_starttime_diff_secs": delay,
            **({"latitude": 40.71, "longitude": -74.01, "medication": "should-never-be-read"} if extra_columns else {}),
        })
    return pd.DataFrame(out)


@pytest.fixture
def csv_path(tmp_path):
    rows = [(1, 7, 12, 0), (1, 31, 36, 1800), (1, 55, 60, 30000),      # user 1: three attacks
            (2, 8, 14, 3600), (2, 80, 90, 5),                            # user 2: two attacks
            (3, 9, 13, 0)]                                               # user 3: single attack (excluded)
    path = tmp_path / "attacks.csv"
    synthetic_extract(rows).to_csv(path, index=False)
    return path
