"""
    Unit tests for the SlackMessageFactory.py main file
"""


from unittest.mock import patch, Mock
from sources.factories.SlackMessageFactory import SlackMessageFactory

# pylint: disable=unused-argument


def mock_request_post_message_check_params(*args, **kwargs):
    """
        Mocks the requests.post and check basic values for test_post_message
    """
    class RequestReturn(object):
        """
            Mocks the return of requests.post
         """
        status_code = 200

        def json(self):
            """
                Mocks the json method of requests.post's return
            """
            json = {"ok": True,
                    "channel": "C123ABC456",
                    "ts": "1503435956.000247",
                    "message": {
                        "text": "Here's a message for you",
                        "username": "ecto1",
                        "bot_id": "B123ABC456",
                        "attachments": [
                            {
                                "text": "This is an attachment",
                                "id": 1,
                                "fallback": "This is an attachment's fallback"
                            }
                        ],
                        "type": "message",
                        "subtype": "bot_message",
                        "ts": "1503435956.000247"
                    }
                    }
            return json

    assert 'https://slack.com/api/chat.postMessage' == kwargs['url']
    assert {"Content-type": "application/json", "Authorization": "Bearer " + 'the_token'} == kwargs['headers']
    assert {"channel": "the_channel", "text": "the_text"} == kwargs['json']
    response = RequestReturn()
    return response


def mock_request_post_reply_check_params(*args, **kwargs):
    """
        Mocks the requests.post and check basic values for test_post_reply
    """
    assert 'https://slack.com/api/chat.postMessage' == kwargs['url']
    assert {"Content-type": "application/json", "Authorization": "Bearer " + 'the_token'} == kwargs['headers']
    assert {"channel": "the_channel", "thread_ts": "the_ts", "text": "the_text"} == kwargs['json']


def mock_request_edit_message_check_params(*args, **kwargs):
    """
        Mocks the requests.post and check basic values for test_edit_message
    """
    assert 'https://slack.com/api/chat.update' == kwargs['url']
    assert {"Content-type": "application/json", "Authorization": "Bearer " + 'the_token'} == kwargs['headers']
    assert {"channel": "the_channel", "ts": "the_ts", "text": "the_text"} == kwargs['json']


def mock_request_search_message_default_check_params(*args, **kwargs):
    """
        Mocks the requests.post and check basic values for test_search_message with default params
    """
    assert 'https://slack.com/api/search.messages' == kwargs['url']
    assert {"Content-type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + 'the_token'} == kwargs['headers']
    assert {"query": "the_query"} == kwargs['data']
    return Mock(json=lambda:
                {
                    "messages": {
                        "matches": [
                            {
                                "channel": {
                                    "id": "C12345678",
                                    "is_ext_shared": False,
                                    "is_mpim": False,
                                    "is_org_shared": False,
                                    "is_pending_ext_shared": False,
                                    "is_private": False,
                                    "is_shared": False,
                                    "name": "random",
                                    "pending_shared": []
                                },
                                "iid": "9a00d3c9-bd2d-45b0-988b-6cff99ae2a90",
                                "permalink": "https://hitchhikers.slack.com/archives/C12345678/p1508795665000236",
                                "team": "T12345678",
                                "text": "The meaning of life the universe and everything is 101010",
                                "ts": "1508795665.000236",
                                "type": "message",
                                "user": "",
                                "username": "robot overlord"
                            }
                        ],
                        "pagination": {
                            "first": 1,
                            "last": 1,
                            "page": 1,
                            "page_count": 1,
                            "per_page": 20,
                            "total_count": 1
                        },
                        "paging": {
                            "count": 20,
                            "page": 1,
                            "pages": 1,
                            "total": 1
                        },
                        "total": 1
                    },
                    "ok": True,
                    "query": "The meaning of life the universe and everything"
                })


def mock_request_search_message_count_check_params(*args, **kwargs):
    """
        Mocks the requests.post and check basic values for test_search_message with given count param
    """
    assert 'https://slack.com/api/search.messages' == kwargs['url']
    assert {"Content-type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + 'the_token'} == kwargs['headers']
    assert {"query": "the_query", "count": 123} == kwargs['data']
    return Mock(json=lambda: {
                "messages": {
                    "matches": [
                        {
                            "channel": {
                                "id": "C12345678",
                                "is_ext_shared": False,
                                "is_mpim": False,
                                "is_org_shared": False,
                                "is_pending_ext_shared": False,
                                "is_private": False,
                                "is_shared": False,
                                "name": "random",
                                "pending_shared": []
                            },
                            "iid": "9a00d3c9-bd2d-45b0-988b-6cff99ae2a90",
                            "permalink": "https://hitchhikers.slack.com/archives/C12345678/p1508795665000236",
                            "team": "T12345678",
                            "text": "The meaning of life the universe and everything is 101010",
                            "ts": "1508795665.000236",
                            "type": "message",
                            "user": "",
                            "username": "robot overlord"
                        }
                    ],
                    "pagination": {
                        "first": 1,
                        "last": 1,
                        "page": 1,
                        "page_count": 1,
                        "per_page": 20,
                        "total_count": 1
                    },
                    "paging": {
                        "count": 20,
                        "page": 1,
                        "pages": 1,
                        "total": 1
                    },
                    "total": 1
                },
                "ok": True,
                "query": "The meaning of life the universe and everything"
                })


@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_bot_user_token', return_value='the_token')
def test_post_message(mock_get_token, mock_requests):
    """
        Checks that the correct parameters are sent to the slack API for post message
    """
    mock_requests.post.side_effect = mock_request_post_message_check_params

    slack_message_factory = SlackMessageFactory()
    slack_message_factory.post_message('app_context', 'the_channel', 'the_text')

    mock_requests.post.assert_called_once()


@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_bot_user_token', return_value='the_token')
def test_post_reply(mock_get_token, mock_requests):
    """
        Checks that the correct parameters are sent to the slack API for post reply
    """
    mock_requests.post.side_effect = mock_request_post_reply_check_params

    slack_message_factory = SlackMessageFactory()
    slack_message_factory.post_reply('app_context', 'the_channel', 'the_ts', 'the_text')

    mock_requests.post.assert_called_once()


@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_bot_user_token', return_value='the_token')
def test_edit_message(mock_get_token, mock_requests):
    """
        Checks that the correct parameters are sent to the slack API for edit message
    """
    mock_requests.post.side_effect = mock_request_edit_message_check_params

    slack_message_factory = SlackMessageFactory()
    slack_message_factory.edit_message('app_context', 'the_channel', 'the_ts', 'the_text')

    mock_requests.post.assert_called_once()


@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_user_token', return_value='the_token')
def test_search_message_default(mock_get_token, mock_requests):
    """
        Checks that the correct parameters are sent to the slack API for search message
    """
    mock_requests.post.side_effect = mock_request_search_message_default_check_params

    slack_message_factory = SlackMessageFactory()
    slack_message_factory.search_message('app_context', 'the_query')

    mock_requests.post.assert_called_once()


@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_user_token', return_value='the_token')
def test_search_message_count_param(mock_get_token, mock_requests):
    """
        Checks that the correct parameters are sent to the slack API for search message with count param
    """
    mock_requests.post.side_effect = mock_request_search_message_count_check_params

    slack_message_factory = SlackMessageFactory()
    slack_message_factory.search_message('app_context', 'the_query', count=123)

    mock_requests.post.assert_called_once()
