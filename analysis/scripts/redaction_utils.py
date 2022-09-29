import pandas as pd
import numpy as np

def round_column(column, base):
    return column.apply(lambda x: base * round(x / base) if pd.notnull(x) else x)

def round_values(x, base=5):
    rounded = x
    if isinstance(x, (int, float)):
        if np.isnan(x):
            rounded = np.nan
        else:
            rounded = int(base * round(x / base))
    return rounded

def drop_and_round(column, base=5, threshold=7):
    column[column <= threshold] = 0
    return round_column(column, base)

def compute_redact_deciles(df, period_column, count_column, column):
    n_practices = df.groupby(by=["date"])[["practice"]].nunique()

    count_df = compute_deciles(
        measure_table=df,
        groupby_col=period_column,
        values_col=count_column,
        has_outer_percentiles=False,
    )
    quintile_10 = count_df[count_df["percentile"] == 10][["date", count_column]]
    df = (
        compute_deciles(df, period_column, column, False)
        .merge(n_practices, on="date")
        .merge(quintile_10, on="date")
    )

    # if quintile 10 is 0, make sure at least 5 practices have 0. If >0, make sure more than 5 practices are in this bottom decile
    df["drop"] = (((df["practice"] * 0.1) * df[count_column]) <= 5) & (
        df[count_column] != 0
    ) | ((df[count_column] == 0) & (df["practice"] <= 5))

    df.loc[df["drop"] == True, ["rate"]] = np.nan

    return df

def redact_small_numbers(df, n, rounding_base, numerator, denominator, rate_column, date_column):
    """
    Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from numerator and denominator until count of redacted values >=n.
    Round counts to rounding_base.
    Rates corresponding to redacted values are also redacted.
    df: input df
    n: threshold for low number suppression
    rounding_base: rounding base to use
    numerator: numerator column to be redacted
    denominator: denominator column to be redacted
    """

    def suppress_column(column):
        suppressed_count = column[column <= n].sum()

        # if 0 dont need to suppress anything
        if suppressed_count == 0:
            pass

        else:
            column[column <= n] = np.nan

            while suppressed_count <= n:
                suppressed_count += column.min()

                column[column.idxmin()] = np.nan
        return column

    df_list = []

    dates = df[date_column].unique()

    for d in dates:
        df_subset = df.loc[df[date_column] == d, :]

        for column in [numerator, denominator]:
            df_subset[column] = suppress_column(df_subset[column])
            df_subset[column] = round_column(df_subset[column], base=rounding_base)

        df_subset.loc[
            (df_subset[numerator].isna()) | (df_subset[denominator].isna()), rate_column
        ] = np.nan
        df_list.append(df_subset)

    return pd.concat(df_list, axis=0)

def group_low_values_series(series):

    suppressed_count = series[series <= 7].sum()

    if suppressed_count == 0:
        series = round_column(series, 5)

    else:
        series[series <= 7] = np.nan

        while suppressed_count <= 7:
            suppressed_count += series.min()
            series[series.idxmin()] = np.nan

        series = series[series.notnull()]

        suppressed_count_series = pd.Series(suppressed_count, index=["Other"])
        suppressed_count_series = round_column(suppressed_count_series, 5)

        series = pd.concat([series, suppressed_count_series])

    return series

def group_low_values(df, count_column, code_column, threshold, rounding_base):
    """Suppresses low values and groups suppressed values into
    a new row "Other". Rounds to rounding base.
    Args:
        df: A measure table of counts by code.
        count_column: The name of the count column in the measure table.
        code_column: The name of the code column in the codelist table.
        threshold: Redaction threshold to use
        rounding_base: Rounding base to use
    Returns:
        A table with redacted counts
    """

    # get sum of any values <= threshold
    suppressed_count = df.loc[df[count_column] <= threshold, count_column].sum()
    suppressed_df = df.loc[df[count_column] > threshold, count_column]

    # if suppressed values >0 ensure total suppressed count > threshold.
    # Also suppress if all values 0
    if (suppressed_count > 0) | (
        (suppressed_count == 0) & (len(suppressed_df) != len(df))
    ):

        # redact counts <= threshold
        df.loc[df[count_column] <= threshold, count_column] = np.nan

        # If all values 0, suppress them
        if suppressed_count == 0:
            df.loc[df[count_column] == 0, :] = np.nan

        else:
            # if suppressed count <= threshold redact further values
            while suppressed_count <= threshold:
                suppressed_count += df[count_column].min()
                df.loc[df[count_column].idxmin(), :] = np.nan

        # drop all rows where count column is null
        df = df.loc[df[count_column].notnull(), :]

        # add suppressed count as "Other" row (if > threshold)
        if suppressed_count > threshold:
            suppressed_count = {code_column: "Other", count_column: suppressed_count}
            df = pd.concat([df, pd.DataFrame([suppressed_count])], ignore_index=True)
        df[count_column] = round_column(df[count_column], rounding_base)

    return df

def redact_table_1(df):
    redacted_table = df.groupby(level=[0]).apply(group_low_values_series)
    return redacted_table
    

