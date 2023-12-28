"""
    This module define the handler for Slack command.
"""


from threading import Thread
from flask import current_app
from sources.factories.SlackModalFactory import SlackModalFactory
from sources.handlers.ServerListHandler import ServerListHandler


class SlackCommandHandler():
    """
        Class to handle Slack command calls received by the app.
    """

    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.slack_modal_factory = SlackModalFactory()
        self.server_list_handler = ServerListHandler()

    def process(self, payload_json):
        """
            Method called to process a request of type "command". It identifies the callback assigned to the Slack command
            and routes the request according to it to the right callback method.
        """

        # Retrieve the shortcut callback
        command = payload_json['command']
        # Process the paylaod according to the callback
        if '/dev-team-escalation' == command:
            self.dev_team_escalation_command_callback(payload_json)
        elif '/wprocket-ips' == command:
            self.wp_rocket_ips_command_callback(payload_json)
        elif '/deploy-manager' == command:
            self.deploy_manager_command_callback(payload_json)
        else:
            raise ValueError('Unknown command.')
        return {}

    def dev_team_escalation_command_callback(self, payload_json):
        """
            Callback method to process the Slack command "/dev-team-escalation"
            A modal should be opened for the user. A dedicated thread is started to create this modal.
        """
        trigger_id = payload_json['trigger_id']

        current_app.logger.info("dev_team_escalation_command_callback: Starting processing thread...")
        thread = Thread(
            target=self.slack_modal_factory.dev_team_escalation_modal, kwargs={
                "app_context": current_app.app_context(), "trigger_id": trigger_id})
        thread.start()

    def wp_rocket_ips_command_callback(self, payload_json):
        """
            Callback method to process the Slack command "/wprocket-ips"
        """
        initiator = payload_json["user_id"]

        current_app.logger.info("wp_rocket_ips_command_callback: Starting processing thread...")
        thread = Thread(
            target=self.server_list_handler.send_wp_rocket_ips_to_slack, kwargs={
                "app_context": current_app.app_context(), "slack_user": initiator})
        thread.start()

    def deploy_manager_command_callback(self, payload_json):
        """
            Callback method to process the Slack command "/deploy-manager"
        """
        trigger_id = payload_json['trigger_id']

        current_app.logger.info("deploy_manager_command_callback: Starting processing thread...")
        thread = Thread(
            target=self.slack_modal_factory.deploy_manager_modal, kwargs={
                "app_context": current_app.app_context(), "trigger_id": trigger_id})
        thread.start()
