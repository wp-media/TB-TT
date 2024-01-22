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
        self.update_message_url = 'https://slack.com/api/chat.update'
        self.search_message_url = 'https://slack.com/api/search.messages'

    def post_message(self, app_context, channel, text, blocks=None):
        """
            Sends a message 'text' to the 'channel' as the app.
        """
        request_open_view_header = {"Content-type": "application/json",
                                    "Authorization": "Bearer " + self._get_slack_bot_user_token(app_context)}
        request_open_view_payload = {}
        request_open_view_payload['channel'] = channel
        request_open_view_payload['text'] = text

        if blocks is not None:
            request_open_view_payload['blocks'] = blocks

        result = requests.post(url=self.post_message_url,
                               headers=request_open_view_header,
                               json=request_open_view_payload, timeout=3000)
        if result is None:
            raise ValueError('Slack post message failed.')
        result_json = result.json()
        if result_json["ok"] is False:
            raise ValueError('Slack post message was not completed.')
        return result_json

    def post_reply(self, app_context, channel, thread_ts, text):
        """
            Sends an answer 'text' to the 'thread_ts' thread in 'channel' as the app.
        """
        request_open_view_header = {"Content-type": "application/json",
                                    "Authorization": "Bearer " + self._get_slack_bot_user_token(app_context)}
        request_open_view_payload = {}
        request_open_view_payload['channel'] = channel
        request_open_view_payload['text'] = text
        request_open_view_payload['thread_ts'] = thread_ts
        requests.post(url=self.post_message_url,
                      headers=request_open_view_header,
                      json=request_open_view_payload, timeout=3000)

    def edit_message(self, app_context, channel, thread_ts, text):
        """
            Edits the message 'thread_ts' thread in 'channel' as the app, with the new 'text'
        """
        request_open_view_header = {"Content-type": "application/json",
                                    "Authorization": "Bearer " + self._get_slack_bot_user_token(app_context)}
        request_open_view_payload = {}
        request_open_view_payload['channel'] = channel
        request_open_view_payload['text'] = text
        request_open_view_payload['ts'] = thread_ts
        requests.post(url=self.update_message_url,
                      headers=request_open_view_header,
                      json=request_open_view_payload, timeout=3000)

    def search_message(self, app_context, query, count=None):
        """
            Perform a search message query with the Slack API
        """
        request_header = {"Content-type": "application/x-www-form-urlencoded",
                          "Authorization": "Bearer " + self._get_slack_user_token(app_context)}
        request_payload = {}
        request_payload['query'] = query
        if count is not None:
            request_payload['count'] = count
        result = requests.post(url=self.search_message_url,
                               headers=request_header,
                               data=request_payload, timeout=3000)
        if result is None:
            raise ValueError('Slack search message failed.')
        result_json = result.json()
        if result_json["ok"] is False:
            raise ValueError('Slack search message was not processed.')
        if 0 == result_json["messages"]["total"]:
            raise KeyError('Slack search message returned no messages.')
        return result_json

    def get_channel(self, flow):
        """
            Returns the channel to post to for a given use-case/flow
        """
        if 'dev-team-escalation' == flow:
            return self.slack_config["dev-team-escalation-channel"]
        if 'engineering-service-team' == flow:
            return self.slack_config["engineering-service-team-channel"]
        if 'releases' == flow:
            return self.slack_config["release-channel"]
        if 'ops' == flow:
            return self.slack_config["ops-channel"]
        raise ValueError('Unknown flow for get_channel.')

    def get_release_note_review_blocks(self, text):
        """
            Build the interactive messages for the release note publication flow
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Publish the release note in the release channel?"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Yes!",
                        "emoji": True
                    },
                    "value": text,
                    "action_id": "publish-release-note"
                }
            }
        ]
        return blocks
