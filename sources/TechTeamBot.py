import json
import sources.utils.constants as cst

from sources.FlaskAppWrapper import FlaskAppWrapper
from sources.listeners.SlackInteractionListener import SlackInteractionListener
from pathlib import Path

class TechTeamBot(FlaskAppWrapper):

    __tokens = []
    __app_config = None

    def __load_keys(self):
        file_token = open(Path(__file__).parent.parent / "config" / "keys" / "tokens.json", encoding='utf-8')
        self.__tokens = json.load(file_token)

    def __setup_keys(self):
        self.__load_keys()
        self.app.config[cst.APP_CONFIG_TOKEN_SLACK_SIGNING_SECRET] = self.__tokens["slack_signing_secret"]
        self.app.config[cst.APP_CONFIG_TOKEN_SLACK_BOT_USER_TOKEN] = self.__tokens["slack_bot_user_token"]
        self.app.config[cst.APP_CONFIG_TOKEN_GITHUB_ACCESS_TOKEN] = self.__tokens["github_token"]

    def __setup_slack_interaction_endpoint(self):
        slack_interaction_endpoint = SlackInteractionListener()
        self.add_endpoint("/slack/interaction", endpoint_name='ad', handler=slack_interaction_endpoint, methods=['POST'])

    def __load_config(self):
        file_app_config = open(Path(__file__).parent.parent / "config" / "app.json", encoding='utf-8')
        self.__app_config = json.load(file_app_config)

    def setup(self):
        self.__load_config()
        self.__setup_keys()
        self.__setup_slack_interaction_endpoint()

    def run(self, **kwargs):
        self.app.run(port=self.__app_config['port'], **kwargs)

