"""
    This module defines the factory for GQL requests to Github
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import current_app
import gql
from gql.transport.requests import RequestsHTTPTransport
import sources.utils.Constants as cst


class GithubGQLCallFactory():
    """
        Class capable of performing GQL request to the Github GQL API.
    """

    def __init__(self):
        """
            Retrieve Github configuration from config/github.json
        """
        self.github_config = None
        self.__github_access_token = None
        self.__github_http_transport = None
        self.__github_gql_client = None

        self.github_gql_url = 'https://api.github.com/graphql'
        with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
            self.github_config = json.load(file_github_config)

    def __get_github_access_token(self, app_context):
        """
            Returns the GitHub access token.
            If not available yet, the Github access token is retrieved from the Flask app configs.
        """
        if self.__github_access_token is None:
            app_context.push()  # The factory usually runs in a dedicated thread, so Flask app context must be applied.
            self.__github_access_token = current_app.config[cst.APP_CONFIG_TOKEN_GITHUB_ACCESS_TOKEN]
        return self.__github_access_token

    def __get_github_http_transport(self, app_context):
        """
            Returns the HTTP Transport layer to the Github API.
            If it is not created yet, the method creates it before returning.
        """
        if self.__github_http_transport is None:
            github_access_token = self.__get_github_access_token(app_context)
            self.__github_http_transport = RequestsHTTPTransport(
                url=self.github_gql_url, headers={'Authorization': f'Bearer {github_access_token}'})
        return self.__github_http_transport

    def __get_github_gql_client(self, app_context):
        """
            Returns the GQL Client to the Github API.
            If it is not created yet, the method creates it before returning.
        """
        if self.__github_gql_client is None:
            github_http_transport = self.__get_github_http_transport(app_context)
            self.__github_gql_client = gql.Client(transport=github_http_transport, fetch_schema_from_transport=True)
        return self.__github_gql_client

    def __send_gql_request(self, app_context, query, params):
        """
            This methods handles sending a GQL request to GitHub through the dedicated HTTP Client.
        """
        client = self.__get_github_gql_client(app_context)
        response = client.execute(query, variable_values=params)
        return response

    def get_user_id_from_login(self, app_context, login):
        """
            Returns the GitHub ID of a user from its GitHub login.
            If it cannot be found or retrieve, returns None
        """
        result = None

        query_params = {}
        query_params['login'] = login
        query = gql.gql(
            """
            query userIDfromLogin($login: String!) {
                user(login: $login) {
                    id
                }
            }
            """
        )
        response = self.__send_gql_request(app_context, query, query_params)
        try:
            # pylint: disable-next=unsubscriptable-object
            result = response['user']['id']
        except TypeError:
            result = None
        return result

    def set_task_to_current_sprint(self, app_context, project_item_id):
        """
            Performs a GitHub mutation to assign the given task to the current sprint of the project.
        """

        mutation_param = {}
        iteration_id = self.get_current_sprint_id(app_context)
        if iteration_id is None:
            raise ValueError('Current iteration not found.')

        query = gql.gql(
            """
            mutation CreateProjectV2Task($fieldMutation: UpdateProjectV2ItemFieldValueInput!) {
                updateProjectV2ItemFieldValue(input: $fieldMutation) {
                    clientMutationId
                }
            }
        """
        )

        mutation_param['clientMutationId'] = 'my_key'
        mutation_param['projectId'] = self.github_config['projectId']
        mutation_param['itemId'] = project_item_id
        mutation_param['fieldId'] = self.github_config['sprintFieldId']
        mutation_param['value'] = {'iterationId': iteration_id}

        query_params = {}
        query_params['fieldMutation'] = mutation_param

        self.__send_gql_request(app_context, query, query_params)

    def get_current_sprint_id(self, app_context):
        """
            Returns the GitHub ID of the current sprint iteration for the project.
            To do this, we retrieve all sprints and find the current one by dates.
        """
        query = gql.gql("""
                    query GetIterations($node_id: ID!) {
                        node(id: $node_id) {
                            ... on ProjectV2IterationField {
                                configuration {
                                    duration,
                                    iterations {
                                        id,
                                        startDate
                                    }
                                }
                            }
                        }
                    }
                """)
        query_params = {}
        query_params['node_id'] = self.github_config['sprintFieldId']
        response = self.__send_gql_request(app_context, query, query_params)

        try:
            # pylint: disable-next=unsubscriptable-object
            duration = response['node']['configuration']['duration']
            now = datetime.now()
            # pylint: disable-next=unsubscriptable-object
            for iteration in response['node']['configuration']['iterations']:
                start_date = datetime.strptime(iteration['startDate'], "%Y-%m-%d")
                end_date = start_date + timedelta(days=duration)
                if start_date <= now < end_date:
                    return iteration['id']
        except KeyError:
            return None
        return None

    def create_github_task(self, app_context, task_params):
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
            assignee_id = self.get_user_id_from_login(app_context, assignee)
        if assignee_id is not None:
            mutation_param['assigneeIds'] = [assignee_id]

        query = gql.gql(
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

        mutation_param['clientMutationId'] = 'my_key'
        mutation_param['projectId'] = self.github_config['projectId']

        query_params = {}
        query_params['task'] = mutation_param

        response = self.__send_gql_request(app_context, query, query_params)

        if handle_immediately:
            try:
                # pylint: disable-next=unsubscriptable-object
                project_item_id = response['addProjectV2DraftIssue']['projectItem']['id']
            except KeyError:
                return
            self.set_task_to_current_sprint(app_context, project_item_id)
