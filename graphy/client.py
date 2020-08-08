from graphy.proxy import MutationServiceProxy, QueryServiceProxy
from graphy.schema import Schema
from graphy.settings import Settings
from graphy.transport import Transporter


class Client(object):
    def __init__(self, endpoint: str, transporter=None, settings=None):
        if not endpoint:
            raise ValueError("No Endpoint specified.")
        self.endpoint = endpoint
        self.transporter: Transporter = transporter or Transporter()
        self.settings: Settings = settings or Settings()

        self._query_services = None
        self._mutation_services = None

        self.schema = Schema(self.endpoint, self.transporter, self.settings)

    @property
    def query(self) -> QueryServiceProxy:
        if self._query_services is None:
            self._query_services = QueryServiceProxy(self)
        return self._query_services

    @property
    def mutation(self) -> MutationServiceProxy:
        if self._mutation_services is None:
            self._mutation_services = MutationServiceProxy(self)
        return self._mutation_services

    @property
    def subscription(self):
        raise Exception("The subscription method is yet not supported.")
