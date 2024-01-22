"""
    This module define the handler for Slack shortcuts.
"""


from flask import current_app
from sources.factories.SlackMessageFactory import SlackMessageFactory


class SlackBlockActionHandler():
    """
        Class to handle Slack block actions calls received by the app.
    """

    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.slack_message_factory = SlackMessageFactory()

    def process(self, payload_json):
        """
            Method called to process a request of type "shortcut". It identifies the callback assigned to the Slack shortcut
            and routes the request according to it to the right callback method.
        """

        # Retrieve the shortcut callback
        callback = payload_json['actions']['action_id']

        # Process the paylaod according to the callback
        if 'publish-release-note' == callback:
            current_app.logger.info("SlackBlockActionHandler: Publish release note callback.")
            self.publish_release_note_callback(payload_json)
        else:
            raise ValueError('Unknown action callback.')
        return {}

    def publish_release_note_callback(self, payload_json):
        """
            Callback method to process the Slack action "publish-release-note"
            The action value should be sent as a message to the release channel.
        """
        self.slack_message_factory.post_message(current_app.app_context(),
                                                self.slack_message_factory.get_channel('releases'),
                                                payload_json['actions']['value'])
