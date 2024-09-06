"""
    This module defines the handler for GitHub Release related logic.
"""
import json
from pathlib import Path
from sources.factories.SlackMessageFactory import SlackMessageFactory
from sources.factories.NotionFactory import NotionFactory


class GithubReleaseHandler():
    """
        Class managing the business logic related to Github releases

    """
    def __init__(self):
        """
            The handler instanciates the objects it needed to complete the processing of the request.
        """
        self.slack_message_factory = SlackMessageFactory()
        self.notion_factory = NotionFactory()
        with open(Path(__file__).parent.parent.parent / "config" / "github.json", encoding='utf-8') as file_github_config:
            self.github_config = json.load(file_github_config)

    def process_release(self, app_context, release_params):
        """
            Processing method when a github release is released
        """
        # Replace the repository name by its readable name
        repository_readable_name = self.github_config["repoNameToReadable"][release_params.repository_name]
        release_params.repository_name = repository_readable_name
        # Create a page in the Notion database
        notion_url = self.notion_factory.create_release_note(app_context, release_params)

        # Send a message to Slack
        text = "The draft release note for " + repository_readable_name + " " + release_params.version
        text += " is available on <" + notion_url + "|Notion>."
        text += "\n"
        text += release_params.body

        blocks = self.slack_message_factory.get_release_note_review_blocks(text)

        self.slack_message_factory.post_message(app_context,
                                                self.slack_message_factory.get_channel('ops'),
                                                text, blocks)
