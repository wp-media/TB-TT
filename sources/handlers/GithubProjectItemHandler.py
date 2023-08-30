"""
    This module defines the handler for GitHub task (ProjectV2Item) related logic.
"""
import json
from pathlib import Path
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory
from sources.factories.SlackMessageFactory import SlackMessageFactory


class GithubProjectItemHandler():
    """
        Class managing the business logic related to Github ProjectV2 items

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.github_gql_call_factory = GithubGQLCallFactory()
        self.slack_message_factory = SlackMessageFactory()
        with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
            self.github_config = json.load(file_github_config)

    def process_update(self, app_context, node_id):
        """
            Processing method when a project item is updated.
        """
        # Get the item details
        project_item_details = self.github_gql_call_factory.get_project_item_for_update(app_context, node_id)

        # Apply corresponding flows
        # dev-team-escalation update flow
        if (project_item_details["typeField"]
           and project_item_details["typeField"]["name"]
           and project_item_details["typeField"]["name"] == 'dev-team-escalation'):
            self.dev_team_escalation_update(app_context, node_id)

    def dev_team_escalation_update(self, app_context, node_id):
        """
            Perform the Slack update of a dev-team-escalation following an update of the GitHub draft issue
        """
        # Get assignee, status, itemID
        project_item_details = self.github_gql_call_factory.get_dev_team_escalation_item_update(app_context, node_id)
        project_item_status = project_item_details["column"]["name"]
        # Concatenate assignee logins
        project_item_assignees = ''
        if assignees_payload := project_item_details["draftIssue"]["assignees"]["nodes"]:
            for node in assignees_payload:
                project_item_assignees += node["login"] + ', '
        else:
            project_item_assignees = 'No one.'

        # Search for Slack thread based on channel, author and itemId part of the GitHub link
        query = 'itemId=' + str(project_item_details["databaseId"]) + ' in:dev-team-escalation from:TB-TT'
        found_slack_messages = self.slack_message_factory.search_message(app_context, query)
        print(found_slack_messages)
        slack_thread = found_slack_messages["messages"]["matches"][0]

        # Maybe update the thread parent
        old_parent_message_split = slack_thread["text"].splitlines(True)
        new_parent_message = old_parent_message_split[0]
        new_parent_message += '\n' + 'Status: ' + project_item_status + '\n'
        new_parent_message += 'Assignees: ' + project_item_assignees
        print(slack_thread["text"])
        print(new_parent_message)
        if slack_thread["text"] != new_parent_message:
            self.slack_message_factory.edit_message(app_context, slack_thread["channel"]["id"],
                                                    slack_thread["ts"], new_parent_message)

            # Post Slack message in the thread
            thread_response = 'This escalation is now ' + project_item_status
            thread_response += ' and currently assigned to: ' + project_item_assignees
            self.slack_message_factory.post_reply(app_context,
                                                  slack_thread["channel"]["id"], slack_thread["ts"], thread_response)
