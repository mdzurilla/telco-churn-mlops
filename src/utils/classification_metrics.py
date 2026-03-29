import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score


def compute_classification_metrics(y_true, y_pred, y_prob=None):
    """
    Compute binary classification metrics.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    tp = ((y_true == 1) & (y_pred == 1)).sum()
    tn = ((y_true == 0) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    fn = ((y_true == 1) & (y_pred == 0)).sum()

    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0.0
    )

    auc = None
    pr_auc = None
    if y_prob is not None:
        auc = roc_auc_score(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "auc": auc,
        "pr_auc": pr_auc,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn
    }


def evaluate_thresholds(
    y_true,
    y_prob,
    thresholds=None
):
    """
    Evaluate threshold-dependent classification metrics.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    if thresholds is None:
        thresholds = np.linspace(0.01, 0.99, 99)

    pr_auc = average_precision_score(y_true, y_prob)
    auc = roc_auc_score(y_true, y_prob)

    results = []

    for threshold in thresholds:
        y_pred = (y_prob >= threshold).astype(int)

        metrics = compute_classification_metrics(
            y_true=y_true,
            y_pred=y_pred,
            y_prob=None
        )

        results.append({
            "threshold": threshold,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "tp": metrics["tp"],
            "tn": metrics["tn"],
            "fp": metrics["fp"],
            "fn": metrics["fn"],
            "auc": auc,
            "pr_auc": pr_auc
        })

    return pd.DataFrame(results)