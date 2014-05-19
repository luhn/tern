from __future__ import absolute_import
import os.path


class Tern(object):
    """
    The Tern API.

    :param adapter:  The adapter for Tern to interact with the database.
    :type adapter:  Object implementing ``tern.adapters.AdapterBase``.
    :param directory:  The directory storing the tern objects.
    :type directory:  str

    """

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
