"""Run data quality checks on an F1 results file with Great Expectations.

Your task: add the missing expectations in build_expectations(). Loading the data,
running the checks and printing the results are done for you. See
exercises/data-engineering/README.md, part 3.

Usage:
    python exercises/data-engineering/quality_checks.py f1/data/races.csv
"""

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("GX_ANALYTICS_ENABLED", "false")

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd
from great_expectations.data_context.types.base import ProgressBarsConfig

MODEL_INPUTS = ["grid", "quali_gap_ms", "driver_form", "team_form", "team_dnf_rate", "rain_prob", "circuit_type"]


def build_expectations():
    expectations = [gxe.ExpectColumnValuesToNotBeNull(column=c) for c in MODEL_INPUTS]
    expectations += [
        # Validity: values a real race can have.
        gxe.ExpectColumnValuesToBeBetween(column="grid", min_value=1, max_value=20),
        # TODO 1: rain_prob is a probability, between 0 and 1.
        # TODO 2: circuit_type is one of street, permanent, high_speed (ExpectColumnValuesToBeInSet).
        # TODO 3: status is one of Finished, DNF.
        # Uniqueness:
        # TODO 4: one row per car per race: race_id and driver_code together are unique
        #         (ExpectCompoundColumnsToBeUnique with column_list=[...]).
        # Distribution:
        # TODO 5: the share of cars that do not finish was 10.9 % in training. main() adds a
        #         column "dnf" (1 = did not finish). Expect its mean to be between 0.05 and 0.20
        #         (ExpectColumnMeanToBeBetween).
    ]
    return expectations


def validate(df: pd.DataFrame, name: str):
    context = gx.get_context(mode="ephemeral")
    context.variables.progress_bars = ProgressBarsConfig(globally=False)
    batch = (
        context.data_sources.add_pandas("f1")
        .add_dataframe_asset(name)
        .add_batch_definition_whole_dataframe("all rows")
        .get_batch(batch_parameters={"dataframe": df})
    )
    suite = gx.ExpectationSuite(name="f1-results")
    for expectation in build_expectations():
        suite.add_expectation(expectation)
    return batch.validate(suite)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", type=Path, help="Path to an F1 results CSV, such as f1/data/races.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df["dnf"] = (df["status"] == "DNF").astype(int)
    result = validate(df, args.csv.stem)

    for r in result.results:
        cfg = r.expectation_config
        target = cfg.kwargs.get("column") or ", ".join(cfg.kwargs.get("column_list", []))
        observed = r.result.get("observed_value", r.result.get("unexpected_count", ""))
        print(f"{'PASS' if r.success else 'FAIL'}  {cfg.type:<40} {target:<22} {observed}")

    passed = sum(r.success for r in result.results)
    print(f"\n{args.csv}: {passed} of {len(result.results)} checks passed")
    # A non-zero exit lets a pipeline stop on bad data.
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
