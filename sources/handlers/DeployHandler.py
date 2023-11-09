"""
    This module defines the handler for deployment with the group.One Deploy Proxy
    This handler is just a API call factory, as there is no special business logic.
"""
import requests
from flask import current_app
import sources.utils.Constants as cst
from sources.models.DeployHandlerParam import DeployHandlerParam


class DeployHandler():
    """
        Class managing the interface with group.One Deploy Proxy

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.__godp_token = None

    def _get_godp_token(self, app_context):
        """
            Returns the godp auth token.
            If not available yet, the token is retrieved from the Flask app configs.
        """
        if self.__godp_token is None:
            app_context.push()  # The factory usually runs in a dedicated thread, so Flask app context must be applied.
            self.__godp_token = current_app.config[cst.APP_CONFIG_TOKEN_GODP_AUTH_TOKEN]
        return self.__godp_token

    def deploy_commit(self, app_context, task_params: DeployHandlerParam):
        request_header = {"Content-type": "application/json",
                          "Authorization": "Bearer " + self._get_godp_token(app_context)}
        request_payload = {}
        request_payload['application'] = task_params.app
        request_payload['environment'] = task_params.env
        request_payload['ref'] = task_params.commit
        print(request_payload)
        print(request_header)
        result = requests.post(url=self.post_message_url,
                               headers=request_header,
                               json=request_payload, timeout=3000)
        if result is None:
            raise ValueError('GODP call failed.')
        result_json = result.json()
        if result_json["url"]:
            print("GODP response: " + result_json)
        else:
            raise ValueError('GODP did not return a deploy URL.')
