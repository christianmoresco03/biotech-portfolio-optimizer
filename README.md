# BioPortfolio

### Biotech Pipeline Capital Allocation & Portfolio Optimization

BioPortfolio is an interactive decision-support prototype designed to help early-stage biotech companies structure capital-allocation decisions across multiple development programs.

The project addresses a common strategic challenge in biotech: a company may have several promising assets in its pipeline, but limited capital to advance all of them simultaneously.

BioPortfolio provides a transparent framework to evaluate individual assets, compare their risk-adjusted attractiveness, and identify a portfolio of programs that best fits the company's available capital, time horizon and strategic priorities.

---

## Project Origin

BioPortfolio originated as an entrepreneurial university project developed with a classmate to explore whether a simple decision-support tool could help early-stage biotech companies structure pipeline capital-allocation decisions.

The initial objective was to develop the concept into a potential startup. The project was therefore used as an early prototype while we explored external funding opportunities and startup competitions.

Although the venture was not ultimately pursued further, the prototype was subsequently developed into a more complete analytical project combining financial analysis, strategic decision-making and portfolio optimization.

The objective of BioPortfolio is not to predict which drugs will succeed, but to provide a transparent framework for structuring difficult resource-allocation decisions under uncertainty.

---

## Problem

Biotech companies often manage several drug-development programs at the same time.

Each program may differ in:

- development stage
- probability of success
- capital required to reach the next milestone
- time to the next milestone
- expected value uplift
- strategic relevance

When capital is limited, management must decide which programs should receive additional funding, which should remain conditional opportunities, and which should be deprioritized.

BioPortfolio structures this decision using a transparent, data-driven framework.

---

## How It Works

The application follows a five-step workflow.

### 1. Portfolio Input

Users can:

- explore a predefined sample biotech portfolio
- manually enter their own pipeline
- upload portfolio data through Excel or CSV

### 2. Asset Analysis

BioPortfolio evaluates each pipeline asset independently before considering portfolio-level constraints.

For each program, the model calculates key financial and strategic metrics such as:

- Value Uplift
- Expected Value Creation
- Capital Efficiency
- Priority Score

The Priority Score combines multiple factors, including probability of success, strategic fit, time to the next milestone and development stage, to provide a comparable measure of asset attractiveness.

This allows users to understand which programs appear stronger on a standalone basis before moving to the portfolio-allocation decision.

### 3. Portfolio Optimization

Once the individual assets have been assessed, BioPortfolio evaluates which programs should receive capital at portfolio level.

Management defines:

- available pipeline capital
- investment time horizon
- strategy profile: Conservative, Balanced or Growth

The selected strategy changes the relative importance assigned to different financial, risk and strategic factors.

The model then generates an Optimization Score for each asset and checks whether it clears the relevant investment hurdle.

Among the eligible assets, BioPortfolio identifies the strongest feasible portfolio while respecting the available capital and time constraints.

The optimizer can classify each asset as:

- Fund
- Conditional Fund
- Deprioritize
- Outside Horizon

The model does not attempt to use all available capital automatically. If the remaining assets are not sufficiently attractive, capital can remain unallocated as Strategic Reserve.

### 4. Portfolio Insights

The Portfolio Insights section translates the optimization output into a concise management view.

It highlights:

- portfolio structure
- capital deployed and strategic reserve
- capital concentration
- key risks and trade-offs
- conditional opportunities
- factors that could potentially change the recommendation

The objective is to help users interpret the recommended allocation rather than simply repeat the optimization results.

### 5. Methodology

The methodology section explains the scoring framework, investment hurdles, optimization logic and model limitations.

