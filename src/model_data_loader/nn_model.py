
import torch
from ..utils.data_preparation_models import prepare_linear_features, transform_with_scaler

def nn_data_loader(df, artifact):
    categorical_cols = artifact["categorical_cols"]
    numerical_cols = artifact["numerical_cols"]
    categorical_orders = artifact["categorical_orders"]
    target_col = artifact["target_col"]
    reference_columns = artifact["reference_columns"]

    scaler = artifact["scaler"]

    X, y = prepare_linear_features(
        df=df,
        categorical_cols=categorical_cols,
        numerical_cols=numerical_cols,
        categorical_orders=categorical_orders,
        target_col = target_col,
        reference_columns=reference_columns,
        add_intercept=False,
        drop_first=False
    )

    scaled_X = transform_with_scaler(X, scaler)

    return(scaled_X,y)