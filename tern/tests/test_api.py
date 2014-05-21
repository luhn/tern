from __future__ import absolute_import

import shutil
import random
import string
import os
import os.path

from nose.tools import eq_

from ..adapters.mock import MockAdapter
from ..api import Tern
from ..changeset import Changeset


class TestAPI(object):
    def setup(self):
        self.adapter = MockAdapter(None, None, None, None)

        # Create a directory to test in.
        # Taken from http://stackoverflow.com/a/2782859/600247
        randstr = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(16)
        )
        self.directory = '.terntest-{}'.format(randstr)
        os.mkdir(self.directory)
        self.tern = Tern(self.adapter, self.directory)

    def teardown(self):
        shutil.rmtree(self.directory)

    def _save_changesets(self, changesets):
        for changeset in changesets:
            fn = os.path.join(self.directory, changeset.hex_hash)
            changeset.save(fn)

    def test_apply(self):
        changeset = Changeset(
            setup='foo',
            teardown='bar',
        )
        self.tern.apply(changeset)
        assert changeset.order is not None

        fn = os.path.join(self.directory, changeset.hex_hash)
        loaded = Changeset.from_file(fn)
        assert loaded == changeset

    def test_diff(self):
        foo = Changeset(
            setup='create foo',
            teardown='drop foo',
            order=1,
        )
        bar = Changeset(
            setup='create bar',
            teardown='drop baz',
            order=2,
        )
        bar2 = Changeset(
            setup='create bar2',
            teardown='drop bar2',
            order=3,
        )
        baz = Changeset(
            setup='create baz',
            teardown='drop baz',
            order=2,
        )
        baz2 = Changeset(
            setup='create baz2',
            teardown='drop baz2',
            order=3,
        )
        self.adapter.applied = [foo, baz, baz2]
        self._save_changesets([foo, bar, bar2])

        teardown, apply = self.tern.diff()
        eq_(teardown, [baz2, baz])
        eq_(apply, [bar, bar2])
