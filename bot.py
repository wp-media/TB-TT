import json
import os
import requests
import time

from flask import Flask, Response, jsonify, request
from slackeventsapi import SlackEventAdapter
from threading import Thread
from slack import WebClient
from flask_slacksigauth import slack_sig_auth



# This `app` represents your existing Flask app
app = Flask(__name__)

greetings = ["hi", "hello", "hello there", "hey"]

app.config['SLACK_SIGNING_SECRET'] = os.environ['SLACK_SIGNING_SECRET']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
slack_token = os.environ['SLACK_BOT_TOKEN']
SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']

#instantiating slack client
slack_client = WebClient(slack_token)

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