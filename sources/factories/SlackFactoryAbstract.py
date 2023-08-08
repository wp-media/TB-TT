"""
    This file contains an abstract class to provide basic functions for Slack factories, like handling tokens.
"""

from abc import ABCMeta
from flask import current_app
import sources.utils.Constants as cst


class SlackFactoryAbstract(metaclass=ABCMeta):
    """
        Class managing the business logic related to Github ProjectV2 items

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.__slack_bot_user_token = None

    def _get_slack_bot_user_token(self, app_context):
        """
            Returns the Slack Bot User token of the app.
            If not retrieved yet, it is retrieved from the Flask app configuration.
        """
        if self.__slack_bot_user_token is None:
            app_context.push()  # The factory usually runs in a dedicated thread, so Flask app context must be applied.
            self.__slack_bot_user_token = current_app.config[cst.APP_CONFIG_TOKEN_SLACK_BOT_USER_TOKEN]
        return self.__slack_bot_user_token
