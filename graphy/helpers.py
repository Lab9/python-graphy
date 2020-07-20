from typing import Dict, List, Union, Tuple

from graphy.schema import Type, Directive, Operation, Argument, TypeDefer, SelectionField


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
    return [Operation(f, raw_types) for f in query_type.fields]


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


def remove_duplicate_spaces(query: str) -> str:
    return " ".join(query.split())


def map_variables_to_types(variables: Dict, operation: Operation) -> Dict[str, str]:
    result = {}
    for key in variables.keys():
        arg = operation.arguments.get(key)
        if not arg:
            raise ValueError(f"Argument '{key}' is not supported by operation '{operation.name}'.")
        result[f"${key}"] = arg
    return result


def is_non_null(defer: TypeDefer) -> bool:
    return defer and defer.kind == "NON_NULL"


def is_list(defer: TypeDefer) -> bool:
    return defer and defer.kind == "LIST"


def is_object(defer: TypeDefer) -> bool:
    return defer and defer.kind == "OBJECT"


def is_input_object(defer: TypeDefer) -> bool:
    return defer and defer.kind == "INPUT_OBJECT"


def is_scalar(defer: TypeDefer) -> bool:
    return defer and defer.kind == "SCALAR"


def find_defer_name_recursively(defer: TypeDefer) -> Union[str, None]:
    if not defer:
        return None
    if defer.name is None:
        return find_defer_name_recursively(defer.of_type)
    else:
        return defer.name


def adapt_arguments(args: Dict[str, Argument]) -> Dict[str, str]:
    result = {}
    for name, arg in args.items():
        type_name = find_defer_name_recursively(arg.type)
        if is_non_null(arg.type):
            type_name += "!"
        result[name] = type_name
    return result


def adapt_return_fields(field_type: TypeDefer, all_types: Dict[str, Type]) -> Tuple[SelectionField]:
    base_return_type_name = find_defer_name_recursively(field_type)
    all_fields = __recursively_find_selection_fields(base_return_type_name, all_types)
    return all_fields if len(all_fields) != 0 else None


def __recursively_find_selection_fields(
        type_name: str,
        all_types: Dict[str, Type]
) -> Tuple[SelectionField]:
    field_type: Type = all_types.get(type_name)
    if field_type is None:
        return tuple()

    args = []
    kwargs = {}

    for field in field_type.fields:
        if field is None:
            continue
        field_name = field.name
        if is_scalar(field.type):
            args.append(field_name)

    from graphy import builder
    return builder.fields(*args, **kwargs)
