"""
    This module defines a factory class, able to create Slack modals and open them for the Slack user.
"""
import json
from pathlib import Path
import requests
from sources.factories.SlackFactoryAbstract import SlackFactoryAbstract


class SlackModalFactory(SlackFactoryAbstract):
    """
        Class capable of creating and opening modal views for Slack users.
    """

    def __init__(self):
        SlackFactoryAbstract.__init__(self)
        self.open_view_url = 'https://slack.com/api/views.open'
        self.__assignee_list = None

    def __get_assignee_list(self):
        """
            Generate the list of options for the drop-down select of assignee, from thegithub.json config file.
        """
        if self.__assignee_list is None:
            self.__assignee_list = []
            self.__assignee_list.append({
                                            "text": {
                                                "type": "plain_text",
                                                "text": "No assignee"
                                            },
                                            "value": "no-assignee"
                                        })
            with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
                github_config = json.load(file_github_config)
            if "assigneeList" in github_config:
                for key, value in github_config["assigneeList"].items():
                    self.__assignee_list.append({
                                                    "text": {
                                                        "type": "plain_text",
                                                        "text": key
                                                    },
                                                    "value": value
                                                })
        return self.__assignee_list

    def dev_team_escalation_modal(self, app_context, trigger_id):
        """
            Method to create and open the dev-team-escalation modal on Slack
        """
        view = '''{
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Create a Github task"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "title_block",
                    "label": {
                        "type": "plain_text",
                        "text": "Subject"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_title",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Type in here"
                        },
                        "multiline": false
                    },
                    "optional": false
                },
                {
                    "type": "input",
                    "block_id": "description_block",
                    "label": {
                        "type": "plain_text",
                        "text": "Description of the issue"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_description",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Describe the issue."
                        },
                        "multiline": true
                    },
                    "optional": false
                },
                {
                    "type": "input",
                    "block_id": "investigation_block",
                    "label": {
                        "type": "plain_text",
                        "text": "Investigation performed"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "investigation_block",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Describe the investigations you already performed."
                        },
                        "multiline": true
                    },
                    "optional": false
                },
                {
                    "type": "input",
                    "block_id": "replication_block",
                    "label": {
                        "type": "plain_text",
                        "text": "How to replicate the issue"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "replication_block",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Describe the steps to replicate."
                        },
                        "multiline": true
                    },
                    "optional": false
                }
            ],
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "submit": {
                "type": "plain_text",
                "text": "Save"
            },
            "private_metadata": "",
            "callback_id": "ttl_dev_team_escalation_modal_submit"
        }'''
        self.send_modal(app_context, view, trigger_id)

    def create_github_task_modal(self, app_context, trigger_id):
        """
            Method to create and open the Create github task modal on Slack
        """
        assignee_list = self.__get_assignee_list()
        view = '''{
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Create a Github task"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "title_block",
                    "label": {
                        "type": "plain_text",
                        "text": "Title of the task"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_title",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Type in here"
                        },
                        "multiline": false
                    },
                    "optional": false
                },
                {
                    "type": "input",
                    "block_id": "description_block",
                    "label": {
                        "type": "plain_text",
                        "text": "Description of the task"
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "task_description",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Describe the task, or provide a Slack thread link."
                        },
                        "multiline": true
                    },
                    "optional": false
                },
                {
                    "type": "input",
                    "block_id": "immediately_block",
                    "element": {
                        "type": "checkboxes",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "The task must be handled immediately.",
                                    "emoji": true
                                },
                                "value": "handle_immediately"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Immediate escalation"
                    },
                    "optional": true
                },
                {
                    "type": "section",
                    "block_id": "assignee_block",
                    "text": {
                        "type": "plain_text",
                        "text": "Select a engineering teammate:"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Assign the task to a teammate."
                        },
                        "options": ''' + json.dumps(assignee_list) + '''
                    }
                }
            ],
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "submit": {
                "type": "plain_text",
                "text": "Save"
            },
            "private_metadata": "",
            "callback_id": "ttl_create_github_task_modal_submit"
        }'''
        self.send_modal(app_context, view, trigger_id)

    def send_modal(self, app_context, view, trigger_id):
        """
            Handles the API request to post a modal
        """
        request_open_view_header = {"Authorization": "Bearer " + self._get_slack_bot_user_token(app_context)}
        request_open_view_payload = {}
        request_open_view_payload['view'] = view
        request_open_view_payload['trigger_id'] = trigger_id
        requests.post(url=self.open_view_url, headers=request_open_view_header, json=request_open_view_payload, timeout=3000)
