from __future__ import absolute_import

from .adapterbase import AdapterBase


class MockAdapter(AdapterBase):
    """
    This is a mock adapter; it has no functionality and is intended for testing
    only.

    """

    def __init__(self, host, dbname, username, password, tern_table='tern'):
        self.applied = list()
        self._open = False

    def open(self):
        self._open = True

    def close(self):
        self._open = False

    def initialize_tern(self):
        pass

    def verify_tern(self):
        pass

    def apply(self, changeset):
        if not self._open:
            raise ValueError('Adapter has not been opened.')
        if changeset.order is None:
            changeset.order = 12
        self.applied.append(changeset)

    def revert(self, changeset):
        pass

    def test(self, changeset):
        pass

    def get_applied(self):
        pass
