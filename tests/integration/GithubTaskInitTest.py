"""
    Integration tests for the Github task creation
"""
from unittest.mock import patch, call, ANY
from freezegun import freeze_time
from sources.handlers.GithubTaskHandler import GithubTaskHandler
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory

# pylint: disable=unused-argument

def mock_send_gql_request_all_fields(*args, **kwargs):
    """
        This is the mock for all send_gql_request for the test_init_github_task_all_fields
    """
    if 'login' in args[2]:
        # This is the request for user ID
        if args[2]['login'] != 'the_assignee':
            raise ValueError
        return {'user': {'id': 'the_assignee_id'}}
    if 'task' in args[2] and 'title' in args[2]['task'] and 'body' in args[2]['task']:
        # This is the task creation ID
        if args[2]['task']['title'] != 'the_title':
            raise ValueError
        if args[2]['task']['body'] != 'the_body':
            raise ValueError
        if args[2]['task']['assigneeIds'] != ['the_assignee_id']:
            raise ValueError
        return {'addProjectV2DraftIssue': {'projectItem': {'id': 'the_item_id'}}}
    if 'fieldMutation' in args[2]:
        # Those are calls to set fields
        if 'iterationId' in args[2]['fieldMutation']['value']:
            if args[2]['fieldMutation']['value']['iterationId'] != "8824dd79":
                raise ValueError
        return {}
    if 'node_id' in args[2]:
        # This is a get node request for the sprint:
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
    raise ValueError

# pylint: enable=unused-argument


@freeze_time('2023-07-27')
@patch.object(GithubGQLCallFactory, "_GithubGQLCallFactory__send_gql_request",
              side_effect=mock_send_gql_request_all_fields)
def test_init_github_task_all_fields(mock_sendrequest):
    """
        Test init_github_task with mandatory fields
    """
    github_task_handler = GithubTaskHandler()
    task_params = {"title": "the_title", "body": "the_body", "handle_immediately": True, "assignee": 'the_assignee'}
    github_task_handler.init_github_task('app_context', task_params)

    mock_sendrequest.assert_called()
