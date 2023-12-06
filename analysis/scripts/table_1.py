import pandas as pd
import argparse
import pathlib
from utilities import OUTPUT_DIR, update_df
from redaction_utils import redact_table_1


def process_data(path, columns, condition_column=None):
    """
    Process the data from the given path with specified columns.
    Optionally filter data based on the condition_column.
    """
    if condition_column is None:
        cols_to_read = columns + ["patient_id"]
    else:
        cols_to_read = columns + ["patient_id", condition_column]

    df = pd.read_csv(path, usecols=cols_to_read)

    if condition_column:
        df = df[df[condition_column] == 1]
        df.drop(condition_column, axis=1, inplace=True)

    df.loc[:, columns] = df.loc[:, columns].fillna("missing")
    return df


def create_table_from_paths(paths, columns, condition_column=None):
    for i, path in enumerate(paths):
        updated_df = process_data(path, columns, condition_column)

        if i == 0:
            df = updated_df
        else:
            df = update_df(df, updated_df, columns=columns)

    df = df.drop("patient_id", axis=1)
    df = df.replace("missing", "Missing")
    df_counts = df.apply(lambda x: x.value_counts()).T.stack()
    df_counts = redact_table_1(df_counts)
    df_counts.index.names = ["condition", "condition_value"]
    df_counts.name = "count"

    return df_counts


def create_tables(paths, demographics):
    df_counts_all = create_table_from_paths(paths, demographics)
    df_counts_at_risk = create_table_from_paths(paths, demographics, "at_risk")
    df_counts_diabetes = create_table_from_paths(paths, demographics, "diabetes")
    df_counts_hypertension = create_table_from_paths(
        paths, demographics, "hypertension"
    )

    return df_counts_all, df_counts_at_risk, df_counts_diabetes, df_counts_hypertension


def get_path(*args):
    return pathlib.Path(*args).resolve()


def match_paths(pattern):
    return sorted(pathlib.Path().glob(pattern))


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--study_def_paths",
        dest="study_def_paths",
        required=True,
        type=match_paths,
        help="Glob pattern for matching input files",
    )

    parser.add_argument(
        "--demographics",
        dest="demographics",
        required=True,
        help="List of strings representing variables to include",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    paths = args.study_def_paths
    demographics = args.demographics.split(",")

    table_total, table_at_risk, table_diabetes, table_hypertension = create_tables(
        paths, demographics
    )

    tables = {
        "total": table_total,
        "at_risk": table_at_risk,
        "diabetes": table_diabetes,
        "hypertension": table_hypertension,
    }

    for table_name, table in tables.items():
        pathlib.Path(get_path(OUTPUT_DIR, "pub/descriptive_tables")).mkdir(
            parents=True, exist_ok=True
        )
        table.to_csv(
            get_path(OUTPUT_DIR, f"pub/descriptive_tables/table_1_{table_name}.csv")
        )


if __name__ == "__main__":
    main()
