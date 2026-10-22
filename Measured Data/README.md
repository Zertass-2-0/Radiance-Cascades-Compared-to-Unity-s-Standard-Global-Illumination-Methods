# Measured Data

Raw performance logs from the experiment. There is one folder per test scene (`Isometric`, `Realistic FPS`, `Stylized Fps`), and each folder has one CSV file per GI method:

```
gi_run_<METHOD>_<date>_<time>.csv
```

Each run is about 60 seconds long, with one sample about every 0.2 seconds.

## How to read the CSV files

**The comma is used both as the column separator and as the decimal separator.** The header has 4 columns, but every data row has 7 comma-separated parts. Read them in pairs:

```
time_sec,ms_per_frame,fps,gi_mode
59,99,3,176,314,90,NoGI
```

| Parts | Column | Example | Value |
|-------|--------|---------|-------|
| 1–2 | `time_sec` | `59,99` | 59.99 s |
| 3–4 | `ms_per_frame` | `3,176` | 3.176 ms |
| 5–6 | `fps` | `314,90` | 314.90 FPS |
| 7 | `gi_mode` | `NoGI` | GI method |

Because of this, Excel or `pandas.read_csv` with default settings will not split the columns correctly. Join parts 1+2, 3+4 and 5+6 with a dot to get the numbers.

## Summary block

At the end of every file, after an empty line, there is a summary of the run. The same comma rule applies (`avg_ms,4,747` means 4.747 ms):

```
SUMMARY
avg_ms,4,747
min_ms,4,285
max_ms,317,761
p95_ms,4,651
```

## Notes

- The first few rows of every run have very high frame times (about 260–330 ms) while the scene is still loading. In all 12 files, `max_ms` in the summary comes from these rows, so it does not show steady-state performance.
- In `Realistic FPS/gi_run_RTLM_*.csv` the `gi_mode` column says `RILM`, while the file name and the other scenes use `RTLM`. This looks like a typo.
