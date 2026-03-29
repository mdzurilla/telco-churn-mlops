import polars as pl


def apply_artifact(df: pl.DataFrame, artifact: dict) -> pl.DataFrame:
    """
    Apply a single transformation artifact to a Polars DataFrame.

    Supported actions in `new_features`:
    - relevel
    - aggregate_sum
    - aggregate_multiply
    - binning

    Supported actions in `missing_values_handelling_features`:
    - impute
    """

    result = df.clone()

    # 1) Missing value handling
    for feature in artifact.get("missing_values_handelling_features", []):
        action = feature.get("action")
        col_name = feature.get("name")

        if col_name not in result.columns:
            continue

        if action == "impute":
            strategy = feature.get("imputation_strategy")

            if strategy == "constant":
                fill_value = feature.get("fill_value")
                result = result.with_columns(
                    pl.col(col_name).fill_null(fill_value).alias(col_name)
                )

            elif strategy == "mean":
                result = result.with_columns(
                    pl.col(col_name)
                    .fill_null(pl.col(col_name).mean())
                    .alias(col_name)
                )

            elif strategy == "median":
                result = result.with_columns(
                    pl.col(col_name)
                    .fill_null(pl.col(col_name).median())
                    .alias(col_name)
                )

            else:
                raise ValueError(
                    f"Unsupported imputation strategy for column '{col_name}': {strategy}"
                )

        else:
            raise ValueError(
                f"Unsupported missing value handling action for column '{col_name}': {action}"
            )

    # 2) New feature creation
    for feature in artifact.get("new_features", []):
        action = feature.get("action")
        new_name = feature.get("name")

        if action == "relevel":
            source_name = feature["source"]["name"]
            target_type = feature.get("data_type")
            mapping = feature["mapping"]

            expr = pl.col(source_name).cast(pl.Utf8).replace(mapping)

            if target_type == "numeric":
                expr = expr.cast(pl.Int64)
            elif target_type == "string":
                expr = expr.cast(pl.Utf8)

            result = result.with_columns(expr.alias(new_name))

        elif action == "aggregate_sum":
            fields = feature["fields"]
            exprs = [pl.col(col).cast(pl.Float64) for col in fields]

            total_expr = exprs[0]
            for expr in exprs[1:]:
                total_expr = total_expr + expr

            result = result.with_columns(total_expr.alias(new_name))

        elif action == "aggregate_multiply":
            fields = feature["fields"]
            exprs = [pl.col(col).cast(pl.Float64) for col in fields]

            product_expr = exprs[0]
            for expr in exprs[1:]:
                product_expr = product_expr * expr

            result = result.with_columns(product_expr.alias(new_name))

        elif action == "binning":
            source_name = feature["source"]["name"]
            breaks = feature["breaks"]

            expr = (
                pl.when(pl.col(source_name) <= breaks[0]).then(pl.lit(0))
                .when(pl.col(source_name) <= breaks[1]).then(pl.lit(1))
                .when(pl.col(source_name) <= breaks[2]).then(pl.lit(2))
                .when(pl.col(source_name) <= breaks[3]).then(pl.lit(3))
                .otherwise(pl.lit(4))
                .cast(pl.Int64)
            )

            result = result.with_columns(expr.alias(new_name))

        else:
            raise ValueError(f"Unsupported action: {action}")

    # 3) Drop features
    dropped = artifact.get("dropped_features", [])
    if dropped:
        existing_to_drop = [col for col in dropped if col in result.columns]
        if existing_to_drop:
            result = result.drop(existing_to_drop)

    return result

def apply_artifacts(df: pl.DataFrame, artifacts: list[dict]) -> pl.DataFrame:
    result = df
    for artifact in artifacts:
        result = apply_artifact(result, artifact)
    return result