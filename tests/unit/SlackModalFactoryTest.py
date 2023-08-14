"""
    Unit tests for the SlackModalFactoryTest.py main file
"""
import json
from unittest.mock import patch, mock_open
from sources.factories.SlackModalFactory import SlackModalFactory

# pylint: disable=protected-access


@patch("builtins.open", new_callable=mock_open, read_data='{"toto": "tata"}')
def test_get_assignee_list_not_exist(mock):
    """
        Test __get_assignee_list when the assigneeList key does not exist in the config file.
        Only the No assignee option must be returned
    """
    slack_modal_factory = SlackModalFactory()
    assignee_list = slack_modal_factory._SlackModalFactory__get_assignee_list()
    mock.assert_called_once()
    assert assignee_list == [{
                                "text": {
                                    "type": "plain_text",
                                    "text": "No assignee"
                                },
                                "value": "no-assignee"
                            }]


@patch("builtins.open", new_callable=mock_open, read_data='{"toto": "tata", "assignee_list":{ }}')
def test_get_assignee_list_empty(mock):
    """
        Test __get_assignee_list when the assigneeList key has an empty value
        Only the No assignee option must be returned
    """
    slack_modal_factory = SlackModalFactory()
    assignee_list = slack_modal_factory._SlackModalFactory__get_assignee_list()
    mock.assert_called_once()
    assert assignee_list == [{
                                "text": {
                                    "type": "plain_text",
                                    "text": "No assignee"
                                },
                                "value": "no-assignee"
                            }]


@patch("builtins.open", new_callable=mock_open,
       read_data='{"toto": "tata", "assigneeList":{"name1":"value1","name2":"value2"} }')
def test_get_assignee_list_data(mock):
    """
        Test __get_assignee_list when the assigneeList key has values
    """
    slack_modal_factory = SlackModalFactory()
    assignee_list = slack_modal_factory._SlackModalFactory__get_assignee_list()
    mock.assert_called_once()
    assert assignee_list == [{
                                "text": {
                                    "type": "plain_text",
                                    "text": "No assignee"
                                },
                                "value": "no-assignee"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "name1"
                                },
                                "value": "value1"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "name2"
                                },
                                "value": "value2"
                            }]


@patch("builtins.open", new_callable=mock_open,
       read_data='{"toto": "tata", "assigneeList":{"name1":"value1","name2":"value2"} }')
def test_get_assignee_list_multiple_calls(mock):
    """
        Test __get_assignee_list when the assigneeList key has values and is called several times.
        The assignee_list must be stored so that the config file is only read once.
    """
    slack_modal_factory = SlackModalFactory()

    assignee_list_1 = slack_modal_factory._SlackModalFactory__get_assignee_list()
    assignee_list_2 = slack_modal_factory._SlackModalFactory__get_assignee_list()

    assert assignee_list_2 == assignee_list_1
    mock.assert_called_once()
    assert assignee_list_1 == [{
                                "text": {
                                    "type": "plain_text",
                                    "text": "No assignee"
                                },
                                "value": "no-assignee"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "name1"
                                },
                                "value": "value1"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "name2"
                                },
                                "value": "value2"
                            }]

# pylint: enable=protected-access
# pylint: disable=unused-argument


def mock_get_slack_bot_user_token(*args, **kwargs):
    """
        Mock of the _get_slack_bot_user_token to return a test token
    """
    return 'the_test_token'


# pylint: disable-extenable=unused-argument
def mock_requests_post_create_github_task_modal(*args, **kwargs):
    """
        Mock of the requests.post to check validity of the request
    """
    send_modal_data_validation(*args, **kwargs)
    try:
        view = json.loads(kwargs['json']['view'])
        is_callback_valid = 'ttl_create_github_task_modal_submit' == view["callback_id"]
    except TypeError:
        is_callback_valid = False
    assert is_callback_valid


def mock_dev_team_escalation_modal(*args, **kwargs):
    """
        Mock of the requests.post to check validity of the request
    """
    send_modal_data_validation(*args, **kwargs)
    try:
        view = json.loads(kwargs['json']['view'])
        is_callback_valid = 'ttl_dev_team_escalation_modal_submit' == view["callback_id"]
    except TypeError:
        is_callback_valid = False
    assert is_callback_valid


def send_modal_data_validation(*args, **kwargs):
    """
        Validates the generic data content of the post request for Slack modals
    """
    assert 'https://slack.com/api/views.open' == kwargs["url"]
    assert {"Authorization": "Bearer the_test_token"} == kwargs["headers"]
    assert 'timeout' in kwargs
    assert kwargs['json']['trigger_id'] == '1234'
    is_payload_valid = False
    try:
        json.loads(kwargs['json']['view'])
        is_payload_valid = True
    except TypeError:
        is_payload_valid = False
    assert is_payload_valid

# pylint: enable=unused-argument


@patch("requests.post", side_effect=mock_requests_post_create_github_task_modal)
@patch("builtins.open", new_callable=mock_open,
       read_data='{"toto": "tata", "assigneeList":{"name1":"value1","name2":"value2"} }')
@patch.object(SlackModalFactory, "_get_slack_bot_user_token", side_effect=mock_get_slack_bot_user_token)
def test_create_github_task_modal(mock_gettoken, mock_openfile, mock_postrequest):
    """
        Test __get_assignee_list when the assigneeList key has values
    """
    slack_modal_factory = SlackModalFactory()
    slack_modal_factory.create_github_task_modal('app_context', '1234')
    mock_postrequest.assert_called_once()
    mock_openfile.assert_called_once()
    mock_gettoken.assert_called_once()


@patch("requests.post", side_effect=mock_dev_team_escalation_modal)
@patch.object(SlackModalFactory, "_get_slack_bot_user_token", side_effect=mock_get_slack_bot_user_token)
def test_dev_team_escalation_modal(mock_gettoken, mock_postrequest):
    """
        Test __get_assignee_list when the assigneeList key has values
    """
    slack_modal_factory = SlackModalFactory()
    slack_modal_factory.dev_team_escalation_modal('app_context', '1234')
    mock_postrequest.assert_called_once()
    mock_gettoken.assert_called_once()
