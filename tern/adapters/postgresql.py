from __future__ import absolute_import
try:
    import psycopg2
except ImportError:
    raise ImportError(
        'You must have psycopg2 installed to use the Postgres adapter.'
    )

from ..exceptions import NotInitialized
from .adapterbase import AdapterBase
from ..changeset import Changeset


class PostgreSQLAdapter(AdapterBase):
    """
    A PostgreSQL adapter for Tern.

    This adapter is the reference implementation, because of the open-source
    RDBMSs, Postgres offers the fullest feature set.

    Many methods are undocumented because they're already documented in
    AdapterBase.

    """

    def __init__(
        self, host, dbname, username, password, port=None, tern_table='tern'
    ):
        self.host = host or None
        self.port = port or None
        self.dbname = dbname or None
        self.username = username or None
        self.password = password or None
        self.tablename = tern_table

    def open(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.dbname,
            user=self.username,
            password=self.password,
        )

    def close(self):
        self.conn.close()

    def _changeset_exists(self, changeset):
        """
        Return ``True`` if the changeset already is saved in the Tern table.

        """
        with self.conn.cursor() as c:
            c.execute(
                """
                select count(*)
                from {0}
                where hash = %s
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
        with self.conn.cursor() as c:
            c.execute(
                """
                insert into {0}(hash, created_at, setup, teardown,
                    "order")
                values (%s, %s, %s, %s, %s)
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
        with self.conn.cursor() as c:
            c.execute(
                """
                delete from {0} where hash = %s
                """.format(self.tablename),
                (changeset.hex_hash,)
            )

    def initialize_tern(self):
        with self.conn:
            with self.conn.cursor() as c:
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
        with self.conn.cursor() as c:
            c.execute(
                """
                SELECT EXISTS(
                    SELECT *
                    FROM information_schema.tables
                    WHERE table_name = '{0}'
                );
                """.format(self.tablename))
            if c.fetchone()[0] == 0:
                raise NotInitialized()

    def apply(self, changeset):
        if self._changeset_exists(changeset):
            raise ValueError('Changeset has already been applied.')

        if changeset.order is None:
            with self.conn.cursor() as c:
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
            try:
                with self.conn.cursor() as c:
                    c.execute(changeset.setup)
                self._save_changeset(changeset)
            except psycopg2.ProgrammingError:
                print('An error occurred while applying {}'.format(
                    changeset.hex_hash
                ))
                print()
                print(changeset.setup)
                print()
                raise

    def revert(self, changeset):
        if not self._changeset_exists(changeset):
            raise ValueError('Changeset has not yet been applied.')

        with self.conn:
            if changeset.teardown:
                with self.conn.cursor() as c:
                    c.execute(changeset.teardown)
            self._delete_changeset(changeset)

    def test(self, changeset):
        try:
            with self.conn.cursor() as c:
                c.execute(changeset.setup)
                if changeset.teardown:
                    c.execute(changeset.teardown)
        finally:
            self.conn.rollback()

    def get_applied(self):
        applied = list()
        with self.conn.cursor() as c:
            c.execute(
                """
                select setup, teardown, "order", created_at
                from {0}
                """.format(self.tablename))
            for row in c:
                applied.append(Changeset(
                    setup=row[0],
                    teardown=row[1],
                    order=row[2],
                    created_at=row[3],
                ))
        return applied
