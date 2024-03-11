"""
    This module defines the endpoint handler (called listener) for the Slack command endpoint.
"""

from flask_slacksigauth import slack_sig_auth
from flask import request
from sources.handlers.SlackCommandHandler import SlackCommandHandler


class SlackCommandListener():
    """
        Class to define the Slack Interaction endpoint handler. It is callable and called when the right url is used.
    """

    def __init__(self):
        """
            The listener instanciates the handlers it will pass the request to so that it is processed.
        """
        self.slack_command_handler = SlackCommandHandler()

    @slack_sig_auth
    def __call__(self):
        """
            Method called to process a request on the registered endpoint.
            It is subject to signed authentication.
            The method extracts the payload and route it to the correct handler.
            This method catches errors and manages their mapping to HTTP error codes.
        """

        # Retrieve the payload of the POST request
        payload_json = request.form.to_dict()

        # Route the request to the correct handler
        response_payload = {}
        try:
            response_payload = self.slack_command_handler.process(payload_json)
        # pylint: disable=R0801
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
