from sqlalchemy import (
    select,
    delete as sqla_delete,
    update as sqla_update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, Union, Tuple, Any, List
from sqlalchemy import func
from sqlalchemy.orm import RelationshipProperty
from .signals import SignalMixin
from .base import BaseQuery


class QueryMixin(BaseQuery, SignalMixin):

    async def get(
        self,
        db_session: AsyncSession,
        joins=set(),
        order_by=None,
        **kwargs
    ) -> Union[Type[Any], Type["QueryMixin"]]:
        self.query = self.build_handler(
            joins=joins,
            order_by=order_by,
            **kwargs
        )
        result = await db_session.execute(self.query)
        self.instance = result.scalars().first()
        return self.instance

    def filter(
        self,
        joins=set(),
        order_by=None,
        skip: int = 0,
        values_fields: list = [],
        where=None,
        select_models=None,
        distinct_fields=None,
        **kwargs
    ) -> Union[Type[Any], Type["QueryMixin"]]:
        self.query = self.build_handler(
            joins=joins, order_by=order_by, skip=skip, where=where,
            distinct_fields=distinct_fields, select_models=select_models,
            **kwargs
        )

        if values_fields:
            self.query = self.query.with_only_columns(
                *[getattr(self.cls, field) for field in values_fields]
            )
        if hasattr(self, "_prefetch_related_joins"):
            self.query = self._apply_prefetch_related(self.query)
        return self

    async def count(self, db_session, stmt) -> int:
        pass

    async def create(
        self,
        db_session: AsyncSession,
        **kwargs
    ) -> Union[Type[Any], Type["QueryMixin"]]:
        self.instance = self.cls()
        for key, value in kwargs.items():
            attr = getattr(self.cls, key, None)

            if attr is None:
                raise ValueError(
                    f"No Attribute '{key}' in class '{self.cls.__name__}'"
                )

            if hasattr(attr, "property") and isinstance(
                attr.property, RelationshipProperty
            ):
                related_instance = value
                setattr(self.instance, key, related_instance)
            else:
                setattr(self.instance, key, value)

        # instance = await self._pre_save(db_session, instance, **kwargs)
        try:
            db_session.add(self.instance)
            await db_session.flush()
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise e
        return self.instance

    def all(
        self,
        joins=set(),
        order_by: str = None,
        skip: int = 0,
    ) -> Union[Type[Any], Type["QueryMixin"]]:
        self.filter(joins, order_by=order_by, skip=0)
        return self

    async def delete(
        self,
        db_session: AsyncSession,
        joins=set(),
        **kwargs
    ) -> int:
        """
        Delete instances matching the given filters.
        :param db_session: The async database session.
        :param kwargs: Filters for the instances to delete.
        :return: None
        """
        self.query = self.build_handler(
            joins=joins, **kwargs
        )
        self.query = await self._pre_delete(db_session, self.query, **kwargs)
        delete_stmt = sqla_delete(self.cls).where(self.query.whereclause)
        result = await db_session.execute(delete_stmt)
        await db_session.commit()
        return result.rowcount

    async def update(
        self,
        db_session: AsyncSession,
        data: dict,
        joins=set(),
        **kwargs
    ) -> int:
        """
        Update instances matching the given filters with the given data.

        :param db_session: The async database session.
        :param update_data: A dictionary containing the data to update.
        :param kwargs: Filters for the instances to update.
        :return: None
        """
        self.query = self.build_handler(
            joins=joins, **kwargs
        )
        self.query = await self._pre_update(db_session, self.query, **kwargs)
        self.query = sqla_update(self.cls).where(
            self.query.whereclause
        ).values(data)
        result = await db_session.execute(self.query)
        await db_session.commit()
        if result.rowcount == 1:
            updated_instance = await self.get(db_session, **kwargs)
            return updated_instance
        else:
            return result.rowcount or None

    async def aggregate(
        self,
        db_session: AsyncSession,
        field: str,
        agg_func: str = "sum",
        joins=set(),
        **kwargs
    ) -> Union[int, float, None]:
        """
        Perform an aggregation on a column.

        :param db_session: The async database session.
        :param aggregation_fn: The aggregation function to use.
        :param column: The column to aggregate.
        :param kwargs: Additional filters for the query.
        :return: The result of the aggregation.
        """
        supported_agg_funcs = {
            "sum": func.sum,
            "count": func.count,
            "avg": func.avg,
            "min": func.min,
            "max": func.max
        }
        if agg_func.lower() not in supported_agg_funcs:
            raise NotImplementedError(
                f"Unsupported aggregation function '{agg_func}'"
            )
        aggregation = supported_agg_funcs[agg_func.lower()](
            getattr(self.cls, field)
        )
        self.query = select(aggregation)
        self.query = self.build_handler(joins=joins, **kwargs)
        self.query = self.query.select_from(self.cls).with_only_columns(
            aggregation
        )
        result = await db_session.execute(self.query)
        return result.scalar()

    async def exclude(
        self,
        db_session: AsyncSession,
        joins=set(),
        order_by=None,
        skip: int = 0,
        **kwargs
    ) -> Union[Type[Any], Type["QueryMixin"]]:
        """
        Retrieve instances that do not match the given filters.

        :param db_session: The async database session.
        :param joins: A set of join conditions.
        :param order_by: A string or tuple of strings indicating the columns
            to order by.
        :param skip: The number of instances to skip.
        :param get_count: If True, also return the count of instances.
        :param kwargs: Additional filters for the query.
        :return: A list of instances or a tuple containing the list of
            instances and the count.
        """
        all_stmt = self.build_handler(
            db_session=db_session, joins=joins, order_by=order_by, skip=skip
        )
        all_result = await db_session.execute(all_stmt)
        all_instances = all_result.scalars().all()
        exclude_stmt = self.build_handler(
            db_session=db_session, joins=joins, order_by=order_by, skip=skip,
            **kwargs
        )
        exclude_result = await db_session.execute(exclude_stmt)
        exclude_instances = exclude_result.scalars().all()
        self.instance = list(set(all_instances) - set(exclude_instances))
        return self.instance

    async def add_m2m(self, db_session: AsyncSession, other_model) -> None:
        """
        Add a many-to-many relationship between two entities.d
        :param db_session: The async database session.
        :param other_model: The entity in the relationship.
        :return: None
        """
        if self.instance is None:
            raise ValueError("Perform a query before using add_m2m method")
        for attr, value in self.instance.__class__.__dict__.items():
            if isinstance(
                value, RelationshipProperty
            ) and value.argument == other_model.__class__.__name__:
                getattr(self.instance, attr).append(other_model)
        for attr, value in other_model.__class__.__dict__.items():
            if isinstance(
                value, RelationshipProperty
            ) and value.argument == self.instance.__class__.__name__:
                getattr(other_model, attr).append(self.instance)

        await db_session.commit()

    async def get_or_create(
        self, db_session: AsyncSession, create_data: dict, **kwargs
    ) -> Tuple[Union[Type[Any], Type["QueryMixin"]], bool]:
        """
        Retrieve an instance if it exists, otherwise create a new one.

        :param db_session: The async database session.
        :param create_data: A dict containing the data for the new instance.
        :param kwargs: Filters for the query.
        :return: A tuple containing the instance and a boolean indicating
            if the instance was created.
        """
        instance = await self.get(db_session, **kwargs)
        created = False
        if not instance:
            instance = await self.create(db_session, **create_data)
            created = True
        return instance, created

    async def bulk_create(
            self, db_session: AsyncSession, instances_data: List[dict]
    ) -> list:
        """
        Create multiple instances in a single bulk operation.
        :param db_session: The async database session.
        :param instances_data: A list of dictionaries containing the data for
            the new instances.
        :return: A list of created instances.
        """
        instances = [self.cls(**data) for data in instances_data]

        try:
            db_session.add_all(instances)
            await db_session.flush()
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise e
        return len(instances)

    async def select_related(self, session, *related_models):
        raise NotImplementedError("Not Implemented Yet")

    def prefetch_related(self, related_model: 'QueryMixin') -> 'QueryMixin':
        model_fields = [
            f for f in related_model.__dict__.keys() if not f.startswith("_")
        ]
        relation_ship_field = next(
            (
                field for field in model_fields if
                self.is_m2m_relationship(
                    related_model, field
                ) and getattr(
                    related_model, field
                ).property.argument == self.cls.__name__
            ), None
        )
        if relation_ship_field:
            self._prefetch_related_joins.append(
                (
                    related_model,
                    getattr(
                        related_model, relation_ship_field
                    ).property.secondary
                )
            )
        else:
            rel_name = related_model.__name__
            this_name = self.cls.__name__
            raise ValueError(
                f"No relationship between model {this_name} and {rel_name}"
            )
        return self

    async def bulk_update(
        self,
        db_sesssion: AsyncSession,
        update_data: List[Tuple[dict, dict]]
    ) -> int:
        raise NotImplementedError("""
        sqlalchemy.exc.InvalidRequestError
        WHERE clause with bulk ORM UPDATE not supported right now
        """)
        """
        Perform a bulk update of instances based on given filters and update.

        :param db_session: The async database session.
        :param update_data: A list of tuples, where each tuple contains a
            dictionary of filters and a dictionary of update data.
        :return: The number of updated instances.
        """
        # num_updated = 0
        # update_params = []
        # for idx, (filter_conditions, data) in enumerate(update_data):
        #     update_params.append(
        #         {
        #             **filter_conditions,
        #             **{f"{key}_{idx}": value for key, value in data.items()}
        #         }
        #     )
        # update_stmt = sqla_update(self.cls)
        # for idx, (filter_conditions, data) in enumerate(update_data):
        #     condition_query = self.build_handler(
        #         db_session, **filter_conditions
        #     )
        #     update_stmt = update_stmt.where(condition_query)
        #     for key in data.keys():
        #         update_stmt = update_stmt.values(
        #             {getattr(self.cls, key): bindparam(f"{key}_{idx}")}
        #         )

        # result = await db_session.execute(update_stmt, update_params)
        # await db_session.commit()
        # num_updated = result.rowcount
        # return num_updated
