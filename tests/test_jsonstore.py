import os
import shutil

from librarypaste import jsonstore

from . import DataStoreTest


class TestJSONStore(DataStoreTest):
    @classmethod
    def setup_class(cls):
        cls.datastore = jsonstore.JsonDataStore('test-repo')

    @classmethod
    def teardown_class(cls):
        if os.path.isdir(cls.datastore.repo):
            shutil.rmtree(cls.datastore.repo)
