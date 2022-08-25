import re
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "../output"
ANALYSIS_DIR = BASE_DIR / "../analysis"


BEST = 0
UPPER_RIGHT = 1
UPPER_LEFT = 2
LOWER_LEFT = 3
LOWER_RIGHT = 4
RIGHT = 5
CENTER_LEFT = 6
CENTER_RIGHT = 7
LOWER_CENTER = 8
UPPER_CENTER = 9
CENTER = 10

def round_column(column, base):
    return column.apply(lambda x: base * round(x / base))

def drop_and_round(column, base=5, threshold=5):
    column[column <= threshold] = 0
    return round_column(column, base)


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


def drop_irrelevant_practices(df):
    """Drops irrelevant practices from the given measure table.
    An irrelevant practice has zero events during the study period.
    Args:
        df: A measure table.
    Returns:
        A copy of the given measure table with irrelevant practices dropped.
    """
    is_relevant = df.groupby("practice").value.any()
    return df[df.practice.isin(is_relevant[is_relevant == True].index)]


def compute_deciles(measure_table, groupby_col, values_col, has_outer_percentiles=True):
    """Computes deciles.
    Args:
        measure_table: A measure table.
        groupby_col: The name of the column to group by.
        values_col: The name of the column for which deciles are computed.
        has_outer_percentiles: Whether to compute the nine largest and nine smallest
            percentiles as well as the deciles.
    Returns:
        A data frame with `groupby_col`, `values_col`, and `percentile` columns.
    """
    quantiles = np.arange(0.1, 1, 0.1)
    if has_outer_percentiles:
        quantiles = np.concatenate(
            [quantiles, np.arange(0.01, 0.1, 0.01), np.arange(0.91, 1, 0.01)]
        )

    percentiles = (
        measure_table.groupby(groupby_col)[values_col]
        .quantile(pd.Series(quantiles, name="percentile"))
        .reset_index()
    )
    percentiles["percentile"] = percentiles["percentile"].apply(lambda x: int(x * 100))

    return percentiles


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


def deciles_chart(
    df,
    filename,
    period_column=None,
    column=None,
    count_column=None,
    title="",
    ylabel="",
):
    """period_column must be dates / datetimes"""
    if count_column:
        df = compute_redact_deciles(df, period_column, count_column, column)

    else:
        df = compute_deciles(df, period_column, column, has_outer_percentiles=False)

    """period_column must be dates / datetimes"""
    sns.set_style("whitegrid", {"grid.color": ".9"})

    fig, ax = plt.subplots(1, 1)

    linestyles = {
        "decile": {
            "line": "b--",
            "linewidth": 1,
            "label": "Decile",
        },
        "median": {
            "line": "b-",
            "linewidth": 1.5,
            "label": "Median",
        },
        "percentile": {
            "line": "b:",
            "linewidth": 0.8,
            "label": "1st-9th, 91st-99th percentile",
        },
    }
    label_seen = []
    for percentile in range(1, 100):  # plot each decile line
        data = df[df["percentile"] == percentile]
        add_label = False

        if percentile == 50:
            style = linestyles["median"]
            add_label = True

        else:
            style = linestyles["decile"]
            if "decile" not in label_seen:
                label_seen.append("decile")
                add_label = True
        if add_label:
            label = style["label"]
        else:
            label = "_nolegend_"

        ax.plot(
            data[period_column],
            data[column],
            style["line"],
            linewidth=style["linewidth"],
            label=label,
        )
    ax.set_ylabel(ylabel, size=15, alpha=0.6)
    if title:
        ax.set_title(title, size=14, wrap=True)
    # set ymax across all subplots as largest value across dataset

    ax.set_ylim(
        [0, 100 if df[column].isnull().values.all() else df[column].max() * 1.05]
    )
    ax.tick_params(labelsize=12)
    ax.set_xlim(
        [df[period_column].min(), df[period_column].max()]
    )  # set x axis range as full date range

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%B %Y"))

    plt.xticks(sorted(df[period_column].unique()), rotation=90)

    ax.legend(
        bbox_to_anchor=(1.1, 0.8),  # arbitrary location in axes
        #  specified as (x0, y0, w, h)
        loc=CENTER_LEFT,  # which part of the bounding box should
        #  be placed at bbox_to_anchor
        ncol=1,  # number of columns in the legend
        fontsize=8,
        borderaxespad=0.0,
    )  # padding between the axes and legend
    #  specified in font-size units

    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()


def redact_small_numbers(df, n, numerator, denominator, rate_column, date_column):
    """
    Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from numerator and denominator until count of redcted values >=n.
    Rates corresponding to redacted values are also redacted.
    df: input df
    n: threshold for low number suppression
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

        df_subset.loc[
            (df_subset[numerator].isna()) | (df_subset[denominator].isna()), rate_column
        ] = np.nan
        df_list.append(df_subset)

    return pd.concat(df_list, axis=0)


def plot_measures(
    df,
    filename: str,
    title: str,
    column_to_plot: str,
    y_label: str,
    as_bar: bool = False,
    category: str = None,
):
    """Produce time series plot from measures table.  One line is plotted for each sub
    category within the category column. Saves output in 'output' dir as jpeg file.
    Args:
        df: A measure table
        title: Plot title
        column_to_plot: Column name for y-axis values
        y_label: Label to use for y-axis
        as_bar: Boolean indicating if bar chart should be plotted instead of line chart. Only valid if no categories.
        category: Name of column indicating different categories
    """
    plt.figure(figsize=(15, 8))
    if category:
        df[category] = df[category].fillna("Missing")
        for unique_category in sorted(df[category].unique()):

            # subset on category column and sort by date
            df_subset = df[df[category] == unique_category].sort_values("date")

            plt.plot(df_subset["date"], df_subset[column_to_plot])
    else:
        if bar:
            df.plot.bar("date", column_to_plot, legend=False)
        else:
            plt.plot(df["date"], df[column_to_plot])

    x_labels = sorted(df["date"].unique())

    plt.ylabel(y_label)
    plt.xlabel("Date")
    plt.xticks(x_labels, rotation="vertical")
    plt.title(title)
    plt.ylim(
        bottom=0,
        top=100
        if df[column_to_plot].isnull().values.all()
        else df[column_to_plot].max() * 1.05,
    )

    if category:
        plt.legend(
            sorted(df[category].unique()), bbox_to_anchor=(1.04, 1), loc="upper left"
        )

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / f"figures/{filename}.jpeg")
    plt.clf()


def group_low_values_series(series):
    
    suppressed_count = series[series<=5].sum()
    
    if suppressed_count == 0:
        pass

    else:
        series[series <=5]  = np.nan

        while suppressed_count <=5:
            suppressed_count += series.min()
            series[series.idxmin()] = np.nan 
            
            
   
        series = series[series.notnull()]
        
        suppressed_count_series= pd.Series(suppressed_count, index=["Other"])
       
        
        series = pd.concat([series, suppressed_count_series])
    
    
    return series

def plot_boxplot_numeric_value(x, title, filename):
    plt.boxplot(x, showfliers=False)
    plt.title(title)
    plt.ylabel("count")
    plt.xlabel("numeric_value")
    plt.savefig(OUTPUT_DIR / f"{filename}.jpeg")
    plt.clf()

def plot_violin_numeric_value(x, title, filename):
    """Plots a violin plot from an array of numeric values. Controls for disclosure by
    calculating percentiles and using this to generate the plots rather than the raw values. 
    This will be sufficient for large the majority of populations. Limits the range of plotted data
    to the top and bottom quantile using `cut=0`.

    """

    percentiles = np.arange(0.01, 0.99, 0.01)
    percentile_values = np.quantile(a=x, q=percentiles)
    figure_output = sns.violinplot(data=percentile_values, cut=0)
    plt.title(title)
    plt.ylabel("numeric value")
    plt.savefig(OUTPUT_DIR /f"{filename}.jpeg")
    plt.clf()


def group_low_values(df, count_column, code_column, threshold):
    """Suppresses low values and groups suppressed values into
    a new row "Other".
    Args:
        df: A measure table of counts by code.
        count_column: The name of the count column in the measure table.
        code_column: The name of the code column in the codelist table.
        threshold: Redaction threshold to use
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

    return df


def create_top_5_code_table(
    df, code_df, code_column, term_column, low_count_threshold, rounding_base, nrows=5
):
    """Creates a table of the top 5 codes recorded with the number of events and % makeup of each code.
    Args:
        df: A measure table.
        code_df: A codelist table.
        code_column: The name of the code column in the codelist table.
        term_column: The name of the term column in the codelist table.
        measure: The measure ID.
        low_count_threshold: Value to use as threshold for disclosure control.
        rounding_base: Base to round to.
        nrows: The number of rows to display.
    Returns:
        A table of the top `nrows` codes.
    """
   
    # cast both code columns to str
    df[code_column] = df[code_column].astype(str)
    code_df[code_column] = code_df[code_column].astype(str)

    # sum event counts over patients
    event_counts = df.sort_values(ascending=False, by="num")

    event_counts = group_low_values(
        event_counts, "num", code_column, low_count_threshold
    )

    # round

    event_counts["num"] = event_counts["num"].apply(
        lambda x: round_values(x, rounding_base)
    )

    # calculate % makeup of each code
    total_events = event_counts["num"].sum()
    event_counts["Proportion of codes (%)"] = round(
        (event_counts["num"] / total_events) * 100, 2
    )

    # Gets the human-friendly description of the code for the given row
    # e.g. "Systolic blood pressure".
    code_df[code_column] = code_df[code_column].astype(str)
    code_df = code_df.set_index(code_column).rename(
        columns={term_column: "Description"}
    )

    event_counts = event_counts.set_index(code_column).join(code_df).reset_index()

    # set description of "Other column" to something readable
    event_counts.loc[event_counts[code_column] == "Other", "Description"] = "-"

    # Rename the code column to something consistent
    event_counts.rename(columns={code_column: "Code", "num": "Events"}, inplace=True)

    # drop events column
    event_counts = event_counts.loc[
        :, ["Code", "Description", "Events","Proportion of codes (%)"]
    ]

    # return top n rows
    return event_counts.head(5)

def write_csv(df, path, **kwargs):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, **kwargs)


def round_values(x, base=5):
    rounded = x
    if isinstance(x, (int, float)):
        if np.isnan(x):
            rounded = np.nan
        else:
            rounded = int(base * round(x / base))
    return rounded

