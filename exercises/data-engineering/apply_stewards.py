"""Apply the stewards' decisions to f1/data/season_2026.csv.

The 2026 results are published twice: provisional results right after each race, and final
results after the stewards hand out penalties (2 to 26 hours later). This script turns the
provisional file into the final one, so you can version both with DVC (part 2).

Usage:
    python exercises/data-engineering/apply_stewards.py
"""

from pathlib import Path

import pandas as pd

DATA = Path("f1/data")
SEASON = DATA / "season_2026.csv"
POINTS = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


def main():
    # Read as text so every column we do not correct is written back unchanged.
    season = pd.read_csv(SEASON, dtype=str)
    final = pd.read_csv(DATA / "season_2026_final.csv", dtype=str)[
        ["race_id", "driver_code", "final_position", "points_finish_final"]
    ]

    merged = season.merge(final, on=["race_id", "driver_code"], how="left", validate="one_to_one")
    changed = merged["finish_position"] != merged["final_position"]

    # Positions and labels come from the final classification; points follow the position.
    merged["finish_position"] = merged["final_position"]
    merged["points_finish"] = merged["points_finish_final"]
    merged["points"] = merged["finish_position"].astype(int).map(POINTS).fillna(0).astype(int)
    merged.drop(columns=["final_position", "points_finish_final"]).to_csv(SEASON, index=False)

    print(f"Applied the stewards' decisions: {changed.sum()} entries changed position.")


if __name__ == "__main__":
    main()
