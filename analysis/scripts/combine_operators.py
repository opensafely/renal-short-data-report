import pandas as pd
import numpy as np
from pathlib import Path
from variables import tests_extended
from utilities import (
    OUTPUT_DIR,
    match_input_files,
    get_date_input_file,
    round_value,
)
from redaction_utils import group_low_values_series, drop_and_round


Path(OUTPUT_DIR / f"pub/operator_counts").mkdir(parents=True, exist_ok=True)


# 1. A count of each code
code_counts = {}

# 2. A count of each code with associated numeric value
numeric_value_counts = {}


# 3. A count of each operator
operator_counts = {}


# 4. A count of each numeric value-operator pair
numeric_value_operator_counts = {}


for test in tests_extended:
    code_counts[test] = []
    numeric_value_counts[test] = []
    operator_counts[test] = []
    numeric_value_operator_counts[test] = {}

    for operator in ["<", ">", "<=", ">=", "="]:
        numeric_value_operator_counts[test][operator] = []


numeric_value_mappings = {
    "albumin": {
        (16, 20): 20,
        (21, 30): 30,
        (31, 40): 40,
        (41, 50): 50,
        (51, 100): 100,
        (101, float("inf")): 101,
    },
    "creatinine": {
        (0, 10): 10,
        (11, 20): 20,
        (21, 30): 30,
        (31, 40): 40,
        (41, 50): 50,
        (51, 60): 60,
        (61, 70): 70,
        (71, 80): 80,
        (81, 90): 90,
        (91, 100): 100,
        (101, 110): 110,
        (111, 120): 120,
        (121, 130): 130,
        (131, 140): 140,
        (141, 150): 150,
        (151, 200): 200,
        (201, 500): 500,
        (501, 1000): 1000,
        (1001, float("inf")): 1001,
    },
    "eGFR": {
        (1, 5): 5,
        (6, 10): 10,
        (11, 15): 15,
        (16, 20): 20,
        (21, 25): 25,
        (26, 30): 30,
        (31, 35): 35,
        (36, 40): 40,
        (41, 45): 45,
        (46, 50): 50,
        (51, 55): 55,
        (56, 60): 60,
        (61, 65): 65,
        (66, 70): 70,
        (71, 75): 75,
        (76, 80): 80,
        (81, 85): 85,
        (86, 90): 90,
        (91, 95): 95,
        (96, 100): 100,
        (101, 105): 105,
        (106, 110): 110,
        (111, 115): 115,
        (116, 120): 120,
        (121, float("inf")): 121,
    },
    "acr": {
        (11, 15): 15,
        (16, 20): 20,
        (21, 25): 25,
        (26, 30): 30,
        (31, 35): 35,
        (36, 40): 40,
        (41, 45): 45,
        (46, 50): 50,
        (51, 100): 100,
        (101, float("inf")): 101,
    },
    "cr_cl": {
        (21, 25): 25,
        (26, 30): 30,
        (31, float("inf")): 31,
    },
}


def map_numeric_values(series, mapping):
    conditions = [
        series.between(lower, upper, inclusive="left")
        for (lower, upper), _ in mapping.items()
    ]
    choices = [mapped_value for _, mapped_value in mapping.items()]

    return np.select(conditions, choices, default=series)


def convert_values(df, test, mapping):
    df.loc[df[f"{test}_numeric_value"] < 0, f"{test}_numeric_value"] = -1

    df.loc[
        (df[f"{test}_numeric_value"] > 0) & (df[f"{test}_numeric_value"] < 1),
        f"{test}_numeric_value",
    ] = 1

    df[f"{test}_numeric_value"] = df[f"{test}_numeric_value"].apply(
        lambda x: round_value(x)
    )


    df[f"{test}_numeric_value"] = map_numeric_values(
        df[f"{test}_numeric_value"], mapping[test]
    )
    return df


for file in (OUTPUT_DIR / "joined").iterdir():
    if match_input_files(file.name):
        df = pd.read_csv((OUTPUT_DIR / "joined") / file.name)

        date = get_date_input_file(file.name)

        for test in tests_extended:
            df[f"{test}_operator"].fillna("missing", inplace=True)

            # 1 A count of each code
            code_counts[test].append(df[f"{test}_code"].value_counts())

            # subset with a numeric value >0 OR where numeric value is 0 but operator is not missing
            df_subset_with_numeric_value = df.loc[
                (
                    (df[f"{test}_numeric_value"].notnull())
                    & (df[f"{test}_numeric_value"] > 0)
                )
                | (
                    (df[f"{test}_numeric_value"] == 0)
                    & (df[f"{test}_operator"] != "missing")
                ),
                :,
            ]

            # 2. A count of each code with associated numeric value
            numeric_value_counts[test].append(
                df_subset_with_numeric_value.loc[
                    :,
                    f"{test}_code",
                ].value_counts()
            )

            # 3. A count of each operator
            operator_counts[test].append(
                df_subset_with_numeric_value[f"{test}_operator"].value_counts()
            )

            # 4. A count of each numeric value-operator pair

            # convert any negative values to -1, any values exactly 0 remain as 0, any values between 0 and 1 are rounded to 1

            convert_values(df_subset_with_numeric_value, test, numeric_value_mappings)

            # replace missing and ~ with =
            df_subset_with_numeric_value[f"{test}_operator"].replace(
                "missing", "=", inplace=True
            )
            df_subset_with_numeric_value[f"{test}_operator"].replace(
                "~", "=", inplace=True
            )

            for operator in ["<", ">", "<=", ">=", "="]:
                subset = df_subset_with_numeric_value.loc[
                    df[f"{test}_operator"] == operator,
                    [f"{test}_numeric_value", f"{test}_operator"],
                ]

                numeric_value_operator_counts[test][operator].append(
                    subset.groupby([f"{test}_numeric_value", f"{test}_operator"]).size()
                )

for test in tests_extended:
    # 1 A count of each code
    test_codes = pd.concat(code_counts[test], axis=1, sort=False).sum(axis=1)
    test_codes = group_low_values_series(test_codes)
    test_codes.rename("count", inplace=True)
    test_codes = test_codes.reset_index()
    test_codes.rename(columns={"index": "code"}, inplace=True)

    test_codes["count"] = drop_and_round(test_codes["count"])

    test_codes.to_csv(
        OUTPUT_DIR / f"pub/operator_counts/{test}_codes_count.csv", index=False
    )

    # 2. A count of each code with associated numeric value
    test_codes_with_numeric_value = pd.concat(
        numeric_value_counts[test], axis=1, sort=False
    ).sum(axis=1)
    test_codes_with_numeric_value = group_low_values_series(
        test_codes_with_numeric_value
    )
    test_codes_with_numeric_value.rename("count", inplace=True)
    test_codes_with_numeric_value = test_codes_with_numeric_value.reset_index()
    test_codes_with_numeric_value.rename(columns={"index": "code"}, inplace=True)
    test_codes_with_numeric_value["count"] = drop_and_round(
        test_codes_with_numeric_value["count"]
    )
    test_codes_with_numeric_value.to_csv(
        OUTPUT_DIR / f"pub/operator_counts/{test}_codes_with_numeric_value_count.csv",
        index=False,
    )

    # 3. A count of each operator

    test_operators = pd.concat(operator_counts[test], axis=1, sort=False).sum(axis=1)
    test_operators = group_low_values_series(test_operators)
    drop_and_round(test_operators).to_csv(
        OUTPUT_DIR / f"pub/operator_counts/{test}_operators_count.csv"
    )

    # 4. A count of each numeric value-operator pair

    combined_values = []
    for operator in ["<", ">", "<=", ">=", "="]:
        operator_combined = pd.concat(
            numeric_value_operator_counts[test][operator]
        ).reset_index()

        operator_combined.rename(
            columns={
                0: "count",
            },
            inplace=True,
        )

        operator_combined.sort_values(by=f"{test}_numeric_value", inplace=True)

        combined_values.append(operator_combined)

    combined_values = pd.concat(combined_values)

    combined_values = combined_values.groupby(
        [f"{test}_numeric_value", f"{test}_operator"]
    ).sum()

    combined_values.sort_values(
        by=[f"{test}_operator", f"{test}_numeric_value"], inplace=True
    )

    combined_values.to_csv(
        OUTPUT_DIR / f"pub/operator_counts/{test}_numeric_value_operator_count.csv",
        index=True,
    )

    # remove any rows where count is <=7
    combined_values = combined_values[combined_values["count"] > 7]
    combined_values["count"] = combined_values["count"].apply(round_value, args=(5,))

    combined_values.to_csv(
        OUTPUT_DIR
        / f"pub/operator_counts/{test}_numeric_value_operator_count_rounded.csv",
        index=True,
    )
