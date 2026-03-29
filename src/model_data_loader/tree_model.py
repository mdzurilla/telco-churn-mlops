from ..utils.data_preparation_models import prepare_tree_features

def tree_model_data_loader(df, artifact):
    categorical_cols = artifact["categorical_cols"]
    numerical_cols = artifact["numerical_cols"]
    categorical_orders = artifact["categorical_orders"]
    target_col = artifact["target_col"]
    reference_columns = artifact["reference_columns"]

    X, y = prepare_tree_features(
        df=df,
        categorical_cols=categorical_cols,
        numerical_cols=numerical_cols,
        categorical_orders=categorical_orders,
        target_col = target_col,
        reference_columns=reference_columns
    )

    return(X,y)