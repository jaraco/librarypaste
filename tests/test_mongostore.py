import pytest

from librarypaste import mongostore

from . import DataStoreTest


@pytest.fixture(scope='class', autouse=True)
def database(request, mongodb_uri):
    mongodb_uri += '/librarypaste-test'
    request.cls.datastore = mongostore.MongoDBDataStore.from_uri(mongodb_uri)


class TestMongoDBDataStore(DataStoreTest):
    pass
