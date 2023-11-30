import re
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from redaction_utils import compute_deciles

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
    ax.tick_params(labelsize=8)
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
        df[category] = df[category].fillna("Missing").astype(str)
        for unique_category in sorted(df[category].unique()):
            # subset on category column and sort by date
            df_subset = df[df[category] == unique_category].sort_values("date")

            plt.plot(df_subset["date"], df_subset[column_to_plot])
    else:
        if as_bar:
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
    plt.margins(x=0)
    plt.grid(True)

    plt.savefig(OUTPUT_DIR / f"{filename}.jpeg")
    plt.close()


def plot_boxplot_numeric_value(x, title, filename):
    plt.boxplot(x, showfliers=False)
    plt.title(title)
    plt.ylabel("count")
    plt.xlabel("numeric_value")
    plt.savefig(OUTPUT_DIR / f"{filename}.jpeg")
    plt.clf()


def plot_distribution_numeric_value(
    x, title, filename, start, end, bin_width, combined=False
):
    """Plots a histogram from an array of numeric values, showing relative frequencies,
    and returns a DataFrame with counts and relative frequencies for each bin.

    Args:
        x (array-like): Numeric values to be plotted.
        title (str): Title of the plot.
        filename (str): Output filename.
        start (float): Start value of the bins.
        end (float): End value of the bins.
        bin_width (float): Width of each bin.
        combined (bool): If True, multiple distributions can be combined in the same plot.

    """
    plt.figure(figsize=(10, 6))

    bins = np.arange(start, end + bin_width, bin_width)

    if combined:
        for label, data in x.items():
            data = data[(data >= start) & (data <= end)]
            counts, bin_edges = np.histogram(data, bins=bins)

            counts[counts <= 7] = 0
            counts = 5 * np.round(counts / 5)

            if counts.sum() > 0:
                relative_frequencies = np.round(counts / counts.sum(), 2)

            else:
                relative_frequencies = np.zeros(len(counts))

            plt.bar(
                bin_edges[:-1],
                relative_frequencies,
                width=bin_width,
                align="edge",
                alpha=0.5,
            )

            df = pd.DataFrame(
                {
                    "Bin_Edges": bin_edges[:-1],
                    "Counts": counts,
                    "Relative_Frequencies": relative_frequencies,
                }
            )

            df.to_csv(OUTPUT_DIR / f"{filename}_{label}_data.csv", index=False)
    else:
        x = x[(x >= start) & (x <= end)]
        counts, bin_edges = np.histogram(x, bins=bins)

        counts[counts <= 7] = 0
        counts = 5 * np.round(counts / 5)

        if counts.sum() > 0:
            relative_frequencies = np.round(counts / counts.sum(), 2)

        else:
            relative_frequencies = np.zeros(len(counts))

        # plot the relative frequencies as bar
        plt.bar(
            bin_edges[:-1],
            relative_frequencies,
            width=bin_width,
            align="edge",
            alpha=0.5,
        )

        df = pd.DataFrame(
            {
                "Bin_Edges": bin_edges[:-1],
                "Counts": counts,
                "Relative_Frequencies": relative_frequencies,
            }
        )

        df.to_csv(OUTPUT_DIR / f"{filename}_data.csv", index=False)

    plt.title(title)
    plt.xlabel("Numeric Value")
    plt.ylabel("Relative Frequency")
    plt.legend()

    if combined:
        plt.legend(x.keys())
    plt.grid(True)
    plt.margins(x=0)
    plt.xlim(left=start)
    plt.savefig(OUTPUT_DIR / f"{filename}.jpeg")
    plt.clf()


def write_csv(df, path, **kwargs):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, **kwargs)


def cockcroft_gault(
    sex, age, weight, weight_date, creatinine, creatinine_date, date_lim
):
    date_lim = pd.to_datetime(date_lim)

    if date_lim < weight_date and date_lim < creatinine_date:
        if sex == "F":
            multiplier = 0.85
        elif sex == "M":
            multiplier = 1
        else:
            return None

        if creatinine == 0.0:
            cg = None
        else:
            cg = ((140 - age) * (weight) * multiplier) / (72 * creatinine)
        return cg
    else:
        return None


def ckd_epi(sex, age, creatinine, creatinine_date, date_lim):
    date_lim = pd.to_datetime(date_lim)

    if date_lim < creatinine_date:
        if sex == "F":
            multiplier = (0.7, -0.241)
        elif sex == "M":
            multiplier = (0.9, -0.302)
        else:
            return None

        if creatinine == 0.0:
            return None

        else:
            return (
                142
                * (min([1, creatinine / multiplier[1]]) ** multiplier[1])
                * (max([1, creatinine / multiplier[1]]) ** -1.200)
                * (0.9938**age)
                * multiplier[0]
            )
    else:
        return None


def update_df(original_df, new_df, columns=[], on="patient_id"):
    updated = original_df.merge(
        new_df, on=on, how="outer", suffixes=("_old", "_new"), indicator=True
    )

    for c in columns:
        updated[c] = np.nan
        updated.loc[updated["_merge"] == "left_only", c] = updated[f"{c}_old"]
        updated.loc[updated["_merge"] != "left_only", c] = updated[f"{c}_new"]
        updated = updated.drop([f"{c}_old", f"{c}_new"], axis=1)
    updated = updated.drop(["_merge"], axis=1)
    return updated


def round_value(x, divisor=None):
    if divisor:
        return int(round(x / divisor) * divisor)
    return int(round(x))
