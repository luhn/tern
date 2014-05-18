import os
import os.path
from nose import with_setup
from nose.tools import eq_
from tern.changeset import Changeset


dir = os.path.dirname(__file__)
changeset_save_fn = os.path.join(dir, 'data/test_save')


def test_changeset_from_file():
    fn = os.path.join(dir, 'data/changeset')
    changeset = Changeset.from_file(fn)

    eq_(changeset.order, 12)
    eq_(changeset.setup.strip(), 'create table foo(id primary key);')
    eq_(changeset.teardown.strip(), 'drop table foo;')


def test_changeset_hash():
    changeset = Changeset(12, 'abc', 'cba')
    eq_(
        changeset.hash,
        '\xc8\x13B\x94#9\xfbE\xa6c>\x8bvy\xc1\x19\xfc\xa3\x84\xac',
    )
    eq_(
        changeset.hex_hash,
        'c81342942339fb45a6633e8b7679c119fca384ac',
    )


def save_teardown():
    if os.path.exists(changeset_save_fn):
        os.remove(changeset_save_fn)


@with_setup(lambda: None, save_teardown)
def test_changeset_save():
    # Save a changeset
    changeset = Changeset(24, 'foo', 'bar')
    changeset.save(changeset_save_fn)

    # Load it, and verify integrity.
    changeset.from_file(changeset_save_fn)
    eq_(changeset.order, 24)
    eq_(changeset.setup, 'foo')
    eq_(changeset.teardown, 'bar')
