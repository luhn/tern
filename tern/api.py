from __future__ import absolute_import
import os
import os.path
import re

from .changeset import Changeset


class Tern(object):
    """
    The Tern API.

    :param adapter:  The adapter for Tern to interact with the database.
    :type adapter:  Object implementing ``tern.adapters.AdapterBase``.
    :param directory:  The directory storing the tern objects.
    :type directory:  str

    """

    _changeset_file_re = re.compile(r'^[0-9a-f]{40}$')

    def __init__(self, adapter, directory):
        self.adapter = adapter
        self.directory = directory
        # Make sure everything has been set up.
        self.adapter.verify_tern()

    def apply(self, changeset):
        """
        Apply the given changeset to the database and save it to the
        filesystem.

        """
        with self.adapter:
            self.adapter.apply(changeset)
            fn = os.path.join(self.directory, changeset.hex_hash)
            changeset.save(fn)

    def _get_saved_changesets(self):
        """
        Get a set of the changesets saved to the local filesystem.

        """
        changesets = set()
        for fn in os.listdir(self.directory):
            path = os.path.join(self.directory, fn)
            if not os.path.isfile(path):
                continue
            if not self._changeset_file_re.match(fn):
                continue
            changesets.add(Changeset.from_file(path))
        return changesets

    def diff(self):
        """
        Find out how the current state of the database differs from the state
        defined in the tern directory.

        :returns:  A 2-element tuple:  The first element is a list of
        changesets that need to be torn down, the second a list of changesets
        that need to be applied.  Both lists are correctly ordered, so the
        changesets can be applied/torn down in sequence.

        """
        applied = self.adapter.get_applied()
        saved = self._get_saved_changesets()
        to_teardown = sorted(
            (x for x in applied if x not in saved),
            key=lambda x: x.order,
            reverse=True,
        )
        to_apply = sorted(
            (x for x in saved if x not in applied),
            key=lambda x: x.order,
        )
        return to_teardown, to_apply
