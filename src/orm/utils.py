from typing import Tuple
from sqlalchemy import Column, ForeignKey


def get_foreign_key(column: Column, model) -> ForeignKey:
    return next((
        fk for fk in column.foreign_keys if fk.column.table == model.__table__
    ), None)


def get_association_id_column(
        association_table, model
) -> Tuple[Column, Column]:
    association_id_column = next(
            (
                column for column in association_table.columns
                if get_foreign_key(column, model)
            ), None
        )
    model_id_column = get_foreign_key(
        association_id_column, model
    ).column if association_id_column is not None else None

    if model_id_column is None or association_id_column is None:
        raise ValueError(
            f"""
            No ID column found in association table '{association_table}'
            with table '{model}'
            """
        )
    return model_id_column, association_id_column
