from __future__ import absolute_import
from nose.tools import eq_

from ..sqlite import SQLiteAdapter
from ...exceptions import NotInitialized
from ...changeset import Changeset


def test_sqlite_initialize():
    adapter = SQLiteAdapter(
        host=':memory:',
        dbname=None,
        username=None,
        password=None,
    )
    with adapter:
        try:
            adapter.verify_tern()
            raise AssertionError('Verify did not throw exception.')
        except NotInitialized:
            pass

        adapter.initialize_tern()
        adapter.verify_tern()


class TestSQLiteAdapter(object):
    def setup(self):
        self.adapter = SQLiteAdapter(
            host=':memory:',
            dbname=None,
            username=None,
            password=None,
        )
        self.adapter.open()
        self.adapter.initialize_tern()

    def teardown(self):
        self.adapter.close()

    def test_sqlite_apply(self):
        """
        Test ``SQLiteAdapter.apply``.

        """
        changeset = Changeset(
            order=1,
            setup=(
                """
                create table foo(id integer primary key);
                insert into foo values (1);
                insert into foo values (2);
                insert into foo values (3);
                """
            ),
            teardown=(
                """
                delete from foo;
                drop table foo;
                """
            ),
            created_at=123,
        )
        self.adapter.apply(changeset)

        with self.adapter._cursor() as c:
            c.execute(
                """
                select created_at, setup, teardown, "order"
                from tern
                where hash = ?
                """, (changeset.hex_hash,))
            data = c.fetchall()
            eq_(len(data), 1)
            row = data[0]
            eq_(row[0], changeset.created_at)
            eq_(row[1], changeset.setup)
            eq_(row[2], changeset.teardown)
            eq_(row[3], changeset.order)

        with self.adapter._cursor() as c:
            c.execute(
                """
                select id from foo
                order by id
                """)
            data = c.fetchall()
            eq_(len(data), 3)
            eq_(data[0][0], 1)
            eq_(data[1][0], 2)
            eq_(data[2][0], 3)

    def test_sqlite_apply_no_order(self):
        """
        Test ``SQLiteAdapter.apply`` with a changeset with no order defined.
        An order should be assigned.

        """
        self.adapter._save_changeset(Changeset(
            3, '', '', 0,
        ))
        changeset = Changeset(
            order=None,
            setup=(
                """
                create table foo(id integer primary key);
                insert into foo values (1);
                insert into foo values (2);
                insert into foo values (3);
                """
            ),
            teardown=(
                """
                delete from foo;
                drop table foo;
                """
            ),
            created_at=123,
        )
        self.adapter.apply(changeset)
        eq_(changeset.order, 4)

        with self.adapter._cursor() as c:
            c.execute(
                """
                select "order"
                from tern
                where hash = ?
                """, (changeset.hex_hash,))
            eq_(c.fetchone()[0], 4)

    def test_sqlite_revert(self):
        """
        Test ``SQLiteAdapter.revert``.

        """
        with self.adapter.conn:
            with self.adapter._cursor() as c:
                c.execute(
                    """
                    create table foo(id integer primary key)
                    """)
                c.executemany(
                    """
                    insert into foo values (?)
                    """, [(1,), (2,), (3,)])

        changeset = Changeset(
            order=1,
            setup='badsql',
            teardown=(
                """
                delete from foo where id = 1;
                delete from foo where id = 3;
                """
            ),
            created_at=123,
        )
        self.adapter._save_changeset(changeset)
        self.adapter.conn.commit()

        self.adapter.revert(changeset)

        with self.adapter._cursor() as c:
            c.execute(
                """
                select id
                from foo
                order by id
                """)
            results = c.fetchall()
            eq_(len(results), 1)
            eq_(results[0][0], 2)

        assert self.adapter._changeset_exists(changeset) is False
