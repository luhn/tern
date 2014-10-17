"""
Sorry!  This is sloppily done and poorly documented.  I'll fix it eventually.
I promise.

"""
from __future__ import absolute_import
import sys
import os
import os.path
import yaml
from six.moves import input
from argparse import ArgumentParser
from importlib import import_module

from .adapters import extract_adapter
from .exceptions import NotInitialized
from .changeset import Changeset
from .api import Tern


def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help=(
        'The path the config file.  Defaults to "tern.yml".',
    ))

    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('setup', help=(
        'A setup process that will get you up and running with Tern.'
    ))
    subparsers.add_parser('init', help=(
        'Initializes the database for use with Tern.'
    ))
    subparsers.add_parser('test', help=(
        'Test the SQL you\'ve written in setup.sql and teardown.sql.'
    ))
    subparsers.add_parser('apply', help=(
        'Apply the SQL to the database and save it to repo.'
    ))
    subparsers.add_parser('update', help=(
        'Bring the database in sync with the repository.'
    ))

    args = parser.parse_args()

    if args.command == 'setup':
        # Incomplete
        try:
            # Get config file
            fh = None
            config = {
                'adapter': dict(),
            }
            while True:
                sys.stdout.write('Config file [tern.yml]: ')
                sys.stdout.flush()
                config_file = input() or 'tern.yml'
                if os.path.isfile(config_file):
                    sys.stdout.write(
                        'File already exists.  Overwrite? (y/n): '
                    )
                    sys.stdout.flush()
                    if input().lower() != 'y':
                        continue
                try:
                    fh = open(config_file, 'w')
                    break
                except IOError:
                    sys.stderr.write('Could not open file.  Try again.\n')

            # Set directory
            while True:
                sys.stdout.write(
                    'Tern directory relative to config file [tern/]: '
                )
                sys.stdout.flush()
                directory = input() or 'tern/'
                test = os.path.join(os.path.dirname(config_file), directory)
                if not os.path.isdir(test):
                    try:
                        os.mkdir(test)
                    except IOError:
                        sys.stderr.write('Could not create directory.\n')
                        continue
                config['directory'] = directory

            # Set adapter
            while True:
                sys.stdout.write('Adapter module [postgres]: ')
                sys.stdout.flush()
                adapter_name = input()

                # First, try in adapter package.
                try:
                    new_name = 'tern.adapters.{0}'.format(adapter_name)
                    module = import_module(new_name)
                    adapter_name = new_name
                except ImportError:
                    try:
                        module = import_module(adapter_name)
                    except ImportError:
                        sys.stderr.write('Could not find adapter.\n')
                        continue

                Adapter = extract_adapter(module)
                if Adapter is None:
                    sys.stderr.write('Module loaded, but no adapter found.\n')
                    continue
                config['adapter']['module'] = adapter_name

                # Configure database
                for name, display, default in Adapter.config:
                    sys.sydout.write('{0} [(1)]: '.format(display, default))
                    sys.stdout.flush()
                    config['adapter'][name] = input() or default
                    # kwargs[name] = config['adapter'][name]

                sys.stdout.write('Tern tablename [tern]: ')
                sys.stdout.flush()
                # Todo:  Make sure connect works, then save to YML, then init.

        finally:
            if fh is not None:
                fh.close()

    if args.command == 'init':
        config, tern, adapter = load(args.config, verify=False)
        try:
            adapter.verify_tern()
            sys.stderr.write('Tern is already initialized.\n')
            sys.exit(1)
        except NotInitialized:
            pass

        sys.stdout.write('Initializing... ')
        sys.stdout.flush()
        adapter.initialize_tern()
        adapter.verify_tern()
        sys.stdout.write('Done.\n')

    elif args.command == 'test':
        config, tern, adapter = load(args.config)
        sys.stdout.write('Testing... ')
        sys.stdout.flush()
        cs = load_pending_changeset(tern)
        try:
            adapter.test(cs)
            sys.stdout.write('Success\n')
        except:
            sys.stdout.write('Error\n')
            raise

    elif args.command == 'apply':
        config, tern, adapter = load(args.config)
        sys.stdout.write('Saving... ')
        sys.stdout.flush()
        cs = load_pending_changeset(tern)

        # Make sure it works
        try:
            adapter.test(cs)
        except:
            raise

        # Make sure we're up-to-date
        a, b = tern.diff()
        if set(a) != set(b):
            sys.stderr.write(
                'Database and repository are in different states.  Please run '
                + '`tern update`'
            )
            sys.exit(1)

        # Apply, then empty files
        tern.apply(cs)
        with open('setup.sql', 'w') as fh:
            fh.write('')
        with open('teardown.sql', 'w') as fh:
            fh.write('')
        sys.stdout.write('Done\n')

    elif args.command == 'update':
        config, tern, adapter = load(args.config)
        sys.stdout.write('Updating... ')
        sys.stdout.flush()
        tern.update()
        sys.stdout.write('Done\n')


def load(config_file, verify=True):
    """
    Load configuration, tern object, and adapter, returns
    ``(config, tern, adapter)``.

    """
    with open(config_file or 'tern.yml') as fh:
        config = yaml.load(fh.read())

    Adapter = extract_adapter(import_module(config['adapter']['module']))
    del config['adapter']['module']
    adapter = Adapter(**config['adapter'])
    adapter.open()
    tern = Tern(adapter, config['directory'], verify=verify)
    return config, tern, adapter


def load_pending_changeset(tern):
    with open('setup.sql') as fh:
        setup = fh.read().strip()
        if not setup:
            raise ValueError('setup.sql is empty')
    with open('teardown.sql') as fh:
        teardown = fh.read().strip()
        if not teardown:
            sys.stderr.write('Warning:  teardown.sql is empty\n')
    return Changeset(setup=setup, teardown=teardown)

if __name__ == '__main__':
    main()
