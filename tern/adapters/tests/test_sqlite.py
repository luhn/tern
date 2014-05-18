from __future__ import absolute_import
from ..sqlite import SQLiteAdapter


def test_sqlite_initialize():
    adapter = SQLiteAdapter(
        host=':memory:',
        dbname=None,
        username=None,
        password=None,
    )
    with adapter:
        adapter.initialize_tern()
        adapter.verify_tern()
