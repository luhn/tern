from __future__ import absolute_import

from .. import extract_adapter
from ..postgresql import PostgreSQLAdapter


def test_extract_adapter():
    assert extract_adapter('tern.adapters.postgresql') is PostgreSQLAdapter
