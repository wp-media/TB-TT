"""
    This module defines the handler for GitHub task (ProjectV2Item) related logic.
"""

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

    def get_task_link(self, project_number, item_number):
        """
            Generates the URL to display a Github task of WP Media from the project number and the project item number
        """
        return f"https://github.com/orgs/wp-media/projects/{project_number}?pane=issue&itemId={item_number}"

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
                    project_item.project_number, project_item.item_database_id)
                self.slack_message_factory.post_message(app_context, task_params.initiator, text)

            if 'dev-team-escalation' == task_params.flow:
                # Set the issue type
                self.github_gql_call_factory.set_task_to_dev_team_escalation_type(app_context, project_item.item_id)

                # Send message on Slack channel
                text = f"{task_params.title} by <@{task_params.initiator}>: " + self.get_task_link(
                    project_item.project_number, project_item.item_database_id)
                self.slack_message_factory.post_message(app_context,
                                                        self.slack_message_factory.get_channel(task_params.flow),
                                                        text)

            # Set the task to Todo
            self.github_gql_call_factory.set_task_to_initial_status(app_context, project_item.item_id)

            if task_params.handle_immediately:
                # Set the task to the current sprint
                self.github_gql_call_factory.set_task_to_current_sprint(app_context, project_item.item_id)
