"""
    Unit tests for the SlackModalFactoryTest.py main file
"""

from unittest.mock import patch, call, ANY, Mock
from sources.handlers.GithubTaskHandler import GithubTaskHandler
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory
from sources.models.InitGithubTaskParam import InitGithubTaskParam
from sources.models.CreatedGithubTaskParam import CreatedGithubTaskParam
from sources.factories.SlackMessageFactory import SlackMessageFactory


# pylint: disable=unused-argument
def mock_request_search_message_no_match(*args, **kwargs):
    """
        Mocks the requests.post for search_message as if there were no messages found
    """
    return Mock(json=lambda: {
                "messages": {
                    "matches": [],
                    "total": 0
                },
                "ok": True,
                })


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_mandatory(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title="the_title", body="the_body")
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_missing_title(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with missing mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title=None, body="the_body")
    error_caught = False
    try:
        github_task_handler.init_github_task('app_context', task_params)
    except TypeError:
        error_caught = True
    assert error_caught

    mock_setsprint.assert_not_called()
    mock_setstatus.assert_not_called()
    mock_createtask.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_missing_body(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with missing mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title='the_title', body=None)
    error_caught = False
    try:
        github_task_handler.init_github_task('app_context', task_params)
    except TypeError:
        error_caught = True
    assert error_caught

    mock_setsprint.assert_not_called()
    mock_setstatus.assert_not_called()
    mock_createtask.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_handle_immediately_true(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with handle_immetiatley option to True
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title='the_title', body='the_body', handle_immediately=True)
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_called_once()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_handle_immediately_false(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with handle_immetiatley option to True
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title='the_title', body='the_body', handle_immediately=False)
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value=None)
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_handle_immediately_error(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with request to handle immediately but the task creation fails
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title='the_title', body='the_body', handle_immediately=True)
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setsprint.assert_not_called()
    mock_setstatus.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
def test_init_github_task_assignee_filled(mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with an assignee
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title='the_title', body='the_body', assignee='the_assignee')
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()
    mock_getuser.assert_called_once()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
def test_init_github_task_no_assignee(mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with specifically no assignees
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title="the_title", body="the_body", assignee='no-assignee')
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()
    mock_getuser.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
@patch.object(SlackMessageFactory, "post_message")
def test_init_github_task_dm_initiator(mock_post_message, mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with an initiator so that he is DMed
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title="the_title", body="the_body", initiator='U123456789')
    github_task_handler.init_github_task('app_context', task_params)
    mock_post_message.assert_called_once()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
@patch.object(SlackMessageFactory, "post_message")
def test_init_github_task_no_initiator(mock_post_message, mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with specifically no initiator
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title="the_title", body="the_body")
    github_task_handler.init_github_task('app_context', task_params)
    mock_post_message.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task",
              return_value=CreatedGithubTaskParam("the_project_item_id", 1234, 104))
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
@patch.object(GithubGQLCallFactory, "set_task_to_dev_team_escalation_type")
@patch.object(SlackMessageFactory, "post_message")
@patch.object(SlackMessageFactory, "get_channel", return_value='the_escalation_channel')
# pylint: disable-next=too-many-arguments
def test_init_github_task_dev_team_escalation(mock_getchannel, mock_post_message, mock_settasktype,
                                              mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with the dev-team-escalation flow ot check the type is set
        and the public message is sent on Slack
    """
    github_task_handler = GithubTaskHandler()
    task_params = InitGithubTaskParam(title="the_title", body="the_body", handle_immediately=True,
                                      initiator='U123456789', flow='dev-team-escalation')
    github_task_handler.init_github_task('app_context', task_params)

    call_post_message = [call('app_context', 'U123456789', ANY), call('app_context', 'the_escalation_channel', ANY)]
    mock_post_message.assert_has_calls(call_post_message)

    call_set_task_type = [call('app_context', "the_project_item_id")]
    mock_settasktype.assert_has_calls(call_set_task_type)

    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_called_once()


@patch.object(GithubGQLCallFactory, "get_project_item_for_update", return_value={"typeField": {"name": "dev-team-escalation"}})
@patch.object(GithubGQLCallFactory, "get_dev_team_escalation_item_update",
              return_value={
                "column": {
                    "name": "In Progress"
                },
                "databaseId": 123456,
                "draftIssue": {
                    "assignees": {
                        "nodes": [
                            {"login": "MathieuLamiot"},
                            {"login": "theOtherOne"}
                        ]
                    }
                }
              })
@patch.object(SlackMessageFactory, 'search_message',
              return_value={
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
                            "text": "The first line\nStatus: In Progress\nAssignees: No-one.",
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
@patch.object(SlackMessageFactory, 'edit_message')
@patch.object(SlackMessageFactory, 'post_reply')
# pylint: disable-next=too-many-arguments
def test_process_update_dev_team_escalation_full(mock_post_reply, mock_edit_message, mock_search_message,
                                                 mock_get_dev_team_escalation_item_update,
                                                 mock_get_project_item_for_update):
    """
        Test process_update with the dev-team-escalation flow
    """
    github_task_handler = GithubTaskHandler()
    github_task_handler.process_update('app_context', ('the_node_id'))

    call_get_project_item = [call('app_context', 'the_node_id')]
    mock_get_project_item_for_update.assert_has_calls(call_get_project_item)
    mock_get_dev_team_escalation_item_update.assert_has_calls(call_get_project_item)
    call_search_message = [call('app_context', 'itemId=123456 in:dev-team-escalation from:tbtt')]
    mock_search_message.assert_has_calls(call_search_message)
    call_edit_message = [call('app_context', 'C12345678', '1508795665.000236',
                              'The first line\nStatus: In Progress\nAssignees: MathieuLamiot, theOtherOne, ')]
    mock_edit_message.assert_has_calls(call_edit_message)
    mock_post_reply.assert_called_once()


@patch.object(GithubGQLCallFactory, "get_project_item_for_update", return_value={"typeField": {"name": "dev-team-escalation"}})
@patch.object(GithubGQLCallFactory, "get_dev_team_escalation_item_update",
              return_value={
                "column": {
                    "name": "In Progress"
                },
                "databaseId": 123456,
                "draftIssue": {
                    "assignees": {
                        "nodes": [
                            {"login": "MathieuLamiot"},
                            {"login": "theOtherOne"}
                        ]
                    }
                }
              })
@patch.object(SlackMessageFactory, 'search_message',
              return_value={
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
                            "text": "The first line\nStatus: In Progress\nAssignees: MathieuLamiot, theOtherOne, ",
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
@patch.object(SlackMessageFactory, 'edit_message')
@patch.object(SlackMessageFactory, 'post_reply')
# pylint: disable-next=too-many-arguments
def test_process_update_dev_team_escalation_no_update(mock_post_reply, mock_edit_message, mock_search_message,
                                                      mock_get_dev_team_escalation_item_update,
                                                      mock_get_project_item_for_update):
    """
        Test process_update with the dev-team-escalation flow
    """
    github_task_handler = GithubTaskHandler()
    github_task_handler.process_update('app_context', ('the_node_id'))

    call_get_project_item = [call('app_context', 'the_node_id')]
    mock_get_project_item_for_update.assert_has_calls(call_get_project_item)
    mock_get_dev_team_escalation_item_update.assert_has_calls(call_get_project_item)
    call_search_message = [call('app_context', 'itemId=123456 in:dev-team-escalation from:tbtt')]
    mock_search_message.assert_has_calls(call_search_message)

    mock_edit_message.assert_not_called()
    mock_post_reply.assert_not_called()


@patch.object(GithubGQLCallFactory, "get_project_item_for_update", return_value={"typeField": {"name": "dev-team-escalation"}})
@patch.object(GithubGQLCallFactory, "get_dev_team_escalation_item_update",
              return_value={
                "column": {
                    "name": "In Progress"
                },
                "databaseId": 123456,
                "draftIssue": {
                    "assignees": {
                        "nodes": None
                    }
                }
              })
@patch.object(SlackMessageFactory, 'search_message',
              return_value={
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
                            "text": "The first line\nStatus: In Progress\nAssignees: MathieuLamiot, theOtherOne, ",
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
@patch.object(SlackMessageFactory, 'edit_message')
@patch.object(SlackMessageFactory, 'post_reply')
# pylint: disable-next=too-many-arguments
def test_process_update_dev_team_escalation_no_assignees(mock_post_reply, mock_edit_message, mock_search_message,
                                                         mock_get_dev_team_escalation_item_update,
                                                         mock_get_project_item_for_update):
    """
        Test process_update with the dev-team-escalation flow
    """
    github_task_handler = GithubTaskHandler()
    github_task_handler.process_update('app_context', ('the_node_id'))

    call_get_project_item = [call('app_context', 'the_node_id')]
    mock_get_project_item_for_update.assert_has_calls(call_get_project_item)
    mock_get_dev_team_escalation_item_update.assert_has_calls(call_get_project_item)
    call_search_message = [call('app_context', 'itemId=123456 in:dev-team-escalation from:tbtt')]
    mock_search_message.assert_has_calls(call_search_message)
    call_edit_message = [call('app_context', 'C12345678', '1508795665.000236',
                              'The first line\nStatus: In Progress\nAssignees: No one.')]
    mock_edit_message.assert_has_calls(call_edit_message)
    mock_post_reply.assert_called_once()


@patch.object(GithubGQLCallFactory, "get_project_item_for_update", return_value={"typeField": {"name": "dev-team-escalation"}})
@patch.object(GithubGQLCallFactory, "get_dev_team_escalation_item_update",
              return_value={
                "column": {
                    "name": "In Progress"
                },
                "databaseId": 123456,
                "draftIssue": {
                    "assignees": {
                        "nodes": None
                    }
                }
              })
@patch('sources.factories.SlackMessageFactory.requests')
@patch.object(SlackMessageFactory, '_get_slack_user_token', return_value='the_token')
@patch.object(SlackMessageFactory, 'edit_message')
@patch.object(SlackMessageFactory, 'post_reply')
# pylint: disable-next=too-many-arguments
def test_process_update_dev_team_escalation_no_messages(mock_post_reply, mock_edit_message, mock_slack_user_token,
                                                        mock_request, mock_get_dev_team_escalation_item_update,
                                                        mock_get_project_item_for_update):
    """
        Test process_update with the dev-team-escalation flow
    """
    mock_request.post.side_effect = mock_request_search_message_no_match

    github_task_handler = GithubTaskHandler()
    github_task_handler.process_update('app_context', ('the_node_id'))

    call_get_project_item = [call('app_context', 'the_node_id')]
    mock_get_project_item_for_update.assert_has_calls(call_get_project_item)
    mock_get_dev_team_escalation_item_update.assert_has_calls(call_get_project_item)
    mock_request.post.assert_called_once()
    mock_edit_message.assert_not_called()
    mock_post_reply.assert_not_called()
# pylint: enable=unused-argument
