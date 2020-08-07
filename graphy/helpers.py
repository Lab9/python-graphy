from typing import Dict, Union, Tuple

from graphy.schema import Type, Operation, Argument, TypeDefer, SelectionField


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
    return all_fields if all_fields is not None and len(all_fields) != 0 else None


MAX_RECURSION_DEPTH = 2


def __recursively_find_selection_fields(
        type_name: str,
        all_types: Dict[str, Type],
        curr_depth=0
) -> Tuple[SelectionField]:
    if curr_depth >= MAX_RECURSION_DEPTH:
        return None
    field_type: Type = all_types.get(type_name)
    if field_type is None:
        return None

    args = []
    kwargs = {}

    for field in field_type.fields:
        if field is None:
            continue
        if is_non_null(field.type):
            type_to_check = field.type.of_type
        else:
            type_to_check = field.type
        field_name = field.name
        if is_scalar(type_to_check):
            args.append(field_name)
        elif is_list(type_to_check) or is_object(type_to_check) or is_non_null(type_to_check):
            sub_type = find_defer_name_recursively(type_to_check)
            sub_fields = __recursively_find_selection_fields(sub_type, all_types, curr_depth=curr_depth + 1)
            if sub_fields is not None:
                kwargs[field_name] = sub_fields

    from graphy import builder
    return_fields = builder.fields(*args, **kwargs)
    if return_fields is None or len(return_fields) == 0:
        return None
    return return_fields
