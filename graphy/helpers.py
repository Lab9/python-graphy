from typing import Dict, List


def parse_queries(raw_schema: Dict) -> List[str]:
    types = raw_schema.get("types", [])
    query_type = next(filter(lambda t: t.get("name", "") == "Query", types), {})
    return [field.get("name", "") for field in query_type.get("fields", []) if field]


def parse_mutations(raw_schema: Dict) -> List[str]:
    types = raw_schema.get("types", [])
    query_type = next(filter(lambda t: t.get("name", "") == "Mutation", types), {})
    return [field.get("name", "") for field in query_type.get("fields", []) if field]


def parse_types(raw_schema: Dict) -> List[str]:
    types = raw_schema.get("types", [])
    return []


def remove_duplicate_spaces(query: str) -> str:
    return " ".join(query.split())
