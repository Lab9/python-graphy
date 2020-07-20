from typing import Dict

from requests import Session

from graphy.logger import logger
from graphy.schema import Schema


def introspect_schema(endpoint: str, session: Session) -> Schema:
    """
    Makes a schema introspection and returns the resulting schema.

    :param endpoint: holds the servers endpoint -> http://...
    :param session: holds the session object to use
    :return: The dictionary with the schema
    :raises: a RequestException if the schema could not be received.
    """
    schema_json = get_raw_schema(endpoint, session)
    logger.debug("Successfully received schema.")
    schema = Schema(schema_json)
    logger.debug("Successfully introspected schema.")
    return schema


def get_raw_schema(endpoint: str, session: Session) -> Dict:
    """
    Makes a schema introspection and returns the resulting schema.
    The current query looks as following:

    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
        directives {
          name
          description
          locations
          args {
            ...InputValue
          }
        }
      }
    }

    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        ...InputValue
      }
      interfaces {
        ...TypeRef
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        ...TypeRef
      }
    }

    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue
    }

    fragment TypeRef on __Type {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
      }
    }

    :param endpoint: holds the servers endpoint -> http://...
    :param session: holds the session object to use
    :return: The dictionary with the schema
    :raises: a RequestException if the schema could not be received.
    """
    variables = {}
    operation_name = "IntrospectionQuery"
    query = """
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
              ...FullType
            }
            directives {
              name
              description
              locations
              args {
                ...InputValue
              }
            }
          }
        }

        fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }

        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue
        }

        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
    introspection_response = session.post(
        endpoint,
        json={
            "query": query,
            "operationName": operation_name,
            "variables": variables
        }
    )
    introspection_response.raise_for_status()
    return introspection_response.json()
