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
from sources.models.CreatedGithubTaskParam import CreatedGithubTaskParam


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
            Returns a HTTP Transport layer to the Github API.
        """
        github_access_token = self.__get_github_access_token(app_context)
        github_http_transport = RequestsHTTPTransport(
                url=self.github_gql_url, headers={'Authorization': f'Bearer {github_access_token}'},
                retries=3
            )
        return github_http_transport

    def __get_github_gql_client(self, app_context):
        """
            Returns the GQL Client to the Github API.
            If it is not created yet, the method creates it before returning.
        """
        github_http_transport = self.__get_github_http_transport(app_context)
        github_gql_client = gql.Client(transport=github_http_transport, fetch_schema_from_transport=False)
        return github_gql_client

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

    def set_task_field_value(self, app_context, project_item_id, field_id, value_id):
        """
            Performs a GitHub mutation to assign the given value to the given field for the given task.
        """
        query = gql.gql(
            """
            mutation SetValueToProjectV2TaskField($fieldMutation: UpdateProjectV2ItemFieldValueInput!) {
                updateProjectV2ItemFieldValue(input: $fieldMutation) {
                    clientMutationId
                }
            }
        """
        )

        mutation_param = {}
        mutation_param['clientMutationId'] = 'my_key'
        mutation_param['projectId'] = self.github_config['projectId']
        mutation_param['itemId'] = project_item_id
        mutation_param['fieldId'] = field_id
        mutation_param['value'] = value_id

        query_params = {}
        query_params['fieldMutation'] = mutation_param

        self.__send_gql_request(app_context, query, query_params)

    def set_task_to_current_sprint(self, app_context, project_item_id):
        """
            Performs a GitHub mutation to assign the given task to the current sprint of the project.
        """

        iteration_id = self.get_current_sprint_id(app_context)
        if iteration_id is None:
            raise ValueError('Current iteration not found.')

        self.set_task_field_value(
            app_context,
            project_item_id,
            self.github_config['sprintFieldId'],
            {'iterationId': iteration_id}
        )

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

    def set_task_to_initial_status(self, app_context, project_item_id):
        """
            Performs a GitHub mutation to assign initial status to the task.
        """
        self.set_task_field_value(
            app_context,
            project_item_id,
            self.github_config['statusFieldId'],
            {'singleSelectOptionId': self.github_config['initialStatusValue']}
        )

    def set_task_to_dev_team_escalation_type(self, app_context, project_item_id):
        """
            Performs a GitHub mutation to assign the type dev-team-escalation
        """
        self.set_task_field_value(
            app_context,
            project_item_id,
            self.github_config['typeFieldId'],
            {'singleSelectOptionId': self.github_config['dev-team-escalationStatusValue']}
        )

    def create_github_task(self, app_context, mutation_param):
        """
            Create a GitHub task in the configured project according to the task parameters.
            To do so, a GQL Mutation is requested to the GitHub API.

            task_params:
                - title (Mandatory): Title of the task
                - body (Mandatory): Description of the task
                - assigneeIds (optional): ID of the GitHub user to assign the task to
        """

        # Check mandatory parameters
        if 'title' not in mutation_param:
            raise TypeError('Missing title in task_params')

        if 'body' not in mutation_param:
            raise TypeError('Missing body in task_params')

        query = gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    projectItem {
                        id
                        databaseId
                        project {
                            number
                        }
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

        project_item = {}
        try:
            # pylint: disable=unsubscriptable-object
            project_item = CreatedGithubTaskParam(
                response['addProjectV2DraftIssue']['projectItem']['id'],
                response['addProjectV2DraftIssue']['projectItem']['databaseId'],
                response['addProjectV2DraftIssue']['projectItem']['project']['number']
            )
            # pylint: enable=unsubscriptable-object
        except KeyError:
            project_item = None
        return project_item

    def get_dev_team_escalation_item_update(self, app_context, node_id):
        """
            Retrieves information on the project item relevant for the dev-team-escalation update flow
        """
        query = gql.gql("""
                    query GetProjectItemForUpdate($node_id: ID!) {
                        node(id: $node_id) {
                            ... on ProjectV2Item {
                                databaseId
                                column: fieldValueByName(name: "Status") {
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                    name
                                    }
                                }
                                draftIssue: content {
                                    ... on DraftIssue {
                                        assignees(first: 20) {
                                            nodes {
                                                login
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                """)
        query_params = {}
        query_params['node_id'] = node_id
        response = self.__send_gql_request(app_context, query, query_params)
        # pylint: disable-next=unsubscriptable-object
        return response["node"]

    def get_project_item_for_update(self, app_context, node_id):
        """
            Retrieves information on the project item relevant for the handler to select what flow to perform.
            Currently returned: "Type" custom SingleSelect field
        """
        query = gql.gql("""
                    query GetProjectItemForUpdate($node_id: ID!) {
                        node(id: $node_id) {
                            ... on ProjectV2Item {
                                typeField: fieldValueByName(name: "Type") {
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                    name
                                    }
                                }
                            }
                        }
                    }
                """)
        query_params = {}
        query_params['node_id'] = node_id
        response = self.__send_gql_request(app_context, query, query_params)
        # pylint: disable-next=unsubscriptable-object
        return response["node"]
