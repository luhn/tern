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

    eq_(changeset.created_at, 123123)
    eq_(changeset.order, 12)
    eq_(changeset.setup.strip(), 'create table foo(id primary key);')
    eq_(changeset.teardown.strip(), 'drop table foo;')


def test_changeset_hash():
    changeset = Changeset('abc', 'cba', 12, 123123)
    eq_(
        changeset.hash,
        b'\xa2\x90\xfa\x0473E\xfc@\xb5\xd9\x89_;\xfb!\xf7\xedN\xf7',
    )
    eq_(
        changeset.hex_hash,
        'a290fa04373345fc40b5d9895f3bfb21f7ed4ef7',
    )


def save_teardown():
    if os.path.exists(changeset_save_fn):
        os.remove(changeset_save_fn)


@with_setup(lambda: None, save_teardown)
def test_changeset_save():
    # Save a changeset
    changeset = Changeset('foo', 'bar', 24)
    changeset.save(changeset_save_fn)

    # Load it, and verify integrity.
    loaded = Changeset.from_file(changeset_save_fn)
    eq_(loaded.created_at, changeset.created_at)
    eq_(loaded.order, 24)
    eq_(loaded.setup, 'foo')
    eq_(loaded.teardown, 'bar')
