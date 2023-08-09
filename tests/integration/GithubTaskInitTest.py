"""
    Integration tests for the Github task creation
"""

import json
from pathlib import Path
from unittest.mock import patch
from freezegun import freeze_time
from sources.handlers.GithubTaskHandler import GithubTaskHandler
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory
from sources.models.InitGithubTaskParam import InitGithubTaskParam

# pylint: disable=unused-argument


def mock_send_gql_request_all_fields(*args, **kwargs):  # noqa: C901
    """
        This is the mock for all send_gql_request for the test_init_github_task_all_fields.
        It checks the values of the query_params for each requests.
    """
    def check_login_request(*args, **kwargs):
        # This is the request for user ID
        if args[2]['login'] != 'the_assignee':
            raise ValueError
        return {'user': {'id': 'the_assignee_id'}}

    def check_task_creation_request(*args, **kwargs):
        # This is the task creation ID
        if args[2]['task']['title'] != 'the_title':
            raise ValueError
        if args[2]['task']['body'] != 'the_body':
            raise ValueError
        if args[2]['task']['assigneeIds'] != ['the_assignee_id']:
            raise ValueError
        return {'addProjectV2DraftIssue': {'projectItem': {'id': 'the_item_id'}}}

    def check_status_request(*args, **kwargs):
        # Those are calls to set fields
        if 'iterationId' in args[2]['fieldMutation']['value']:
            # Call to set sprint
            if args[2]['fieldMutation']['value']['iterationId'] != "8824dd79":
                raise ValueError
            with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
                github_config = json.load(file_github_config)
                if args[2]['fieldMutation']['fieldId'] != github_config["sprintFieldId"]:
                    raise ValueError

        elif 'singleSelectOptionId' in args[2]['fieldMutation']['value']:
            # Call to set status
            with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
                github_config = json.load(file_github_config)
                if args[2]['fieldMutation']['value']['singleSelectOptionId'] != github_config["initialStatusValue"]:
                    raise ValueError
                if args[2]['fieldMutation']['fieldId'] != github_config["statusFieldId"]:
                    raise ValueError

        else:
            raise ValueError
        return {}

    def check_get_sprints_request(*args, **kwargs):
        # This is a get node request for the sprint:
        with open(Path(__file__).parent.parent / "utils" / "GithubGQLReturns.json", encoding='utf-8') as file_github_config:
            returns = json.load(file_github_config)
            return returns["get_iterations"]

    if 'login' in args[2]:
        return check_login_request(*args, **kwargs)

    if 'task' in args[2] and 'title' in args[2]['task'] and 'body' in args[2]['task']:
        return check_task_creation_request(*args, **kwargs)

    if 'fieldMutation' in args[2]:
        return check_status_request(*args, **kwargs)

    if 'node_id' in args[2]:
        return check_get_sprints_request(*args, **kwargs)

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
    task_params = InitGithubTaskParam(title="the_title", body="the_body", handle_immediately=True, assignee='the_assignee')
    github_task_handler.init_github_task('app_context', task_params)

    mock_sendrequest.assert_called()
