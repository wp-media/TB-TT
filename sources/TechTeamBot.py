"""
    This module describes the TechTeamBot class. It is the top-level class of the Tech Team Bot.
"""

import json
from pathlib import Path
from decouple import config
from sources.FlaskAppWrapper import FlaskAppWrapper
from sources.listeners.SlackInteractionListener import SlackInteractionListener
from sources.listeners.SlackCommandListener import SlackCommandListener
import sources.utils.Constants as cst


class TechTeamBot(FlaskAppWrapper):
    """
        This class defines the app object to run with Flask. It inherits a Flask app wrapper to handle Flask specific
        operations.
    """

    def __init__(self, flask_app):
        FlaskAppWrapper.__init__(self, flask_app)
        self.__app_config = None

    def __load_key(self, var_name, key_name):
        """
            Reads var_name in environment variables and store it as an app.config under key_name.
            Throws a KeyError if it is not found.
        """
        BASE_DIR = Path(__file__).parent.parent  # noqa :F841 # pylint: disable=invalid-name, unused-variable
        self.app.config[key_name] = config(var_name)

        if self.app.config[key_name] is None:
            raise KeyError(var_name + ' is not found.')

    def __setup_keys(self):
        """
            Manages the setup of the keys/token as config of the Flask app
        """
        self.__load_key("TBTT_SLACK_SIGNING_SECRET", cst.APP_CONFIG_TOKEN_SLACK_SIGNING_SECRET)
        self.__load_key("TBTT_SLACK_BOT_USER_TOKEN", cst.APP_CONFIG_TOKEN_SLACK_BOT_USER_TOKEN)
        self.__load_key("TBTT_GITHUB_TOKEN", cst.APP_CONFIG_TOKEN_GITHUB_ACCESS_TOKEN)

    def __setup_slack_interaction_endpoint(self):
        """
            Creates the endpoint for Slack interactions
        """
        slack_interaction_endpoint = SlackInteractionListener()
        self.add_endpoint("/slack/interaction", endpoint_name='slack_interaction', handler=slack_interaction_endpoint, methods=['POST'])

    def __setup_slack_command_endpoint(self):
        """
            Creates the endpoint for Slack interactions
        """
        slack_command_endpoint = SlackCommandListener()
        self.add_endpoint("/slack/command", endpoint_name='slack_command', handler=slack_command_endpoint, methods=['POST'])

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
        self.__setup_slack_command_endpoint()

    def run(self, **kwargs):
        self.app.run(port=self.__app_config['port'], **kwargs)
