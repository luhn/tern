from abc import ABCMeta, abstractmethod


class AdapterBase(object):
    __metaclass__ = ABCMeta

    # A list of attributes to be defined in config.
    # (var name, display name, default)
    config = [
        ('host', 'Host', ''),
        ('dbname', 'Database name', ''),
        ('username', 'Username', ''),
        ('password', 'Password', ''),
    ]

    @abstractmethod
    def __init__(self, host, dbname, username, password, tern_table='tern'):
        """
        Initialize the Adapter; do not yet connect to database.

        """
        pass

    def __enter__(self):
        self.open()

    def __exit__(self, type, value, traceback):
        self.close()

    @abstractmethod
    def open(self):
        """
        Do whatever needs to be done to open a connection.

        """
        pass

    @abstractmethod
    def close(self):
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
        Apply the given changeset.  If the order is ``None``, an ordering
        should be assigned.  (max(order) + 1)

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
        transaction.  Throws any SQL errors that might occur.

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
