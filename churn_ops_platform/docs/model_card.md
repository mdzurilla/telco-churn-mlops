# Model Card

## Model Identity

- Model name: `churn_hist_gradient_boosting`
- Model family: `HistGradientBoostingClassifier`
- API version: `v1`
- Current serving artifact ID: `artifact_legacy_v1`
- Current serving threshold: `0.31`

This document describes the currently operationalized churn model in the portfolio platform.

## Purpose

The model is used to:

- identify customers who are likely to churn
- rank customers by churn risk
- support prioritization of retention actions

The model is therefore more than a binary classifier. It is primarily a ranking tool that helps the business focus attention on customers who appear most at risk.

## Intended Use

The intended use is operational churn risk prioritization across business functions such as:

- marketing
- customer care
- analytics

Typical uses include:

- selecting customers for retention campaigns
- prioritizing proactive outreach
- identifying customers who may need additional service attention
- supporting retention-focused review workflows in downstream systems

In the current platform, the API is the main operational interface. The included UI is mainly for demonstration.

## Out-Of-Scope Use

This model is not intended for:

- fully automated customer decisions without human review
- use as a causal explanation engine
- interpreting risk scores as proof of why a customer will churn
- use outside the telco churn problem this project was built for
- use without review when the input data or business environment has materially changed

## Dataset And Ownership

- Dataset: Telco Customer Churn Dataset
- Source: https://www.kaggle.com/datasets/blastchar/telco-customer-churn
- Data ownership note: I do not own the underlying dataset used in this project

## Target Variable

- Target: `Churn`

This is a binary target representing whether the customer churned.

## Modeling Context

The full modeling workflow explored multiple model families before selecting the current serving direction:

- Logistic Regression
- Decision Tree
- Random Forest
- Histogram Gradient Boosting
- XGBoost / LightGBM
- SVM
- Neural Networks

The final serving choice was Histogram Gradient Boosting because it was a strong practical fit for ranking quality and operational scoring.

## Input Features

The current serving artifact uses artifact-driven preprocessing and then scores on the following core feature groups.

Categorical feature groups:

- `SeniorCitizenRelevel`
- `Partner`
- `Dependents`
- `Contract`
- `PaperlessBilling`
- `PaymentMethod_bin_3`

Numerical or count-based feature groups:

- `tenure`
- `MonthlyCharges`
- `AdditionalInternetServicesCount`
- `StreamingServicesCount`

These features are transformed and aligned through the stored preprocessing artifacts before inference.

## Actionable Vs Non-Actionable Factors

Not all predictive features are equally useful for intervention.

Examples of factors that are not realistically controllable:

- gender
- senior citizen status
- partner
- dependents
- tenure

Examples of factors that are more actionable:

- service configuration
- support experience
- offer design
- pricing or contract incentives
- retention care strategy

This matters because a useful churn model should help guide interventions on variables the business can actually influence.

## Evaluation Focus

This project treats ranking quality as especially important.

Primary evaluation priorities:

- `pr_auc`
- `auc`

Threshold-based metrics are also tracked:

- accuracy
- precision
- recall
- f1
- tp
- tn
- fp
- fn

The reason `pr_auc` and `auc` matter so much is that the business usually cannot intervene on every customer. The model needs to rank the most at-risk customers high enough to support prioritization.

## Threshold Policy

The current serving artifact uses threshold `0.31`.

This reflects the broader modeling approach in the project:

- threshold choice is treated as an operating decision
- the default `0.5` cutoff is not assumed to be appropriate
- threshold behavior must be interpreted against business tradeoffs, not just statistics

In retraining, challenger thresholds are selected through threshold sweeps rather than being fixed in advance.

## Interpretability Note

The current serving pipeline does not include a dedicated explanation model.

That means this platform can currently:

- score
- rank
- compare model behavior

But it does not yet provide a formal explanation layer for individual predictions.

This is an important limitation. Interpretation must be handled carefully, especially when working with variables that are correlated with churn but may not be meaningful levers for intervention.

One important example is price-related behavior:

- if analysis suggests that higher price is associated with lower churn, that does not automatically mean raising prices is a sensible retention strategy

Without close interpretation and business context, a model can appear statistically reasonable while becoming operationally misguided. That is why any future explanation layer would need careful monitoring and business review.

## Known Limitations

- only one serving model family is currently operationalized
- the platform is local-first and portfolio-scoped
- no dedicated explanation model is included in the serving path
- no formal fairness analysis is implemented yet
- no formal drift detector is implemented yet
- the model should not be treated as causal
- periodic retraining is a check on model stability, not a full replacement for renewed EDA and modeling when business conditions change

## Monitoring Expectations

The model should be monitored through:

- prediction volume
- prediction distribution
- average score behavior
- status breakdown
- comparison of serving and challenger performance on fresh labeled data

Operationally concerning signals include:

- noticeable drop in `pr_auc` or `auc`
- major shifts in score distribution
- unexplained changes in positive prediction rate
- retraining that no longer restores acceptable ranking quality

## Retraining Expectations

The current retraining process is meant to check whether the existing modeling approach still holds on newer data.

A reasonable interpretation for this project is:

- if `pr_auc` and `auc` remain roughly within `2%` to `5%`, the current approach is likely still acceptable
- if ranking quality materially declines and retraining with the same approach does not recover it, deeper EDA and model redesign are needed

Given the nature of the available data, yearly review is a more sensible default than aggressive monthly retraining.

## Ethical And Operational Cautions

- churn scores should support human decision-making, not replace it blindly
- interventions should focus on customer-beneficial and business-reasonable actions
- teams should avoid using model outputs as if they were direct explanations
- teams should pay extra attention to whether recommended actions target variables that can actually be influenced

## Summary

This model is best understood as a churn risk ranking model embedded in a broader operational workflow.

Its value comes from:

- surfacing likely churners early
- supporting retention prioritization
- fitting into a reproducible artifact-based serving process

Its limitations come from:

- lack of a dedicated explanation layer
- dependence on stable business behavior over time
- the need to interpret model outputs with business judgment rather than raw statistics alone
