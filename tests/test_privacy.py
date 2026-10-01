"""Privacy guarantees of the code: what is read, and what is refused."""
import pandas as pd
import pytest

from onset.data import USED_COLUMNS, read_extract, load, DataValidationError
from conftest import synthetic_extract

FORBIDDEN_FRAGMENTS = ["lat", "lon", "geohash", "postcode", "zip", "city", "address", "country",   # location
                       "name", "email", "phone", "device", "ip",                                    # direct identifiers
                       "age", "sex", "gender", "birth",                                             # demographics
                       "drug", "medic", "treat", "trigger", "symptom", "note", "comment", "free"]  # clinical / free text


def test_only_declared_columns_are_used():
    assert set(USED_COLUMNS) == {
        "hashed_userid", "timezone", "starttime_local", "starttime_utc_unix_timestamp", "endtime_utc_unix_timestamp",
        "starttime_local_unix_timestamp", "endtime_local_unix_timestamp", "creation_starttime_diff_secs",
        "research_opt_in", "adult", "under_87_years"}


@pytest.mark.parametrize("fragment", FORBIDDEN_FRAGMENTS)
def test_no_location_identity_or_clinical_field_is_used(fragment):
    for col in USED_COLUMNS:
        if col == "timezone":
            continue
        assert fragment not in col.lower(), f"{col} looks like a forbidden field"


def test_shareable_file_is_read_with_exactly_the_declared_columns(csv_path):
    df = read_extract(csv_path)
    assert list(df.columns) == list(USED_COLUMNS)


def test_a_file_with_additional_fields_is_refused(tmp_path):
    path = tmp_path / "file_with_additional_fields.csv"
    synthetic_extract([(1, 7, 12, 0), (1, 31, 36, 0)], extra_columns=True).to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="Unexpected"):
        read_extract(path)


def test_non_hashed_user_identifiers_are_refused(tmp_path):
    df = synthetic_extract([(1, 7, 12, 0), (1, 31, 36, 0)])
    df["hashed_userid"] = "user@example.com"
    path = tmp_path / "bad.csv"
    df.to_csv(path, index=False)
    with pytest.raises(DataValidationError):
        load(path)


def test_other_time_zones_are_refused(tmp_path):
    df = synthetic_extract([(1, 7, 12, 0), (1, 31, 36, 0)])
    df.loc[0, "timezone"] = "Europe/London"
    path = tmp_path / "tz.csv"
    df.to_csv(path, index=False)
    with pytest.raises(DataValidationError):
        load(path)


def test_a_file_containing_a_single_attack_user_is_refused(tmp_path):
    """Excluded records must not be shared: the extract is refused rather than filtered."""
    path = tmp_path / "single.csv"
    synthetic_extract([(1, 7, 12, 0), (1, 31, 36, 0), (3, 9, 13, 0)]).to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="single attack"):
        load(path)


@pytest.mark.parametrize("criterion", ["research_opt_in", "adult", "under_87_years"])
@pytest.mark.parametrize("value", [False, None])
def test_records_not_attested_for_an_inclusion_criterion_are_refused(tmp_path, criterion, value):
    df = synthetic_extract([(1, 7, 12, 0), (1, 31, 36, 0)])
    df[criterion] = df[criterion].astype(object)
    df.loc[1, criterion] = value
    path = tmp_path / "criterion.csv"
    df.to_csv(path, index=False)
    with pytest.raises(DataValidationError, match=criterion):
        load(path)


@pytest.mark.parametrize("criterion", ["research_opt_in", "adult", "under_87_years"])
def test_a_file_without_an_inclusion_criterion_column_is_refused(tmp_path, criterion):
    path = tmp_path / "missing.csv"
    synthetic_extract([(1, 7, 12, 0), (1, 31, 36, 0)]).drop(columns=criterion).to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="missing"):
        read_extract(path)
