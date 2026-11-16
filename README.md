# mlops-training · Lesson 01: data engineering

Synthetic datasets for hands-on MLOps training: data validation, leakage, drift, training-serving skew and delayed labels.

**In this lesson** you explore the F1 race data, find the columns that leak the answer, keep two versions of the 2026 results with DVC, and write data quality checks with Great Expectations that catch a change in the data.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majlisofai/mlops-training?ref=01-data-engineering)

## Trainees: start here

1. **Open your codespace.** Click the badge above. Check that the branch is **`01-data-engineering`**, then click **Create codespace**. A copy of VS Code opens in your browser. You need a GitHub account. The codespace runs on your account and uses your free monthly Codespaces hours.
2. **Wait for the setup.** The first start takes a few minutes, because the codespace installs Python packages. Wait until the terminal says the setup has finished before you run any command.
3. **Open the lesson.** In the file explorer, open [`exercises/data-engineering/README.md`](exercises/data-engineering/README.md). Right-click it and choose **Open Preview** to read it formatted.
4. **Do the three parts** in order:

   | Part | What you do | You are done when |
   |---|---|---|
   | 1. Explore | Run `exercises/data-engineering/explore.ipynb` and complete the four *Your turn* cells | You can name the leakage columns and say what changed in 2026 |
   | 2. Version | Keep the provisional and the final 2026 results as two DVC versions of `f1/data/season_2026.csv`, then switch between them | `dvc diff HEAD~1` shows the file as modified, with 23 positions and 6 labels changed |
   | 3. Check quality | Complete TODO 1 to TODO 5 in `exercises/data-engineering/quality_checks.py` | The checks pass on `races.csv` (13 of 13) and fail on `season_2026.csv` (12 of 13) |

5. **Discuss** the four questions at the end of the lesson with your group.

**Rules for this lesson**

- Run every command from the repository root, `/workspaces/mlops-training`.
- Commit in your codespace when the lesson tells you to, but **do not push**.
- Try the TODOs before you open the reference solution in `exercises/data-engineering/solution/`.

**If something goes wrong**

| Problem | Fix |
|---|---|
| `dvc: command not found` or `No module named ...` | The setup has not finished. Wait, or run `pip install -r .devcontainer/requirements.txt`. |
| VS Code asks you to pick a kernel | Choose **Python Environments → Python 3.12**. |
| A notebook cell says `FileNotFoundError` | Run the first cell again. It moves to the repository root. |
| `dvc add` says the file is already tracked by Git | Only `season_2026.csv` is new. For a file Git already tracks, run `git rm --cached <file>` first. |
| `dvc checkout` changes nothing | Run `git checkout` on the `.dvc` file first. DVC follows the pointer that Git has checked out. |
| You closed the browser tab | Go to [github.com/codespaces](https://github.com/codespaces) and open your codespace again. Your work is still there. |

When you finish, stop the codespace (**Codespaces** menu at the bottom left → **Stop Current Codespace**) so it does not use your hours.

## Tools in the codespace

The codespace runs Python 3.12 and installs the tools from [`.devcontainer/requirements.txt`](.devcontainer/requirements.txt):

| Task | Tools |
|---|---|
| Data exploration | pandas, DuckDB, JupyterLab, matplotlib, seaborn, ydata-profiling, and the Data Wrangler and Rainbow CSV extensions (right-click a CSV → **Open in Data Wrangler**) |
| Data versioning | DVC and the DVC extension |
| Data quality | Great Expectations and pandera for validation, Evidently for drift and training-serving skew reports |

## Datasets

| Folder | Dataset | Target |
|---|---|---|
| [`f1/data/`](f1/data/) | Synthetic Grand Prix championship: 10 fictional teams, 24 circuits, five seasons, 2,400 car-race rows | `points_finish` |
| [`spl/data/`](spl/data/) | Synthetic Saudi league: 18 clubs per season, 34 rounds, five seasons, 3,060 club-match rows | `win` |

**All results, players, teams and drivers are synthetic.** They were generated from seed 2026 and describe no real season or person. They are not a basis for betting, club or team decisions, or claims about anyone real.

Each dataset folder has a `README.md` with the file list, the column dictionary, which columns are known before versus after the event (leakage), and the facts you can check. Besides the main training and holdout CSV, each folder holds the 2026 provisional and final results, a corrections file, and `scenarios/*.json` windows for monitoring exercises (a reference window, an input-drift window and a training-serving-skew window).
