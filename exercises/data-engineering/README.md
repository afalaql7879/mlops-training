# Lesson 01: data engineering

A model is only as good as its data. In this lesson you **explore** the F1 data, **version** it with DVC, and **check its quality** with Great Expectations.

Time: about 75 minutes. Three parts, about 25 minutes each.

| Part | You use | You learn |
|---|---|---|
| 1. Explore | Jupyter, DuckDB, ydata-profiling, Data Wrangler | Check the facts, find leakage, spot a change between years |
| 2. Version | DVC, Git | Keep two versions of the same file and switch between them |
| 3. Check quality | Great Expectations | Write checks that pass on good data and fail on changed data |

Run every command from the repository root, `/workspaces/mlops-training`.

## Part 1: explore the data

1. Open [`f1/data/README.md`](../../f1/data/README.md) and read the column table. The **Known** column says if a value is known before or after the race.
2. In the file explorer, right-click `f1/data/races.csv` and choose **Open in Data Wrangler**. Click a column header to see its summary. Close it when you are done.
3. Open [`explore.ipynb`](explore.ipynb). When VS Code asks for a kernel, pick **Python 3.12**. Run each cell with **Shift+Enter** and complete the four *Your turn* cells.

> **Check:** the first query gives 120 races, 2,400 entries, 28 drivers, a points share of 0.5 and a DNF rate of 0.10875.

<details>
<summary>Answers for part 1 (open after you try)</summary>

1. The grid rule is right for **0.804** of 2025 entries (0.8041...).
2. `points_finish` is defined from `finish_position` (top 10), and only top-10 finishers score points. Both are known only after the race. The leakage columns are `finish_position`, `points`, `status`, `laps_completed`, `fastest_lap` and `actual_rain`.
3. The DNF rate in 2026 is **0.275**, against 0.109 in training. It is high for every team tier. A model trained on 2021-2025 has not seen this many retirements, so its predictions get worse. Also look at `points_share` by tier: the backmarker tier scores much more in 2026, because Cobalt Racing (a backmarker team in training) leads the season.
4. `rain_prob` goes from 0 to 0.55 and `quali_gap_ms` from 0 to 2,839.

</details>

## Part 2: version the data with DVC

The 2026 results are published twice. The **provisional** results come right after each race. The **final** results come after the stewards hand out penalties, 2 to 26 hours later (see `f1/data/stewards_2026.csv`). A model that learns from the results must know which version it used.

You keep both versions of one file, `f1/data/season_2026.csv`, with DVC.

**1. Start DVC** in the repository:

```bash
dvc init
git commit -m "Initialise DVC"
```

**2. Version 1: the provisional results.**

```bash
cp f1/data/season_2026_provisional.csv f1/data/season_2026.csv
dvc add f1/data/season_2026.csv
git add f1/data/season_2026.csv.dvc f1/data/.gitignore
git commit -m "2026 results: provisional"
```

Open `f1/data/season_2026.csv.dvc`. Git stores this small pointer file. DVC stores the data itself in its cache (`.dvc/cache`). The `md5` is the data version.

> **Check:** the md5 is `1dee862a3599e087b764cfb9ebd79ee8`.

**3. Version 2: the final results.** Apply the stewards' decisions, then save the new version:

```bash
python exercises/data-engineering/apply_stewards.py
dvc add f1/data/season_2026.csv
git add f1/data/season_2026.csv.dvc
git commit -m "2026 results: final, after the stewards"
```

> **Check:** the script says `23 entries changed position`, and the md5 is now `87ffbc792aeb259333a41f7f573a38e3`.

**4. Compare the versions.**

```bash
dvc diff HEAD~1
python -c "
import pandas as pd
v1 = pd.read_csv('f1/data/season_2026_provisional.csv')
v2 = pd.read_csv('f1/data/season_2026.csv')
print('positions changed:', (v1.finish_position != v2.finish_position).sum())
print('labels changed:', (v1.points_finish != v2.points_finish).sum())
"
```

> **Check:** `dvc diff` shows `f1/data/season_2026.csv` as modified. 23 positions changed and 6 labels (`points_finish`) changed.

**5. Go back in time.** Get version 1 back, then return to version 2:

```bash
git checkout HEAD~1 -- f1/data/season_2026.csv.dvc
dvc checkout f1/data/season_2026.csv
head -3 f1/data/season_2026.csv

git checkout HEAD -- f1/data/season_2026.csv.dvc
dvc checkout f1/data/season_2026.csv
```

Git moves the pointer, and DVC puts the matching data in place. You commit only in your codespace. Do not push.

## Part 3: check data quality with Great Expectations

An *expectation* is a check that data must pass, such as "`grid` is between 1 and 20". A *suite* is a list of expectations. You run the suite on a file and get a pass or a fail for each check.

1. Open [`quality_checks.py`](quality_checks.py). Not-null checks for the model inputs and the `grid` range check are done for you.
2. Complete **TODO 1 to TODO 5** in `build_expectations()`. Use your notes from part 1, step 4.
3. Run the suite on the training data:

   ```bash
   python exercises/data-engineering/quality_checks.py f1/data/races.csv
   ```

   > **Check:** `13 of 13 checks passed`, and the exit code (`echo $?`) is `0`.

4. Run the same suite on the 2026 data:

   ```bash
   python exercises/data-engineering/quality_checks.py f1/data/season_2026.csv
   ```

   > **Check:** `12 of 13 checks passed`. The `dnf` mean check fails with 0.275, and the exit code is `1`.

Every value in the 2026 file is valid: no nulls, no values out of range, no duplicates. The data is still different from the training data. Only the distribution check (TODO 5) catches that.

## Discuss

1. You train a model on Monday morning and the stewards publish a penalty on Monday afternoon. Which version of the labels did your model use? How does DVC help you answer this question three months later?
2. Six labels changed between the provisional and the final results. Which version should you use to evaluate a model, and why?
3. Which checks in part 3 check that values are *valid*, and which check that the data is *like the training data*? Which kind fails more often in production?
4. The `dnf` check uses the range 0.05 to 0.20. How would you choose that range for a real system?

## Stretch

- Add a check that `quali_gap_ms` is between 0 and 5,000. Then make a copy of `races.csv` with `quali_gap_ms` divided by 1,000 (seconds, not milliseconds) and run the suite on it. Does your new check catch the change? Which check would?
- Put `f1/data/races.csv` under DVC as well. You must run `git rm --cached f1/data/races.csv` first, because Git already tracks it.
- Explore the Saudi league data in `spl/data/` with the same notebook queries.

## Stuck?

There is a reference solution in [`solution/quality_checks.py`](solution/quality_checks.py). Try the TODOs first.

## Next lesson

Lesson 02, on the `02-mlflow` branch, logs the data version and the quality checks to an MLflow tracking server.
