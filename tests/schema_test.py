import unittest

from graphy import Client


class SchemaTest(unittest.TestCase):
    def test_something(self):
        client = Client("http://localhost:8080")
        self.assertIsInstance(client.schema.raw, dict)


if __name__ == '__main__':
    unittest.main()
