import os
import os.path
from unittest import TestCase
from tern.changeset import Changeset


class ChangesetTests(TestCase):
    def test_changeset_from_file(self):
        dir = os.path.dirname(__file__)
        fn = os.path.join(dir, 'data/changeset')
        changeset = Changeset.from_file(fn)

        self.assertEquals(changeset.order, 12)
        self.assertEquals(changeset.setup.strip(),
                          'create table foo(id primary key);')
        self.assertEquals(changeset.teardown.strip(),
                          'drop table foo;')

    def test_changeset_hash(self):
        changeset = Changeset(12, 'abc', 'cba')
        self.assertEquals(
            changeset.hash,
            '\xc8\x13B\x94#9\xfbE\xa6c>\x8bvy\xc1\x19\xfc\xa3\x84\xac',
        )
        self.assertEquals(
            changeset.hex_hash,
            'c81342942339fb45a6633e8b7679c119fca384ac',
        )

    def test_changeset_save(self):
        dir = os.path.dirname(__file__)
        fn = os.path.join(dir, 'data/test_save')

        try:
            # Save a changeset
            changeset = Changeset(24, 'foo', 'bar')
            changeset.save(fn)

            # Load it, and verify integrity.
            changeset.from_file(fn)
            self.assertEquals(changeset.order, 24)
            self.assertEquals(changeset.setup, 'foo')
            self.assertEquals(changeset.teardown, 'bar')
        finally:
            if os.path.exists(fn):
                os.remove(fn)
