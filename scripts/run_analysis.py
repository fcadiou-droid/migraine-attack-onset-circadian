"""Reproduce Fig. 1A, its source data and Supplementary Table 2.

Usage: python scripts/run_analysis.py [--data data/migraine_attacks_us_east_shareable.csv] [--out outputs]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from onset import config                                                    # noqa: E402
from onset.analysis import user_hour_matrix, robustness_table, reporting_characteristics   # noqa: E402
from onset.data import load                                                  # noqa: E402
from onset.figures import rose_plot                                          # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=config.DATA_FILE, help="the shareable extract (see DATA.md); not distributed")
    ap.add_argument("--out", default="outputs", help="output folder")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df, n_single = load(args.data)
    counts = user_hour_matrix(df).sum(axis=0)
    rose_plot(counts, out / "fig1a")
    with open(out / "fig1a_source_data.csv", "w") as f:              # aggregated hourly counts (Source Data)
        f.write("hour,attacks,proportion\n")
        for h, c in enumerate(counts):
            f.write(f"{h:02d}:00,{int(c)},{c / counts.sum():.6f}\n")
    rob = robustness_table(df)
    rob.to_csv(out / "stable2_robustness.csv", index=False)
    rep = reporting_characteristics(df)
    rep["users_excluded_single_attack"] = n_single
    rep["period"] = f"{df['start_local'].min():%Y-%m-%d} to {df['start_local'].max():%Y-%m-%d}"
    (out / "stable2_reporting.json").write_text(json.dumps(rep, indent=2))

    main_row = rob.iloc[0]
    print(f"{rep['attacks']:,} attacks from {rep['users']:,} users ({rep['period']}); "
          f"{n_single:,} single-attack users excluded.")
    print(f"Onsets 06:00–11:00: {main_row.share_06_11:.1%} (95% CI {main_row.ci_low:.1%}–{main_row.ci_high:.1%}); "
          f"modal hour {main_row.modal_hour:02d}:00; minimum {main_row.min_hour:02d}:00.")
    print(f"Outputs written to {out}/")


if __name__ == "__main__":
    main()
