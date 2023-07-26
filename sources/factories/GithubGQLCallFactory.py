import gql
import json
import sources.utils.constants as cst

from flask import current_app
from gql.transport.requests import RequestsHTTPTransport
from pathlib import Path


class GithubGQLCallFactory():

    github_gql_url = ''
    github_config = None
    __github_access_token = None
    __github_http_transport = None
    __github_gql_client = None

    def __init__(self):
        self.github_gql_url = 'https://api.github.com/graphql'

        file_github_config = open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8')
        self.github_config = json.load(file_github_config)
        return

    def __get_github_access_token(self, app_context):
        if self.__github_access_token is None:
            app_context.push()
            self.__github_access_token = current_app.config[cst.APP_CONFIG_TOKEN_GITHUB_ACCESS_TOKEN]
        return self.__github_access_token
    
    def __get_github_http_transport(self, app_context):
        if self.__github_http_transport is None:
            github_access_token = self.__get_github_access_token(app_context)
            self.__github_http_transport = RequestsHTTPTransport(url=self.github_gql_url, headers={'Authorization': f'Bearer {github_access_token}'})
        return self.__github_http_transport
    
    def __get_github_gql_client(self, app_context):
        if self.__github_gql_client is None:
            github_http_transport = self.__get_github_http_transport(app_context)
            self.__github_gql_client = gql.Client(transport=github_http_transport, fetch_schema_from_transport=True)
        return self.__github_gql_client

    def create_github_task(self, app_context, task_params):
        query = gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    clientMutationId
                }
            }
        """
        )
        task_params["clientMutationId"] = 'my_key'
        task_params["projectId"] = self.github_config['projectId']
        query_params = {}
        query_params['task'] = task_params

        client = self.__get_github_gql_client(app_context)
        client.execute(query, variable_values=query_params)
