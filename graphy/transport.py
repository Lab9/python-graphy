from typing import Dict

import requests
from promise import Promise
from requests import Session, Response


class Transporter:
    def __init__(self, session=None):
        if session is None:
            session = requests.sessions.session()

        self.session: Session = session

    def post(self, address: str, query: str, variables: Dict, operation_name: str) -> Response:
        return self.session.post(
            address,
            json={
                "query": query,
                "variables": variables,
                "operationName": operation_name
            }
        )


class AsyncTransporter(Transporter):

    def post(self, address: str, query: str, variables: Dict, operation_name: str) -> Promise[Response]:
        return Promise(
            lambda resolve, reject: resolve(super(AsyncTransporter, self).post(
                address, query, variables, operation_name
            ))
        )
