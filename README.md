# Graphy: Python GraphQL Client

A fast and modern graphql client library designed with simplicity in mind.

## Getting Started

You can download it from https://pypi.org/

### Installing

```shell script
pip install python-graphy
```

### Usage

```python
from requests import Response

from graphy import Client, fields

client = Client("https://countries.trevorblades.com/")

response: Response = client.query.country(select=fields("name", "capital"), where={"code": "CH"})
```

## Authors

* **Daniel Seifert** - *Initial work* - [Lab9](https://github.com/Lab9)

## Acknowledgments

* Heavily inspired by [Zeep](https://github.com/mvantellingen/python-zeep)