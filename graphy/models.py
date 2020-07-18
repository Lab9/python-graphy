import itertools
from typing import Dict, Iterable, List, Tuple

from requests import Response

from graphy.client import Client


class Schema:
    def __init__(self, raw: Dict):
        from graphy import helpers
        # graphql schema properties
        self.raw_schema = raw.get("data", {}).get("__schema", {})
        self.query_type: str = helpers.parse_query_type(self.raw_schema)
        self.mutation_type: str = helpers.parse_mutation_type(self.raw_schema)
        self.subscription_type: str = helpers.parse_subscription_type(self.raw_schema)
        self.types: Dict[str, Type] = helpers.parse_types(self.raw_schema.get("types", []))
        self.directives: Dict[str, Directive] = helpers.parse_directives(self.raw_schema.get("directives", []))

        # custom schema properties
        self.queries: List[Operation] = helpers.parse_operations(self.types, self.query_type)
        self.mutations: List[Operation] = helpers.parse_operations(self.types, self.mutation_type)
        self.subscriptions: List[Operation] = helpers.parse_operations(self.types, self.subscription_type)


class Operation:
    def __init__(self, field: "TypeField"):
        self.name = field.name
        self.description = field.description
        self.arguments = field.args
        self.return_type = field.type

    def get_return_type(self, all_types: "Dict[str, Type]") -> "Type":
        return_type_name = self.return_type.name
        return all_types.get(return_type_name)


class Query(Operation):
    pass


class Mutation(Operation):
    pass


class Subscription(Operation):
    pass


class Directive:
    def __init__(self, raw_directive: Dict):
        from graphy import helpers
        self.name: str = raw_directive.get("name")
        self.description: str = raw_directive.get("description")
        self.locations: List[str] = raw_directive.get("locations", [])
        self.args: Dict[str, Argument] = helpers.parse_arguments(raw_directive.get("args", []))


class Argument:
    def __init__(self, raw_argument: Dict):
        self.name = raw_argument.get("name")
        self.description = raw_argument.get("description")
        self.type = TypeDefer(raw_argument.get("type")) if raw_argument.get("type") is not None else None
        self.default_value = raw_argument.get("defaultValue")


class TypeDefer:
    def __init__(self, raw_defer: Dict):
        self.kind = raw_defer.get("kind")
        self.name = raw_defer.get("name")
        self.of_type: 'TypeDefer' = TypeDefer(raw_defer.get("ofType")) if raw_defer.get("ofType") is not None else None


class Type:
    def __init__(self, raw_type: Dict):
        self.kind = raw_type.get("kind")
        self.name = raw_type.get("name")
        self.description = raw_type.get("description")
        self.fields: List[TypeField] = [TypeField(f) for f in raw_type.get("fields", []) or [] if f]
        self.input_fields = raw_type.get("inputFields")
        self.interfaces = raw_type.get("interfaces")
        self.enum_values = raw_type.get("enumValues")
        self.possible_types = raw_type.get("possibleTypes")


class TypeField:
    def __init__(self, raw_field: Dict):
        from graphy import helpers
        self.name = raw_field.get("name")
        self.description = raw_field.get("description")
        self.args: Dict[str, Argument] = helpers.parse_arguments(raw_field.get("args", []))
        self.type: TypeDefer = TypeDefer(raw_field.get("type")) if raw_field.get("type") is not None else None
        self.is_deprecated: bool = raw_field.get("isDeprecated")
        self.deprecation_reason: str = raw_field.get("deprecationReason")


class SelectionField:
    def __init__(self, name: str, children: List = None):
        self.name: str = name
        self.children: List = children

    def __str__(self):
        result = self.name
        if self.children:
            result += " { " + " ".join([str(c) for c in self.children]) + " } "
        return result


class OperationProxy:
    def __init__(self, client: Client, operation: Operation):
        self.client = client
        self.operation = operation

    @property
    def operation_name(self) -> str:
        return self.operation.name

    @property
    def get_all_selectable_fields(self) -> Tuple[SelectionField]:
        from graphy import builder
        base_return_type = self.operation.get_return_type(self.client.schema.types)
        result = []
        for type_field in base_return_type.fields or []:
            if not type_field:
                continue
            if type_field.type.kind in ("OBJECT", "LIST"):
                continue
            result.append(type_field.name)
        return builder.fields(*result)

    def __call__(self, query: str, variables: Dict = None, operation_name: str = "", *args, **kwargs) -> Response:
        if variables is None:
            variables = {}
        if operation_name == "":
            operation_name = self.operation_name
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
            from graphy import builder
            select = self.get_all_selectable_fields
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
            select = self.get_all_selectable_fields
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
