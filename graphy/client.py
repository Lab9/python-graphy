from requests import Session


class Client(object):
    def __init__(self, endpoint: str, introspect=True, session=None):
        if not endpoint:
            raise ValueError("No Endpoint specified.")
        self.endpoint = endpoint
        self.introspect = introspect
        self.session: Session = session if session is not None else Session()

        self._query_services = None
        self._mutation_services = None

        if introspect:
            from graphy import loaders
            self.schema = loaders.introspect_schema(self.endpoint, self.session)
        else:
            from graphy.models import EMPTY_SCHEMA
            self.schema = EMPTY_SCHEMA

    @property
    def query(self) -> "QueryServices":
        if self._query_services is None:
            from graphy.models import QueryServices
            self._query_services = QueryServices(self)
        return self._query_services

    @property
    def mutation(self) -> "MutationServices":
        if self._mutation_services is None:
            from graphy.models import MutationServices
            self._mutation_services = MutationServices(self)
        return self._mutation_services
