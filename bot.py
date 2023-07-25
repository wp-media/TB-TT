import json
import os
import requests
import time
import jwt
import gql

from gql.transport.requests import RequestsHTTPTransport
from pathlib import Path
from flask import Flask, Response, jsonify, request
from slackeventsapi import SlackEventAdapter
from threading import Thread
from slack import WebClient
from flask_slacksigauth import slack_sig_auth



# This `app` represents your existing Flask app
app = Flask(__name__)

greetings = ["hi", "hello", "hello there", "hey"]


# Your GitHub access token from JSON file
file = open(Path(__file__).parent / "config" / "keys" / "tokens.json", encoding='utf-8')
file_token_data = json.load(file)
GITHUB_ACCESS_TOKEN = file_token_data["github_token"]
GITHUB_APP_ID = file_token_data["github_app_id"]
SLACK_SIGNING_SECRET = file_token_data["slack_signing_secret"]
app.config['SLACK_SIGNING_SECRET'] = SLACK_SIGNING_SECRET
SLACK_VERIFICATION_TOKEN = file_token_data["slack_verification_token"]
SLACK_BOT_USER_TOKEN = file_token_data["slack_bot_user_token"]


#instantiating slack client
slack_client = WebClient(SLACK_BOT_USER_TOKEN)

# An example of one of your Flask app's routes
@app.route("/")
def event_hook(received_request):
    json_dict = json.loads(received_request.body.decode("utf-8"))
    if json_dict["token"] != SLACK_VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict
    return {"status": 500}
    return


# An example of one of your Flask app's routes
@app.route("/slack/interaction", methods=['POST'])
@slack_sig_auth
def interaction_hook():
    print(request.headers)
    print(request.form)
    payload_json = json.loads(request.form.get('payload'))

    interaction_type = payload_json['type']

    if 'view_submission' == interaction_type:
        print('See this page to connect to Github: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation')
        """ Authentication as a GitHub app works but no visibility over the projectV2 is granted.
        #Generate JWT
        pem_path = Path(__file__).parent / "config/keys/techteambot.2023-07-23.private-key.pem"
        with open(pem_path, 'rb') as pem_file:
            signing_key = jwt.jwk_from_pem(pem_file.read())
            payload = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's identifier
            'iss': GITHUB_APP_ID
            }
            # Create JWT
            jwt_instance = jwt.JWT()
            encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')
            print(f"JWT:  {encoded_jwt}")

            #Retrieve access token
            url = 'https://api.github.com/app/installations/39984386/access_tokens'
            headers = {'Accept':'application/vnd.github+json', 'X-GitHub-Api-Version':'2022-11-28', 'Authorization': 'Bearer ' + encoded_jwt}
            token_response = requests.post(url, headers=headers)
            token_response_payload = token_response.json()
            access_token = token_response_payload['token']
            print(f"access_token:  {access_token}")
        """
        #Create task
        # GitHub API endpoint

        url = 'https://api.github.com/graphql'
        # Set up the HTTP transport and add authentication header
        transport = RequestsHTTPTransport(
            url=url, headers={'Authorization': f'Bearer {GITHUB_ACCESS_TOKEN}'})
        # Create a GraphQL client
        client = gql.Client(transport=transport, fetch_schema_from_transport=True)
        query = gql.gql(
            """
            mutation CreateProjectV2Task($task: AddProjectV2DraftIssueInput!) {
                addProjectV2DraftIssue(input: $task) {
                    clientMutationId
                }
            }
        """
        )
        params = {
            "task": {"body": 'This is the body', "title": "This is the title", "clientMutationId":'my_key', 'projectId':'PVT_kwHOAOhwBs4ANXSV' },
        }
        result = client.execute(query, variable_values=params)
        print(result)
        return {"response_action": "clear"}
    elif 'shortcut' == interaction_type:
        callback = payload_json['callback_id']
        if 'ttl_create_github_task_general_shortcut' == callback:
            print('create github task')
            view = '''{
                    "type": "modal",
                    "title": {
                        "type": "plain_text",
                        "text": "Create a Github task"
                    },
                    "blocks": [
                        {
                            "type": "input",
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
                            "label": {
                                "type": "plain_text",
                                "text": "Description of the task"
                            },
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "task_title",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Describe the task, or provide a Slack thread link."
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
                    "callback_id": "ttl_create_github_task_modal_submit"
                    }'''

            request_open_view_payload = dict()
            request_open_view_header = {"Authorization": "Bearer " + SLACK_BOT_USER_TOKEN}
            request_open_view_payload['view'] = view
            request_open_view_payload['trigger_id'] = payload_json['trigger_id']
            response = requests.post(url='https://slack.com/api/views.open', headers=request_open_view_header, json=request_open_view_payload, timeout=3000)
            print(response)
        else:
            return Response(status=501)
    else:
        return Response(status=501)
    return Response(status=200)

# An example of one of your Flask app's routes
@app.route("/slack/command", methods=['POST'])
@slack_sig_auth
def command_hook():
    def post_command(form):
        print("command_hook")
        print(form)
        message = {
            # Uncomment the line below for the response to be visible to everyone
            'response_type': 'in_channel',
            'text': 'More fleshed out response to the slash command',
            'attachments': [
                {
                    'fallback': 'Required plain-text summary of the attachment.',
                    'color': '#36a64f',
                    'pretext': 'Optional text above the attachment block',
                    'author_name': 'Bobby Tables',
                    'author_link': 'http://flickr.com/bobby/',
                    'author_icon': 'http://flickr.com/icons/bobby.jpg',
                    'title': 'Slack API Documentation',
                    'title_link': 'https://api.slack.com/',
                    'text': 'Optional text that appears within the attachment',
                    'fields': [
                        {
                            'title': 'Priority',
                            'value': 'High',
                            'short': False
                        }
                    ],
                    'image_url': 'http://my-website.com/path/to/image.jpg',
                    'thumb_url': 'http://example.com/path/to/thumb.png'
                }
            ]
        }
        requests.post(url=form.get('response_url'), json=message)
        return
    if request.form.get('response_url') != SLACK_VERIFICATION_TOKEN:
        return {"status": 403}
    thread = Thread(target=post_command, kwargs={"form": request.form})
    thread.start()
    return Response(status=200)

slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)  


@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    def send_reply(value):
        event_data = value
        message = event_data["event"]
        if message.get("subtype") is None:
            command = message.get("text")
            channel_id = message["channel"]
            if any(item in command.lower() for item in greetings):
                message = (
                    "Hello <@%s>! :tada:"
                    % message["user"]  # noqa
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)


# Start the server on port 3000
if __name__ == "__main__":
  app.run(port=3000)