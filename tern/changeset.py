import re
import hashlib


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

    """

    file_end_regex = re.compile(
        r'^-{2,}\s*end$', flags=re.IGNORECASE
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

    def __init__(self, order, setup, teardown):
        self.order = order
        self.setup = setup
        self.teardown = teardown

    @classmethod
    def from_file(cls, filename):
        """
        Parse a file and create a Changeset object from that.  The format of
        the file:

        * Order marked by ``--- Order: XX``.
        * Setup SQL begun by ``--- Begin setup`` and ended with ``--- End``.
        * Teardown SQL begun by ``--- Begin teardown`` and ended with
            ``--- End``.
        * Any lines outside of these are ignored.

        """
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

                # Check for order
                m = cls.file_order_regex.match(line)
                if m is not None:
                    order = int(m.group(1))

                # Check for setup
                if cls.file_begin_setup_regex.match(line) is not None:
                    setup = read_block(fh)

                # Check for teardown
                if cls.file_begin_teardown_regex.match(line) is not None:
                    teardown = read_block(fh)

        if order is None:
            raise ValueError('File did not define order.')
        if setup is None:
            raise ValueError('File did not define setup SQL.')
        if teardown is None:
            raise ValueError('File did not define teardown SQL.')

        return cls(order, setup, teardown)

    def save(self, filename):
        """
        Save this change to the specified file.

        :param filename:  The file to save to.
        :type filename:  str

        """
        with open(filename, 'w') as fh:
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

    def _make_hash(self):
        h = hashlib.sha1()
        h.update(str(self.order))
        h.update(self.setup)
        h.update(self.teardown)
        return h

    @property
    def hash(self):
        """
        Returns a hash as a binary string of the object, which is the SHA-1
        hash of ``str(order) + setup + teardown``.

        """
        return self._make_hash().digest()

    @property
    def hex_hash(self):
        """
        Returns a hexidecimal hash of the object, which is the SHA-1 hash of
        ``str(order) + setup + teardown``.

        """
        return self._make_hash().hexdigest()
