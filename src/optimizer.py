import itertools

import pandas as pd


# ============================================================
# STRATEGY CONFIGURATION
# ============================================================

STRATEGY_CONFIG = {
    "Conservative": {
        "weights": {
            "priority": 0.30,
            "expected_value": 0.15,
            "probability": 0.25,
            "stage": 0.20,
            "strategic_fit": 0.10
        },
        "fund_hurdle": 55,
        "conditional_hurdle": 40
    },

    "Balanced": {
        "weights": {
            "priority": 0.35,
            "expected_value": 0.25,
            "probability": 0.15,
            "stage": 0.10,
            "strategic_fit": 0.15
        },
        "fund_hurdle": 45,
        "conditional_hurdle": 35
    },

    "Growth": {
        "weights": {
            "priority": 0.25,
            "expected_value": 0.35,
            "probability": 0.10,
            "stage": 0.05,
            "strategic_fit": 0.25
        },
        "fund_hurdle": 40,
        "conditional_hurdle": 30
    }
}


STAGE_VALUES = {
    "Discovery": 20,
    "Preclinical": 35,
    "Phase I": 55,
    "Phase II": 75,
    "Phase III": 90
}


# ============================================================
# HELPERS
# ============================================================

def normalize_series(series):
    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(
            [0.0] * len(series),
            index=series.index
        )

    if minimum == maximum:
        return pd.Series(
            [50.0] * len(series),
            index=series.index
        )

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    )


# ============================================================
# STRATEGY SCORE
# ============================================================

def build_strategy_score(
    analysis_df,
    strategy
):
    df = analysis_df.copy()

    config = STRATEGY_CONFIG[
        strategy
    ]

    weights = config[
        "weights"
    ]

    df["Optimization EV Score"] = (
        normalize_series(
            df[
                "Expected Value Creation (€m)"
            ]
        )
    )

    df["Optimization PoS Score"] = (
        df[
            "Probability of Success (%)"
        ]
        .clip(
            lower=0,
            upper=100
        )
    )

    df["Optimization Stage Score"] = (
        df[
            "Development Stage"
        ]
        .map(
            STAGE_VALUES
        )
        .fillna(30)
    )

    df["Optimization Strategic Fit Score"] = (
        df[
            "Strategic Fit (1-10)"
        ]
        .clip(
            lower=0,
            upper=10
        )
        * 10
    )

    df["Optimization Score"] = (
        weights["priority"]
        * df["Priority Score"]

        + weights["expected_value"]
        * df["Optimization EV Score"]

        + weights["probability"]
        * df["Optimization PoS Score"]

        + weights["stage"]
        * df["Optimization Stage Score"]

        + weights["strategic_fit"]
        * df["Optimization Strategic Fit Score"]
    )

    df["Optimization Score"] = (
        df[
            "Optimization Score"
        ]
        .round(1)
    )

    return df


# ============================================================
# RATIONALE
# ============================================================

def build_decision_rationale(
    row,
    df,
    recommendation,
    fund_hurdle,
    conditional_hurdle
):
    positives = []

    median_ev = df[
        "Expected Value Creation (€m)"
    ].median()

    median_efficiency = df[
        "Capital Efficiency (x)"
    ].median()

    median_pos = df[
        "Probability of Success (%)"
    ].median()

    max_score = df[
        "Optimization Score"
    ].max()

    if row["Optimization Score"] == max_score:
        positives.append(
            "highest optimization score in the portfolio"
        )

    if (
        row["Expected Value Creation (€m)"]
        >= median_ev
    ):
        positives.append(
            "above-median expected value creation"
        )

    if (
        row["Capital Efficiency (x)"]
        >= median_efficiency
    ):
        positives.append(
            "strong relative capital efficiency"
        )

    if (
        row["Probability of Success (%)"]
        >= median_pos
    ):
        positives.append(
            "comparatively attractive probability of success"
        )

    if row["Strategic Fit (1-10)"] >= 8:
        positives.append(
            "strong strategic fit"
        )

    if (
        row["Time to Next Milestone (months)"]
        <= 15
    ):
        positives.append(
            "near-term milestone"
        )

    if recommendation == "Fund":

        if positives:
            detail = ", ".join(
                positives[:3]
            )

            return (
                f"Funded because the asset combines {detail}. "
                f"Its optimization score of "
                f"{row['Optimization Score']:.1f} exceeds the "
                f"primary investment hurdle of {fund_hurdle:.0f}."
            )

        return (
            f"Funded because its optimization score of "
            f"{row['Optimization Score']:.1f} exceeds the "
            f"primary investment hurdle of {fund_hurdle:.0f} "
            f"and it fits within the selected portfolio constraints."
        )

    if recommendation == "Conditional Fund":

        if row["Optimization Score"] >= fund_hurdle:

            return (
                f"The asset clears the primary investment hurdle "
                f"with a score of {row['Optimization Score']:.1f}, "
                f"but is not included in the recommended portfolio "
                f"because of the current capital constraint. "
                f"It becomes a natural candidate if additional "
                f"funding becomes available."
            )

        return (
            f"The asset shows some investment merit with an "
            f"optimization score of "
            f"{row['Optimization Score']:.1f}, above the secondary "
            f"hurdle of {conditional_hurdle:.0f}, but below the "
            f"primary funding hurdle of {fund_hurdle:.0f}. "
            f"It should be reconsidered if assumptions improve "
            f"or additional strategic importance emerges."
        )

    if recommendation == "Deprioritize":

        return (
            f"The optimization score of "
            f"{row['Optimization Score']:.1f} is below the "
            f"secondary investment hurdle of "
            f"{conditional_hurdle:.0f}. "
            f"The availability of unused capital alone does not "
            f"justify funding an asset with insufficient "
            f"risk-adjusted attractiveness."
        )

    if recommendation == "Outside Horizon":

        return (
            f"The next milestone is expected in "
            f"{row['Time to Next Milestone (months)']:.0f} months, "
            f"which falls outside the selected portfolio time horizon."
        )

    return ""


# ============================================================
# PORTFOLIO OPTIMIZATION
# ============================================================

def optimize_portfolio(
    analysis_df,
    available_capital,
    time_horizon,
    strategy
):
    df = build_strategy_score(
        analysis_df,
        strategy
    )

    config = STRATEGY_CONFIG[
        strategy
    ]

    fund_hurdle = config[
        "fund_hurdle"
    ]

    conditional_hurdle = config[
        "conditional_hurdle"
    ]

    # --------------------------------------------------------
    # INITIAL CLASSIFICATION
    # --------------------------------------------------------

    df["Recommendation"] = (
        "Deprioritize"
    )

    outside_horizon_mask = (
        df[
            "Time to Next Milestone (months)"
        ]
        > time_horizon
    )

    df.loc[
        outside_horizon_mask,
        "Recommendation"
    ] = "Outside Horizon"

    # Assets eligible for primary funding
    eligible_df = df[
        (
            df[
                "Time to Next Milestone (months)"
            ]
            <= time_horizon
        )
        &
        (
            df[
                "Optimization Score"
            ]
            >= fund_hurdle
        )
    ].copy()

    # --------------------------------------------------------
    # FIND BEST COMBINATION
    # --------------------------------------------------------

    best_combination = []

    best_objective = -1

    if not eligible_df.empty:

        eligible_indices = list(
            eligible_df.index
        )

        for number_assets in range(
            1,
            len(eligible_indices) + 1
        ):

            for combination in itertools.combinations(
                eligible_indices,
                number_assets
            ):

                selected = eligible_df.loc[
                    list(combination)
                ]

                total_capital = (
                    selected[
                        "Capital to Next Milestone (€m)"
                    ].sum()
                )

                if (
                    total_capital
                    > available_capital
                ):
                    continue

                # IMPORTANT:
                # No reward for spending more capital.
                # We maximize portfolio quality only.

                objective = (
                    selected[
                        "Optimization Score"
                    ].sum()
                )

                if objective > best_objective:

                    best_objective = objective

                    best_combination = list(
                        combination
                    )

    # --------------------------------------------------------
    # FINAL RECOMMENDATIONS
    # --------------------------------------------------------

    if best_combination:

        df.loc[
            best_combination,
            "Recommendation"
        ] = "Fund"

    # Assets that clear the primary hurdle
    # but were excluded because of capital constraints
    primary_not_funded_mask = (
        (
            df[
                "Optimization Score"
            ]
            >= fund_hurdle
        )
        &
        (
            df[
                "Time to Next Milestone (months)"
            ]
            <= time_horizon
        )
        &
        (
            df[
                "Recommendation"
            ]
            != "Fund"
        )
    )

    df.loc[
        primary_not_funded_mask,
        "Recommendation"
    ] = "Conditional Fund"

    # Assets between secondary and primary hurdle
    secondary_mask = (
        (
            df[
                "Optimization Score"
            ]
            >= conditional_hurdle
        )
        &
        (
            df[
                "Optimization Score"
            ]
            < fund_hurdle
        )
        &
        (
            df[
                "Time to Next Milestone (months)"
            ]
            <= time_horizon
        )
    )

    df.loc[
        secondary_mask,
        "Recommendation"
    ] = "Conditional Fund"

    # Re-apply outside horizon
    df.loc[
        outside_horizon_mask,
        "Recommendation"
    ] = "Outside Horizon"

    # --------------------------------------------------------
    # DECISION RATIONALE
    # --------------------------------------------------------

    df["Decision Rationale"] = (
        df.apply(
            lambda row: build_decision_rationale(
                row=row,
                df=df,
                recommendation=row[
                    "Recommendation"
                ],
                fund_hurdle=fund_hurdle,
                conditional_hurdle=conditional_hurdle
            ),
            axis=1
        )
    )

    # --------------------------------------------------------
    # FUNDED PORTFOLIO
    # --------------------------------------------------------

    recommended_df = df[
        df[
            "Recommendation"
        ]
        == "Fund"
    ].copy()

    capital_deployed = (
        recommended_df[
            "Capital to Next Milestone (€m)"
        ].sum()
        if not recommended_df.empty
        else 0.0
    )

    expected_value_creation = (
        recommended_df[
            "Expected Value Creation (€m)"
        ].sum()
        if not recommended_df.empty
        else 0.0
    )

    portfolio_score = (
        recommended_df[
            "Optimization Score"
        ].mean()
        if not recommended_df.empty
        else 0.0
    )

    strategic_reserve = (
        available_capital
        - capital_deployed
    )

    capital_utilization = (
        capital_deployed
        / available_capital
        * 100
        if available_capital > 0
        else 0.0
    )

    return {
        "recommended_df": recommended_df,

        "full_df": df,

        "capital_available": float(
            available_capital
        ),

        "capital_deployed": float(
            capital_deployed
        ),

        "strategic_reserve": float(
            strategic_reserve
        ),

        "capital_utilization": float(
            capital_utilization
        ),

        "expected_value_creation": float(
            expected_value_creation
        ),

        "portfolio_score": float(
            portfolio_score
        ),

        "fund_hurdle": float(
            fund_hurdle
        ),

        "conditional_hurdle": float(
            conditional_hurdle
        )
    }