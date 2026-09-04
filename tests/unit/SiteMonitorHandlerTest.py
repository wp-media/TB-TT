"""
    Unit tests for the SiteMonitorHandler.py main file
"""
from unittest.mock import Mock, patch

import pytest

from sources.handlers.SiteMonitorHandler import SiteMonitorHandler

# pylint: disable=unused-argument

SITE = {
    'label': 'one.com',
    'url': 'https://example.test',
    'app_user': 'tbtt-monitor',
    'app_password_env': 'TBTT_SITE_ONE_COM_APP_PASSWORD',
    'app_password': 'app-password',
}


def build_handler_with_mocks(health_results, updates_result):
    """
    Builds a SiteMonitorHandler with its factories mocked.
    """
    handler = SiteMonitorHandler()
    handler.site_config_factory.get_site = Mock(return_value=SITE)
    handler.wordpress_site_factory.check_health = Mock(return_value=health_results)
    handler.wordpress_site_factory.check_updates_pending = Mock(return_value=updates_result)
    handler.slack_message_factory.post_message = Mock()
    handler.slack_message_factory.get_channel = Mock(return_value='C0925D6CBPF')
    return handler


def test_run_check_all_ok_posts_success_summary():
    """
    Tests run_check posts a Slack message reflecting that all checks passed
    """
    health_results = {
        'homepage (cached)': {'url': 'https://example.test/', 'status': 'ok', 'detail': '120ms'},
    }
    updates_result = {'url': 'https://example.test/wp-json/tbtt-monitor/v1/updates-pending',
                      'status': 'ok', 'detail': 'No pending updates'}

    handler = build_handler_with_mocks(health_results, updates_result)
    mock_app_context = Mock()

    results = handler.run_check(mock_app_context, 'one-com')

    assert results['homepage (cached)']['status'] == 'ok'
    assert results['pending updates']['status'] == 'ok'

    handler.slack_message_factory.post_message.assert_called_once()
    call_args = handler.slack_message_factory.post_message.call_args[0]
    assert call_args[0] == mock_app_context
    assert call_args[1] == 'C0925D6CBPF'
    assert 'all checks passed' in call_args[2]
    assert 'warning' not in call_args[2]


def test_run_check_with_failure_posts_failure_summary():
    """
    Tests run_check posts a Slack message reflecting that a check failed
    """
    health_results = {
        'homepage (cached)': {'url': 'https://example.test/', 'status': 'fail', 'detail': 'Status code 500'},
    }
    updates_result = {'url': 'https://example.test/wp-json/tbtt-monitor/v1/updates-pending',
                      'status': 'ok', 'detail': 'No pending updates'}

    handler = build_handler_with_mocks(health_results, updates_result)
    mock_app_context = Mock()

    results = handler.run_check(mock_app_context, 'one-com')

    assert results['homepage (cached)']['status'] == 'fail'

    call_args = handler.slack_message_factory.post_message.call_args[0]
    assert 'one or more checks failed' in call_args[2]


def test_run_check_with_pending_updates_only_posts_warning_not_failure():
    """
    Tests run_check treats a pending-updates warning as a warning, not a failure, in the summary
    text and header emoji, so a routine pending nightly build doesn't read as an outage.
    """
    health_results = {
        'homepage (cached)': {'url': 'https://example.test/', 'status': 'ok', 'detail': '120ms'},
    }
    updates_result = {'url': 'https://example.test/wp-json/tbtt-monitor/v1/updates-pending',
                      'status': 'warning', 'detail': 'Pending updates: core (development)'}

    handler = build_handler_with_mocks(health_results, updates_result)
    mock_app_context = Mock()

    handler.run_check(mock_app_context, 'one-com')

    call_args = handler.slack_message_factory.post_message.call_args[0]
    text = call_args[2]
    blocks = call_args[3]
    assert 'all checks passed' in text
    assert 'failed' not in text
    assert ':warning:' in blocks[0]['text']['text']
    assert ':x:' not in blocks[0]['text']['text']


@patch("sources.handlers.SiteMonitorHandler.SiteConfigFactory")
@patch("sources.handlers.SiteMonitorHandler.WordPressSiteFactory")
@patch("sources.handlers.SiteMonitorHandler.SlackMessageFactory")
def test_run_check_calls_both_checks(mock_slack_factory, mock_wp_factory, mock_config_factory):
    """
    Tests run_check calls both the health checks and the pending-updates check for the site
    """
    mock_config_factory.return_value.get_site.return_value = SITE
    mock_wp_factory.return_value.check_health.return_value = {}
    mock_wp_factory.return_value.check_updates_pending.return_value = {
        'url': 'x', 'status': 'ok', 'detail': 'No pending updates'}
    mock_slack_factory.return_value.get_channel.return_value = 'C0925D6CBPF'

    handler = SiteMonitorHandler()
    handler.run_check(Mock(), 'one-com')

    mock_wp_factory.return_value.check_health.assert_called_once_with(SITE)
    mock_wp_factory.return_value.check_updates_pending.assert_called_once_with(SITE)


def test_run_check_pushes_app_context():
    """
    Tests run_check pushes the given app_context, since it is meant to run in a dedicated thread
    with no ambient Flask context of its own.
    """
    handler = build_handler_with_mocks({}, {'url': 'x', 'status': 'ok', 'detail': 'No pending updates'})
    mock_app_context = Mock()

    handler.run_check(mock_app_context, 'one-com')

    mock_app_context.push.assert_called_once()


def test_run_check_logs_and_swallows_errors():
    """
    Tests run_check logs (rather than raises) when an error occurs, since it runs in a background
    thread where an uncaught exception would be silently lost.
    """
    handler = build_handler_with_mocks({}, {'url': 'x', 'status': 'ok', 'detail': 'No pending updates'})
    handler.slack_message_factory.post_message = Mock(side_effect=ValueError('Slack post message failed.'))
    mock_app_context = Mock()

    result = handler.run_check(mock_app_context, 'one-com')

    assert result is None
    mock_app_context.app.logger.error.assert_called_once()


def test_validate_site_known_site():
    """
    Tests validate_site does not raise for a known site
    """
    handler = build_handler_with_mocks({}, {})
    handler.validate_site('one-com')


def test_validate_site_unknown_site():
    """
    Tests validate_site raises a KeyError for an unknown site
    """
    handler = SiteMonitorHandler()
    with pytest.raises(KeyError):
        handler.validate_site('does-not-exist')
