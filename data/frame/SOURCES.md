# Sampling frame sources

Downloaded 2026-11-11T10:03:41-05:00 by Claude with `curl`, from the IPEDS Data Center
(National Center for Education Statistics). 2024 was the newest year available: the 2025 files
returned HTTP 404 at 10:03:18.

| File | URL | Bytes | SHA-256 |
|---|---|---|---|
| HD2024.zip | https://nces.ed.gov/ipeds/datacenter/data/HD2024.zip | 1,088,372 | d98425c123d7c0e872aec6e83960dfb501884818bf17385c340790f3d1f28345 |
| C2024_A.zip | https://nces.ed.gov/ipeds/datacenter/data/C2024_A.zip | 4,680,679 | 03234cc27fe4e7eb835a66d4f37aaec11bdac8dfa278f971584e1b20d03e1159 |
| HD2024_Dict.zip | https://nces.ed.gov/ipeds/datacenter/data/HD2024_Dict.zip | 140,379 | a68c38003a9e56b1b5f444377540d5120d86cecc35855f84f1393480b862487d |
| C2024_A_Dict.zip | https://nces.ed.gov/ipeds/datacenter/data/C2024_A_Dict.zip | 94,034 | a586396973828cd09fefdfe0f33432df300248189343e7e6b796ba931e998921 |

To rebuild: unzip all four into `data/frame/extracted/` (gitignored), then from the repo root run
`uv run --no-project python -I study/draw_sample.py`.

## Fields used (names and labels read from the dictionaries, not from memory)
Institution file `HD2024.csv`:
- `UNITID`, `INSTNM`, `STABBR`, `WEBADDR`
- `OBEREG`: Bureau of Economic Analysis region (9 = outlying areas, excluded)
- `CONTROL`: 1 public, 2 private not-for-profit, 3 private for-profit (excluded)
- `CYACTIVE` (1 = active) and `DEGGRANT` (1 = degree-granting)
- `CARNEGIERSCH`: Carnegie Classification 2025, Research Activity Designation (1 = Research 1)
- `CARNEGIEIC`: Carnegie Classification 2025, Institutional Classification (codes 1 to 31, -2)
- `HLOFFER`: highest level of offering (5 bachelor's, 6 and up graduate)

Completions file `C2024_a.csv`:
- `CIPCODE` (CIP 2020): 11.0701 Computer Science, 11.0101 Computer and Information Sciences, General
- `MAJORNUM` (1 = first major), `AWLEVEL` (3 associate's, 5 bachelor's, 7 master's, 17 research
  doctorate), `CTOTALT` (grand total awarded)

## Outputs
- `frame.csv`: 1,509 eligible schools, each with its stratum.
- `sample.csv`: the 15 schools (seed 20261111).
