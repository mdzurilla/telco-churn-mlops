# Model Governance

## Goal

This document describes how to think about retraining, drift, challenger review, and promotion decisions in the current platform.

The intent is not to define a strict regulated-model policy. The intent is to establish a sensible operating guide for a portfolio-scale churn platform.

## What Gets Compared

During retraining, the platform compares:

- current serving model
- newly trained challenger model

Both are evaluated on the same held-out evaluation split from the uploaded training dataset.

The retraining response includes:

- selected threshold for the challenger
- challenger metrics
- serving metrics on the same evaluation set

## Current Metrics

The evaluation includes:

- accuracy
- precision
- recall
- f1
- auc
- pr_auc
- tp
- tn
- fp
- fn

## Why `pr_auc` Matters

This churn problem is a binary classification problem where ranking likely churners well is important.

`pr_auc` is especially useful when:

- the positive class is less frequent
- the business cares about precision-recall tradeoffs
- the team wants to understand how much value the model creates in the likely-actionable region

In this project, `pr_auc` should be treated as a primary model-quality metric, not just a secondary metric.

## Why Threshold Metrics Also Matter

`auc` and `pr_auc` measure ranking quality, but promotion decisions often depend on thresholded decisions:

- how many churners are caught
- how many false positives are created
- what tradeoff the business is willing to accept

That is why the retraining flow also searches over thresholds and selects one based on model behavior.

## Current Threshold Rule

The challenger threshold is chosen from a threshold sweep using the best:

- `f1`
- then `pr_auc`
- then `recall`
- then `precision`

This is a practical portfolio default, not a hard production policy.

## When Promotion Makes Sense

A challenger is a good promotion candidate when most of the following are true:

- `pr_auc` is equal or better than the current serving model
- `auc` is equal or better than the current serving model
- `f1` improves at the selected threshold
- recall improves without an unacceptable jump in false positives
- the threshold choice is understandable and not overly aggressive
- no obvious data-quality issue exists in the uploaded retraining dataset

## When Not To Promote

A challenger should usually stay in `challenger` when any of the following happens:

- `pr_auc` drops materially
- `auc` drops materially
- recall improves only because the threshold became too aggressive
- false positives rise sharply with little business justification
- the uploaded training dataset is too small or unrepresentative
- the challenger outperforms only on one metric that is not operationally important

## Practical Promotion Heuristic

For this project, a reasonable rule of thumb is:

- promote when threshold metrics improve and ranking quality is at least stable
- hold when ranking quality gets clearly worse even if recall improves

This is intentionally qualitative. The purpose is to show sound reasoning rather than pretend there is a universal numeric cutoff.

## Drift Guidance

This platform does not implement formal drift detection yet. For now, drift should be interpreted operationally.

### Drift Is Probably Still Acceptable When

- prediction distribution remains broadly stable
- average score does not move dramatically
- positive prediction rate changes only gradually
- challenger and serving performance stay close on new uploaded data

### Drift Is Potentially Concerning When

- score distributions shift noticeably
- positive prediction rates move sharply
- monitoring trends change quickly without business explanation
- challenger evaluation suggests the serving model is degrading on recent data

## Suggested Portfolio-Scale Drift Rule

Treat drift as worth investigating when one or more of these happen:

- positive prediction rate changes by roughly 5 to 10 percentage points
- average probability changes materially across a recent period
- uploaded retraining data shows consistent deterioration in `pr_auc` or `recall`

These are not strict production thresholds. They are sensible triggers for review in a portfolio setting.

## Recommended Operating Flow

1. Upload a recent labeled dataset to retrain a challenger.
2. Review challenger vs serving metrics.
3. Decide whether the challenger is better in a way that matches the business objective.
4. Promote only if the challenger improves the right tradeoff.
5. Keep the previous serving artifact in `archive`.
6. Use historical scoring if later audit questions require exact replay.

## Why Historical Scoring Matters

Audit questions are usually about a specific prediction made in the past.

To answer those questions well, the platform logs:

- API version
- model name
- artifact ID

and keeps archived artifacts available for replay.

That is what allows the team to say:

"This exact archived artifact produced that score."
