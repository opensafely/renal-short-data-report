import pandas as pd
import numpy as np
from variables import tests
from utilities import (
    OUTPUT_DIR,
    match_input_files,
    get_date_input_file,
    combine_value_with_operator,
)
from redaction_utils import (group_low_values,group_low_values_series, 
    drop_and_round,
    round_column,)

numeric_value_operator_counts = {}
numeric_value_counts = {}
code_counts = {}
operator_counts = {}

for test in tests:
    numeric_value_operator_counts[test] = []
    numeric_value_counts[test] = []
    code_counts[test] = []
    operator_counts[test] = []


for file in (OUTPUT_DIR / "joined").iterdir():
    if match_input_files(file.name):
        df = pd.read_csv((OUTPUT_DIR / "joined") / file.name)
        date = get_date_input_file(file.name)

        # replace null operator with missing
        for test in tests:
            df[f"{test}_operator"].fillna("missing", inplace=True)

            # how many numeric values have a matched operator?
            num_with_numeric_value_and_operator = (
                df.loc[
                    (
                        (df[f"{test}_numeric_value"].notnull())
                        & (df[f"{test}_numeric_value"] > 0)
                    ),
                    :,
                ]
                .groupby(f"{test}_operator")[[test]]
                .sum()
            )

            operator_counts[test].append(
                num_with_numeric_value_and_operator.replace(np.nan, "missing")
            )

            # combine value with operator (after rounding to nearest int)
            df[f"{test}_numeric_value"] = round_column(df[f"{test}_numeric_value"], 1)

            combine_value_with_operator(df, f"{test}_numeric_value", f"{test}_operator")

            


            numeric_value_operator_counts[test].append(
                df[f"{test}_numeric_value_with_operator"].value_counts(sort=True)
            )

            # find codes where attached numeric value
            numeric_value_counts[test].append(
                df.loc[
                    (
                        (df[f"{test}_numeric_value"].notnull())
                        & (df[f"{test}_numeric_value"] > 0)
                    ),
                    f"{test}_code",
                ].value_counts()
            )

            code_counts[test].append(df[f"{test}_code"].value_counts())


for test in tests:
    # combine numeric value operator counts
   
    combined_values = pd.concat(numeric_value_operator_counts[test])
    test_count = combined_values.groupby(combined_values.index).sum()
    test_count = test_count.reset_index(name="count")
  
    test_count.rename(columns={"index": "value"}, inplace=True)
    
    for operator in ["<", ">", "<=", ">=", "~", "="]:
        subset = test_count.loc[test_count["value"].str.startswith(operator),:]

        subset = group_low_values(subset, "count", "value", 7, 5)
        subset = subset.sort_values(by="count")
    
        subset.to_csv(
            OUTPUT_DIR / f"{test}_numeric_value_operator_count_{operator}.csv",index=False
        )
    
 

    # combine numeric value counts
    test_codes = pd.concat(numeric_value_counts[test])
    test_codes_count = test_codes.groupby(test_codes.index).sum().reset_index()
    test_codes_count.rename(columns={"index": "code", f"{test}_code": "num"}, inplace=True)
    test_codes_count.to_csv(
        OUTPUT_DIR / f"{test}_numeric_value_count.csv", index=False
    )

    # combine code counts

    test_codes_all = pd.concat(code_counts[test])
    test_codes_count_all = test_codes_all.groupby(test_codes_all.index).sum().reset_index()

    test_codes_count_all.rename(columns={"index": "code", f"{test}_code": "num"}, inplace=True)
    

    test_codes_count_all.to_csv(OUTPUT_DIR / f"{test}_codes_count.csv", index=False)

    # combine operator counts

    test_operators = pd.concat(operator_counts[test], axis=1, sort=False).sum(axis=1)
    test_operators = group_low_values_series(test_operators)
    drop_and_round(test_operators).to_csv(OUTPUT_DIR / f"{test}_operators_count.csv", index=False)
