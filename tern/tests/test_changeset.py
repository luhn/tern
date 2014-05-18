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
    changeset = Changeset(12, 'abc', 'cba', 123123)
    eq_(
        changeset.hash,
        b'N\xe6\x94\xde\xe3\x10%\x1c[\xfe\x02\x02\xd3\x14\xc7Q\xaez\xccZ',
    )
    eq_(
        changeset.hex_hash,
        '4ee694dee310251c5bfe0202d314c751ae7acc5a',
    )


def save_teardown():
    if os.path.exists(changeset_save_fn):
        os.remove(changeset_save_fn)


@with_setup(lambda: None, save_teardown)
def test_changeset_save():
    # Save a changeset
    changeset = Changeset(24, 'foo', 'bar', 123321)
    changeset.save(changeset_save_fn)

    # Load it, and verify integrity.
    changeset.from_file(changeset_save_fn)
    eq_(changeset.created_at, 123321)
    eq_(changeset.order, 24)
    eq_(changeset.setup, 'foo')
    eq_(changeset.teardown, 'bar')
