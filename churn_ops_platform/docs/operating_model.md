# Operating Model

## Purpose

This document explains how the churn platform is meant to be used operationally, what business decision it supports, what success looks like, and how retraining and promotion should be interpreted in a realistic organization.

It is written as an operating model for a portfolio project, not as a formal enterprise policy.

## Who Uses The System

The platform is intended to support multiple business functions across the company, especially:

- marketing
- customer care
- analytics

The model output is cross-functional because churn risk affects more than one workflow:

- marketing may use it for retention campaigns
- customer care may use it for outreach prioritization or extra service attention
- analytics may own the model logic, evaluation, and monitoring

In this project, the team owning the endpoint is the analytics or ML side of the system. The API is the operational interface. The simple UI exists mainly to demonstrate the workflow, while real integrations would typically happen through direct API calls from other internal systems.

## Access Model

This portfolio project does not implement authentication or authorization.

In a real organization, the likely model would be:

- endpoint ownership by the analytics or ML platform team
- system-to-system API usage by internal tools
- user access handled through company SSO or a shared identity provider

The important operating idea is that business teams consume the scoring capability, while the technical team owns the endpoint, the model lifecycle, and the quality controls around it.

## What Decision The Model Supports

The model supports one primary business decision:

- which customers appear most likely to churn and should be prioritized for intervention

The business motivation is straightforward:

- churned customers represent lost revenue
- identifying likely churners early creates a chance to retain them

The output is therefore most useful when it drives action such as:

- targeted retention offers
- additional care from customer-facing teams
- prioritization of limited intervention capacity

This is not only a prediction problem. It is a prioritization problem tied directly to revenue preservation.

## What Success Looks Like

The most meaningful success story is not just a better model metric. It is:

- a customer is identified as high risk
- the business intervenes with a meaningful action
- the customer stays
- the customer state changes in ways that reduce future churn risk

In a practical sense, the model is valuable when it helps the business intervene early enough to change the outcome.

That is why ranking quality matters so much in this project. The system should help surface the right customers early, not only maximize a threshold metric in isolation.

## Acceptable Failure And Business Tradeoffs

There are two important failure types.

### False Positive

The model identifies a customer as likely to churn, but the customer would have stayed anyway.

Business consequence:

- wasted retention resources
- unnecessary discounts, outreach, or care effort

### False Negative

The model identifies a customer as likely to stay, but the customer churns.

Business consequence:

- missed intervention opportunity
- full revenue loss from that customer relationship

## How To Think About The Tradeoff

This platform assumes that model evaluation should be tied to business cost, not just abstract statistics.

The real tension is:

- too many false positives wastes budget and team effort
- too many false negatives loses customers and revenue

That means the best operating threshold is not simply the one that looks best mathematically. It should reflect the balance between:

- retention capacity
- intervention cost
- expected customer value
- risk tolerance for missed churners

This is why the project emphasizes ranking quality and threshold selection rather than relying only on default classification settings.

## Actionability Matters

A useful churn model should support interventions on factors the business can actually influence.

Examples of features that are not realistically controllable:

- gender
- senior citizen status
- partner
- dependents
- tenure

Examples of factors that are more actionable from a business perspective:

- service bundle
- support experience
- offer structure
- pricing or contract incentives
- engagement and care strategy

That means the model is most valuable when it helps direct actions that can plausibly change a customer's future state, rather than only describing static profile characteristics.

## Why Ranking Metrics Matter

In this use case, ranking quality is especially important because the business usually cannot intervene on every customer.

That is why `auc` and `pr_auc` matter so much:

- they indicate how well the model surfaces likely churners near the top
- they support prioritization even before a fixed threshold is chosen

Threshold metrics still matter, but they are downstream of the more important question:

- does the model rank the right customers high enough for action?

## Retraining Philosophy

In the current platform, retraining is treated primarily as a check on whether the current modeling approach still holds.

It is not intended to mean:

- full model redevelopment
- full EDA refresh every time new data appears
- complete feature redesign on every cycle

Instead, the current retraining flow asks:

- if we keep the same modeling family and general setup, does performance remain acceptably stable on newer data?

This is a practical operating check rather than a full research cycle.

## Retraining Decision Rule

The current model should generally be considered stable if:

- `pr_auc` and `auc` remain broadly similar
- changes stay within roughly `2%` to `5%`

That tolerance exists because some movement is normal, especially with new yearly data.

If ranking metrics drift materially downward, two different interpretations are possible:

1. Retraining with the current approach restores acceptable performance.
2. Retraining with the current approach also performs poorly.

Those cases imply different actions.

### Case 1: Retraining Restores Performance

Interpretation:

- the underlying modeling approach is still valid
- the model likely needed refresh on newer data

Reasonable action:

- keep using the same overall modeling strategy
- review challenger results and promote only if the tradeoff is sensible

### Case 2: Retraining Also Performs Poorly

Interpretation:

- something larger may have changed in the data-generating process
- previous feature logic may no longer capture current churn behavior well

Reasonable action:

- revisit EDA
- reassess feature engineering
- review model family choice
- investigate whether the business process itself has changed

This is the point where retraining stops being enough and deeper modeling work becomes necessary.

## Retraining Cadence

Given the nature of the available data in this project, a yearly review cadence is the most reasonable default.

Why:

- the data appears to be more suitable for periodic refresh than very frequent retraining
- monthly retraining would likely create instability and overreaction
- a yearly cycle gives a more meaningful comparison window for this use case

That does not mean the model should be ignored between reviews. It means:

- monitor behavior continuously
- evaluate formally when fresh, meaningful data becomes available

## Promotion Ownership In A Real Organization

In a real company, promotion of a churn model would likely not be approved by engineering alone.

The most likely approving owner would be one of:

- analytics leadership
- the project or product owner
- a business owner in marketing or customer care

The exact owner depends on who is accountable for the retention workflow and the business outcome.

## How Promotion Should Be Presented

Promotion decisions should not be framed only as:

- metric tables
- charts
- model-versus-model technical comparison

For non-technical stakeholders, the story needs to be translated into business terms:

- what changed
- why the challenger is better or worse
- what tradeoff is being accepted
- what operational effect is expected
- what risk comes with promotion

That is especially important for marketing or customer care stakeholders, because they are often most affected by the decisions while being less interested in raw model diagnostics.

## Recommended Approval Story

A sensible promotion story in a real organization would answer:

- does the challenger rank churn risk at least as well as the current model?
- does the thresholded behavior improve the business tradeoff we care about?
- is the shift understandable enough to explain to downstream teams?
- do we have reason to believe the training data is representative?

If the answer to those questions is not clear, the correct choice is to hold the challenger and investigate further.

## What This Operating Model Demonstrates

This operating model shows that the project is not only about training a classifier. It is about connecting model behavior to:

- business intervention
- ownership boundaries
- acceptable failure
- retraining cadence
- promotion decision-making

That is the intended operating story of the platform.
