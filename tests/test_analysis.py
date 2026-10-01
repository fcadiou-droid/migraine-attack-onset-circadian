import numpy as np
import pandas as pd

from onset.analysis import hourly_profile, bootstrap_profiles, headache_days_per_month, user_hour_matrix
from onset.data import load, entry_mode


def test_all_shared_records_are_analysed(csv_path):
    df = load(csv_path)
    assert df["hashed_userid"].nunique() == 2 and len(df) == 5


def test_derived_variables(csv_path):
    df = load(csv_path)
    from conftest import fake_hash
    u1 = df[df["hashed_userid"] == fake_hash(1)].reset_index(drop=True)
    assert u1["hour"].tolist() == [7, 7, 7]
    assert u1["gap_prev_end_h"].tolist()[1] == 19.0                  # 12 h → 31 h
    assert bool(u1["no_attack_previous_day"].iloc[1]) is False       # previous attack on the previous day
    assert bool(u1["no_attack_previous_day"].iloc[2]) is False


def test_entry_mode():
    assert list(entry_mode([10, 1805, 3590, 5000, -5])) == ["now", "preset", "preset", "manual", "negative"]


def test_user_weighting():
    M = np.zeros((2, 24)); M[0, 8] = 10; M[1, 20] = 1
    assert np.isclose(hourly_profile(M)[8], 10 / 11)
    assert np.isclose(hourly_profile(M, user_weighted=True)[8], 0.5)


def test_bootstrap_is_reproducible():
    M = np.random.default_rng(0).integers(0, 5, (50, 24))
    assert np.array_equal(bootstrap_profiles(M, 20, 1), bootstrap_profiles(M, 20, 1))


def test_headache_days_cap(tmp_path):
    from conftest import synthetic_extract
    path = tmp_path / "long.csv"
    synthetic_extract([(1, 0, 200, 0), (1, 300, 305, 0)]).to_csv(path, index=False)
    df = load(path)
    hdm = headache_days_per_month(df.iloc[[0]], cap_h=72)
    assert hdm.sum() in (3, 4)


def test_user_hour_matrix(csv_path):
    df = load(csv_path)
    M = user_hour_matrix(df)
    assert M.shape == (2, 24) and M.sum() == 5
