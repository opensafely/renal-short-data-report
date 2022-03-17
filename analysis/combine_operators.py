import pandas as pd
import numpy as np
import re
from pathlib import Path

OUTPUT_DIR = Path("output")


def drop_and_round(column):
    column[column <= 5] = 0
    return column.apply(lambda x: 5 * round(float(x) / 5))


def match_input_files(file: str) -> bool:
    """Checks if file name has format outputted by cohort extractor"""
    pattern = r"^input_20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])\.csv.gz"
    return True if re.match(pattern, file) else False


def get_date_input_file(file: str) -> str:
    """Gets the date in format YYYY-MM-DD from input file name string"""
    # check format
    if not match_input_files(file):
        raise Exception("Not valid input file format")

    else:
        date = result = re.search(r"input_(.*)\.csv.gz", file)
        return date.group(1)


def combine_value_with_operator(df, value_column, operator_column):
    df[f"{value_column}_with_operator"] = df[operator_column].str.cat(
        df[value_column].astype("str")
    )


# counts of each numeric value - operator pair
value_counts_creatinine = []
value_counts_cr_cl = []

# counts of numeric values for each code
codes_creatinine = []
codes_cr_cl = []

# counts for each operator type
operators_creatinine = []
operators_cr_cl = []


for file in OUTPUT_DIR.iterdir():
    if match_input_files(file.name):
        df = pd.read_csv(OUTPUT_DIR / file.name)
        date = get_date_input_file(file.name)

        # how many numeric values have a matched operator?
        num_with_numeric_value_and_operator_creatinine = (
            df.loc[df["creatinine_numeric_value"].notnull(), :]
            .groupby("creatinine_operator")[["creatinine"]]
            .sum()
        )
        operators_creatinine.append(num_with_numeric_value_and_operator_creatinine)

        num_with_numeric_value_and_operator_cr_cl = (
            df.loc[df["cr_cl_numeric_value"].notnull(), :]
            .groupby("cr_cl_operator")[["cr_cl"]]
            .sum()
        )
        operators_cr_cl.append(num_with_numeric_value_and_operator_cr_cl)

        combine_value_with_operator(
            df, "creatinine_numeric_value", "creatinine_operator"
        )
        combine_value_with_operator(df, "cr_cl_numeric_value", "cr_cl_operator")

        value_counts_creatinine.append(
            df["creatinine_numeric_value_with_operator"].value_counts(sort=True)
        )
        value_counts_cr_cl.append(
            df["cr_cl_numeric_value_with_operator"].value_counts(sort=True)
        )

        # find codes where attached numeric value
        codes_creatinine.append(
            df.loc[
                df["creatinine_numeric_value"].notnull(), "creatinine_code"
            ].value_counts()
        )
        codes_cr_cl.append(
            df.loc[df["cr_cl_numeric_value"].notnull(), "cr_cl_code"].value_counts()
        )


combined_creatinine_values = pd.concat(value_counts_creatinine)
creatinine_count = combined_creatinine_values.groupby(
    combined_creatinine_values.index
).sum()
creatinine_count = drop_and_round(creatinine_count)
creatinine_count.to_csv(OUTPUT_DIR / "creatinine_count.csv")

combined_cr_cl_values = pd.concat(value_counts_cr_cl)
cr_cl_count = combined_cr_cl_values.groupby(combined_cr_cl_values.index).sum()
cr_cl_count = drop_and_round(cr_cl_count)
cr_cl_count.to_csv(OUTPUT_DIR / "cr_cl_count.csv")

cr_cl_codes = pd.concat(codes_cr_cl)
cr_cl_codes_count = cr_cl_codes.groupby(cr_cl_codes.index).sum()
cr_cl_codes_count = drop_and_round(cr_cl_codes_count)
cr_cl_codes_count.to_csv(OUTPUT_DIR / "cr_cl_codes_count.csv")


creatinine_codes = pd.concat(codes_creatinine)
creatinine_codes_count = creatinine_codes.groupby(creatinine_codes.index).sum()
creatinine_codes_count = drop_and_round(creatinine_codes_count)
creatinine_codes_count.to_csv(OUTPUT_DIR / "creatinine_codes_count.csv")


creatinine_operators = pd.concat(operators_creatinine)
creatinine_operators_count = creatinine_operators.groupby(
    creatinine_operators.index
).sum()
creatinine_operators["creatinine"] = drop_and_round(creatinine_operators["creatinine"])
creatinine_operators_count.to_csv(OUTPUT_DIR / "creatinine_operators_count.csv")

cr_cl_operators = pd.concat(operators_cr_cl)
cr_cl_operators_count = creatinine_operators.groupby(cr_cl_operators.index).sum()
cr_cl_operators["cr_cl"] = drop_and_round(cr_cl_operators["cr_cl"])
cr_cl_operators_count.to_csv(OUTPUT_DIR / "cr_cl_operators_count.csv")
