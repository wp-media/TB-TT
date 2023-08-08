"""
    This module defines the factory for Slack messages (DM, public, etc.)
"""
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
        requests.post(url=self.post_message_url, headers=request_open_view_header,
                      json=request_open_view_payload, timeout=3000)
