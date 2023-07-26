"""
    This module describes the TechTeamBot class. It is the top-level class of the Tech Team Bot.
"""

import json
from pathlib import Path
from sources.FlaskAppWrapper import FlaskAppWrapper
from sources.listeners.SlackInteractionListener import SlackInteractionListener
import sources.utils.Constants as cst


class TechTeamBot(FlaskAppWrapper):
    """
        This class defines the app object to run with Flask. It inherits a Flask app wrapper to handle Flask specific
        operations.
    """

    def __init__(self, flask_app):
        FlaskAppWrapper.__init__(self, flask_app)
        self.__tokens = []
        self.__app_config = None

    def __load_keys(self):
        """
            Reads the config/keys/token.json file and store the results in a private attribute.
        """
        with open(Path(__file__).parent.parent / "config" / "keys" / "tokens.json", encoding='utf-8') as file_token:
            self.__tokens = json.load(file_token)

    def __setup_keys(self):
        """
            Manages the setup of the keys/token as config of the Flask app
        """
        self.__load_keys()
        self.app.config[cst.APP_CONFIG_TOKEN_SLACK_SIGNING_SECRET] = self.__tokens["slack_signing_secret"]
        self.app.config[cst.APP_CONFIG_TOKEN_SLACK_BOT_USER_TOKEN] = self.__tokens["slack_bot_user_token"]
        self.app.config[cst.APP_CONFIG_TOKEN_GITHUB_ACCESS_TOKEN] = self.__tokens["github_token"]

    def __setup_slack_interaction_endpoint(self):
        """
            Creates the endpoint for Slack interactions
        """
        slack_interaction_endpoint = SlackInteractionListener()
        self.add_endpoint("/slack/interaction", endpoint_name='ad', handler=slack_interaction_endpoint, methods=['POST'])

    def __load_config(self):
        with open(Path(__file__).parent.parent / "config" / "app.json", encoding='utf-8') as file_app_config:
            self.__app_config = json.load(file_app_config)

    def setup(self):
        """
            Manages the configuration of the app. Must be called before running the app.
        """
        self.__load_config()
        self.__setup_keys()
        self.__setup_slack_interaction_endpoint()

    def run(self, **kwargs):
        self.app.run(port=self.__app_config['port'], **kwargs)
