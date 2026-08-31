import os
import sys

import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    CURRENT_DIR
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(
        PROJECT_ROOT
    )


from src.scoring import calculate_asset_metrics
from src.optimizer import optimize_portfolio


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BioPortfolio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "BioPortfolio"
)

st.sidebar.caption(
    "Biotech Pipeline Capital Allocation"
)

st.sidebar.divider()

section = st.sidebar.radio(
    "Navigate",
    [
        "1. Portfolio Input",
        "2. Asset Analysis",
        "3. Portfolio Optimization",
        "4. Portfolio Insights",
        "5. Methodology"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Decision-support prototype for early-stage biotech companies."
)


# ============================================================
# PORTFOLIO SCHEMA
# ============================================================

PORTFOLIO_COLUMNS = [
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


# ============================================================
# SAMPLE DATA
# ============================================================

SAMPLE_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "sample_portfolio.csv"
)

sample_df = pd.read_csv(
    SAMPLE_DATA_PATH
)


# ============================================================
# SESSION STATE
# ============================================================

if "portfolio_mode" not in st.session_state:
    st.session_state.portfolio_mode = None

if "portfolio_df" not in st.session_state:
    st.session_state.portfolio_df = None

if "available_capital" not in st.session_state:
    st.session_state.available_capital = 25.0

if "time_horizon" not in st.session_state:
    st.session_state.time_horizon = 24

if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = "Balanced"

if "optimization_results" not in st.session_state:
    st.session_state.optimization_results = None


# ============================================================
# HELPERS
# ============================================================

def portfolio_is_available():

    return (
        st.session_state.portfolio_df
        is not None
        and
        not st.session_state.portfolio_df.empty
    )


def build_asset_rationale(row):

    reasons = []

    if (
        row[
            "Capital Efficiency (x)"
        ]
        >= 2
    ):
        reasons.append(
            "strong capital efficiency"
        )

    if (
        row[
            "Probability of Success (%)"
        ]
        >= 30
    ):
        reasons.append(
            "relatively high probability of success"
        )

    if (
        row[
            "Strategic Fit (1-10)"
        ]
        >= 8
    ):
        reasons.append(
            "strong strategic fit"
        )

    if (
        row[
            "Time to Next Milestone (months)"
        ]
        <= 15
    ):
        reasons.append(
            "near-term milestone"
        )

    if (
        row[
            "Expected Value Creation (€m)"
        ]
        >= 15
    ):
        reasons.append(
            "meaningful expected value creation"
        )

    if not reasons:

        reasons.append(
            "more limited risk-adjusted attractiveness "
            "relative to the rest of the portfolio"
        )

    return ", ".join(
        reasons
    )


# ============================================================
# 1. PORTFOLIO INPUT
# ============================================================

if section == "1. Portfolio Input":

    st.title(
        "Portfolio Input"
    )

    st.write(
        "Define the biotech pipeline that will be evaluated by the model."
    )

    st.info(
        "Choose the sample portfolio to explore BioPortfolio, "
        "or start a new analysis using your own pipeline data."
    )

    col1, col2 = st.columns(
        2
    )

    with col1:

        if st.button(
            "Explore Sample Portfolio",
            use_container_width=True
        ):

            st.session_state.portfolio_mode = (
                "Sample Portfolio"
            )

            st.session_state.portfolio_df = (
                sample_df.copy()
            )

            st.session_state.optimization_results = None

    with col2:

        if st.button(
            "Start New Analysis",
            use_container_width=True
        ):

            st.session_state.portfolio_mode = (
                "Custom Portfolio"
            )

            st.session_state.portfolio_df = (
                pd.DataFrame(
                    columns=PORTFOLIO_COLUMNS
                )
            )

            st.session_state.optimization_results = None

    if (
        st.session_state.portfolio_mode
        is None
    ):

        st.divider()

        st.subheader(
            "Choose how to begin"
        )

        st.write(
            "No portfolio is currently loaded. "
            "Select one of the options above to begin."
        )

    else:

        st.divider()

        st.subheader(
            st.session_state.portfolio_mode
        )

        if (
            st.session_state.portfolio_mode
            == "Sample Portfolio"
        ):

            st.caption(
                "This fictional portfolio is provided "
                "to demonstrate how BioPortfolio works."
            )

        else:

            st.caption(
                "Enter your pipeline manually "
                "or upload an Excel / CSV file."
            )

            uploaded_file = (
                st.file_uploader(
                    "Upload portfolio",
                    type=[
                        "xlsx",
                        "csv"
                    ]
                )
            )

            if uploaded_file is not None:

                try:

                    if (
                        uploaded_file
                        .name
                        .lower()
                        .endswith(".csv")
                    ):

                        uploaded_df = (
                            pd.read_csv(
                                uploaded_file
                            )
                        )

                    else:

                        uploaded_df = (
                            pd.read_excel(
                                uploaded_file
                            )
                        )

                    st.session_state.portfolio_df = (
                        uploaded_df
                    )

                    st.session_state.optimization_results = None

                    st.success(
                        "Portfolio uploaded successfully."
                    )

                except Exception as error:

                    st.error(
                        f"Unable to read the uploaded file: {error}"
                    )

        st.write(
            "You can edit the portfolio directly in the table below."
        )

        edited_df = st.data_editor(
            st.session_state.portfolio_df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="portfolio_editor"
        )

        st.session_state.portfolio_df = (
            edited_df
        )

        st.caption(
            "Changes made here automatically feed into "
            "the following sections."
        )


# ============================================================
# 2. ASSET ANALYSIS
# ============================================================

elif section == "2. Asset Analysis":

    st.title(
        "Asset Analysis"
    )

    st.write(
        "Evaluate the financial, strategic and risk profile "
        "of each pipeline asset."
    )

    if not portfolio_is_available():

        st.warning(
            "No portfolio has been loaded yet."
        )

    else:

        try:

            analysis_df = (
                calculate_asset_metrics(
                    st.session_state.portfolio_df
                )
            )

            analysis_df = (
                analysis_df
                .sort_values(
                    "Priority Score",
                    ascending=False
                )
                .reset_index(
                    drop=True
                )
            )

            analysis_df[
                "Rank"
            ] = (
                analysis_df.index
                + 1
            )

            analysis_df[
                "Rationale"
            ] = (
                analysis_df.apply(
                    build_asset_rationale,
                    axis=1
                )
            )

            col1, col2, col3, col4 = (
                st.columns(
                    4
                )
            )

            with col1:

                st.metric(
                    "Pipeline Assets",
                    len(
                        analysis_df
                    )
                )

            with col2:

                total_capital = (
                    analysis_df[
                        "Capital to Next Milestone (€m)"
                    ]
                    .sum()
                )

                st.metric(
                    "Capital Required",
                    f"€{total_capital:.1f}m"
                )

            with col3:

                total_expected_value = (
                    analysis_df[
                        "Expected Value Creation (€m)"
                    ]
                    .sum()
                )

                st.metric(
                    "Expected Value Creation",
                    f"€{total_expected_value:.1f}m"
                )

            with col4:

                average_score = (
                    analysis_df[
                        "Priority Score"
                    ]
                    .mean()
                )

                st.metric(
                    "Average Priority Score",
                    f"{average_score:.1f}"
                )

            st.divider()

            st.subheader(
                "Asset Ranking"
            )

            ranking_columns = [
                "Rank",
                "Asset",
                "Development Stage",
                "Capital to Next Milestone (€m)",
                "Probability of Success (%)",
                "Expected Value Creation (€m)",
                "Capital Efficiency (x)",
                "Priority Score",
                "Priority"
            ]

            st.dataframe(
                analysis_df[
                    ranking_columns
                ],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Priority Score":
                        st.column_config.ProgressColumn(
                            "Priority Score",
                            min_value=0,
                            max_value=100,
                            format="%.1f"
                        )
                }
            )

            st.divider()

            st.subheader(
                "Expected Value Creation vs Capital Required"
            )

            chart_df = analysis_df[
                [
                    "Asset",
                    "Development Stage",
                    "Therapeutic Area",
                    "Capital to Next Milestone (€m)",
                    "Expected Value Creation (€m)",
                    "Probability of Success (%)",
                    "Priority Score"
                ]
            ].copy()

            points = (
                alt.Chart(
                    chart_df
                )
                .mark_circle(
                    size=220
                )
                .encode(
                    x=alt.X(
                        "Capital to Next Milestone (€m):Q",
                        title="Capital to Next Milestone (€m)"
                    ),
                    y=alt.Y(
                        "Expected Value Creation (€m):Q",
                        title="Expected Value Creation (€m)"
                    ),
                    tooltip=[
                        "Asset",
                        "Development Stage",
                        "Therapeutic Area",
                        "Capital to Next Milestone (€m)",
                        "Expected Value Creation (€m)",
                        "Probability of Success (%)",
                        "Priority Score"
                    ]
                )
            )

            labels = (
                alt.Chart(
                    chart_df
                )
                .mark_text(
                    align="left",
                    baseline="middle",
                    dx=12,
                    fontSize=13
                )
                .encode(
                    x="Capital to Next Milestone (€m):Q",
                    y="Expected Value Creation (€m):Q",
                    text="Asset:N"
                )
            )

            chart = (
                points
                + labels
            ).properties(
                height=450
            ).interactive()

            st.altair_chart(
                chart,
                use_container_width=True
            )

            st.caption(
                "Assets positioned higher and further left combine "
                "greater expected value creation with lower capital requirements."
            )

            st.divider()

            st.subheader(
                "Asset Rationale"
            )

            for _, row in (
                analysis_df.iterrows()
            ):

                with st.expander(
                    f"#{int(row['Rank'])} — "
                    f"{row['Asset']} | "
                    f"{row['Priority']} priority"
                ):

                    metric1, metric2, metric3, metric4 = (
                        st.columns(
                            4
                        )
                    )

                    with metric1:

                        st.metric(
                            "Priority Score",
                            f"{row['Priority Score']:.1f}"
                        )

                    with metric2:

                        st.metric(
                            "Expected Value Creation",
                            f"€{row['Expected Value Creation (€m)']:.1f}m"
                        )

                    with metric3:

                        st.metric(
                            "Capital Efficiency",
                            f"{row['Capital Efficiency (x)']:.2f}x"
                        )

                    with metric4:

                        st.metric(
                            "Probability of Success",
                            f"{row['Probability of Success (%)']:.0f}%"
                        )

                    st.write(
                        f"**Model rationale:** "
                        f"{row['Rationale']}."
                    )

                    st.write(
                        f"**Development stage:** "
                        f"{row['Development Stage']}  \n"
                        f"**Therapeutic area:** "
                        f"{row['Therapeutic Area']}  \n"
                        f"**Capital to next milestone:** "
                        f"€{row['Capital to Next Milestone (€m)']:.1f}m  \n"
                        f"**Time to next milestone:** "
                        f"{row['Time to Next Milestone (months)']:.0f} months  \n"
                        f"**Strategic fit:** "
                        f"{row['Strategic Fit (1-10)']:.0f}/10"
                    )

            st.divider()

            st.subheader(
                "How to Read the Analysis"
            )

            col1, col2, col3 = (
                st.columns(
                    3
                )
            )

            with col1:

                st.markdown(
                    """
                    **Expected Value Creation**

                    Risk-adjusted value associated with
                    successfully reaching the next milestone.
                    """
                )

            with col2:

                st.markdown(
                    """
                    **Capital Efficiency**

                    Expected value creation relative to
                    capital required.
                    """
                )

            with col3:

                st.markdown(
                    """
                    **Priority Score**

                    Combines value, efficiency, risk,
                    strategic fit, timing and maturity.
                    """
                )

        except Exception as error:

            st.error(
                "The asset analysis could not be completed."
            )

            st.code(
                str(error)
            )


# ============================================================
# 3. PORTFOLIO OPTIMIZATION
# ============================================================

elif section == "3. Portfolio Optimization":

    st.title(
        "Portfolio Optimization"
    )

    st.write(
        "Define company-level constraints and identify which "
        "pipeline assets merit capital allocation."
    )

    if not portfolio_is_available():

        st.warning(
            "Load a portfolio before running the optimization."
        )

    else:

        try:

            analysis_df = (
                calculate_asset_metrics(
                    st.session_state.portfolio_df
                )
            )

            st.subheader(
                "Company Constraints"
            )

            col1, col2, col3 = (
                st.columns(
                    3
                )
            )

            with col1:

                st.session_state.available_capital = (
                    st.number_input(
                        "Available Pipeline Capital (€m)",
                        min_value=0.0,
                        value=float(
                            st.session_state.available_capital
                        ),
                        step=1.0
                    )
                )

            with col2:

                st.session_state.time_horizon = (
                    st.number_input(
                        "Time Horizon (months)",
                        min_value=1,
                        value=int(
                            st.session_state.time_horizon
                        ),
                        step=1
                    )
                )

            with col3:

                strategy_options = [
                    "Conservative",
                    "Balanced",
                    "Growth"
                ]

                strategy_index = (
                    strategy_options.index(
                        st.session_state.risk_profile
                    )
                )

                st.session_state.risk_profile = (
                    st.selectbox(
                        "Portfolio Strategy",
                        strategy_options,
                        index=strategy_index
                    )
                )

            st.caption(
                "The model does not attempt to spend all available capital. "
                "Assets must first clear a strategy-specific investment hurdle."
            )

            st.divider()

            results = (
                optimize_portfolio(
                    analysis_df=analysis_df,
                    available_capital=(
                        st.session_state.available_capital
                    ),
                    time_horizon=(
                        st.session_state.time_horizon
                    ),
                    strategy=(
                        st.session_state.risk_profile
                    )
                )
            )

            st.session_state.optimization_results = (
                results
            )

            st.subheader(
                "Recommended Portfolio"
            )

            metric1, metric2, metric3, metric4 = (
                st.columns(
                    4
                )
            )

            with metric1:

                st.metric(
                    "Capital Available",
                    f"€{results['capital_available']:.1f}m"
                )

            with metric2:

                st.metric(
                    "Recommended Deployment",
                    f"€{results['capital_deployed']:.1f}m"
                )

            with metric3:

                st.metric(
                    "Strategic Reserve",
                    f"€{results['strategic_reserve']:.1f}m"
                )

            with metric4:

                st.metric(
                    "Expected Value Creation",
                    f"€{results['expected_value_creation']:.1f}m"
                )

            st.write(
                f"**Capital utilization:** "
                f"{results['capital_utilization']:.0f}%"
            )

            if (
                results[
                    "strategic_reserve"
                ]
                > 0
            ):

                st.info(
                    f"The model recommends retaining "
                    f"€{results['strategic_reserve']:.1f}m "
                    f"rather than allocating capital to assets "
                    f"that do not clear the relevant investment hurdle."
                )

            st.divider()

            full_results_df = (
                results[
                    "full_df"
                ]
                .sort_values(
                    "Optimization Score",
                    ascending=False
                )
            )

            st.subheader(
                "Decision Summary"
            )

            recommendation_columns = [
                "Asset",
                "Development Stage",
                "Capital to Next Milestone (€m)",
                "Expected Value Creation (€m)",
                "Probability of Success (%)",
                "Priority Score",
                "Optimization Score",
                "Recommendation"
            ]

            st.dataframe(
                full_results_df[
                    recommendation_columns
                ],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Optimization Score":
                        st.column_config.ProgressColumn(
                            "Optimization Score",
                            min_value=0,
                            max_value=100,
                            format="%.1f"
                        )
                }
            )

            st.caption(
                f"Primary investment hurdle: "
                f"{results['fund_hurdle']:.0f} | "
                f"Conditional hurdle: "
                f"{results['conditional_hurdle']:.0f}"
            )

            st.divider()

            st.subheader(
                "Decision Rationale"
            )

            for _, row in (
                full_results_df.iterrows()
            ):

                with st.expander(
                    f"{row['Asset']} — "
                    f"{row['Recommendation']}"
                ):

                    col1, col2, col3 = (
                        st.columns(
                            3
                        )
                    )

                    with col1:

                        st.metric(
                            "Capital Required",
                            f"€{row['Capital to Next Milestone (€m)']:.1f}m"
                        )

                    with col2:

                        st.metric(
                            "Expected Value Creation",
                            f"€{row['Expected Value Creation (€m)']:.1f}m"
                        )

                    with col3:

                        st.metric(
                            "Optimization Score",
                            f"{row['Optimization Score']:.1f}"
                        )

                    st.write(
                        f"**Why {row['Recommendation']}?** "
                        f"{row['Decision Rationale']}"
                    )

            st.divider()

            st.subheader(
                "Recommended Capital Allocation"
            )

            funded_df = (
                full_results_df[
                    full_results_df[
                        "Recommendation"
                    ]
                    == "Fund"
                ]
            )

            if funded_df.empty:

                st.warning(
                    "No asset currently clears both the investment "
                    "and portfolio constraints."
                )

            else:

                chart_df = funded_df[
                    [
                        "Asset",
                        "Capital to Next Milestone (€m)"
                    ]
                ]

                capital_chart = (
                    alt.Chart(
                        chart_df
                    )
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "Asset:N",
                            title="Funded Asset"
                        ),
                        y=alt.Y(
                            "Capital to Next Milestone (€m):Q",
                            title="Capital Allocated (€m)"
                        ),
                        tooltip=[
                            "Asset",
                            "Capital to Next Milestone (€m)"
                        ]
                    )
                    .properties(
                        height=350
                    )
                )

                st.altair_chart(
                    capital_chart,
                    use_container_width=True
                )

            st.caption(
                "Selected assets are fully funded through their next milestone. "
                "Unused capital is retained rather than automatically deployed."
            )

        except Exception as error:

            st.error(
                "The portfolio optimization could not be completed."
            )

            st.code(
                str(error)
            )


# ============================================================
# 4. PORTFOLIO INSIGHTS
# ============================================================

elif section == "4. Portfolio Insights":

    st.title(
        "Portfolio Insights"
    )

    st.write(
        "Translate the optimization output into a concise "
        "portfolio-level management view."
    )

    if not portfolio_is_available():

        st.warning(
            "No portfolio has been loaded."
        )

    elif (
        st.session_state.optimization_results
        is None
    ):

        st.warning(
            "Run Portfolio Optimization first."
        )

    else:

        try:

            results = (
                st.session_state.optimization_results
            )

            full_df = (
                results[
                    "full_df"
                ]
                .copy()
            )

            funded_df = (
                full_df[
                    full_df[
                        "Recommendation"
                    ]
                    == "Fund"
                ]
                .copy()
            )

            conditional_df = (
                full_df[
                    full_df[
                        "Recommendation"
                    ]
                    == "Conditional Fund"
                ]
                .copy()
            )

            deprioritized_df = (
                full_df[
                    full_df[
                        "Recommendation"
                    ]
                    == "Deprioritize"
                ]
                .copy()
            )

            outside_df = (
                full_df[
                    full_df[
                        "Recommendation"
                    ]
                    == "Outside Horizon"
                ]
                .copy()
            )

            # ------------------------------------------------
            # EXECUTIVE SUMMARY
            # ------------------------------------------------

            st.subheader(
                "Executive Summary"
            )

            total_assets = len(
                full_df
            )

            funded_assets = len(
                funded_df
            )

            st.write(
                f"BioPortfolio recommends funding "
                f"**{funded_assets} of {total_assets} pipeline assets**, "
                f"deploying **€{results['capital_deployed']:.1f}m** "
                f"of the **€{results['capital_available']:.1f}m** "
                f"available capital."
            )

            if (
                results[
                    "strategic_reserve"
                ]
                > 0
            ):

                st.write(
                    f"The remaining "
                    f"**€{results['strategic_reserve']:.1f}m** "
                    f"is retained as strategic reserve rather than "
                    f"allocated to assets below the relevant investment hurdle."
                )

            st.write(
                f"The funded portfolio generates "
                f"**€{results['expected_value_creation']:.1f}m** "
                f"of modeled expected value creation."
            )

            st.divider()

            # ------------------------------------------------
            # PORTFOLIO STRUCTURE
            # ------------------------------------------------

            st.subheader(
                "Portfolio Structure"
            )

            col1, col2, col3, col4 = (
                st.columns(
                    4
                )
            )

            with col1:

                st.metric(
                    "Fund",
                    len(
                        funded_df
                    )
                )

            with col2:

                st.metric(
                    "Conditional Fund",
                    len(
                        conditional_df
                    )
                )

            with col3:

                st.metric(
                    "Deprioritize",
                    len(
                        deprioritized_df
                    )
                )

            with col4:

                st.metric(
                    "Outside Horizon",
                    len(
                        outside_df
                    )
                )

            structure_data = (
                full_df[
                    [
                        "Asset",
                        "Recommendation",
                        "Optimization Score",
                        "Capital to Next Milestone (€m)"
                    ]
                ]
                .sort_values(
                    "Optimization Score",
                    ascending=False
                )
            )

            st.dataframe(
                structure_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # ------------------------------------------------
            # KEY RISKS & TRADE-OFFS
            # ------------------------------------------------

            st.subheader(
                "Key Risks & Trade-offs"
            )

            insights = []

            if not funded_df.empty:

                largest_funded_asset = (
                    funded_df
                    .sort_values(
                        "Capital to Next Milestone (€m)",
                        ascending=False
                    )
                    .iloc[0]
                )

                if (
                    results[
                        "capital_deployed"
                    ]
                    > 0
                ):

                    largest_share = (
                        largest_funded_asset[
                            "Capital to Next Milestone (€m)"
                        ]
                        /
                        results[
                            "capital_deployed"
                        ]
                        * 100
                    )

                    if largest_share >= 60:

                        insights.append(
                            f"Capital concentration is relatively high: "
                            f"{largest_funded_asset['Asset']} represents "
                            f"approximately {largest_share:.0f}% "
                            f"of recommended deployment."
                        )

            if not conditional_df.empty:

                strongest_conditional = (
                    conditional_df
                    .sort_values(
                        "Optimization Score",
                        ascending=False
                    )
                    .iloc[0]
                )

                insights.append(
                    f"{strongest_conditional['Asset']} is the strongest "
                    f"secondary opportunity, with an optimization score of "
                    f"{strongest_conditional['Optimization Score']:.1f}."
                )

            if not deprioritized_df.empty:

                weakest_asset = (
                    deprioritized_df
                    .sort_values(
                        "Optimization Score",
                        ascending=True
                    )
                    .iloc[0]
                )

                insights.append(
                    f"{weakest_asset['Asset']} remains the weakest "
                    f"risk-adjusted allocation candidate and does not justify "
                    f"funding solely because capital is available."
                )

            if (
                results[
                    "capital_utilization"
                ]
                < 80
            ):

                insights.append(
                    f"Only {results['capital_utilization']:.0f}% of available "
                    f"capital is deployed, indicating that portfolio quality "
                    f"takes priority over full budget utilization."
                )

            if not funded_df.empty:

                funded_stages = (
                    funded_df[
                        "Development Stage"
                    ]
                    .value_counts()
                )

                if len(
                    funded_stages
                ) == 1:

                    insights.append(
                        "The funded portfolio is concentrated in a single "
                        "development stage, which may increase stage-specific risk."
                    )

            if not insights:

                insights.append(
                    "The recommended portfolio does not show any major "
                    "concentration or allocation concerns under the current assumptions."
                )

            for insight in insights:

                st.write(
                    f"- {insight}"
                )

            st.divider()

            # ------------------------------------------------
            # WHAT WOULD CHANGE THE DECISION?
            # ------------------------------------------------

            st.subheader(
                "What Would Change the Decision?"
            )

            if not conditional_df.empty:

                for _, row in (
                    conditional_df
                    .sort_values(
                        "Optimization Score",
                        ascending=False
                    )
                    .iterrows()
                ):

                    gap_to_hurdle = (
                        results[
                            "fund_hurdle"
                        ]
                        -
                        row[
                            "Optimization Score"
                        ]
                    )

                    if gap_to_hurdle > 0:

                        st.write(
                            f"- **{row['Asset']}** is "
                            f"{gap_to_hurdle:.1f} score points below "
                            f"the primary funding hurdle. "
                            f"Improved probability of success, expected value, "
                            f"strategic fit or capital efficiency could move it "
                            f"into the Fund category."
                        )

                    else:

                        st.write(
                            f"- **{row['Asset']}** clears the primary hurdle "
                            f"but is currently excluded by portfolio constraints. "
                            f"Additional available capital could move it into "
                            f"the funded portfolio."
                        )

            if not deprioritized_df.empty:

                for _, row in (
                    deprioritized_df
                    .sort_values(
                        "Optimization Score",
                        ascending=False
                    )
                    .iterrows()
                ):

                    gap_to_conditional = (
                        results[
                            "conditional_hurdle"
                        ]
                        -
                        row[
                            "Optimization Score"
                        ]
                    )

                    st.write(
                        f"- **{row['Asset']}** would require a material "
                        f"improvement in its underlying assumptions to become "
                        f"investable. Its current optimization score is "
                        f"{row['Optimization Score']:.1f}, "
                        f"{max(gap_to_conditional, 0):.1f} points below "
                        f"the conditional hurdle."
                    )

            if not outside_df.empty:

                for _, row in (
                    outside_df.iterrows()
                ):

                    st.write(
                        f"- **{row['Asset']}** could re-enter the decision set "
                        f"if the portfolio time horizon extends beyond "
                        f"{row['Time to Next Milestone (months)']:.0f} months."
                    )

            st.caption(
                "These insights are diagnostic rather than predictive. "
                "They show which assumptions or constraints are currently "
                "driving the portfolio recommendation."
            )

        except Exception as error:

            st.error(
                "Portfolio Insights could not be completed."
            )

            st.code(
                str(error)
            )


# ============================================================
# 5. METHODOLOGY
# ============================================================

elif section == "5. Methodology":

    st.title(
        "Methodology"
    )

    st.write(
        "BioPortfolio converts management-provided assumptions "
        "into a structured and transparent capital-allocation framework."
    )

    # --------------------------------------------------------
    # CORE PRINCIPLE
    # --------------------------------------------------------

    st.subheader(
        "Core Principle"
    )

    st.write(
        """
        BioPortfolio does not assess the scientific validity of a drug
        candidate and does not attempt to predict clinical outcomes.

        Instead, it takes management-provided assumptions and uses them
        to compare pipeline assets under capital, time and strategic constraints.
        """
    )

    st.info(
        "The model is designed to support portfolio decisions, "
        "not to replace scientific, clinical or management judgment."
    )

    st.divider()

    # --------------------------------------------------------
    # CORE METRICS
    # --------------------------------------------------------

    st.subheader(
        "Core Metrics"
    )

    st.markdown(
        """
        **1. Value Uplift**

        Measures the increase in estimated asset value if the next
        development milestone is successfully reached.
        """
    )

    st.latex(
        r"""
        ValueUplift
        =
        PostMilestoneValue
        -
        CurrentValue
        """
    )

    st.markdown(
        """
        **2. Expected Value Creation**

        Adjusts the potential value uplift for the probability of
        successfully reaching the next milestone.
        """
    )

    st.latex(
        r"""
        ExpectedValueCreation
        =
        PoS
        \times
        ValueUplift
        """
    )

    st.markdown(
        """
        **3. Capital Efficiency**

        Measures how much expected value creation is generated relative
        to the capital required to reach the next milestone.
        """
    )

    st.latex(
        r"""
        CapitalEfficiency
        =
        \frac{
        ExpectedValueCreation
        }{
        CapitalRequired
        }
        """
    )

    st.divider()

    # --------------------------------------------------------
    # SCORING FRAMEWORK
    # --------------------------------------------------------

    st.subheader(
        "Scoring Framework"
    )

    st.write(
        """
        Each pipeline asset is assessed across several dimensions and
        converted into comparable scores on a common scale.
        """
    )

    st.markdown(
        """
        The framework considers:

        - **Expected value creation**
        - **Capital efficiency**
        - **Probability of success**
        - **Strategic fit**
        - **Time to next milestone**
        - **Development stage**
        """
    )

    st.write(
        """
        These dimensions are combined into a Priority Score that provides
        a structured view of each asset's relative attractiveness within
        the portfolio.
        """
    )

    st.caption(
        "The score is a decision-support metric rather than an industry-standard "
        "valuation measure."
    )

    st.divider()

    # --------------------------------------------------------
    # STRATEGY PROFILES
    # --------------------------------------------------------

    st.subheader(
        "Strategy Profiles"
    )

    st.write(
        """
        BioPortfolio allows management to change the decision framework
        according to the company's strategic priorities.
        """
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.markdown(
            """
            **Conservative**

            Places greater emphasis on:

            - probability of success
            - development maturity
            - downside protection
            """
        )

    with col2:

        st.markdown(
            """
            **Balanced**

            Seeks a balance between:

            - expected value creation
            - capital efficiency
            - risk
            - strategic fit
            """
        )

    with col3:

        st.markdown(
            """
            **Growth**

            Places greater emphasis on:

            - upside potential
            - expected value creation
            - strategic importance
            """
        )

    st.write(
        """
        The selected profile changes the relative importance of the
        underlying scoring dimensions and therefore can change asset rankings
        and portfolio recommendations.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # INVESTMENT HURDLES
    # --------------------------------------------------------

    st.subheader(
        "Investment Hurdles"
    )

    st.write(
        """
        Asset selection occurs in two stages.
        """
    )

    st.markdown(
        """
        **Step 1 — Investment eligibility**

        Each asset is evaluated against strategy-specific investment hurdles.
        Assets with insufficient risk-adjusted attractiveness are not funded
        simply because capital remains available.

        **Step 2 — Portfolio selection**

        Among the eligible assets, the optimizer identifies the strongest
        feasible combination subject to the company's available capital
        and selected time horizon.
        """
    )

    st.caption(
        "Investment hurdles are model parameters and should not be interpreted "
        "as clinical, regulatory or industry-standard thresholds."
    )

    st.divider()

    # --------------------------------------------------------
    # OPTIMIZATION LOGIC
    # --------------------------------------------------------

    st.subheader(
        "Optimization Logic"
    )

    st.write(
        """
        The optimizer evaluates combinations of eligible assets and selects
        the portfolio that best satisfies the selected strategic objective
        while respecting the company's constraints.
        """
    )

    st.markdown(
        """
        The model follows three core principles:

        - Assets are assumed to be **fully funded to their next milestone**
        - Total allocated capital cannot exceed the available budget
        - **Unused capital is allowed**
        """
    )

    st.success(
        "BioPortfolio maximizes portfolio attractiveness, not budget utilization."
    )

    st.write(
        """
        This means that the model can recommend retaining capital as
        strategic reserve when remaining assets do not justify additional
        investment.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # RECOMMENDATION CATEGORIES
    # --------------------------------------------------------

    st.subheader(
        "Recommendation Categories"
    )

    st.markdown(
        """
        **Fund**

        The asset demonstrates sufficient investment attractiveness and
        is included in the recommended portfolio.

        **Conditional Fund**

        The asset shows meaningful potential but is not currently included
        in the core funded portfolio. It may become investable if capital
        availability, strategic priorities or underlying assumptions improve.

        **Deprioritize**

        The asset does not currently demonstrate sufficient risk-adjusted
        attractiveness relative to alternative uses of capital.

        **Outside Horizon**

        The asset's next milestone falls beyond the selected portfolio
        time horizon and is therefore excluded from the current decision set.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # MODEL LIMITATIONS
    # --------------------------------------------------------

    st.subheader(
        "Model Limitations"
    )

    st.write(
        """
        BioPortfolio is a decision-support prototype and its outputs depend
        directly on the quality of the assumptions supplied by the user.
        """
    )

    st.markdown(
        """
        Current limitations include:

        - Probability of success is provided by the user and is not independently estimated
        - Current and post-milestone asset values are management assumptions
        - Clinical and scientific data are not independently validated
        - Funding decisions are modeled as binary through the next milestone
        - Interdependencies and correlations between pipeline assets are not modeled
        - Regulatory, competitive and financing events outside the selected inputs are not explicitly simulated
        """
    )

    st.warning(
        "The model should be interpreted as a structured decision-support tool, "
        "not as an investment recommendation or a substitute for specialist judgment."
    )