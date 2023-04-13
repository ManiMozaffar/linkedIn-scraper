from sqlalchemy import func
from sqlalchemy import (
    select,
    and_,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipProperty
from .utils import get_association_id_column
from sqlalchemy.sql.selectable import Select
from typing import (Union, Sequence, Tuple)


class BaseQuery:
    needs_scalar: bool = True
    _instance = None
    _prefetch_related_joins = []
    _joint: list = list()
    _query: Select = None
    condition_map = {
        'exact': lambda column, value: column == value,
        'contains': lambda column, value: column.contains(value),
        'in': lambda column, value: column.in_(value),
        'gt': lambda column, value: column > value,
        'gte': lambda column, value: column >= value,
        'lt': lambda column, value: column < value,
        'lte': lambda column, value: column <= value,
        'startswith': lambda column, value: column.startswith(value),
        'endswith': lambda column, value: column.endswith(value),
        'range': lambda column, value: column.between(value[0], value[1]),
        'date': lambda column, value: func.date(column) == value,
        'year': lambda column, value: func.extract('year', column) == value,
        'month': lambda column, value: func.extract('month', column) == value,
        'day': lambda column, value: func.extract('day', column) == value,
        'iexact': lambda column, value: column.ilike(value),
        'icontains': lambda column, value: column.ilike(f"%{value}%"),
        'istartswith': lambda column, value: column.ilike(f"{value}%"),
        'iendswith': lambda column, value: column.ilike(f"%{value}"),
    }

    def __init__(self, cls):
        self.cls = cls

    def __iter__(self):
        return self.execute().__iter__()

    async def execute(
            self, db_session: AsyncSession, get_count=False
    ) -> Sequence:
        if self.query is not None:
            result = await db_session.execute(self.query)
            if self.needs_scalar:
                return result.scalars().all()
            else:
                return result.all()
        else:
            raise ValueError("Query is not built")

    @property
    def query(self) -> Select:
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        self._instance = value

    def _build_query(
        self,
        joins: set = set(),
        order_by=None,
        skip: int = None,
        limit: int = None,
        distinct_fields=None,
        where=None,
        select_models=None,
        **kwargs
    ) -> Select:
        """
        Build a basic query for the current model.
        :return: A query object.
        """
        joint = []
        if select_models is not None:
            query = select(*select_models, self.cls).select_from(self.cls)
            self.needs_scalar = False
        else:
            query = select(self.cls)
            self.needs_scalar = True

        if where is not None:
            query = query.where(*where)

        for join_condition in joins:
            related_model = (
                join_condition.left.table
                if join_condition.left.table != self.cls.__table__
                else join_condition.right.table
            )
            query = query.join(related_model, join_condition)
            joint.append(related_model)

        conditions = []
        for key, value in kwargs.items():
            filter_parts = key.split('__')
            column_name = filter_parts[0]
            filter_type = filter_parts[-1] if len(filter_parts) > 1 else None

            if column_name and hasattr(self.cls, column_name):
                if isinstance(
                    (getattr(
                        self.cls, column_name
                    ).property), RelationshipProperty
                ):
                    parent_cls = getattr(
                        self.cls, column_name
                    ).property.mapper.class_
                    if parent_cls not in joint:
                        query = query.join(parent_cls)
                        joint.append(parent_cls)
                else:
                    parent_cls = self.cls

                filter_field = next(
                    (obj for obj in filter_parts if hasattr(parent_cls, obj)),
                    None
                )
                if filter_field is None:
                    raise ValueError("This Column does not exist")
                column = getattr(parent_cls, filter_field)
                conditions = self.apply_filter_type(
                    filter_type, conditions, column, value
                )

        if conditions:
            query = query.where(and_(*conditions))

        if order_by:
            query = self._apply_ordering(query, order_by)
            query = self._apply_distinct(
                query, distinct_fields
            )
        elif distinct_fields:
            raise ValueError(
                "You must specify order_by when using distinct_fields"
            )

        if skip:
            query = query.offset(skip)

        if limit:
            query = query.limit(limit)

        self._joint.extend(joint)
        return query

    def build_handler(
        self,
        joins=set(),
        order_by=None,
        skip: int = 0,
        limit: int = 20,
        distinct_fields=None,
        where=None,
        select_models=None,
        **kwargs
    ) -> Select:
        """
        Build a query handler with the given filters.
        :param kwargs: Filters for the query.
        :return: A query handler.
        """
        cached_query = self._build_query(
            joins, skip=skip, limit=limit, order_by=order_by,
            distinct_fields=distinct_fields, where=where,
            select_models=select_models, **kwargs
        )
        return cached_query

    def is_relationship_field(self, model, field_name):
        field = getattr(model, field_name)
        return isinstance(field.property, RelationshipProperty)

    def is_m2m_relationship(self, model, field_name):
        field = getattr(model, field_name)
        return (
            isinstance(field.property, RelationshipProperty)
            and field.property.secondary is not None
        )

    def _apply_prefetch_related(self, query):
        for prefetch_joins in self._prefetch_related_joins:
            if len(prefetch_joins) == 2:
                related_model, association_table = prefetch_joins
                related_model_id, association_related_id = (
                    get_association_id_column(association_table, related_model)
                )
                self_model_id_column, association_self_id = (
                        get_association_id_column(association_table, self.cls)
                    )

                if association_table not in self._joint:
                    query = query.join(
                        association_table,
                        self_model_id_column == association_self_id
                    )
                    self._joint.append(association_table)

                if related_model not in self._joint:
                    query = query.join(
                        related_model,
                        related_model_id == association_related_id
                    )
                    self._joint.append(related_model)

            elif len(prefetch_joins) == 1:
                query = query.join(prefetch_joins)
        return query

    def apply_filter_type(
        self,
        filter_type: str,
        conditions: list,
        column,
        value,
    ) -> Select:
        conditions.append(self.condition_map.get(
            filter_type, lambda column, value: column == value)(column, value)
        )
        return conditions

    def _apply_ordering(self, query, order_by: Union[str, Tuple[str]]) -> None:
        """
        Apply ordering to the SQL statement based on the given order_by parm.

        :param order_by: A string or tuple of strings indicating orderby col.
        :return: None
        """
        if order_by == "?":
            return query.order_by(func.random())

        order_by = (order_by,) if isinstance(order_by, str) else order_by
        cols = [
            getattr(self.cls, col.lstrip("-")).desc() if col.startswith("-")
            else getattr(self.cls, col).asc() for col in order_by
        ]
        query = query.order_by(*cols)
        return query

    def _apply_distinct(self, query, distinct_fields=None):
        """
        Apply a DISTINCT clause to the SQL statement.

        :return: None
        """

        if distinct_fields is not None:
            if isinstance(distinct_fields, (list, tuple)):
                columns = [
                    getattr(self.cls, field) for field in distinct_fields
                ]
                query = query.distinct(*columns)
            else:
                raise ValueError(
                    "distinct_fields should be a list or tuple of field names."
                )
        return query
