"""
    This module defines the handler for deployment with the group.One Deploy Proxy
    This handler is just a API call factory, as there is no special business logic.
"""
import requests
from flask import current_app
import json
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
        self.godp_deploy_url = "https://godp.wp-media.me/v1/deploy"

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
        app_context.push()
        request_header = {"Content-type": "application/json",
                          "Authorization": "Bearer " + self._get_godp_token(app_context)}
        request_payload = {}
        request_payload['application'] = task_params.app
        request_payload['environment'] = task_params.env
        request_payload['ref'] = task_params.commit

        current_app.logger.info("deploy_commit: Requesting a deployment:/n" +
                                json.dumps(request_payload) + "/n" +
                                json.dumps(request_header))
        result = requests.post(url=self.godp_deploy_url,
                               headers=request_header,
                               json=request_payload, timeout=3000)
        if result is None:
            current_app.logger.error("deploy_commit: GODP call failed.")
            raise ValueError('GODP call failed.')
        result_json = result.json()
        if result_json["url"]:
            current_app.logger.info("deploy_commit: GODP Response:/n" + result_json)
        else:
            current_app.logger.error("deploy_commit: GODP did not return a deploy URL.")
            raise ValueError('GODP did not return a deploy URL.')
