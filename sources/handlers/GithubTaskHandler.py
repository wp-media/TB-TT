"""
    This module defines the handler for GitHub task (ProjectV2Item) related logic.
"""
import json
from pathlib import Path
from flask import current_app
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory
from sources.factories.SlackMessageFactory import SlackMessageFactory
from sources.models.InitGithubTaskParam import InitGithubTaskParam


class GithubTaskHandler():
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

    def get_task_link(self, project_number, view_number, item_number):
        """
            Generates the URL to display a Github task of WP Media from the project number and the project item number
        """
        # pylint: disable-next=line-too-long
        return f"https://github.com/orgs/wp-media/projects/{project_number}/views/{view_number}?pane=issue&itemId={item_number}" # noqa

    def get_board_view(self, flow):
        """
            Returns the board view associated to a given flow.
        """
        view_number = self.github_config["board_views"]["default"]

        if flow is not None and flow in self.github_config["board_views"]:
            view_number = self.github_config["board_views"][flow]

        return view_number

    def init_github_task(self, app_context, task_params: InitGithubTaskParam):
        """
            Create a GitHub task in the configured project according to the task parameters.
            To do so, a GQL Mutation is requested to the GitHub API.

            task_params
                - title (Mandatory): Title of the task
                - body (Mandatory): Description of the task
        """
        mutation_param = {}
        # Check mandatory parameters
        if task_params.title is None:
            raise TypeError('Missing title in task_params')
        mutation_param['title'] = task_params.title

        if task_params.body is None:
            raise TypeError('Missing body in task_params')
        mutation_param['body'] = task_params.body

        # Check optional parameters

        assignee_id = None
        if 'no-assignee' != task_params.assignee:
            assignee_id = self.github_gql_call_factory.get_user_id_from_login(app_context, task_params.assignee)
        if assignee_id is not None:
            mutation_param['assigneeIds'] = [assignee_id]

        # Create the task and retrieve its ID
        project_item = self.github_gql_call_factory.create_github_task(app_context, mutation_param)

        if project_item is not None:

            # Send notifications to Slack
            if task_params.initiator is not None:
                text = "You created a Github task: " + self.get_task_link(
                    project_item.project_number,
                    self.get_board_view(task_params.flow),
                    project_item.item_database_id
                    )
                self.slack_message_factory.post_message(app_context, task_params.initiator, text)

            # Set the task to Todo
            self.github_gql_call_factory.set_task_to_initial_status(app_context, project_item.item_id)

            if task_params.handle_immediately:
                # Set the task to the current sprint
                self.github_gql_call_factory.set_task_to_current_sprint(app_context, project_item.item_id)

            if 'dev-team-escalation' == task_params.flow:
                # Set the issue type
                self.github_gql_call_factory.set_task_to_dev_team_escalation_type(app_context, project_item.item_id)

                # Send message on Slack channel
                main_text = f"{task_params.title} by <@{task_params.initiator}>: " + self.get_task_link(
                    project_item.project_number,
                    self.get_board_view(task_params.flow),
                    project_item.item_database_id)
                thread = self.slack_message_factory.post_message(app_context,
                                                                 self.slack_message_factory.get_channel(task_params.flow),
                                                                 main_text)

                # Add details of the escalation in the thread
                if thread is not None:
                    detail_text = f"{task_params.body}"
                    self.slack_message_factory.post_reply(app_context,
                                                          thread["channel"], thread["ts"], detail_text)

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
        else:
            app_context.push()
            current_app.logger.info("GitHubTaskHandler.process_update: No corresponding flow.")

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
        query = 'itemId=' + str(project_item_details["databaseId"]) + ' in:dev-team-escalation from:tbtt'
        found_slack_messages = self.slack_message_factory.search_message(app_context, query)
        slack_thread = found_slack_messages["messages"]["matches"][0]
        # Maybe update the thread parent
        old_parent_message_split = slack_thread["text"].splitlines(False)
        new_parent_message = old_parent_message_split[0]
        new_parent_message += '\n' + 'Status: ' + project_item_status + '\n'
        new_parent_message += 'Assignees: ' + project_item_assignees
        if slack_thread["text"] != new_parent_message:
            self.slack_message_factory.edit_message(app_context, slack_thread["channel"]["id"],
                                                    slack_thread["ts"], new_parent_message)

            # Post Slack message in the thread
            thread_response = 'This escalation is now ' + project_item_status
            thread_response += ' and currently assigned to: ' + project_item_assignees
            self.slack_message_factory.post_reply(app_context,
                                                  slack_thread["channel"]["id"], slack_thread["ts"], thread_response)
        else:
            app_context.push()
            current_app.logger.info("dev_team_escalation_update: Nex message identical to the current one.")
