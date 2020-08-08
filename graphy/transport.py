from typing import Dict, Union

import requests
from promise import Promise
from requests import Session, Response

from graphy.settings import Settings
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

    def post(
            self,
            address: str,
            query: str,
            variables: Dict,
            operation_name: str,
            settings: Settings
    ) -> Union[Response, Dict]:
        """
        Wrapper for the requests.post() method.

        :param address: holds the request endpoint
        :param query: holds the query string
        :param variables: holds the query variables if there are any
        :param operation_name: holds an optional operation name
        :param settings: holds the clients settings
        :return:
        """
        response = self.session.post(
            address,
            json={
                "query": query,
                "variables": variables,
                "operationName": operation_name
            },
            timeout=self.operation_timeout
        )

        return response if settings.return_requests_response else response.json()


class PromiseTransporter(Transporter):
    """
    A promise transporter returns Promises instead of the Response.
    Use this when you do not want to wait for the request to finish and continue to run with your code.
    """

    def post(
            self,
            address: str,
            query: str,
            variables: Dict,
            operation_name: str,
            settings: Settings
    ) -> Promise[Union[Response, Dict]]:
        """
        This method wraps the parents post method in a Promise.
        """
        return Promise(
            lambda resolve, reject: resolve(super(PromiseTransporter, self).post(
                address, query, variables, operation_name, settings
            ))
        )


class AsyncTransporter(Transporter):
    """
    An async transporter wraps the default post in an async method.
    Use this for async programming.
    """

    async def post(
            self,
            address: str,
            query: str,
            variables: Dict,
            operation_name: str,
            settings: Settings
    ) -> Union[Response, Dict]:
        """
        This method wraps the parents post method in an awaitable.
        """
        return super().post(address, query, variables, operation_name, settings)
