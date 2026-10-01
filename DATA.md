# Shareable extract: data dictionary

The analysis runs on a **shareable extract** derived from Healint's internal Migraine Buddy extract. The shareable
extract keeps **only the 8 fields listed below**, and nothing else. It is **not distributed** with this repository and
is available on reasonable request (see README).

Each row is one migraine attack recorded by a Migraine Buddy user who had opted in to the anonymous use of their data
for research.

| Field | Type | Content | Use in the analysis |
|---|---|---|---|
| `hashed_userid` | text (32 hexadecimal characters) | One-way hash of the app user identifier. No non-hashed identifier is included. | Grouping attacks by user (exclusion of single-attack users, bootstrap by user, previous-day attacks, months with ≥ 15 headache days) |
| `timezone` | text | IANA time zone of the device (`America/New_York` for every row). The only location information. | Defines the regional dataset; local clock time |
| `starttime_local` | text (`YYYY-MM-DD hh:mm:ss.sss`) | Attack start, local clock time | Onset hour (main outcome), calendar year, study window |
| `starttime_utc_unix_timestamp` | integer (s) | Attack start, UTC | Ordering of attacks; interval since the previous attack |
| `endtime_utc_unix_timestamp` | integer (s) | Attack end, UTC | Attack duration (≥ 2 h); interval since the previous attack |
| `starttime_local_unix_timestamp` | integer (s) | Attack start, local clock time, in seconds | Calendar days (previous-day attacks, headache days) |
| `endtime_local_unix_timestamp` | integer (s) | Attack end, local clock time, in seconds | Calendar days covered by an attack (headache days) |
| `creation_starttime_diff_secs` | integer (s) | Delay between the attack start and the creation of the record in the app | How the start time was entered: in real time, preset offset or manual entry |

**Not included in the shareable extract**, and never used by this analysis:
- any non-hashed identifier;
- location below time-zone level;
- medication or drug names;
- triggers or premonitory symptoms;
- demographic data;
- free text.

**Selection applied at extraction:**
- users located in the United States Eastern time zone;
- attacks recorded between January 2014 and May 2023;
- attacks lasting at least 2 h, since shorter episodes cannot be reliably classified as migraine attacks (untreated
  attacks last at least 4 h, and treatment efficacy is conventionally assessed at 2 h).
