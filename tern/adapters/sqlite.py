from __future__ import absolute_import
from contextlib import closing
import sqlite3

from ..exceptions import NotInitialized
from .adapterbase import AdapterBase


class SQLiteAdapter(AdapterBase):
    """
    This allows Tern to work on SQLite databases.  This is the reference
    implementation for AdapterBase.

    Why is this the reference implement?  Although SQLite is rarely used in
    production (for good reason), it's ideal for fast development and testing
    and yields clean, readable code.

    Many methods are undocumented because they're already documented in
    AdapterBase.

    """

    def __init__(self, host, dbname, username, password, tern_table='tern'):
        if dbname is not None:
            raise ValueError('``dbname`` is not supported.')
        if username is not None:
            raise ValueError('``username`` is not supported.')
        if password is not None:
            raise ValueError('``password`` is not supported.')
        self.host = host
        self.tablename = tern_table

    def open(self):
        self.conn = sqlite3.connect(self.host)

    def close(self):
        self.conn.close()

    def _cursor(self):
        """
        Return a cursor which can be used with ``with``.

        """
        return closing(self.conn.cursor())

    def _changeset_exists(self, changeset):
        """
        Return ``True`` if the changeset already is saved in the Tern table.

        """
        with self._cursor() as c:
            c.execute(
                """
                select count(*)
                from {0}
                where hash = ?
                """.format(self.tablename),
                (changeset.hex_hash,)
            )
            return c.fetchone()[0] > 0

    def _save_changeset(self, changeset):
        """
        Save changeset in the tern table.  Does not commit the change.

        """
        if self._changeset_exists(changeset):
            return ValueError('Changeset already exists in database.')
        with self._cursor() as c:
            c.execute(
                """
                insert into {0}(hash, created_at, setup, teardown,
                    "order")
                values (?, ?, ?, ?, ?)
                """.format(self.tablename),
                (
                    changeset.hex_hash, changeset.created_at,
                    changeset.setup, changeset.teardown, changeset.order
                )
            )

    def _delete_changeset(self, changeset):
        """
        Delete changeset in the tern table.  Does not commit the change.

        """
        if not self._changeset_exists(changeset):
            raise ValueError('Changeset does not exist in database.')
        with self._cursor() as c:
            c.execute(
                """
                delete from {0} where hash = ?
                """.format(self.tablename),
                (changeset.hex_hash,)
            )

    def initialize_tern(self):
        with self.conn:
            with self._cursor() as c:
                c.execute(
                    """
                    create table {0} (
                        hash text primary key,
                        created_at integer not null,
                        setup text not null,
                        teardown text not null,
                        "order" integer not null
                    )
                    """.format(self.tablename))

    def verify_tern(self):
        with self._cursor() as c:
            c.execute(
                """
                select count(*)
                from sqlite_master
                where type = 'table' and name = '{0}'
                """.format(self.tablename))
            if c.fetchone()[0] == 0:
                raise NotInitialized()

    def apply(self, changeset):
        if self._changeset_exists(changeset):
            raise ValueError('Changeset has already been applied.')

        if changeset.order is None:
            with self._cursor() as c:
                c.execute(
                    """
                    select max("order")
                    from {0}
                    """.format(self.tablename))
                order = c.fetchone()[0]
                if order is None:
                    order = 1
                else:
                    order += 1
                changeset.order = order

        with self.conn:
            with self._cursor() as c:
                c.executescript(changeset.setup)
            self._save_changeset(changeset)

    def revert(self, changeset):
        if not self._changeset_exists(changeset):
            raise ValueError('Changeset has not yet been applied.')

        with self.conn:
            with self._cursor() as c:
                c.executescript(changeset.teardown)
            self._delete_changeset(changeset)

    def test(self, changeset):
        pass

    def get_applied(self):
        pass
