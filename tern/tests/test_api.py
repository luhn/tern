from __future__ import absolute_import

import shutil
import random
import string
import os
import os.path

from ..adapters.mock import MockAdapter
from ..api import Tern
from ..changeset import Changeset


class TestAPI(object):
    def setup(self):
        self.adapter = MockAdapter(None, None, None, None)

        # Create a directory to test in.
        # Taken from http://stackoverflow.com/a/2782859/600247
        randstr = ''.join(random.choice(string.lowercase) for _ in range(16))
        self.directory = '.terntest-{}'.format(randstr)
        os.mkdir(self.directory)
        self.tern = Tern(self.adapter, self.directory)

    def teardown(self):
        shutil.rmtree(self.directory)

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
