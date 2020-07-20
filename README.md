# Graphy: Python GraphQL Client

A fast and modern graphql client library designed with simplicity in mind.

NOTE: THIS PACKAGE IS STILL UNDER DEVELOPMENT.

## Getting Started

### Installing

```shell script
pip install python-graphy
```

### Usage
This example shows a simple query
```python
from requests import Response

from graphy import Client

client = Client("https://graphql-pokemon.now.sh/")

response: Response = client.query.pokemon(select=["id", "name"], where={"name": "Pikachu"})
```

## Documentation
The Documentation covers the following points:
* [Custom Session](#custom-session)
* [Query](#query)
* [Mutation](#mutation)
* [Subscription](#subscription)

### Custom Session
Sometimes you want your own custom session to be used for making requests.
For example if you need to authenticate yourself with some sort of an api key.
Therefor, you can pass it directly to the client.

```python
import requests

from graphy import Client

my_session = requests.sessions.session()

my_session.headers["Authorization"] = "Bearer some-api-token"

client = Client("https://foo.bar/", session=my_session)
```

### Query
Queries are the A and O of graphql and are as easy as:
```python
from graphy import Client

client = Client("https://graphql-pokemon.now.sh/")

response = client.query.pokemons(select=["id", "name"], where={"first": 10})
```
Which will make a request to the server and return the id and name of the first 10 pokemons found in the pokedex.

But what if you want to make a more complex query with fields within fields?
Don't need to worry, we got you covered:
```python
from graphy import Client, fields

client = Client("https://graphql-pokemon.now.sh/")

response = client.query.pokemons(
    select=fields("id", "name", evolutions=fields("id", "name")), 
    where={"first": 10}
)
```
Using the fields method from `graphy` you can simply use `*args` and `**kwargs` for making deeper selections.
By the way, you could stack this like forever.

### Mutation
I haven't found an real world example for making mutations without being authenticated,
so here's a hypothetical one.
```python
from graphy import Client

client = Client("https://some-host.com/authentication")

response = client.mutation.register(data={"email": "foo@bar.com", "password": "987654321"})
```
Mind that the select keyword is optional in mutations but can still be passed by.

### Subscription
Subscriptions are not yet available

## Authors

* **Daniel Seifert** - *Initial work* - [Lab9](https://github.com/Lab9)

## Acknowledgments

* Heavily inspired by [Zeep](https://github.com/mvantellingen/python-zeep)