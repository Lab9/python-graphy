import itertools
from typing import Dict, Iterable, List

from requests import Response

from graphy.client import Client


class Schema(object):
    def __init__(self, raw: Dict):
        from graphy import helpers
        self.raw_data = raw.get("data", {})
        self.raw_schema = self.raw_data.get("__schema", {})
        self.types: List[str] = helpers.parse_types(self.raw_schema)
        self.queries: List[str] = helpers.parse_queries(self.raw_schema)
        self.mutations: List[str] = helpers.parse_mutations(self.raw_schema)


EMPTY_SCHEMA = Schema({})


class Type(object):
    def __init__(self, raw_type: Dict):
        self.kind = raw_type.get("kind", "")
        self.name = raw_type.get("name", "")
        self.description = raw_type.get("description", "")
        self.fields = raw_type.get("fields")
        self.input_fields = raw_type.get("inputFields")
        self.interfaces = raw_type.get("interfaces")
        self.enum_values = raw_type.get("enumValues")
        self.possible_types = raw_type.get("possibleTypes")


class Service:
    def __init__(self, client: Client, operation_name: str):
        self.client = client
        self.operation_name = operation_name

    def __call__(self, query: str, *args, **kwargs) -> Response:
        return self.client.session.post(
            self.client.endpoint,
            json={"query": query}
        )


class Services:
    def __init__(self, services: Dict[str, Service]):
        self._services: Dict[str, Service] = services

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


class QueryService(Service):

    def __call__(self, select=None, where=None, *args, **kwargs) -> Response:
        if select is None:
            raise ValueError("No fields to select were specified.")
        from graphy import builder
        query = builder.build_query(self.operation_name, params=where, fields=select)
        return super(QueryService, self).__call__(query, *args, **kwargs)


class QueryServices(Services):

    def __init__(self, client: Client):
        super(QueryServices, self).__init__({
            name: QueryService(client, name) for name in client.schema.queries
        })


class MutationService(Service):

    def __call__(self, data=None, select=None, *args, **kwargs) -> Response:
        if data is None:
            raise ValueError("No Data specified")
        from graphy import builder
        query = builder.build_mutation(self.operation_name, params=data, fields=select)
        return super(MutationService, self).__call__(query, *args, **kwargs)


class MutationServices(Services):

    def __init__(self, client: Client):
        super(MutationServices, self).__init__({
            name: MutationService(client, name) for name in client.schema.mutations
        })
