"""
    Unit tests for the SlackModalFactoryTest.py main file
"""

from unittest.mock import patch
import gql
from freezegun import freeze_time
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory

# pylint: disable=unused-argument


def mock_send_gql_request_login(*args, **kwargs):
    """
        Mock the send_gql_method to check validity of the user query
    """
    assert 'app_context' == args[0]
    assert args[2]['login'] == 'the_test_login'
    assert args[1] == gql.gql(
            """
            query userIDfromLogin($login: String!) {
                user(login: $login) {
                    id
                }
            }
            """
        )


def mock_send_gql_request_set_current_sprint(*args, **kwargs):
    """
        Mock the send_gql_method to check validity of the set current sprint mutation
    """
    assert 'app_context' == args[0]
    assert args[2]['fieldMutation']['itemId'] == 'the_project_item_id'
    assert args[2]['fieldMutation']['projectId'] == 'the_project_id'
    assert args[2]['fieldMutation']['fieldId'] == 'the_field_id'
    assert args[2]['fieldMutation']['value'] == {'iterationId': 'the_iteration_id'}
    assert args[1] == gql.gql(
            """
            mutation CreateProjectV2Task($fieldMutation: UpdateProjectV2ItemFieldValueInput!) {
                updateProjectV2ItemFieldValue(input: $fieldMutation) {
                    clientMutationId
                }
            }
        """
        )


def mock_send_gql_request_create_task_mandatory(*args, **kwargs):
    """
        Mock the send_gql_method to check validity of the set current sprint mutation
    """
    assert 'app_context' == args[0]
    assert args[2]['task']['title'] == 'the_title'
    assert args[2]['task']['body'] == 'the_body'
    assert args[1] == gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    projectItem {
                        id
                    }
                }
            }
        """
    )
    return {"addProjectV2DraftIssue": {"projectItem": {"id": "the_item_id"}}}


def mock_send_gql_request_create_task_assignee(*args, **kwargs):
    """
        Mock the send_gql_method to check validity of the set current sprint mutation
    """
    assert 'app_context' == args[0]
    assert args[2]['task']['title'] == 'the_title'
    assert args[2]['task']['body'] == 'the_body'
    assert args[2]['task']['assigneeIds'] == ['the_user_id']
    assert args[1] == gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    projectItem {
                        id
                    }
                }
            }
        """
    )
    return {"addProjectV2DraftIssue": {"projectItem": {"id": "the_item_id"}}}


def mock_send_gql_request_create_task_no_assignee(*args, **kwargs):
    """
        Mock the send_gql_method to check validity of the set current sprint mutation
    """
    assert 'app_context' == args[0]
    assert args[2]['task']['title'] == 'the_title'
    assert args[2]['task']['body'] == 'the_body'
    assert 'assigneeIds' not in args[2]['task']
    assert args[1] == gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    projectItem {
                        id
                    }
                }
            }
        """
    )
    return {"addProjectV2DraftIssue": {"projectItem": {"id": "the_item_id"}}}


def mock_send_gql_request_create_task_error(*args, **kwargs):
    """
        Mock the send_gql_method to return an empty payload
    """
    return {"addProjectV2DraftIssue": {}}


def mock_get_current_sprint_id(*args, **kwargs):
    """
        Mock for the get_current_sprint_id method that returns a dummy id
    """
    return 'the_iteration_id'


def mock_get_current_sprint_id_none(*args, **kwargs):
    """
        Mock for the get_current_sprint_id method that returns None
    """
    return None


def mock_get_user_id_from_login(*args, **kwargs):
    """
        Mock for the get_user_id_from_login method that returns a dummy id
    """
    return 'the_user_id'


def mock_set_task_to_current_sprint(*args, **kwargs):
    """
        Mock for the set_task_to_current_sprint method to check the passed project item
    """
    assert 'the_item_id' == args[1]


def mock_send_gql_request_get_iterations(*args, **kwargs):
    """
        Mock the send_sql_request to query sprint iterations.
    """
    print('toto')
    return {
            "node": {
                "configuration": {
                    "duration": 14,
                    "iterations": [
                        {
                            "id": "8824dd79",
                            "startDate": "2023-07-17"
                        },
                        {
                            "id": "d8a8bb1d",
                            "startDate": "2023-07-31"
                        },
                        {
                            "id": "57d4c421",
                            "startDate": "2023-08-14"
                        }
                    ]
                }
            }
        }
# pylint: enable=unused-argument


@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request", side_effect=mock_send_gql_request_login)
def test_get_user_id_from_login(mock_sendrequest):
    """
        Test get_user_id_from_login to check the created GQL call is correct.
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.get_user_id_from_login('app_context', 'the_test_login')
    mock_sendrequest.assert_called_once()


@patch.object(GithubGQLCallFactory, "get_current_sprint_id", side_effect=mock_get_current_sprint_id)
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_set_current_sprint)
def test_set_task_to_current_sprint(mock_sendrequest, mock_getsprint):
    """
        Test set_task_to_current_sprint with dummy values
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    github_gql_call_factory.github_config['sprintFieldId'] = 'the_field_id'
    github_gql_call_factory.set_task_to_current_sprint('app_context', 'the_project_item_id')
    mock_sendrequest.assert_called_once()
    mock_getsprint.assert_called_once()


@patch.object(GithubGQLCallFactory, "get_current_sprint_id", side_effect=mock_get_current_sprint_id_none)
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request")
def test_set_task_to_current_sprint_not_found(mock_sendrequest, mock_getsprint):
    """
        Test set_task_to_current_sprint when the sprint is not found
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    github_gql_call_factory.github_config['sprintFieldId'] = 'the_field_id'
    error_caught = False
    try:
        github_gql_call_factory.set_task_to_current_sprint('app_context', 'the_project_item_id')
    except ValueError:
        error_caught = True
    assert error_caught
    mock_sendrequest.assert_not_called()
    mock_getsprint.assert_called_once()


@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_create_task_mandatory)
def test_create_github_task_mandatory(mock_sendrequest):
    """
        Test create_github_task with mandatory fields
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title", "body": "the_body"}
    github_gql_call_factory.create_github_task('app_context', task_params)
    mock_sendrequest.assert_called_once()


def test_create_github_task_missing_title():
    """
        Test create_github_task with missing mandatory fields
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"body": "the_body"}
    error_caught = False
    try:
        github_gql_call_factory.create_github_task('app_context', task_params)
    except TypeError:
        error_caught = True
    assert error_caught


def test_create_github_task_missing_body():
    """
        Test create_github_task with missing mandatory fields
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title"}
    error_caught = False
    try:
        github_gql_call_factory.create_github_task('app_context', task_params)
    except TypeError:
        error_caught = True
    assert error_caught


@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint", side_effect=mock_set_task_to_current_sprint)
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_create_task_mandatory)
def test_create_github_task_handle_immediately_true(mock_sendrequest, mock_setcurrentsprint):
    """
        Test create_github_task with request to handle immediately
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": True}
    github_gql_call_factory.create_github_task('app_context', task_params)
    mock_sendrequest.assert_called_once()
    mock_setcurrentsprint.assert_called_once()


@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_create_task_mandatory)
@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint", side_effect=mock_set_task_to_current_sprint)
def test_create_github_task_handle_immediately_false(mock_setcurrentsprint, mock_sendrequest):
    """
        Test create_github_task with missing mandatory fields
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": False}
    github_gql_call_factory.create_github_task('app_context', task_params)
    mock_sendrequest.assert_called_once()
    mock_setcurrentsprint.assert_not_called()


@patch.object(GithubGQLCallFactory, "set_task_to_current_sprint", side_effect=mock_set_task_to_current_sprint)
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_create_task_error)
def test_create_github_task_handle_immediately_error(mock_sendrequest, mock_setcurrentsprint):
    """
        Test create_github_task with request to handle immediately but the task creation fails
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": True}
    github_gql_call_factory.create_github_task('app_context', task_params)
    mock_sendrequest.assert_called_once()
    mock_setcurrentsprint.assert_not_called()


@patch.object(GithubGQLCallFactory, 'get_user_id_from_login',
              side_effect=mock_get_user_id_from_login)
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_create_task_assignee)
def test_create_github_task_assignee_filled(mock_sendrequest, mock_login):
    """
        Test create_github_task with an assignee
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title", "body": "the_body", "assignee": 'the_assignee'}
    github_gql_call_factory.create_github_task('app_context', task_params)
    mock_sendrequest.assert_called_once()
    mock_login.assert_called_once()


@patch.object(GithubGQLCallFactory, 'get_user_id_from_login',
              side_effect=mock_get_user_id_from_login)
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_create_task_no_assignee)
def test_create_github_task_no_assignee(mock_sendrequest, mock_login):
    """
        Test create_github_task with assignee set to no-assignee
    """
    github_gql_call_factory = GithubGQLCallFactory()
    github_gql_call_factory.github_config['projectId'] = 'the_project_id'
    task_params = {"title": "the_title", "body": "the_body", "assignee": 'no-assignee'}
    github_gql_call_factory.create_github_task('app_context', task_params)
    mock_sendrequest.assert_called_once()
    mock_login.assert_not_called()


@freeze_time('2023-07-27')
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_get_iterations)
def test_get_current_sprint_id(mock_sendrequest):
    """
        Test get_current_sprint_id with date within iterations
    """
    github_gql_call_factory = GithubGQLCallFactory()
    result = github_gql_call_factory.get_current_sprint_id('app_context')
    mock_sendrequest.assert_called_once()
    assert '8824dd79' == result


@freeze_time('2022-07-27')
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_get_iterations)
def test_get_current_sprint_id_past(mock_sendrequest):
    """
        Test get_current_sprint_id with date before iterations
    """
    github_gql_call_factory = GithubGQLCallFactory()
    result = github_gql_call_factory.get_current_sprint_id('app_context')
    mock_sendrequest.assert_called_once()
    assert result is None


@freeze_time('2024-07-27')
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_get_iterations)
def test_get_current_sprint_id_future(mock_sendrequest):
    """
        Test get_current_sprint_id with date after iterations
    """
    github_gql_call_factory = GithubGQLCallFactory()
    result = github_gql_call_factory.get_current_sprint_id('app_context')
    mock_sendrequest.assert_called_once()
    assert result is None


@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              return_value={'toto': 'tata'})
def test_get_current_sprint_id_error(mock_sendrequest):
    """
        Test get_current_sprint_id with unexpected return from the GitHub API
    """
    github_gql_call_factory = GithubGQLCallFactory()
    result = github_gql_call_factory.get_current_sprint_id('app_context')
    mock_sendrequest.assert_called_once()
    assert result is None
