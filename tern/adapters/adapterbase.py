from abc import ABCMeta, abstractmethod


class AdapterBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, host, dbname, username, password, tern_table='tern'):
        """
        Initialize the Adapter; do not yet connect to database.

        """
        pass

    @abstractmethod
    def __enter__(self):
        """
        Do whatever needs to be done to open a connection.

        """
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback):
        """
        Do whatever needs to be done to close the connection.

        """
        pass

    @abstractmethod
    def initialize_tern(self):
        """
        Create a table, named ``self.tern_table`` with the following
        attributes:

        * hash (text, primary key)
        * created_at (64-bit integer, not null)
        * setup (text, not null)
        * teardown (text, not null)
        * order (int, not null)

        """
        pass

    @abstractmethod
    def verify_tern(self):
        """
        Verify that the setup function has been executed successfully, throws
        a tern.exceptions.NotInitialized if not.

        """
        pass

    @abstractmethod
    def apply(self, changeset):
        """
        Apply the given changeset.

        :param changeset:  The changeset to apply.
        :type changeset:  tern.Changeset

        """
        pass

    @abstractmethod
    def revert(self, changeset):
        """
        Revert the given changeset.

        :param changeset:  The changeset to revert.
        :type changeset:  tern.Changeset

        """
        pass

    @abstractmethod
    def test(self, changeset):
        """
        Apply and revert the given changeset, and then rollback the
        transaction.

        :param changeset:  The changeset to test.
        :type changeset:  tern.Changeset

        """
        pass

    @abstractmethod
    def get_applied(self):
        """
        Return a list of Changeset objects which have been applied to the
        database.

        """
        pass
