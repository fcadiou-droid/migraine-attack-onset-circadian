"""Analysis parameters. All values are fixed in advance and documented in the README."""

# Dataset (see DATA.md)
DATA_FILE = "data/migraine_attacks_us_east_shareable.csv"

# Study population
TIME_ZONE = "America/New_York"      # regional dataset: users in the United States Eastern time zone
MIN_ATTACKS_PER_USER = 2            # users with a single recorded attack are excluded (possible test records)
MIN_DURATION_S = 2 * 3600           # the shareable extract contains only attacks lasting ≥ 2 h; verified on load

# Outcome
PEAK_HOURS = [6, 7, 8, 9, 10]       # 06:00–10:59 local time ("06:00–11:00")
ORIGINAL_WINDOW = ("2018-01-01", "2020-07-01")   # [start, end) of the original study window, local dates

# Sensitivity analyses
DURATION_CAP_H = 72                 # attack duration cap when counting headache days
CHRONIC_DAYS = 15                   # headache days per calendar month defining a "chronic" month
GAP_H = 48                          # minimum interval since the end of the previous attack
LOGGED_NOW_MAX_S = 60               # start time recorded at the moment of logging ("now")
PRESETS_S = (900, 1800, 3540, 3600) + tuple(3600 * h for h in range(2, 25))  # app preset offsets (15 min … 24 h)
PRESET_TOLERANCE_S = 60

# Resampling
SEED = 20260927
N_BOOT_MAIN = 1000
N_BOOT_SENSITIVITY = 200
