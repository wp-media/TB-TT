"""
    Unit tests for the GithubWebhookHandler.py main file
"""
from threading import Thread
from unittest.mock import patch
from flask import Flask
from sources.handlers.GithubWebhookHandler import GithubWebhookHandler

# pylint: disable=unused-argument


@patch.object(Thread, 'start')
def test_process_project_item_v2_assignee_update(mock_thread_start):
    """
        Test that an incoming webhook for updated assignee of a project item v2 is processed
    """
    github_webhook_handler = GithubWebhookHandler()
    payload = {
        "action": "edited",
        "projects_v2_item": {
            "id": 37263884,
            "node_id": "PVTI_lADOAMEyYM4ASOQZzgI4mgw",
            "project_node_id": "PVT_kwDOAMEyYM4AaLeb",
            "content_node_id": "DI_lADOAMEyYM4ASOQZzgDzxWE",
            "content_type": "DraftIssue",
            "creator": {
                "login": "MathieuLamiot",
                "id": 15233030,
                "node_id": "MDQ6VXNlcjE1MjMzMDMw",
                "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/MathieuLamiot",
                "html_url": "https://github.com/MathieuLamiot",
                "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
                "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
                "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
                "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
                "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
                "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
                "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
                "type": "User",
                "site_admin": False
            },
            "created_at": "2023-08-30T16:18:57Z",
            "updated_at": "2023-08-30T16:21:16Z",
            "archived_at": None
        },
        "changes": {
            "field_value": {
                "field_node_id": "PVTF_lADOAMEyYM4ASOQZzgLoyz4",
                "field_type": "assignees"
            }
        },
        "organization": {
            "login": "wp-media",
            "id": 12661344,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEyNjYxMzQ0",
            "url": "https://api.github.com/orgs/wp-media",
            "repos_url": "https://api.github.com/orgs/wp-media/repos",
            "events_url": "https://api.github.com/orgs/wp-media/events",
            "hooks_url": "https://api.github.com/orgs/wp-media/hooks",
            "issues_url": "https://api.github.com/orgs/wp-media/issues",
            "members_url": "https://api.github.com/orgs/wp-media/members{/member}",
            "public_members_url": "https://api.github.com/orgs/wp-media/public_members{/member}",
            "avatar_url": "https://avatars.githubusercontent.com/u/12661344?v=4",
            "description": "Our mission? Make the web Better, Faster and Lighter!"
        },
        "sender": {
            "login": "MathieuLamiot",
            "id": 15233030,
            "node_id": "MDQ6VXNlcjE1MjMzMDMw",
            "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/MathieuLamiot",
            "html_url": "https://github.com/MathieuLamiot",
            "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
            "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
            "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
            "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
            "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
            "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
            "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
            "type": "User",
            "site_admin": False
        }
    }
    app = Flask('test')
    with app.app_context():
        github_webhook_handler.process(payload)
    mock_thread_start.assert_called_once()


@patch.object(Thread, 'start')
def test_process_project_item_v2_status_update(mock_thread_start):
    """
        Test that an incoming webhook for updated status of a project item v2 is processed
    """
    github_webhook_handler = GithubWebhookHandler()
    payload = {
        "action": "edited",
        "projects_v2_item": {
            "id": 37263884,
            "node_id": "PVTI_lADOAMEyYM4ASOQZzgI4mgw",
            "project_node_id": "PVT_kwDOAMEyYM4AaLeb",
            "content_node_id": "DI_lADOAMEyYM4ASOQZzgDzxWE",
            "content_type": "DraftIssue",
            "creator": {
                "login": "MathieuLamiot",
                "id": 15233030,
                "node_id": "MDQ6VXNlcjE1MjMzMDMw",
                "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/MathieuLamiot",
                "html_url": "https://github.com/MathieuLamiot",
                "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
                "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
                "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
                "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
                "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
                "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
                "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
                "type": "User",
                "site_admin": False
            },
            "created_at": "2023-08-30T16:18:57Z",
            "updated_at": "2023-08-30T16:21:16Z",
            "archived_at": None
        },
        "changes": {
            "field_value": {
                "field_node_id": "PVTSSF_lADOAMEyYM4AaLebzgQxzGc",
                "field_type": "single_select"
            }
        },
        "organization": {
            "login": "wp-media",
            "id": 12661344,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEyNjYxMzQ0",
            "url": "https://api.github.com/orgs/wp-media",
            "repos_url": "https://api.github.com/orgs/wp-media/repos",
            "events_url": "https://api.github.com/orgs/wp-media/events",
            "hooks_url": "https://api.github.com/orgs/wp-media/hooks",
            "issues_url": "https://api.github.com/orgs/wp-media/issues",
            "members_url": "https://api.github.com/orgs/wp-media/members{/member}",
            "public_members_url": "https://api.github.com/orgs/wp-media/public_members{/member}",
            "avatar_url": "https://avatars.githubusercontent.com/u/12661344?v=4",
            "description": "Our mission? Make the web Better, Faster and Lighter!"
        },
        "sender": {
            "login": "MathieuLamiot",
            "id": 15233030,
            "node_id": "MDQ6VXNlcjE1MjMzMDMw",
            "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/MathieuLamiot",
            "html_url": "https://github.com/MathieuLamiot",
            "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
            "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
            "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
            "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
            "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
            "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
            "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
            "type": "User",
            "site_admin": False
        }
    }
    app = Flask('test')
    with app.app_context():
        github_webhook_handler.process(payload)
    mock_thread_start.assert_called_once()


@patch.object(Thread, 'start')
def test_process_project_item_v2_irrelevant_update(mock_thread_start):
    """
        Test that an incoming webhook for update of a not used field of a project item v2 is not processed
    """
    github_webhook_handler = GithubWebhookHandler()
    payload = {
        "action": "edited",
        "projects_v2_item": {
            "id": 37263884,
            "node_id": "PVTI_lADOAMEyYM4ASOQZzgI4mgw",
            "project_node_id": "PVT_kwDOAMEyYM4ASOQZ",
            "content_node_id": "DI_lADOAMEyYM4ASOQZzgDzxWE",
            "content_type": "DraftIssue",
            "creator": {
                "login": "MathieuLamiot",
                "id": 15233030,
                "node_id": "MDQ6VXNlcjE1MjMzMDMw",
                "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/MathieuLamiot",
                "html_url": "https://github.com/MathieuLamiot",
                "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
                "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
                "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
                "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
                "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
                "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
                "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
                "type": "User",
                "site_admin": False
            },
            "created_at": "2023-08-30T16:18:57Z",
            "updated_at": "2023-08-30T16:21:16Z",
            "archived_at": None
        },
        "changes": {
            "field_value": {
                "field_node_id": "PVTIF_lADOAMEyYM4ASOQZzgL-iB8",
                "field_type": "iteration"
            }
        },
        "organization": {
            "login": "wp-media",
            "id": 12661344,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEyNjYxMzQ0",
            "url": "https://api.github.com/orgs/wp-media",
            "repos_url": "https://api.github.com/orgs/wp-media/repos",
            "events_url": "https://api.github.com/orgs/wp-media/events",
            "hooks_url": "https://api.github.com/orgs/wp-media/hooks",
            "issues_url": "https://api.github.com/orgs/wp-media/issues",
            "members_url": "https://api.github.com/orgs/wp-media/members{/member}",
            "public_members_url": "https://api.github.com/orgs/wp-media/public_members{/member}",
            "avatar_url": "https://avatars.githubusercontent.com/u/12661344?v=4",
            "description": "Our mission? Make the web Better, Faster and Lighter!"
        },
        "sender": {
            "login": "MathieuLamiot",
            "id": 15233030,
            "node_id": "MDQ6VXNlcjE1MjMzMDMw",
            "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/MathieuLamiot",
            "html_url": "https://github.com/MathieuLamiot",
            "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
            "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
            "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
            "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
            "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
            "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
            "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
            "type": "User",
            "site_admin": False
        }
    }
    app = Flask('test')
    with app.app_context():
        github_webhook_handler.process(payload)
    mock_thread_start.assert_not_called()


@patch.object(Thread, 'start')
def test_process_project_item_v2_creation(mock_thread_start):
    """
        Test that an incoming webhook for update of a not used field of a project item v2 is not processed
    """
    github_webhook_handler = GithubWebhookHandler()
    payload = {
        "action": "created",
        "projects_v2_item": {
            "id": 37263884,
            "node_id": "PVTI_lADOAMEyYM4ASOQZzgI4mgw",
            "project_node_id": "PVT_kwDOAMEyYM4ASOQZ",
            "content_node_id": "DI_lADOAMEyYM4ASOQZzgDzxWE",
            "content_type": "DraftIssue",
            "creator": {
                "login": "MathieuLamiot",
                "id": 15233030,
                "node_id": "MDQ6VXNlcjE1MjMzMDMw",
                "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/MathieuLamiot",
                "html_url": "https://github.com/MathieuLamiot",
                "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
                "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
                "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
                "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
                "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
                "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
                "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
                "type": "User",
                "site_admin": False
            },
            "created_at": "2023-08-30T16:18:57Z",
            "updated_at": "2023-08-30T16:18:57Z",
            "archived_at": None
        },
        "organization": {
            "login": "wp-media",
            "id": 12661344,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEyNjYxMzQ0",
            "url": "https://api.github.com/orgs/wp-media",
            "repos_url": "https://api.github.com/orgs/wp-media/repos",
            "events_url": "https://api.github.com/orgs/wp-media/events",
            "hooks_url": "https://api.github.com/orgs/wp-media/hooks",
            "issues_url": "https://api.github.com/orgs/wp-media/issues",
            "members_url": "https://api.github.com/orgs/wp-media/members{/member}",
            "public_members_url": "https://api.github.com/orgs/wp-media/public_members{/member}",
            "avatar_url": "https://avatars.githubusercontent.com/u/12661344?v=4",
            "description": "Our mission? Make the web Better, Faster and Lighter!"
        },
        "sender": {
            "login": "MathieuLamiot",
            "id": 15233030,
            "node_id": "MDQ6VXNlcjE1MjMzMDMw",
            "avatar_url": "https://avatars.githubusercontent.com/u/15233030?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/MathieuLamiot",
            "html_url": "https://github.com/MathieuLamiot",
            "followers_url": "https://api.github.com/users/MathieuLamiot/followers",
            "following_url": "https://api.github.com/users/MathieuLamiot/following{/other_user}",
            "gists_url": "https://api.github.com/users/MathieuLamiot/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/MathieuLamiot/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/MathieuLamiot/subscriptions",
            "organizations_url": "https://api.github.com/users/MathieuLamiot/orgs",
            "repos_url": "https://api.github.com/users/MathieuLamiot/repos",
            "events_url": "https://api.github.com/users/MathieuLamiot/events{/privacy}",
            "received_events_url": "https://api.github.com/users/MathieuLamiot/received_events",
            "type": "User",
            "site_admin": False
        }
    }
    app = Flask('test')
    with app.app_context():
        github_webhook_handler.process(payload)
    mock_thread_start.assert_not_called()
