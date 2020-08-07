from typing import Dict, Union, List

from graphy.schema import Operation, Type, Argument, Directive


def parse_query_type(raw_schema: Dict) -> Union[str, None]:
    query_type = raw_schema.get("queryType", {})
    if not query_type:
        return None
    return query_type.get("name")


def parse_mutation_type(raw_schema: Dict) -> Union[str, None]:
    query_type = raw_schema.get("mutationType", {})
    if not query_type:
        return None
    return query_type.get("name")


def parse_subscription_type(raw_schema: Dict) -> Union[str, None]:
    query_type = raw_schema.get("subscriptionType", {})
    if not query_type:
        return None
    return query_type.get("name")


def parse_operations(raw_types: Dict[str, Type], query_type_name: str) -> List[Operation]:
    if not query_type_name:
        return []
    query_type = raw_types.get(query_type_name)
    if not query_type:
        return []
    return [Operation(f) for f in query_type.fields]


def parse_types(schema_types: List[Dict]) -> Dict[str, Type]:
    result = {}
    for schema_type in schema_types:
        new_type = Type(schema_type)
        result[new_type.name] = new_type
    return result


def parse_arguments(args: List[Dict]) -> 'Dict[str, Argument]':
    if not args:
        return {}
    result = {}
    for a in args:
        if not a:
            continue
        arg = Argument(a)
        result[arg.name] = arg
    return result


def parse_directives(schema_directives: List[Dict]) -> Dict[str, Directive]:
    result = {}
    for schema_directive in schema_directives:
        new_directive = Directive(schema_directive)
        result[new_directive.name] = new_directive
    return result
