"""
    This module defines the handler for GitHub task (ProjectV2Item) related logic.
"""
from threading import Thread
from flask import current_app
from sources.handlers.GithubProjectItemHandler import GithubProjectItemHandler


class GithubWebhookHandler():
    """
        Class managing the business logic related to Github Webhooks

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.github_project_item_handler = GithubProjectItemHandler()

    def process(self, payload_json):
        """
            Method called to process a rGithub webhook. It identifies the callback assigned to the webhook type
            and routes the request according to it to the right callback method.
        """
        if "projects_v2_item" in payload_json:
            if "action" in payload_json and "edited" == payload_json["action"]:
                self.project_v2_item_update_callback(payload_json)
        else:
            raise ValueError('Unknown webhook payload.')
        return {}

    def project_v2_item_update_callback(self, payload_json):
        """
            Callback for webhooks linked to a project V2 item update.
            Retrieve the node_id of the updated item and start a dedicated thread to handle the udpate
        """
        node_id = payload_json["projects_v2_item"]["node_id"]
        thread = Thread(target=self.github_project_item_handler.process_update, kwargs={
            "app_context": current_app.app_context(), "node_id": node_id})
        thread.start()
