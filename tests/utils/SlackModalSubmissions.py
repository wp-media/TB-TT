"""
    This file provides Slack modal submission payloads for testing purposes
"""

# pylint: disable=line-too-long


class SlackModalSubmissionRequestRepo():
    """
        This class generates Slack modal submission payloads for testing purposes
    """

    def get_general_shortcut_github_task_submission_basic(self):
        """
            Returns the submsission payload of the general shortcut Github task creation modal
             with no assignee and no urgent escalation.
        """
        return {"type": "view_submission", "team": {"id": "T05GU5920KZ", "domain": "mathieulamiot"}, "user": {"id": "U05H21P562J", "username": "mathieu.lamiot", "name": "mathieu.lamiot", "team_id": "T05GU5920KZ"}, "api_app_id": "A05GU5C6EDD", "token": "si73v0oRnpIlVGA8vDKjD3Q2", "trigger_id": "5684005076758.5572179068679.457a01364047b762a19724c4cbdbdccb", "view": {"id": "V05LD2X8PPE", "team_id": "T05GU5920KZ", "type": "modal", "blocks": [{"type": "input", "block_id": "title_block", "label": {"type": "plain_text", "text": "Title of the task", "emoji": True}, "optional": False, "dispatch_action": False, "element": {"type": "plain_text_input", "action_id": "task_title", "placeholder": {"type": "plain_text", "text": "Type in here", "emoji": True}, "multiline": False, "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]}}}, {"type": "input", "block_id": "description_block", "label": {"type": "plain_text", "text": "Description of the task", "emoji": True}, "optional": False, "dispatch_action": False, "element": {"type": "plain_text_input", "action_id": "task_description", "placeholder": {"type": "plain_text", "text": "Describe the task, or provide a Slack thread link.", "emoji": True}, "multiline": True, "dispatch_action_config": {"trigger_actions_on": ["on_enter_pressed"]}}}, {"type": "input", "block_id": "immediately_block", "label": {"type": "plain_text", "text": "Immediate escalation", "emoji": True}, "optional": True, "dispatch_action": False, "element": {"type": "checkboxes", "options": [{"text": {"type": "plain_text", "text": "The task must be handled immediately.", "emoji": True}, "value": "handle_immediately"}], "action_id": "=efyj"}}, {"type": "section", "block_id": "assignee_block", "text": {"type": "plain_text", "text": "Select a engineering teammate:", "emoji": True}, "accessory": {"type": "static_select", "placeholder": {"type": "plain_text", "text": "Assign the task to a teammate.", "emoji": True}, "options": [{"text": {"type": "plain_text", "text": "No assignee", "emoji": True}, "value": "no-assignee"}, {"text": {"type": "plain_text", "text": "Ahmed Saeed", "emoji": True}, "value": "engahmeds3ed"}, {"text": {"type": "plain_text", "text": "Rémy Perona", "emoji": True}, "value": "Tabrisrp"}, {"text": {"type": "plain_text", "text": "Mostafa Hisham", "emoji": True}, "value": "mostafa-hisham"}, {"text": {"type": "plain_text", "text": "Nicolas Mollet", "emoji": True}, "value": "nicomollet"}, {"text": {"type": "plain_text", "text": "Cyrille Coquard", "emoji": True}, "value": "CrochetFeve025"}, {"text": {"type": "plain_text", "text": "John Gathure", "emoji": True}, "value": "johngathure"}, {"text": {"type": "plain_text", "text": "Michael Lee", "emoji": True}, "value": "jeawhanlee"}, {"text": {"type": "plain_text", "text": "Mathieu Lamiot", "emoji": True}, "value": "MathieuLamiot"}], "action_id": "JX24N"}}], "private_metadata": "", "callback_id": "ttl_create_github_task_modal_submit", "state": {"values": {"title_block": {"task_title": {"type": "plain_text_input", "value": "This is a test"}}, "description_block": {"task_description": {"type": "plain_text_input", "value": "This is a test task"}}, "immediately_block": {"=efyj": {"type": "checkboxes", "selected_options": []}}, "assignee_block": {"JX24N": {"type": "static_select", "selected_option": None}}}}, "hash": "1691135316.ebAt9hdW", "title": {"type": "plain_text", "text": "Create a Github task", "emoji": True}, "clear_on_close": False, "notify_on_close": False, "close": {"type": "plain_text", "text": "Cancel", "emoji": True}, "submit": {"type": "plain_text", "text": "Save", "emoji": True}, "previous_view_id": None, "root_view_id": "V05LD2X8PPE", "app_id": "A05GU5C6EDD", "external_id": "", "app_installed_team_id": "T05GU5920KZ", "bot_id": "B05HYCNFLN4"}, "response_urls": [], "is_enterprise_install": False, "enterprise": None}  # noqa

    def get_command_dev_team_escalation_basic(self):
        """
            Returns the submsission payload of the general shortcut Github task creation modal
             with no assignee and no urgent escalation.
        """
        return {
                "type": "view_submission",
                "team": {
                    "id": "T05GU5920KZ",
                    "domain": "mathieulamiot"
                },
                "user": {
                    "id": "U05H21P562J",
                    "username": "mathieu.lamiot",
                    "name": "mathieu.lamiot",
                    "team_id": "T05GU5920KZ"
                },
                "api_app_id": "A05GU5C6EDD",
                "token": "si73v0oRnpIlVGA8vDKjD3Q2",
                "trigger_id": "5707067509811.5572179068679.f23161f189dbb8329feeb02e823c5330",
                "view": {
                    "id": "V05LLFBMZAA",
                    "team_id": "T05GU5920KZ",
                    "type": "modal",
                    "blocks": [
                        {
                            "type": "input",
                            "block_id": "title_block",
                            "label": {
                                "type": "plain_text",
                                "text": "Subject",
                                "emoji": "True"
                            },
                            "optional": "False",
                            "dispatch_action": "False",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "task_title",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Type in here",
                                    "emoji": "True"
                                },
                                "multiline": "False",
                                "dispatch_action_config": {
                                    "trigger_actions_on": [
                                        "on_enter_pressed"
                                    ]
                                }
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "description_block",
                            "label": {
                                "type": "plain_text",
                                "text": "Description of the issue",
                                "emoji": "True"
                            },
                            "optional": "False",
                            "dispatch_action": "False",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "task_description",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Describe the issue.",
                                    "emoji": "True"
                                },
                                "multiline": "True",
                                "dispatch_action_config": {
                                    "trigger_actions_on": [
                                        "on_enter_pressed"
                                    ]
                                }
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "investigation_block",
                            "label": {
                                "type": "plain_text",
                                "text": "Investigation performed",
                                "emoji": "True"
                            },
                            "optional": "False",
                            "dispatch_action": "False",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "investigation_block",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Describe the investigations you already performed.",
                                    "emoji": "True"
                                },
                                "multiline": "True",
                                "dispatch_action_config": {
                                    "trigger_actions_on": [
                                        "on_enter_pressed"
                                    ]
                                }
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "replication_block",
                            "label": {
                                "type": "plain_text",
                                "text": "How to replicate the issue",
                                "emoji": "True"
                            },
                            "optional": "False",
                            "dispatch_action": "False",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "replication_block",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Describe the steps to replicate.",
                                    "emoji": "True"
                                },
                                "multiline": "True",
                                "dispatch_action_config": {
                                    "trigger_actions_on": [
                                        "on_enter_pressed"
                                    ]
                                }
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "link_helpscout_block",
                            "label": {
                                "type": "plain_text",
                                "text": "How to replicate the issue",
                                "emoji": "True"
                            },
                            "optional": "False",
                            "dispatch_action": "False",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "link_helpscout",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Describe the steps to replicate.",
                                    "emoji": "True"
                                },
                                "multiline": "True",
                                "dispatch_action_config": {
                                    "trigger_actions_on": [
                                        "on_enter_pressed"
                                    ]
                                }
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "link_slack_block",
                            "label": {
                                "type": "plain_text",
                                "text": "How to replicate the issue",
                                "emoji": "True"
                            },
                            "optional": "False",
                            "dispatch_action": "False",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "link_slack",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Describe the steps to replicate.",
                                    "emoji": "True"
                                },
                                "multiline": "True",
                                "dispatch_action_config": {
                                    "trigger_actions_on": [
                                        "on_enter_pressed"
                                    ]
                                }
                            }
                        }

                    ],
                    "private_metadata": "",
                    "callback_id": "ttl_dev_team_escalation_modal_submit",
                    "state": {
                        "values": {
                            "title_block": {
                                "task_title": {
                                    "type": "plain_text_input",
                                    "value": "a"
                                }
                            },
                            "description_block": {
                                "task_description": {
                                    "type": "plain_text_input",
                                    "value": "b"
                                }
                            },
                            "investigation_block": {
                                "investigation_block": {
                                    "type": "plain_text_input",
                                    "value": "c"
                                }
                            },
                            "replication_block": {
                                "replication_block": {
                                    "type": "plain_text_input",
                                    "value": "d"
                                }
                            },
                            "link_helpscout_block": {
                                "link_helpscout": {
                                    "type": "plain_text_input",
                                    "value": "d"
                                }
                            },
                            "link_slack_block": {
                                "link_slack": {
                                    "type": "plain_text_input",
                                    "value": None
                                }
                            }
                        }
                    },
                    "hash": "1691487692.HLYyqqD9",
                    "title": {
                        "type": "plain_text",
                        "text": "Create a Github task",
                        "emoji": "True"
                    },
                    "clear_on_close": "False",
                    "notify_on_close": "False",
                    "close": {
                        "type": "plain_text",
                        "text": "Cancel",
                        "emoji": "True"
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Save",
                        "emoji": "True"
                    },
                    "previous_view_id": "None",
                    "root_view_id": "V05LLFBMZAA",
                    "app_id": "A05GU5C6EDD",
                    "external_id": "",
                    "app_installed_team_id": "T05GU5920KZ",
                    "bot_id": "B05HYCNFLN4"
                },
                "response_urls": [],
                "is_enterprise_install": "False",
                "enterprise": "None"
        } # noqa
