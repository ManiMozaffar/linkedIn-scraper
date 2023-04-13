from .queries import QueryMixin


class QueryMixinDescriptor:
    def __get__(self, instance, owner):
        return QueryMixin(owner)


class AbstractModel:
    __abstract__ = True
    objects: QueryMixin = QueryMixinDescriptor()
