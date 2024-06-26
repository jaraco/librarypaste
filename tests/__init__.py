import abc
import datetime

from importlib_resources import files


class DataStoreTest:
    common_content = dict(
        nick='nick',
        time=datetime.datetime.now().replace(
            # some tests fail at the microsecond precision (jsonstore)
            microsecond=0,
        ),
        makeshort=True,
    )
    code_content = common_content.copy()
    file_content = common_content.copy()
    code = files('librarypaste').joinpath('pastebin.py').read_text(encoding='utf-8')
    code_content.update(
        type='code',
        fmt='python',
        code=code,
    )
    file_content.update(
        type='file',
        mime='image/png',
        filename='librarypaste.png',
        data=files('librarypaste').joinpath('static/librarypaste.png').read_bytes(),
    )

    @abc.abstractproperty
    def datastore(self):
        """
        The datastore instance under test
        """

    def test__store_code(self):
        uid = 'some-id'
        res = self.datastore._store(uid, self.code_content)
        assert res is None

    def test__store_file(self):
        uid = 'file-id'
        file_content = self.file_content.copy()
        data = file_content.pop('data')
        res = self.datastore._store(uid, file_content, data)
        assert res is None

    def test__retrieve_file(self):
        uid = 'file-id'
        expected_content = self.file_content.copy()
        res = self.datastore._retrieve(uid)
        for key in list(res):
            if key not in expected_content:
                del res[key]
        assert res == expected_content
