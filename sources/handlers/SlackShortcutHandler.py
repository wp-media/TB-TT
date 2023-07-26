from threading import Thread
from flask import current_app
from sources.factories.SlackModalFactory import SlackModalFactory

class SlackShortcutHandler():

    slack_modal_factory = None

    def __init__(self):
        self.slack_modal_factory = SlackModalFactory()
        return

    def process(self, payload_json):
        # Retrieve the shortcut callback
        callback = payload_json['callback_id']

        # Process the paylaod according to the callback
        if 'ttl_create_github_task_general_shortcut' == callback:
            self.create_github_task_general_shortcut_callback(payload_json)
        else:
            raise ValueError('Unknown shortcut callback.')
        return {}
    
    def create_github_task_general_shortcut_callback(self, payload_json):
        trigger_id = payload_json['trigger_id']

        thread = Thread(
            target=self.slack_modal_factory.create_github_task_modal, kwargs={"app_context": current_app.app_context(), "trigger_id": trigger_id})
        thread.start()
        return
