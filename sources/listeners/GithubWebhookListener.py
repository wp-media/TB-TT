"""
    This module defines the endpoint handler (called listener) for the Slack command endpoint.
"""
import json
from flask import request, current_app
from sources.handlers.GithubWebhookHandler import GithubWebhookHandler
from sources.utils import Security
import sources.utils.Constants as cst


class GithubWebhookListener():
    """
        Class to define the GitHub Webhook endpoint listener. It is callable and called when the right url is used.
    """

    def __init__(self):
        """
            The listener instanciates the handlers it will pass the request to so that it is processed.
        """
        self.github_webhook_handler = GithubWebhookHandler()
        self.__github_access_token = None

    def __get_github_webhook_secret(self):
        """
            Returns the GitHub secret.
            If not available yet, the Github secret is retrieved from the Flask app configs.
        """
        if self.__github_access_token is None:
            self.__github_access_token = current_app.config[cst.APP_CONFIG_TOKEN_GITHUB_WEBHOOK_SECRET]
        return self.__github_access_token

    def __call__(self):
        """
            Method called to process a request on the registered endpoint.
            It is subject to signed authentication.
            The method extracts the payload and route it to the correct handler.
            This method catches errors and manages their mapping to HTTP error codes.
        """

        # Check the Webhook signature
        security_check = Security.validate_github_webhook_signature(request, self.__get_github_webhook_secret())
        if not security_check:
            return 'Wrong webhook signature.', 401

        # Retrieve the payload of the POST request
        payload_json = json.loads(request.data.decode('utf-8'))
        # Route the request to the correct handler
        response_payload = {}
        try:
            response_payload = self.github_webhook_handler.process(payload_json)
        except ValueError as error:
            return str(error), 500
        except KeyError as error:
            return str(error), 500
        except NotImplementedError as error:
            return str(error), 501
        # pylint: disable-next=broad-exception-caught
        except Exception as error:
            return str(error), 500
        return response_payload, 200
