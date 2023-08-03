"""
    Unit tests for the SlackModalFactoryTest.py main file
"""

from unittest.mock import patch
from sources.handlers.GithubTaskHandler import GithubTaskHandler
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory

# pylint: disable=unused-argument

# pylint: enable=unused-argument


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_mandatory(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title", "body": "the_body"}
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_missing_title(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with missing mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"body": "the_body"}
    error_caught = False
    try:
        github_task_handler.init_github_task('app_context', task_params)
    except TypeError:
        error_caught = True
    assert error_caught

    mock_setsprint.assert_not_called()
    mock_setstatus.assert_not_called()
    mock_createtask.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_missing_body(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with missing mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title"}
    error_caught = False
    try:
        github_task_handler.init_github_task('app_context', task_params)
    except TypeError:
        error_caught = True
    assert error_caught

    mock_setsprint.assert_not_called()
    mock_setstatus.assert_not_called()
    mock_createtask.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_handle_immediately_true(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with handle_immetiatley option to True
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": True}
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_called_once()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
def test_init_github_task_handle_immediately_false(mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with handle_immetiatley option to True
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": False}
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
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": True}
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setsprint.assert_not_called()
    mock_setstatus.assert_not_called()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
def test_init_github_task_assignee_filled(mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with an assignee
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title", "body": "the_body", "assignee": 'the_assignee'}
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()
    mock_getuser.assert_called_once()


@patch.object(GithubGQLCallFactory, "create_github_task", return_value="the_project_item_id")
@patch.object(GithubGQLCallFactory, "set_task_to_initial_status")
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint")
@patch.object(GithubGQLCallFactory, "get_user_id_from_login", return_value='the_user_id')
def test_init_github_task_no_assignee(mock_getuser, mock_setsprint, mock_setstatus, mock_createtask):
    """
        Test init_github_task with specifically no assignees
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title", "body": "the_body", "assignee": 'no-assignee'}
    github_task_handler.init_github_task('app_context', task_params)
    mock_createtask.assert_called_once()
    mock_setstatus.assert_called_once()
    mock_setsprint.assert_not_called()
    mock_getuser.assert_not_called()
