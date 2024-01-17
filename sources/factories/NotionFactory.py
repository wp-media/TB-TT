"""
    This module defines the factory for Notion API
"""
from datetime import date
import json
from pathlib import Path
import requests
from flask import current_app
import sources.utils.Constants as cst
from sources.models.GithubReleaseParam import GithubReleaseParam


class NotionFactory():
    """
        Class managing the API for OVH

    """
    def __init__(self):
        """
            The factory instanciates the objects it needed to complete the processing of the request.
        """
        self.api_key = None
        with open(Path(__file__).parent.parent.parent / "config" / "notion.json", encoding='utf-8') as file_notion_config:
            self.notion_config = json.load(file_notion_config)

    def _get_notion_api_key(self, app_context):
        """
            Return the Notion API key and creates it if needed
        """
        if self.api_key is None:
            app_context.push()
            self.api_key = current_app.config[cst.APP_CONFIG_TOKEN_NOTION_API_KEY]
        return self.api_key

    def _create_notion_db_row(self, app_context, db_id, properties, children):
        """
            Requests the creation of a row in a Notion DB through the API.
            Properties should match the DB columns, and children is the content of the created page.
        """
        headers = {
            'Authorization': 'Bearer ' + self._get_notion_api_key(app_context),
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',
        }

        data = {
            'parent': {'database_id': db_id},
            'properties': properties,
            'children': children
        }

        response = requests.post(
            'https://api.notion.com/v1/pages',
            headers=headers,
            json=data,
            timeout=3000
        )

        if response.status_code != 200:
            raise ValueError('Notion API could not create the DB row.')
        page_id = response.json().get('id')
        page_url = f'https://www.notion.so/{page_id}'
        return page_url

    def create_release_note(self, app_context, release_params: GithubReleaseParam):
        """
            Creates a release note in Notion for a GitHub release.
        """
        today = date.today()

        properties = {
            "Version": {
                "title": [
                    {
                        "text": {
                            "content": release_params.version
                        }
                    }
                ]
            },
            "Product": {
                "select": {
                    "name": release_params.repository_name
                }
            },
            'date_property': {
                'date': {
                    'start': today.strftime("%Y-%m-%d")
                }
            }
        }

        content = [
            {
                "object": "block",
                "heading_2": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "Complete Changelog"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": release_params.body
                            },
                        }
                    ],
                    "color": "default"
                }
            },
            {
                "object": "block",
                "heading_2": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "User notes"
                            }
                        }
                    ]
                }
            }
        ]
        return self._create_notion_db_row(app_context, self.notion_config["release-note-db-id"], properties, content)
