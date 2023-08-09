"""
    Unit tests for the SlackMessageFactory.py main file
"""


from unittest.mock import patch
from sources.factories.SlackMessageFactory import SlackMessageFactory

# pylint: disable=unused-argument


def mock_request_post_check_params(*args, **kwargs):
    """
        Mocks the requests.post and check basic values for test_post_message
    """
    assert 'https://slack.com/api/chat.postMessage' == kwargs['url']
    assert {"Content-type": "application/json", "Authorization": "Bearer " + 'the_token'} == kwargs['headers']
    assert {"channel": "the_channel", "text": "the_text"} == kwargs['json']


@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_bot_user_token', return_value='the_token')
def test_post_message(mock_get_token, mock_requests):
    """
        Test __get_assignee_list when the assigneeList key does not exist in the config file.
        Only the No assignee option must be returned
    """
    mock_requests.post.side_effect = mock_request_post_check_params

    slack_message_factory = SlackMessageFactory()
    slack_message_factory.post_message('app_context', 'the_channel', 'the_text')

    mock_requests.post.assert_called_once()
