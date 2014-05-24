from __future__ import absolute_import
from importlib import import_module
from inspect import getmembers
import six

from .adapterbase import AdapterBase


def extract_adapter(module):
    """
    Find the adapter (that is, the class subclassing
    ``tern.adapter.AdapterBase``) in the given module and return it.

    :param module:  The module or module name.
    :type module:  str or namespace

    :returns:  The adapter, or ``None`` if it's not found.

    """
    if isinstance(module, six.string_types):
        module = import_module(module)
    for _, member in getmembers(module):
        if member is not AdapterBase and issubclass(member, AdapterBase):
            return member
