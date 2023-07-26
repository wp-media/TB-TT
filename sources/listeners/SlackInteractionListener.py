import json


from flask_slacksigauth import slack_sig_auth
from flask import Response, request

from sources.handlers.SlackShortcutHandler import SlackShortcutHandler
from sources.handlers.SlackViewSubmissionHandler import SlackViewSubmissionHandler

class SlackInteractionListener():

    slack_shortcut_handler = None
    slack_view_submission_handler = None

    def __init__(self):
        self.slack_shortcut_handler = SlackShortcutHandler()
        self.slack_view_submission_handler = SlackViewSubmissionHandler()
        return

    @slack_sig_auth
    def __call__(self):
        # Retrieve the payload of the POST request
        payload_json = json.loads(request.form.get('payload'))

        # Route the request to the correct handler
        payload_type = payload_json['type']
        response_payload = {}
        try:
            if 'view_submission' == payload_type:
                response_payload = self.slack_view_submission_handler.process(payload_json)
            elif 'shortcut' == payload_type:
                response_payload = self.slack_shortcut_handler.process(payload_json)
            else:
                raise ValueError('Unknown payload type.')
        except ValueError as error:
            return str(error), 500
        except KeyError as error:
            return str(error), 500
        except NotImplementedError as error:
            return str(error), 501
        except Exception as error:
            return str(error), 500
        return response_payload, 200
