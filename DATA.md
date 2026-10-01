# Shareable extract: data dictionary

The analysis uses the shareable extract `migraine_attacks_us_east_shareable.csv`, which contains
the 11 fields listed below. It is not included in this repository and is not distributed: it
remains with Healint Pte Ltd, which runs this code on it upon reasonable request and returns the aggregated outputs (see
README).

| | |
|---|---|
| File name | `migraine_attacks_us_east_shareable.csv` |
| Rows (attacks) / users | 2,288,551 / 138,025 (included records only; see the selection below) |
| Period (local time) | 9 January 2014 – 24 May 2023 |
| SHA-256 | `b522916e1c596605324140b023cb9688fe40305882b53a757dc855414c1c7d05` |

To check that you have received the exact file: `shasum -a 256 migraine_attacks_us_east_shareable.csv`.

Each row is one migraine attack recorded by a Migraine Buddy user who had opted in, within the app, to the use of their
data for research. The records are de-identified: they contain no direct identifier.

| Field | Type | Content | Use in the analysis |
|---|---|---|---|
| `hashed_userid` | text (32 hexadecimal characters) | De-identified user identifier, specific to this study. No direct identifier is included. | Grouping attacks by user (check that every user has at least two attacks, bootstrap by user, previous-day attacks, months with ≥ 15 headache days) |
| `timezone` | text | IANA time zone of the device (`America/New_York` for every row). The only location information. | Defines the regional dataset; local clock time |
| `starttime_local` | text (`YYYY-MM-DD hh:mm:ss.sss`) | Attack start, local clock time | Onset hour (main outcome), calendar year, study window |
| `starttime_utc_unix_timestamp` | integer (s) | Attack start, UTC | Ordering of attacks; interval since the previous attack |
| `endtime_utc_unix_timestamp` | integer (s) | Attack end, UTC | Attack duration (≥ 2 h); interval since the previous attack |
| `starttime_local_unix_timestamp` | integer (s) | Attack start, local clock time, in seconds | Calendar days (previous-day attacks, headache days) |
| `endtime_local_unix_timestamp` | integer (s) | Attack end, local clock time, in seconds | Calendar days covered by an attack (headache days) |
| `creation_starttime_diff_secs` | integer (s) | Delay between the attack start and the creation of the record in the app | How the start time was entered: in real time, preset offset or manual entry |
| `research_opt_in` | boolean (`True` on every row) | The user opted in, within the app, to the use of their data for research. Attestation by Healint, verified at the initial extraction | Inclusion criterion; a file with any other value is refused |
| `adult` | boolean (`True` on every row) | The user is an adult. Attestation by Healint, verified at the initial extraction | Inclusion criterion; a file with any other value is refused |
| `under_87_years` | boolean (`True` on every row) | The user is less than 87 years old. Attestation by Healint, verified at the initial extraction | Inclusion criterion; a file with any other value is refused |

The three inclusion-criterion fields are attestations by the data provider. They are not derived from other content of
the file, which contains no age, date of birth or consent record, and they cannot be re-verified from it.

**Not included in the shareable extract**, and never used by this analysis:
- any direct identifier (name, e-mail, phone, device identifier);
- location below time-zone level;
- medication or drug names;
- triggers or premonitory symptoms;
- demographic data (age, sex, date of birth), beyond the three inclusion-criterion attestations above;
- free text.

**Selection applied by Healint before sharing.** Only records that meet all the criteria below are included; records
that do not meet them are not shared.
- users who opted in to research use, adults, less than 87 years old (verified at the initial extraction);
- users located in the United States Eastern time zone;
- attacks recorded between January 2014 and May 2023;
- attacks lasting at least 2 h, since shorter episodes cannot be reliably classified as migraine attacks (untreated
  attacks last at least 4 h, and treatment efficacy is conventionally assessed at 2 h).
- users with at least two recorded attacks: 56,333 users with a single recorded attack (possible test records) were
  removed before sharing.

**Checks made by the code on loading.** The code refuses a file whose columns differ from the 11 fields above, or that
contains another time zone, an attack shorter than 2 h, a user with a single attack, or a record not attested for one of
the three inclusion criteria. It does not check the period (January 2014 – May 2023), which is documented by the data
provider.
