"""
    Unit tests for the Security.py main file
"""
from unittest.mock import Mock

from sources.utils import Security


def test_validate_api_key_matching():
    """
    Tests validate_api_key returns True when the header matches the expected key
    """
    payload = Mock()
    payload.headers = {'X-Api-Key': 'the-secret-key'}

    assert Security.validate_api_key(payload, 'the-secret-key') is True


def test_validate_api_key_mismatching():
    """
    Tests validate_api_key returns False when the header does not match the expected key
    """
    payload = Mock()
    payload.headers = {'X-Api-Key': 'wrong-key'}

    assert Security.validate_api_key(payload, 'the-secret-key') is False


def test_validate_api_key_missing_header():
    """
    Tests validate_api_key returns False when the header is missing
    """
    payload = Mock()
    payload.headers = {}

    assert Security.validate_api_key(payload, 'the-secret-key') is False
