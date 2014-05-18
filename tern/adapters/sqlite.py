from __future__ import absolute_import
import sqlite3

from ..exceptions import NotInitialized
from .adapterbase import AdapterBase


class SQLiteAdapter(AdapterBase):
    def __init__(self, host, dbname, username, password, tern_table='tern'):
        if dbname is not None:
            raise ValueError('``dbname`` is not supported.')
        if username is not None:
            raise ValueError('``username`` is not supported.')
        if password is not None:
            raise ValueError('``password`` is not supported.')
        self.host = host
        self.tablename = tern_table

    def __enter__(self):
        self.conn = sqlite3.connect(self.host)

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def initialize_tern(self):
        c = self.conn.cursor()
        c.execute(
            """
            create table {} (
                hash text primary key,
                created_at integer not null,
                setup text not null,
                teardown text not null,
                "order" integer not null
            )
            """.format(self.tablename))
        self.conn.commit()

    def verify_tern(self):
        c = self.conn.cursor()
        c.execute(
            """
            select count(*)
            from sqlite_master
            where type = 'table' and name = '{}'
            """.format(self.tablename))
        if c.fetchone()[0] == 0:
            raise NotInitialized()

    def apply(self, changeset):
        pass

    def revert(self, changeset):
        pass

    def test(self, changeset):
        pass

    def get_applied(self):
        pass
