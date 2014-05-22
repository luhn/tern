from __future__ import unicode_literals
import re
import hashlib
from time import time as unix_timestamp

from .exceptions import InvalidChangesetFile


class Changeset(object):
    """
    This class represents a database changeset, which is the following:

    :param order:  The order for this to be applied relative to other
        changesets.
    :type order:  int
    :param setup: The SQL to apply the change.
    :type setup: str
    :param teardown: The SQL to reverse the change.
    :type teardown: str
    :param created_at:  The unix timestamp when the changeset was created.
    :type created_at:  int

    """

    file_end_regex = re.compile(
        r'^-{2,}\s*end$', flags=re.IGNORECASE
    )
    file_created_at_regex = re.compile(
        r'^-{2,}\s*created at\s*:\s*([0-9]+)$', flags=re.IGNORECASE
    )
    file_order_regex = re.compile(
        r'^-{2,}\s*order\s*:\s*([0-9]+)$', flags=re.IGNORECASE
    )
    file_begin_setup_regex = re.compile(
        r'^-{2,}\s*begin setup$', flags=re.IGNORECASE
    )
    file_begin_teardown_regex = re.compile(
        r'^-{2,}\s*begin teardown$', flags=re.IGNORECASE
    )

    def __init__(self, setup, teardown, order=None, created_at=None):
        self.setup = setup
        self.teardown = teardown
        self.order = order
        if created_at is None:
            self.created_at = int(unix_timestamp())
        else:
            self.created_at = created_at

    @classmethod
    def from_file(cls, filename):
        """
        Parse a file and create a Changeset object from that.  The format of
        the file:

        * Created at marked by ``--- Created at: XXXXXX``
        * Order marked by ``--- Order: XX``.
        * Setup SQL begun by ``--- Begin setup`` and ended with ``--- End``.
        * Teardown SQL begun by ``--- Begin teardown`` and ended with
            ``--- End``.
        * Any lines outside of these are ignored.

        """
        created_at = None
        order = None
        setup = None
        teardown = None

        def read_block(fh):
            """
            Read the file up until the ``--- End`` line and return the contents
            as a string.

            """
            content = ''
            for line in fh:
                if cls.file_end_regex.match(line.strip()) is not None:
                    break
                else:
                    content += line
            return content

        with open(filename) as fh:
            for line in fh:
                line = line.strip()

                # Check for created at and order
                created_re = cls.file_created_at_regex.match(line)
                order_re = cls.file_order_regex.match(line)
                if order_re is not None:
                    order = int(order_re.group(1))
                elif created_re is not None:
                    created_at = int(created_re.group(1))

                # Check for setup
                elif cls.file_begin_setup_regex.match(line) is not None:
                    setup = read_block(fh)

                # Check for teardown
                elif cls.file_begin_teardown_regex.match(line) is not None:
                    teardown = read_block(fh)

        if order is None:
            raise InvalidChangesetFile('File did not define order.')
        if setup is None:
            raise InvalidChangesetFile('File did not define setup SQL.')
        if teardown is None:
            raise InvalidChangesetFile('File did not define teardown SQL.')
        if created_at is None:
            raise InvalidChangesetFile('File did not define created at.')

        return cls(setup, teardown, order, created_at)

    def save(self, filename):
        """
        Save this change to the specified file.

        :param filename:  The file to save to.
        :type filename:  str

        """
        with open(filename, 'w') as fh:
            fh.write('--- Created at: {0}\n'.format(self.created_at))
            fh.write('--- Order: {0}\n'.format(self.order))
            fh.write('--- Begin setup\n')
            fh.write(self.setup)
            fh.write('\n')
            fh.write('--- End\n')
            fh.write('--- Begin teardown\n')
            fh.write(self.teardown)
            fh.write('\n')
            fh.write('--- End\n')

    @property
    def setup(self):
        return self._setup

    @setup.setter
    def setup(self, value):
        self._setup = value.strip()

    @property
    def teardown(self):
        return self._teardown

    @teardown.setter
    def teardown(self, value):
        self._teardown = value.strip()

    def _quintessence(self):
        """
        This returns a tuple which contains the important data of this object.
        Used for hashing and equality.

        """
        return self.created_at, self.order, self.setup, self.teardown

    def __hash__(self):
        return hash(self._quintessence())

    def __eq__(self, other):
        return self._quintessence() == other._quintessence()

    def _make_hash(self):
        h = hashlib.sha1()
        h.update(':'.join(
            str(s) for s in self._quintessence()
        ).encode('utf-8'))
        return h

    @property
    def hash(self):
        """
        Returns a hash as a binary string of the object, which is the SHA-1
        hash of the quintessence (created at, order, setup, teardown) joined
        by colons.

        """
        return self._make_hash().digest()

    @property
    def hex_hash(self):
        """
        Returns a hash as a binary string of the object, which is the SHA-1
        hash of the quintessence (created at, order, setup, teardown) joined
        by colons.

        """
        return self._make_hash().hexdigest()

    def __repr__(self):
        return 'Changeset{0!r}'.format(self._quintessence())
