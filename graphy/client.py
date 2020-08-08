from graphy.proxy import MutationServiceProxy, QueryServiceProxy
from graphy.schema import Schema
from graphy.settings import Settings
from graphy.transport import Transporter


class Client(object):
    """
    The graphy client is the core of this package.

    It is used for requests and holds important variables like endpoint, settings and the schema.
    """

    def __init__(self, endpoint: str, transporter=None, settings=None):
        """
        Instantiate a new Client.

        :param endpoint: holds the endpoint URL.
        :param transporter: holds the transporter to use for requests.
        :param settings: holds the settings to apply.
        """
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
        """
        Property for lazy loading the query service proxy
        :return: the clients query service proxy
        """
        if self._query_services is None:
            self._query_services = QueryServiceProxy(self)
        return self._query_services

    @property
    def mutation(self) -> MutationServiceProxy:
        """
        Property for lazy loading the mutation service proxy
        :return: the clients query mutation proxy
        """
        if self._mutation_services is None:
            self._mutation_services = MutationServiceProxy(self)
        return self._mutation_services

    @property
    def subscription(self):
        """
        Property for lazy loading the subscription service proxy
        :return: the clients query subscription proxy
        """
        raise Exception("The subscription method is yet not supported.")
