from typing import Dict, List


class Schema:
    def __init__(self, raw: Dict):
        from graphy import helpers
        # graphql schema properties
        self.raw_schema = raw.get("data", {}).get("__schema", {})
        self.query_type: str = helpers.parse_query_type(self.raw_schema)
        self.mutation_type: str = helpers.parse_mutation_type(self.raw_schema)
        self.subscription_type: str = helpers.parse_subscription_type(self.raw_schema)
        self.types: Dict[str, Type] = helpers.parse_types(self.raw_schema.get("types", []))
        self.directives: Dict[str, Directive] = helpers.parse_directives(self.raw_schema.get("directives", []))

        # custom schema properties
        self.queries: List[Operation] = helpers.parse_operations(self.types, self.query_type)
        self.mutations: List[Operation] = helpers.parse_operations(self.types, self.mutation_type)
        self.subscriptions: List[Operation] = helpers.parse_operations(self.types, self.subscription_type)


class Operation:
    def __init__(self, field: "TypeField"):
        from graphy import helpers
        self.name = field.name
        self.description = field.description
        self.arguments = helpers.adapt_arguments(field.args)
        self.return_type = field.type


class Directive:
    def __init__(self, raw_directive: Dict):
        from graphy import helpers
        self.name: str = raw_directive.get("name")
        self.description: str = raw_directive.get("description")
        self.locations: List[str] = raw_directive.get("locations", [])
        self.args: Dict[str, Argument] = helpers.parse_arguments(raw_directive.get("args", []))


class Argument:
    def __init__(self, raw_argument: Dict):
        self.name = raw_argument.get("name")
        self.description = raw_argument.get("description")
        self.type = TypeDefer(raw_argument.get("type")) if raw_argument.get("type") is not None else None
        self.default_value = raw_argument.get("defaultValue")


class TypeDefer:
    def __init__(self, raw_defer: Dict):
        self.kind = raw_defer.get("kind")
        self.name = raw_defer.get("name")
        self.of_type: 'TypeDefer' = TypeDefer(raw_defer.get("ofType")) if raw_defer.get("ofType") is not None else None


class Type:
    def __init__(self, raw_type: Dict):
        self.kind = raw_type.get("kind")
        self.name = raw_type.get("name")
        self.description = raw_type.get("description")
        self.fields: List[TypeField] = [TypeField(f) for f in raw_type.get("fields", []) or [] if f]
        self.input_fields = [InputField(f) for f in raw_type.get("inputFields", []) or [] if f]
        self.interfaces = raw_type.get("interfaces")
        self.enum_values = raw_type.get("enumValues")
        self.possible_types = raw_type.get("possibleTypes")


class TypeField:
    def __init__(self, raw_field: Dict):
        from graphy import helpers
        self.name = raw_field.get("name")
        self.description = raw_field.get("description")
        self.args: Dict[str, Argument] = helpers.parse_arguments(raw_field.get("args", []))
        self.type: TypeDefer = TypeDefer(raw_field.get("type")) if raw_field.get("type") is not None else None
        self.is_deprecated: bool = raw_field.get("isDeprecated")
        self.deprecation_reason: str = raw_field.get("deprecationReason")


class InputField:
    def __init__(self, raw_input: Dict):
        self.name = raw_input.get("name")
        self.description = raw_input.get("description")
        self.type: TypeDefer = TypeDefer(raw_input.get("type")) if raw_input.get("type") is not None else None
        self.default_value = raw_input.get("defaultValue")


class SelectionField:
    def __init__(self, name: str, children: List = None):
        self.name: str = name
        self.children: List = children

    def __str__(self):
        result = self.name
        if self.children:
            result += " { " + " ".join([str(c) for c in self.children]) + " } "
        return result
