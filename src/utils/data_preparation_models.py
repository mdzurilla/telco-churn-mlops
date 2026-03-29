import pandas as pd


def prepare_tree_features(
    df,
    categorical_cols,
    numerical_cols,
    categorical_orders=None,
    target_col="Churn",
    reference_columns=None
):
    """
    Prepare feature matrix for tree-based models.

    Parameters
    ----------
    df : pd.DataFrame or polars.DataFrame
        Input dataset.
    categorical_cols : list[str]
        Categorical predictor columns to one-hot encode.
    numerical_cols : list[str]
        Numerical / ordinal predictor columns to keep as-is.
    categorical_orders : dict[str, list] or None, default=None
        Optional mapping of categorical column names to ordered category lists.
        If provided, categories are cast explicitly before one-hot encoding.
    target_col : str, default="Churn"
        Target column.
    reference_columns : list[str] or None, default=None
        Optional reference feature columns for alignment (useful for test data).

    Returns
    -------
    X : pd.DataFrame
        Model matrix.
    y : pd.Series
        Binary target vector.
    """

    if categorical_orders is None:
        categorical_orders = {}

    # convert Polars -> pandas if needed
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()

    df = df.copy()

    # target
    y = (
        df[target_col]
        .replace({"Yes": 1, "No": 0})
        .astype(int)
    )

    # apply ordered categorical dtype where specified
    for col in categorical_cols:
        if col in categorical_orders:
            df[col] = pd.Categorical(
                df[col],
                categories=categorical_orders[col],
                ordered=True
            )

    # one-hot encode categoricals
    X_cat = pd.get_dummies(
        df[categorical_cols],
        drop_first=False,
        dtype=int
    )

    # keep numeric / ordinal features as numeric
    X_num = df[numerical_cols].copy()

    # combine
    X = pd.concat([X_cat, X_num], axis=1)

    # align columns if reference provided
    if reference_columns is not None:
        X = X.reindex(columns=reference_columns, fill_value=0)

    return X, y

import statsmodels.api as sm


def prepare_linear_features(
    df,
    categorical_cols,
    numerical_cols,
    categorical_orders=None,
    target_col="Churn",
    reference_columns=None,
    drop_first=True,
    add_intercept=True
):
    """
    Prepare design matrix for statsmodels logistic regression.

    Parameters
    ----------
    df : pl.DataFrame or pd.DataFrame
        Input dataset.
    categorical_cols : list[str]
        List of categorical feature names.
    numerical_cols : list[str]
        List of numerical feature names.
    categorical_orders : dict[str, list[str]] or None, default=None
        Optional mapping specifying category order for selected variables.
        This allows control over the reference category when using
        one-hot encoding with drop_first=True.
    target_col : str or None, default="Churn"
        Name of target column. If None, only X is returned.
    reference_columns : list[str] or None, default=None
        Column structure from training design matrix used to align new data
        (e.g. validation/test folds), in case some categories are missing.
    drop_first : bool, default=True
        Whether to drop the first level in one-hot encoding.
    add_intercept : bool, default=True
        Whether to add an intercept column.

    Returns
    -------
    X : pd.DataFrame
        Design matrix with named columns.
    y : pd.Series or None
        Target variable if target_col is provided, otherwise None.
    """

    if categorical_orders is None:
        categorical_orders = {}

    # Convert Polars to pandas if needed
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()

    # Select only relevant columns
    selected_cols = categorical_cols + numerical_cols
    if target_col is not None:
        selected_cols = selected_cols + [target_col]

    df = df[selected_cols].copy()

    # Apply category ordering where specified
    for col, categories in categorical_orders.items():
        if col in df.columns:
            df[col] = pd.Categorical(df[col], categories=categories, ordered=True)

    # Separate target if available
    y = (
        pd.to_numeric(df[target_col].replace({"Yes": 1, "No": 0}), errors="raise")
        .astype(int)
        .copy()
        if target_col is not None else None
    )

    # One-hot encode categorical variables
    X_cat = pd.get_dummies(
        df[categorical_cols],
        drop_first=drop_first,
        dtype=float
    ) if categorical_cols else pd.DataFrame(index=df.index)

    # Keep numerical variables as they are
    X_num = df[numerical_cols].astype(float) if numerical_cols else pd.DataFrame(index=df.index)

    # Combine into one design matrix
    X = pd.concat([X_num, X_cat], axis=1)

    # Align columns to training reference if provided
    if reference_columns is not None:
        X = X.reindex(columns=reference_columns, fill_value=0.0)

    # Add intercept explicitly for statsmodels
    if add_intercept:
        X = sm.add_constant(X, has_constant="add")

    return X, y

from sklearn.preprocessing import StandardScaler

def fit_scaler(X):
    """
    Fit a standardization transformer on the feature matrix.

    This function estimates the mean and standard deviation of each feature
    using the provided dataset. The fitted scaler can then be reused to
    transform other datasets (e.g., validation or test sets) in a consistent
    manner.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix used to estimate scaling parameters. In practice,
        this should be the training dataset to avoid data leakage.

    Returns
    -------
    scaler : sklearn.preprocessing.StandardScaler
        Fitted scaler containing feature-wise mean and variance.
    """
    scaler = StandardScaler()
    scaler.fit(X)
    return scaler

def transform_with_scaler(X, scaler):
    """
    Apply a fitted standardization transformer to a feature matrix.

    This function transforms the input dataset using a previously fitted
    scaler, ensuring that all datasets are scaled using the same parameters.
    This is critical for maintaining consistency between training, validation,
    and test data.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix to be transformed.
    scaler : sklearn.preprocessing.StandardScaler
        Fitted scaler obtained from the training data.

    Returns
    -------
    X_scaled : pd.DataFrame
        Scaled feature matrix with the same structure (column names and index)
        as the input.
    """
    return pd.DataFrame(
        scaler.transform(X),
        columns=X.columns,
        index=X.index
    )