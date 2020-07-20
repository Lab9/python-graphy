from typing import Dict, Union, List, Tuple

from graphy.schema import SelectionField


class GraphQLQueryBuilder:
    def __init__(self):
        self.object: str = ""
        self.return_field: str = ""
        self.query_field: str = ""
        self.operation_field: str = ""
        self.fragment_field: str = ""

    def fields(self, selection: Tuple[SelectionField]):
        if selection is None or len(selection) == 0:
            self.return_field = ""
            return self

        self.return_field = "{ " + " ".join([str(s) for s in selection if s]) + " }"
        return self

    def query(self, name: str, alias: str = '', params: Dict[str, Union[str, int]] = None):
        if params is None:
            params = {}
        self.query_field = name
        inputs: List[str] = []
        if params != {}:
            for key, value in params.items():
                inputs.append(f'{key}: {value}')
            self.query_field = self.query_field + ' (' + ", ".join(inputs) + ') '
        if alias != '':
            self.query_field = f'{alias}: {self.query_field}'

        return self

    def operation(self, query_type: str = 'query', name: str = '',
                  params: Dict[str, Union[str, int]] = None,
                  queries: List[str] = None):
        if params is None:
            params = {}

        if queries is None:
            queries = []
        self.operation_field = query_type
        inputs: List[str] = []
        if name != '':
            self.operation_field = f'{self.operation_field} {name}'
            if params != {}:
                for key, value in params.items():
                    inputs.append(f'{key}: {value}')
                self.operation_field = self.operation_field + ' (' + ", ".join(inputs) + ') '

        if len(queries) != 0:
            self.object = self.operation_field + ' { ' + " ".join(queries) + ' }'

        return self

    def fragment(self, name: str, interface: str):
        self.fragment_field = f'fragment {name} on {interface}'
        return self

    def generate(self) -> str:
        from graphy import helpers
        if self.fragment_field != '':
            self.object = f'{self.fragment_field} {self.return_field}'
        else:
            if self.object == '' and self.operation_field == '' and self.query_field == '':
                self.object = self.return_field
            elif self.object == '' and self.operation_field == '':
                self.object = self.query_field + ' ' + self.return_field
            elif self.object == '':
                self.object = self.operation_field + ' { ' + self.query_field + ' ' + self.return_field + ' }'

        return helpers.remove_duplicate_spaces(self.object)


def map_value(value: Union[str, int, float, bool]) -> str:
    if isinstance(value, str):
        return '"' + value + '"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return str(value)


def fields(*args, **kwargs) -> Tuple[SelectionField]:
    result = []
    for arg in args:
        result.append(SelectionField(str(arg)))
    for key, value in kwargs.items():
        result.append(
            SelectionField(
                key,
                children=[v if isinstance(v, SelectionField) else SelectionField(str(v)) for v in value if v]
            )
        )
    return tuple(result)
