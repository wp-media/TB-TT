"""
    Unit tests for the WordPressSiteFactory.py main file
"""
from unittest.mock import patch

import requests

from sources.factories.WordPressSiteFactory import WordPressSiteFactory

# pylint: disable=unused-argument

SITE = {
    'label': 'one.com',
    'url': 'https://example.test',
    'app_user': 'tbtt-monitor',
    'app_password': 'app-password',
}


def mock_ok_response(*args, **kwargs):
    """
    Mocks a successful requests.get response
    """
    class RequestReturn:
        """
        Mocks the return of requests.get
        """
        status_code = 200

    return RequestReturn()


def mock_error_response(*args, **kwargs):
    """
    Mocks a failing requests.get response
    """
    class RequestReturn:
        """
        Mocks the return of requests.get
        """
        status_code = 500

    return RequestReturn()


@patch("sources.factories.WordPressSiteFactory.requests.get", side_effect=mock_ok_response)
def test_check_health_all_ok(mock_requests):
    """
    Tests check_health reports every check as ok when all requests succeed
    """
    factory = WordPressSiteFactory()
    results = factory.check_health(SITE)

    assert len(results) == 5
    for result in results.values():
        assert result['status'] == 'ok'


@patch("sources.factories.WordPressSiteFactory.requests.get", side_effect=mock_ok_response)
def test_check_health_authenticates_wp_admin_check(mock_requests):
    """
    Tests check_health calls the wp-admin check with the site's application password
    """
    factory = WordPressSiteFactory()
    factory.check_health(SITE)

    admin_calls = [call for call in mock_requests.call_args_list if 'users/me' in call.args[0]]
    assert len(admin_calls) == 1
    assert admin_calls[0].kwargs['auth'] == ('tbtt-monitor', 'app-password')


@patch("sources.factories.WordPressSiteFactory.requests.get", side_effect=mock_error_response)
def test_check_health_failure(mock_requests):
    """
    Tests check_health reports a check as failed when the request returns a non-200 status
    """
    factory = WordPressSiteFactory()
    results = factory.check_health(SITE)

    for result in results.values():
        assert result['status'] == 'fail'
        assert 'Status code 500' in result['detail']


@patch("sources.factories.WordPressSiteFactory.requests.get")
def test_check_health_request_exception(mock_requests):
    """
    Tests check_health handles request exceptions gracefully
    """
    mock_requests.side_effect = requests.exceptions.RequestException("Connection timeout")
    factory = WordPressSiteFactory()
    results = factory.check_health(SITE)

    for result in results.values():
        assert result['status'] == 'fail'
        assert 'Request failed' in result['detail']


def mock_updates_pending_response(*args, **kwargs):
    """
    Mocks a response reporting pending updates
    """
    class RequestReturn:
        """
        Mocks the return of requests.get
        """
        status_code = 200

        def json(self):
            """ Mocks json() """
            return {
                'plugins_pending': 2,
                'themes_pending': 0,
                'core_pending': True,
                'core_response_type': 'upgrade',
            }

    return RequestReturn()


def mock_no_updates_pending_response(*args, **kwargs):
    """
    Mocks a response reporting no pending updates
    """
    class RequestReturn:
        """
        Mocks the return of requests.get
        """
        status_code = 200

        def json(self):
            """ Mocks json() """
            return {
                'plugins_pending': 0,
                'themes_pending': 0,
                'core_pending': False,
                'core_response_type': None,
            }

    return RequestReturn()


@patch("sources.factories.WordPressSiteFactory.requests.get", side_effect=mock_updates_pending_response)
def test_check_updates_pending_with_pending_updates(mock_requests):
    """
    Tests check_updates_pending reports a warning (not a failure) when updates are pending, since
    a pending update is expected from time to time and not itself an emergency.
    """
    factory = WordPressSiteFactory()
    result = factory.check_updates_pending(SITE)

    assert result['status'] == 'warning'
    assert '2 plugin(s)' in result['detail']
    assert 'core (upgrade)' in result['detail']
    mock_requests.assert_called_once()
    call_kwargs = mock_requests.call_args
    assert call_kwargs[1]['auth'] == ('tbtt-monitor', 'app-password')


@patch("sources.factories.WordPressSiteFactory.requests.get", side_effect=mock_no_updates_pending_response)
def test_check_updates_pending_no_pending_updates(mock_requests):
    """
    Tests check_updates_pending reports ok when no updates are pending
    """
    factory = WordPressSiteFactory()
    result = factory.check_updates_pending(SITE)

    assert result['status'] == 'ok'
    assert result['detail'] == 'No pending updates'


@patch("sources.factories.WordPressSiteFactory.requests.get", side_effect=mock_error_response)
def test_check_updates_pending_request_failure(mock_requests):
    """
    Tests check_updates_pending reports a failure (not a warning) when the call itself fails,
    e.g. the plugin was deactivated and its REST route no longer exists.
    """
    factory = WordPressSiteFactory()
    result = factory.check_updates_pending(SITE)

    assert result['status'] == 'fail'
    assert 'Status code 500' in result['detail']
