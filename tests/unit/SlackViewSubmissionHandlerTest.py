"""
    Unit tests for the SlackViewSubmissionHandler.py main file
"""

from sources.handlers.SlackViewSubmissionHandler import SlackViewSubmissionHandler
from tests.utils.SlackModalSubmissions import SlackModalSubmissionRequestRepo

# pylint: disable=protected-access


def test_create_github_task_modal_retrieve_params():
    """
        Test __get_assignee_list when the assigneeList key does not exist in the config file.
        Only the No assignee option must be returned
    """
    slack_submission_handler = SlackViewSubmissionHandler()
    slack_payload_repo = SlackModalSubmissionRequestRepo()

    test_payload = slack_payload_repo.get_general_shortcut_github_task_submission_basic()
    task_param_uut = slack_submission_handler.create_github_task_modal_retrieve_params(test_payload)

    assert "This is a test" == task_param_uut["title"]
    assert "Task submitted by mathieu.lamiot through TBTT.\n\nThis is a test task" == task_param_uut["body"]
