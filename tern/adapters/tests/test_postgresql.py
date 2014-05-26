from __future__ import absolute_import
from nose.tools import eq_
from testconfig import config
import psycopg2

from ..postgresql import PostgreSQLAdapter
from ...exceptions import NotInitialized
from ...changeset import Changeset


class TestPostgreSQLAdapter(object):
    def setup(self):
        self.adapter = PostgreSQLAdapter(
            host=config['database'].get('host') or None,
            dbname=config['database'].get('dbname') or None,
            username=config['database'].get('username') or None,
            password=config['database'].get('password') or None,
        )
        self.adapter.open()
        self.adapter.initialize_tern()

    def teardown(self):
        self._rollback()
        with self._cursor() as c:
            try:
                c.execute(
                    """
                    drop table tern;
                    """)
                self._commit()
            except psycopg2.Error:
                self._rollback()

        # Drop other tables that may have been created.
        with self._cursor() as c:
            try:
                c.execute(
                    """
                    drop table foo;
                    """
                )
                self._commit()
            except psycopg2.Error:
                self._rollback()

        self.adapter.close()

    def _cursor(self):
        return self.adapter.conn.cursor()

    def _commit(self):
        self.adapter.conn.commit()

    def _rollback(self):
        self.adapter.conn.rollback()

    def test_postgresql_verify(self):
        self.adapter.verify_tern()

        # Delete tern table, and try again.
        with self._cursor() as c:
            c.execute(
                """
                drop table tern;
                """)
            self._commit()
        try:
            self.adapter.verify_tern()
            raise AssertionError('Verify did not throw exception.')
        except NotInitialized:
            pass

    def test_postgresql_apply(self):
        """
        Test ``PostgreSQLAdapter.apply``.

        """
        changeset = Changeset(
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
            order=1,
            created_at=123,
        )
        self.adapter.apply(changeset)

        with self._cursor() as c:
            c.execute(
                """
                select created_at, setup, teardown, "order"
                from tern
                where hash = %s
                """, (changeset.hex_hash,))
            data = c.fetchall()
            eq_(len(data), 1)
            row = data[0]
            eq_(row[0], changeset.created_at)
            eq_(row[1], changeset.setup)
            eq_(row[2], changeset.teardown)
            eq_(row[3], changeset.order)

        with self._cursor() as c:
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

    def test_postgresql_apply_no_order(self):
        """
        Test ``PostgreSQLAdapter.apply`` with a changeset with no order
        defined.  An order should be assigned.

        """
        self.adapter._save_changeset(Changeset(
            '', '', 3,
        ))
        changeset = Changeset(
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
            order=None,
            created_at=123,
        )
        self.adapter.apply(changeset)
        eq_(changeset.order, 4)

        with self._cursor() as c:
            c.execute(
                """
                select "order"
                from tern
                where hash = %s
                """, (changeset.hex_hash,))
            eq_(c.fetchone()[0], 4)

    def test_postgresql_revert(self):
        """
        Test ``PostgreSQLAdapter.revert``.

        """
        with self.adapter.conn:
            with self._cursor() as c:
                c.execute(
                    """
                    create table foo(id integer primary key)
                    """)
                c.execute(
                    """
                    insert into foo values (1), (2), (3)
                    """)

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

        with self._cursor() as c:
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

    def test_postgresql_test(self):
        """
        Test ``PostgreSQLAdapter.test``.

        """
        # Error in setup
        changeset = Changeset(
            order=1,
            setup='create table asdf;',
            teardown='drop table faux;',
            created_at=123,
        )
        try:
            self.adapter.test(changeset)
            raise AssertionError('No error was thrown.')
        except psycopg2.Error:
            pass

        # Error in teardown
        changeset = Changeset(
            order=1,
            setup='create table foo(id integer primary key);',
            teardown='drop table faux;',
            created_at=123,
        )
        try:
            self.adapter.test(changeset)
            raise AssertionError('No error was thrown.')
        except psycopg2.Error:
            pass

        # No error.
        # This also verifies that the previous transactions were rolled back.
        changeset = Changeset(
            order=1,
            setup='create table foo(id integer primary key);',
            teardown='drop table foo;',
            created_at=123,
        )
        self.adapter.test(changeset)

    def test_get_applied(self):
        cs1 = Changeset(
            order=1,
            setup='sqlsql',
            teardown='pizzapizza',
            created_at=123,
        )
        cs2 = Changeset(
            order=2,
            setup='wowsql',
            teardown='suchsql',
            created_at=124,
        )
        self.adapter._save_changeset(cs1)
        self.adapter._save_changeset(cs2)

        applied = self.adapter.get_applied()
        eq_(len(applied), 2)
        assert cs1 in applied
        assert cs2 in applied
