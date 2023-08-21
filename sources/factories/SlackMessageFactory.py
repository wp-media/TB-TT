"""
    This module defines the factory for Slack messages (DM, public, etc.)
"""
import json
from pathlib import Path
import requests
from sources.factories.SlackFactoryAbstract import SlackFactoryAbstract


class SlackMessageFactory(SlackFactoryAbstract):
    """
        Class managing the business logic related to Github ProjectV2 items

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        SlackFactoryAbstract.__init__(self)
        with open(Path(__file__).parent.parent.parent / "config" / "slack.json", encoding='utf-8') as file_slack_config:
            self.slack_config = json.load(file_slack_config)

        self.post_message_url = 'https://slack.com/api/chat.postMessage'

    def post_message(self, app_context, channel, text):
        """
            Sends a message 'text' to the 'channel' as the app.
        """
        request_open_view_header = {"Content-type": "application/json",
                                    "Authorization": "Bearer " + self._get_slack_bot_user_token(app_context)}
        request_open_view_payload = {}
        request_open_view_payload['channel'] = channel
        request_open_view_payload['text'] = text
        requests.post(url=self.post_message_url,
                      headers=request_open_view_header,
                      json=request_open_view_payload, timeout=3000)

    def get_channel(self, flow):
        """
            Returns the channel to post to for a given use-case/flow
        """
        if 'dev-team-escalation' == flow:
            return self.slack_config["dev-team-escalation-channel"]
        raise ValueError('Unknown flow for get_channel.')
