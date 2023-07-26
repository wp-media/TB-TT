"""
    This module defines the factory for GQL requests to Github
"""

import json
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

    def create_github_task(self, app_context, task_params):
        """
            Create a GitHub task in the configured project according to the task parameters.
            To do so, a GQL Mutation is requested to the GitHub API.

            task_params:
                - title (Mandatory): Title of the task
                - body (Mandatory): Description of the task
        """
        # Check mandatory parameters
        if 'title' not in task_params:
            raise TypeError('Missing title in task_params')
        if 'body' not in task_params:
            raise TypeError('Missing body in task_params')

        query = gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    clientMutationId
                }
            }
        """
        )
        task_params['clientMutationId'] = 'my_key'
        task_params['projectId'] = self.github_config['projectId']
        query_params = {}
        query_params['task'] = task_params

        client = self.__get_github_gql_client(app_context)
        client.execute(query, variable_values=query_params)
