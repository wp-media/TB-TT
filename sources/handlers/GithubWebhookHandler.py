"""
    This module defines the handler for GitHub task (ProjectV2Item) related logic.
"""
import json
from threading import Thread
from pathlib import Path
from flask import current_app
from sources.handlers.GithubTaskHandler import GithubTaskHandler
from sources.handlers.GithubReleaseHandler import GithubReleaseHandler
from sources.models.GithubReleaseParam import GithubReleaseParam


class GithubWebhookHandler():
    """
        Class managing the business logic related to Github Webhooks

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.github_project_item_handler = GithubTaskHandler()
        self.github_release_handler = GithubReleaseHandler()
        with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
            self.github_config = json.load(file_github_config)

    def process(self, payload_json):
        """
            Method called to process a rGithub webhook. It identifies the callback assigned to the webhook type
            and routes the request according to it to the right callback method.
        """
        if "projects_v2_item" in payload_json:
            self.project_v2_item_update_callback(payload_json)
        elif "release" in payload_json:
            self.release_callback(payload_json)
        else:
            raise ValueError('Unknown webhook payload.')
        return {}

    def project_v2_item_update_callback(self, payload_json):
        """
            Callback for webhooks linked to a project V2 item update.
            Filter out irrelevant webhooks.
            Retrieve the node_id of the updated item and start a dedicated thread to handle the udpate
        """
        # Keep only update actions
        if "action" not in payload_json or "edited" != payload_json["action"]:
            current_app.logger.info("project_v2_item_update_callback: Not an update action.")
            return
        # Keep only changes on status or assignees
        if (payload_json["changes"]["field_value"]["field_type"] != "assignees" and
           payload_json["changes"]["field_value"]["field_node_id"] != self.github_config['statusFieldId']):
            current_app.logger.info("project_v2_item_update_callback: Update not related to assignee nor status.")
            return

        node_id = payload_json["projects_v2_item"]["node_id"]
        thread = Thread(target=self.github_project_item_handler.process_update, kwargs={
            "app_context": current_app.app_context(), "node_id": node_id})
        current_app.logger.info("project_v2_item_update_callback: Starting processing thread...")
        thread.start()

    def release_callback(self, payload_json):
        """
            Callback for webhooks linked to a Github release.
            Filter out irrelevant webhooks.
            Retrieve the relevant data in paylaod and start a thread for further processing
        """
        # Keep only released actions
        if "action" not in payload_json or "released" != payload_json["action"]:
            current_app.logger.info("release_callback: Not a released release action.")
            return
        # Keep only changes on status or assignees
        repository_name = payload_json["repository"]["name"]
        if repository_name not in self.github_config["repoNameToReadable"]:
            current_app.logger.info("release_callback: Release not linked to a tracked repository.")
            return

        version = payload_json["release"]["tag_name"]
        body = payload_json["release"]["body"]

        release_params = GithubReleaseParam(repository_name, version, body)
        thread = Thread(target=self.github_release_handler.process_release, kwargs={
            "app_context": current_app.app_context(), "release_params": release_params})
        current_app.logger.info("release_callback: Starting processing thread...")
        thread.start()
