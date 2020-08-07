from typing import Dict

import requests
from promise import Promise
from requests import Session, Response

from graphy.utils import get_version


class Transporter:
    """
    A transport object handles communication between client and server.

    Optionally a custom session can be passed by and an operation timeout be set.
    """

    def __init__(self, session=None, operation_timeout=None):
        """
        Create a new Transporter object.

        :param session: (optional) a requests session object
        :param operation_timeout: (optional) requests operation timeout
        """
        self.operation_timeout = operation_timeout
        self.session: Session = session or requests.sessions.session()
        self.session.headers["User-Agent"] = f"Graphy/{get_version()} (https://pypi.org/project/python-graphy/)"

    def post(self, address: str, query: str, variables: Dict, operation_name: str) -> Response:
        """
        Wrapper for the requests.post() method.

        :param address: holds the request endpoint
        :param query: holds the query string
        :param variables: holds the query variables if there are any
        :param operation_name: holds an optional operation name
        :return:
        """
        return self.session.post(
            address,
            json={
                "query": query,
                "variables": variables,
                "operationName": operation_name
            },
            timeout=self.operation_timeout
        )


class PromiseTransporter(Transporter):
    """
    A promise transporter returns Promises instead of the Response.
    Use this when you do not want to wait for the request to finish and continue to run with your code.
    """

    def post(self, address: str, query: str, variables: Dict, operation_name: str) -> Promise[Response]:
        """
        This method wraps the parents post method in a Promise.
        """
        return Promise(
            lambda resolve, reject: resolve(super(PromiseTransporter, self).post(
                address, query, variables, operation_name
            ))
        )


class AsyncTransporter(Transporter):
    """
    An async transporter wraps the default post in an async method.
    Use this for async programming.
    """

    async def post(self, address: str, query: str, variables: Dict, operation_name: str) -> Response:
        return super().post(address, query, variables, operation_name)
