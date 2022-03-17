import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("output")

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


if not (OUTPUT_DIR / "figures").exists():
    Path.mkdir(OUTPUT_DIR / "figures")

demographics = ["age_band", "sex", "imd", "region"]

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

    plt.savefig(f"output/figures/{filename}.jpeg")
    plt.clf()

for i in ["cr_cl", "creatinine"]:

    df = pd.read_csv(
            OUTPUT_DIR / f"measure_{i}_rate.csv", parse_dates=["date"]
        )
    df = drop_irrelevant_practices(df)

    df["rate"] = df[f"value"] * 100

    df = df.drop(["value"], axis=1)

    df_deciles = compute_redact_deciles(df, "date", i, "rate")


    deciles_chart(
        df,
        filename=f"output/figures/plot_{i}.jpeg",
        period_column="date",
        column="rate",
        count_column=i,
        ylabel="Percentage"
    )

    # demographic plots
    for d in demographics:
        print(d)
        df = pd.read_csv(
            OUTPUT_DIR / f"measure_{i}_{d}_rate.csv", parse_dates=["date"]
        )

        if d == "sex":
            df = df[df["sex"].isin(["M", "F"])]

        elif d == "imd":
            df = df[df["imd"] != 0]

        elif d == "age_band":
            df = df[df["age_band"] != "missing"]
        
        elif d == "region":
            df = df[df["region"].notnull()]  

        df["rate"] = df[f"value"] * 100

        df = redact_small_numbers(
            df, 10, i, "population", "rate", "date"
        )

        plot_measures(
            df=df,
            filename=f"plot_{i}_{d}",
            title=f"{i} by {d}",
            column_to_plot="rate",
            y_label="Proportion",
            as_bar=False,
            category=d,
        )



