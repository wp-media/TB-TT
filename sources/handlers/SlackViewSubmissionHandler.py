import json

from threading import Thread
from flask import current_app
from sources.factories.GithubGQLCallFactory import GithubGQLCallFactory

class SlackViewSubmissionHandler():

    github_gql_call_factory = None

    def __init__(self):
        self.github_gql_call_factory = GithubGQLCallFactory()
        return

    def process(self, payload_json):

        # Retrieve the modal callback
        callback = payload_json['view']['callback_id']

        # Process the paylaod according to the callback
        if 'ttl_create_github_task_modal_submit' == callback:
            self.create_github_task_modal_submit_callback(payload_json)
        else:
            raise ValueError('Unknown modal callback.')
        return {"response_action": "clear"}

    def create_github_task_modal_submit_callback(self, payload_json):
        task_params = self.create_github_task_modal_retrieve_params(payload_json)

        thread = Thread(target=self.github_gql_call_factory.create_github_task, kwargs={"app_context": current_app.app_context(), "task_params": task_params})
        thread.start()
        return

    def create_github_task_modal_retrieve_params(self, payload_json):
        task_params = {}      
        modal_values = payload_json["view"]["state"]["values"]
        for key in modal_values:
            for item_key in modal_values[key]:
                if 'task_title' == item_key:
                    task_params['title'] = modal_values[key][item_key]['value']
                elif 'task_description' == item_key:
                    task_params['body'] = modal_values[key][item_key]['value']
        return task_params
