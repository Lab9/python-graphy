import itertools
from typing import Dict, Iterable, Tuple

from requests import Response

from graphy.client import Client
from graphy.schema import Operation, SelectionField


class OperationProxy:
    def __init__(self, client: Client, operation: Operation):
        self.client = client
        self.operation = operation

    @property
    def operation_name(self) -> str:
        return self.operation.name

    def __call__(self, query: str, variables: Dict = None, operation_name: str = "", *args, **kwargs) -> Response:
        if variables is None:
            variables = {}
        return self.client.session.post(
            self.client.endpoint,
            json={
                "query": query,
                "variables": variables,
                "operationName": operation_name
            }
        )


class ServiceProxy:
    def __init__(self, services: Dict[str, OperationProxy]):
        self._services: Dict[str, OperationProxy] = services

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        try:
            return self._services[item]
        except KeyError:
            raise AttributeError(f"No Service found for key {item}")

    def __iter__(self):
        return iter(self._services.items())

    def __dir__(self) -> Iterable[str]:
        return list(itertools.chain(dir(super()), self._services))


class QueryOperationProxy(OperationProxy):

    def __call__(self, select: Tuple[SelectionField] = None, where: Dict = None, *args, **kwargs) -> Response:
        if select is None:
            select = self.operation.return_fields
            if select is None:
                raise ValueError("Missing field selection")
        from graphy.builder import GraphQLQueryBuilder
        from graphy import helpers
        query_builder = GraphQLQueryBuilder()
        if where is not None:
            variables = helpers.map_variables_to_types(where, self.operation)
            query_builder = query_builder.operation("query", name=self.operation_name, params=variables)
            query_builder = query_builder.query(self.operation_name, params={key: f"${key}" for key in where.keys()})
        else:
            query_builder = query_builder.operation("query").query(self.operation_name)

        query_builder = query_builder.fields(select)
        query_string = query_builder.generate()
        return super(QueryOperationProxy, self).__call__(query=query_string, variables=where, *args, **kwargs)


class QueryServiceProxy(ServiceProxy):

    def __init__(self, client: Client):
        super(QueryServiceProxy, self).__init__({
            op.name: QueryOperationProxy(client, op) for op in client.schema.queries
        })


class MutationOperationProxy(OperationProxy):

    def __call__(self, select: Tuple[SelectionField] = None, data: Dict = None, *args, **kwargs) -> Response:
        if data is None:
            raise ValueError("No Data specified")
        if select is None:
            select = tuple()
        from graphy.builder import GraphQLQueryBuilder
        from graphy import helpers
        query_builder = GraphQLQueryBuilder()
        variables = helpers.map_variables_to_types(data, self.operation)
        query_builder = query_builder.operation("mutation", name=self.operation_name, params=variables)
        query_builder = query_builder.query(self.operation_name, params={key: f"${key}" for key in data.keys()})

        query_builder = query_builder.fields(select)
        query_string = query_builder.generate()
        return super(MutationOperationProxy, self).__call__(query=query_string, variables=data, *args, **kwargs)


class MutationServiceProxy(ServiceProxy):

    def __init__(self, client: Client):
        super(MutationServiceProxy, self).__init__({
            op.name: MutationOperationProxy(client, op) for op in client.schema.mutations
        })
