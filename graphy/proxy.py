import itertools
from typing import Dict, Iterable, Tuple

from graphy import helpers
from graphy.builder import GraphQLBuilder
from graphy.builder import SelectedField
from graphy.schema import Operation


class OperationProxy:
    """
    The operation proxy class provides callable instances where the query,
    variables and an optional operation name can be passed by.
    An instance of this class is not intended to be called directly.
    Use it's sub classes instead.
    """

    def __init__(self, client, operation: Operation):
        """
        Instantiate a new OperationProxy instance
        :param client: holds the client
        :param operation: holds the to be executed operation
        """
        self.client = client
        self.operation = operation

    @property
    def name(self) -> str:
        """ Shortcut for the operations name """
        return self.operation.name

    def __call__(self, query: str, variables: Dict = None, *args, **kwargs):
        """
        The call makes the actual request to the endpoint.
        The result depends on the settings and transport in use.

        :param query: holds the query string
        :param variables: holds a dictionary of variables that will be passed by as well
        :param operation_name: holds an optional operation name
        :param args: holds additional arguments
        :param kwargs: holds additional key word arguments
        :return: the result depending on settings and transport in use.
        """
        variables = variables or {}
        return self.client.transporter.post(
            self.client.endpoint,
            query,
            variables,
            self.name,
            self.operation.settings
        )


class ServiceProxy:
    """
    The base service proxy class.
    An instance of this class holds a dictionary of all possible operations that are
    available for this service.
    """

    def __init__(self, services: Dict[str, OperationProxy]):
        """
        Instantiate a new instance of ServiceProxy

        :param services: holds a dictionary with all available services
        """
        self._services: Dict[str, OperationProxy] = services

    def __getattr__(self, key) -> OperationProxy:
        """
        Return the OperationProxy for the given key.

        :param key: holds the operation key
        :return: the according OperationProxy
        :raises: AttributeError when the no operation with that key exists.
        """
        return self[key]

    def __getitem__(self, key) -> OperationProxy:
        """
        Return the OperationProxy for the given key.

        :param key: holds the operation key
        :return: the according OperationProxy
        :raises: AttributeError when the no operation with that key exists.
        """
        try:
            return self._services[key]
        except KeyError:
            raise AttributeError(f"No operation found for key {key}")

    def __iter__(self):
        """ Return iterator for the services and their callables. """
        return iter(self._services.items())

    def __dir__(self) -> Iterable[str]:
        """ Return the names of the operations. """
        return list(itertools.chain(dir(super()), self._services))


class QueryOperationProxy(OperationProxy):
    """
    The operation proxy for a query.
    The call method was slightly changed for better readability which makes it easier to use as well.
    I'm open for any suggestions and improvements.
    """

    def __call__(self, select: Tuple[SelectedField] = None, where: Dict = None, *args, **kwargs):
        """
        This method is used to build the query request.

        When no selection is specified and the automatic lookup has not been disabled via the settings,
        it will try to create a tuple of possible selection fields.
        If the automatic lookup fails it will fallback to None.

        Then a query builder will be instantiated and optional variables as well as the fields are being set.

        Finally the request will be made and the result returned.

        :param select: holds a selection of all fields.
        :param where: holds a dictionary with query conditions.
        :param args: holds additional arguments
        :param kwargs: holds additional key word arguments
        :return: the result from the transporter
        """
        if select is None and not self.operation.settings.disable_selection_lookup:
            select = self.operation.get_return_fields(self.client.schema.types)

        query_builder = GraphQLBuilder()

        if where is not None:
            variables = helpers.map_variables_to_types(where, self.operation)
            query_builder = query_builder.operation("query", name=self.name, params=variables)
            query_builder = query_builder.query(self.name, params={key: f"${key}" for key in where.keys()})
        else:
            query_builder = query_builder.operation("query").query(self.name)

        query_builder = query_builder.fields(select)
        query_string = query_builder.generate()
        return super(QueryOperationProxy, self).__call__(query=query_string, variables=where, *args, **kwargs)


class QueryServiceProxy(ServiceProxy):
    """ The query service proxy holds all query operations """

    def __init__(self, client):
        """
        Instantiate a new QueryServiceProxy.
        :param client: holds the client
        """
        super(QueryServiceProxy, self).__init__({
            op.name: QueryOperationProxy(client, op) for op in client.schema.queries
        })


class MutationOperationProxy(OperationProxy):
    """
    The operation proxy for a mutation.
    The call method was slightly changed for better readability which makes it easier to use as well.
    I'm open for any suggestions and improvements.
    """

    def __call__(self, select: Tuple[SelectedField] = None, data: Dict = None, *args, **kwargs):
        """
        This method is used to build the mutation request.

        No selection is widely accepted so the automatic lookup was not implemented here.
        Please specify the fields yourself if necessary.

        Then a query builder will be instantiated and necessary variables as well as the fields are being set.

        Finally the request will be made and the result returned.

        :param select: holds a selection of all fields.
        :param data: holds a dictionary with the data to pass by
        :param args: holds additional arguments
        :param kwargs: holds additional key word arguments
        :return: the result from the transporter
        """
        if data is None:
            raise ValueError("No Data specified")
        query_builder = GraphQLBuilder()
        variables = helpers.map_variables_to_types(data, self.operation)
        query_builder = query_builder.operation("mutation", name=self.name, params=variables)
        query_builder = query_builder.query(self.name, params={key: f"${key}" for key in data.keys()})

        query_builder = query_builder.fields(select)
        query_string = query_builder.generate()
        return super(MutationOperationProxy, self).__call__(query=query_string, variables=data, *args, **kwargs)


class MutationServiceProxy(ServiceProxy):
    """ The mutation service proxy holds all mutation operations """

    def __init__(self, client):
        """
        Instantiate a new MutationServiceProxy.
        :param client: holds the client
        """
        super(MutationServiceProxy, self).__init__({
            op.name: MutationOperationProxy(client, op) for op in client.schema.mutations
        })
