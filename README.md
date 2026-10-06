# Circadian pattern of migraine attack onset — analysis code

Code for reproducing the human attack-onset analysis of *Circadian regulation of migraine susceptibility* (Strother et al.):
the 24-hour distribution of migraine attack onset recorded in the Migraine Buddy application (Fig. 1A), its source data,
and the reporting characteristics and robustness analyses of Supplementary Table 2.

## Privacy and data governance

- **This repository contains no individual-level data**, and in particular no personal or health data. It contains code
  and documentation only; the only figures it reports are aggregated results. The tests run on synthetic records generated
  on the fly.
- **Consent.** Only data from Migraine Buddy users who had opted in, within the app, to the use of their data for
  research were analyzed.
- **Minimal, de-identified fields.** The analysis runs on a *shareable extract* restricted to the 8 fields it actually
  uses, plus 3 attestations of the inclusion criteria (research opt-in, adult, less than 87 years old) (see
  [DATA.md](DATA.md)). The code refuses any file containing other fields.
- **Included records only.** Records that do not meet the inclusion criteria are not shared; the code refuses a file
  containing any.
  - **De-identified, study-specific user identifiers.** The extract contains no name, e-mail or other direct identifier.
    The user identifier is specific to this study; the code checks its format (32 hexadecimal characters).
  - **Location is limited to the device time zone** (America/New_York). It is used only to place each attack in local
    clock time.
  - **The analysis uses no other information:** no medication or drug names, no triggers or symptoms, no
    demographic, free-text or contact information.
- **Origin of the data.** The de-identified extract was provided by Healint Pte Ltd, developer of Migraine Buddy, in 2023
  to Prof. Peter J. Goadsby (King's College London) under a data-sharing arrangement.
- **Data access.** The attack-level data remain with Aptar Digital Health, which acquired Migraine Buddy from Healint
  Pte Ltd, and are not distributed. To verify the analyses, Aptar Digital Health runs this code (an identified version
  of this repository) on the shareable extract upon reasonable request to contact@migrainebuddy.com and returns the
  aggregated outputs, so that no individual-level data are transferred.
- **Licence.** The MIT License covers the code only. It grants no right to the data.

## What the code does

| Step | Description |
|---|---|
| Load and validate | Reads the shareable extract (exactly the declared fields) and checks the format of the user identifiers, that there is a single time zone, that all attacks last at least 2 h, that every record is attested for the three inclusion criteria and that every user has at least two attacks. |
| Study population | All records of the shareable extract. Users with a single recorded attack (possible test records) were removed before sharing. |
| Main outcome | Distribution of attack onset across the 24 hours of local clock time, and the share of onsets between 06:00 and 11:00. 95% confidence intervals come from bootstrap resampling of users, since attacks are clustered within individuals. |
| Sensitivity analyses | Each user weighted equally; original study window only (Jan 2018 – Jun 2020); attacks with no attack on the previous day; exclusion of users with any month with ≥ 15 headache days; exclusion of attacks starting < 48 h after the previous one; start time recorded in real time vs entered retrospectively; each calendar year 2015–2022. |
| Outputs | `fig1a.{pdf,png,tiff}`, `fig1a_source_data.csv` (aggregated hourly counts), `stable2_robustness.csv`, `stable2_reporting.json`. |

All parameters are fixed in [`src/onset/config.py`](src/onset/config.py).

## Running the analysis

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests            # synthetic data only
# place the shareable extract in data/ (see DATA.md), then:
.venv/bin/python scripts/run_analysis.py
```

The analysis takes about one minute on a laptop for 2.3 million attacks. It was tested with Python 3.14.

## Expected results (shareable extract, United States Eastern time zone, 2014–2023)

| | |
|---|---|
| Attacks / users | 2,288,551 / 138,025 (56,333 users with a single recorded attack removed before sharing) |
| Onsets between 06:00 and 11:00 | 32.7% (95% CI 32.4–33.1), vs 20.8% under a uniform distribution |
| Modal / least frequent hour | 07:00 / 01:00 |

## License and citation

The code is released under the MIT License (see [LICENSE](LICENSE)). If you use this code, please cite the article (see [CITATION.cff](CITATION.cff)).
