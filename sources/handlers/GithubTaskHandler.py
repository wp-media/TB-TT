"""
    This module defines the handler for GitHub task (ProjectV2Item) related logic.
"""

from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory


class GithubTaskHandler():
    """
        Class managing the business logic related to Github ProjectV2 items

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.github_gql_call_factory = GithubGQLCallFactory()

    def init_github_task(self, app_context, task_params):
        """
            Create a GitHub task in the configured project according to the task parameters.
            To do so, a GQL Mutation is requested to the GitHub API.

            task_params:
                - title (Mandatory): Title of the task
                - body (Mandatory): Description of the task
        """
        mutation_param = {}
        # Check mandatory parameters
        if 'title' not in task_params:
            raise TypeError('Missing title in task_params')
        mutation_param['title'] = task_params['title']

        if 'body' not in task_params:
            raise TypeError('Missing body in task_params')
        mutation_param['body'] = task_params['body']

        # Check optional parameters
        handle_immediately = False
        if 'handle_immediately' in task_params:
            handle_immediately = task_params['handle_immediately']

        assignee_id = None
        if 'assignee' in task_params and 'no-assignee' != task_params['assignee']:
            assignee = task_params['assignee']
            assignee_id = self.github_gql_call_factory.get_user_id_from_login(app_context, assignee)
        if assignee_id is not None:
            mutation_param['assigneeIds'] = [assignee_id]

        # Create the task and retrieve its ID
        project_item_id = self.github_gql_call_factory.create_github_task(app_context, mutation_param)

        if project_item_id is not None:
            # Set the task to Todo
            self.github_gql_call_factory.set_task_to_initial_status(app_context, project_item_id)

            if handle_immediately:
                # Set the task to the current sprint
                self.github_gql_call_factory.set_task_to_current_sprint(app_context, project_item_id)
