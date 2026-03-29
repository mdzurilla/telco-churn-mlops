from .logistic_regression import logistic_data_loader
from .tree_model import tree_model_data_loader
from .svm_model import svm_data_loader
from .nn_model import nn_data_loader


def prepare_data_from_artifact(df, artifact, model_type):
    """
    Prepare model-specific feature matrix and target vector from a preprocessed dataset
    using a stored model artifact.

    This function dispatches to the appropriate data preparation routine based on the
    specified model type. Each routine reconstructs the exact feature representation
    used during model training, including column alignment and (if applicable) scaling.

    Parameters
    ----------
    df : pd.DataFrame or pl.DataFrame
        Input dataset after applying the full feature engineering pipeline
        (i.e., output of sequential `apply_artifact` transformations).
    artifact : dict
        Model artifact containing all necessary metadata for data preparation,
        such as:
        - categorical and numerical column definitions
        - category ordering
        - reference column structure
        - fitted scaler (for SVM and neural network models)
    model_type : str
        Identifier of the model type. Supported values:
        - "logistic_regression"
        - "tree_model"
        - "svm"
        - "nn"

    Returns
    -------
    prepared_X : pd.DataFrame
        Model-ready feature matrix aligned with the training design.
    prepared_y : pd.Series
        Target vector corresponding to the input dataset.

    Raises
    ------
    ValueError
        If an unsupported model_type is provided.

    Notes
    -----
    - This function assumes that all upstream feature engineering steps have already
      been applied to `df` via the configuration-driven pipeline.
    - Ensures consistency between training and evaluation by reusing artifact metadata.
    """

    if model_type == "logistic_regression":
        prepared_X, prepared_y = logistic_data_loader(df, artifact)

    elif model_type == "tree_model":
        prepared_X, prepared_y = tree_model_data_loader(df, artifact)

    elif model_type == "svm":
        prepared_X, prepared_y = svm_data_loader(df, artifact)

    elif model_type == "nn":
        prepared_X, prepared_y = nn_data_loader(df, artifact)

    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    return prepared_X, prepared_y