# Modeling Notes

This document summarizes the modeling part of the project in a concise way.

## Scope

The modeling work focuses on a binary churn prediction problem using the Telco Customer Churn dataset, with emphasis on reproducibility, fair comparison, and decision-ready outputs.

## Main Focus Areas

1. Reproducible preprocessing:
- Feature engineering is driven by JSON transformation artifacts.
- The same transformation logic is reused across training and evaluation.

2. Model comparison:
- Trained and compared multiple algorithm families:
  - Logistic Regression
  - Decision Tree
  - Random Forest
  - Histogram Gradient Boosting
  - XGBoost / LightGBM
  - SVM (linear and RBF)
  - Neural Networks

3. Decision calibration:
- Evaluated models across threshold ranges (not only the default 0.5).
- Compared precision, recall, F1, ROC-AUC, and PR-AUC.
- Focused on ranking and prioritization quality for retention use cases.

4. Artifact-oriented workflow:
- Model outputs are saved as reusable artifacts in `models/`.
- Supporting transformation metadata is stored in `data/configs/`.

## Outcome

- The workflow identified tree-based boosting as the strongest practical direction for serving.
- Threshold choice was treated as a first-class decision variable, not an afterthought.
- The final selected model family aligns with what is operationalized in `churn_ops_platform`.

## Data Ownership Notice

I do not own the underlying dataset used in this project.
Dataset source: https://www.kaggle.com/datasets/blastchar/telco-customer-churn
