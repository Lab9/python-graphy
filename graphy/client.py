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

        from graphy import loaders
        self.schema = loaders.introspect_schema(self.endpoint, self.session)

    @property
    def query(self) -> "QueryServiceProxy":
        if self._query_services is None:
            from graphy.proxy import QueryServiceProxy
            self._query_services = QueryServiceProxy(self)
        return self._query_services

    @property
    def mutation(self) -> "MutationServiceProxy":
        if self._mutation_services is None:
            from graphy.proxy import MutationServiceProxy
            self._mutation_services = MutationServiceProxy(self)
        return self._mutation_services

    @property
    def subscription(self):
        raise Exception("The subscription method is yet not supported.")
