# TB-TT
This app is a helper bot  for the Engineering team at WP Media, leveraging Slack and GitHub integrations for better agile workflows.

## Configuration
To run the app, you must first configure it with Slack and GitHub information, including credentials.
To do so, fill the different json files in the config folder.

### Slack integration
The Slack integration requires the app to be declared and installed as a Slack App. The "interactivity" feature must be configured and webhooks directed to the app server.

## Running the app
Run the script app.py
The app will listen on the configured port for API calls.

## Features
### Create GitHub tasks from Slack
The Slack app adds a shortcut to create a GitHub task in the configured GitHub Project(V2). When triggered, a modal is opened to fill out information related to the task.
