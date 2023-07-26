"""
    This module define the handler for Slack shortcuts.
"""


from threading import Thread
from flask import current_app
from sources.factories.SlackModalFactory import SlackModalFactory


class SlackShortcutHandler():
    """
        Class to handle Slack shortcut calls received by the app.
    """

    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.slack_modal_factory = SlackModalFactory()

    def process(self, payload_json):
        """
            Method called to process a request of type "shortcut". It identifies the callback assigned to the Slack shortcut
            and routes the request according to it to the right callback method.
        """

        # Retrieve the shortcut callback
        callback = payload_json['callback_id']

        # Process the paylaod according to the callback
        if 'ttl_create_github_task_general_shortcut' == callback:
            self.create_github_task_general_shortcut_callback(payload_json)
        else:
            raise ValueError('Unknown shortcut callback.')
        return {}

    def create_github_task_general_shortcut_callback(self, payload_json):
        """
            Callback method to process the Slack shortcut "github_task_general_shortcut"
            A modal should be opened for the user. A dedicated thread is started to create this modal.
        """
        trigger_id = payload_json['trigger_id']

        thread = Thread(
            target=self.slack_modal_factory.create_github_task_modal, kwargs={
                "app_context": current_app.app_context(), "trigger_id": trigger_id})
        thread.start()
