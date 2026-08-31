import pandas as pd
import numpy as np


STAGE_SCORE_MAP = {
    "Discovery": 20,
    "Preclinical": 35,
    "Phase I": 55,
    "Phase II": 75,
    "Phase III": 90
}


def _min_max_score(series, higher_is_better=True):
    """
    Convert a numeric pandas Series into a 0-100 score.

    If higher_is_better=True:
        highest value -> 100
        lowest value -> 0

    If higher_is_better=False:
        lowest value -> 100
        highest value -> 0
    """

    series = pd.to_numeric(series, errors="coerce")

    min_value = series.min()
    max_value = series.max()

    if pd.isna(min_value) or pd.isna(max_value):
        return pd.Series([np.nan] * len(series), index=series.index)

    if min_value == max_value:
        return pd.Series([50.0] * len(series), index=series.index)

    score = (series - min_value) / (max_value - min_value) * 100

    if not higher_is_better:
        score = 100 - score

    return score


def calculate_asset_metrics(portfolio_df):
    """
    Takes the portfolio input dataframe and returns
    asset-level financial and strategic metrics.
    """

    df = portfolio_df.copy()

    required_columns = [
        "Asset",
        "Development Stage",
        "Therapeutic Area",
        "Capital to Next Milestone (€m)",
        "Time to Next Milestone (months)",
        "Probability of Success (%)",
        "Current Asset Value (€m)",
        "Post-Milestone Value (€m)",
        "Strategic Fit (1-10)"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    numeric_columns = [
        "Capital to Next Milestone (€m)",
        "Time to Next Milestone (months)",
        "Probability of Success (%)",
        "Current Asset Value (€m)",
        "Post-Milestone Value (€m)",
        "Strategic Fit (1-10)"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # CORE METRICS
    # --------------------------------------------------------

    df["Value Uplift (€m)"] = (
        df["Post-Milestone Value (€m)"]
        - df["Current Asset Value (€m)"]
    )

    df["Expected Value Creation (€m)"] = (
        df["Probability of Success (%)"] / 100
        * df["Value Uplift (€m)"]
    )

    df["Capital Efficiency (x)"] = (
        df["Expected Value Creation (€m)"]
        / df["Capital to Next Milestone (€m)"]
    )

    # --------------------------------------------------------
    # SCORING COMPONENTS
    # --------------------------------------------------------

    df["Expected Value Score"] = _min_max_score(
        df["Expected Value Creation (€m)"],
        higher_is_better=True
    )

    df["Capital Efficiency Score"] = _min_max_score(
        df["Capital Efficiency (x)"],
        higher_is_better=True
    )

    df["Probability Score"] = (
        df["Probability of Success (%)"]
        .clip(lower=0, upper=100)
    )

    df["Strategic Fit Score"] = (
        df["Strategic Fit (1-10)"]
        .clip(lower=0, upper=10)
        * 10
    )

    df["Time Score"] = _min_max_score(
        df["Time to Next Milestone (months)"],
        higher_is_better=False
    )

    df["Stage Score"] = (
        df["Development Stage"]
        .map(STAGE_SCORE_MAP)
        .fillna(30)
    )

    # --------------------------------------------------------
    # BALANCED PRIORITY SCORE
    # --------------------------------------------------------

    df["Priority Score"] = (
        0.30 * df["Expected Value Score"]
        + 0.25 * df["Capital Efficiency Score"]
        + 0.15 * df["Probability Score"]
        + 0.15 * df["Strategic Fit Score"]
        + 0.10 * df["Time Score"]
        + 0.05 * df["Stage Score"]
    )

    df["Priority Score"] = (
        df["Priority Score"]
        .round(1)
    )

    # --------------------------------------------------------
    # PRIORITY BAND
    # --------------------------------------------------------

    df["Priority"] = pd.cut(
        df["Priority Score"],
        bins=[
            -np.inf,
            45,
            65,
            80,
            np.inf
        ],
        labels=[
            "Low",
            "Moderate",
            "High",
            "Very High"
        ]
    )

    # --------------------------------------------------------
    # ROUNDING
    # --------------------------------------------------------

    df["Value Uplift (€m)"] = (
        df["Value Uplift (€m)"].round(1)
    )

    df["Expected Value Creation (€m)"] = (
        df["Expected Value Creation (€m)"].round(1)
    )

    df["Capital Efficiency (x)"] = (
        df["Capital Efficiency (x)"].round(2)
    )

    return df