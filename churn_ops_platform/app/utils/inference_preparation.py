import pandas as pd


def prepare_tree_features_for_inference(
    df,
    categorical_cols,
    numerical_cols,
    categorical_orders=None,
    reference_columns=None,
):
    """
    Prepare feature matrix for inference for tree-based models.

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
    reference_columns : list[str] or None, default=None
        Optional reference feature columns for alignment.

    Returns
    -------
    X : pd.DataFrame
        Model matrix aligned for inference.
    """
    if categorical_orders is None:
        categorical_orders = {}

    if hasattr(df, "to_pandas"):
        df = df.to_pandas()

    df = df.copy()

    for col in categorical_cols:
        if col in categorical_orders:
            df[col] = pd.Categorical(
                df[col],
                categories=categorical_orders[col],
                ordered=True,
            )

    X_cat = pd.get_dummies(
        df[categorical_cols],
        drop_first=False,
        dtype=int,
    )

    X_num = df[numerical_cols].copy()

    X = pd.concat([X_cat, X_num], axis=1)

    if reference_columns is not None:
        X = X.reindex(columns=reference_columns, fill_value=0)

    return X